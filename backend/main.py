import os
from datetime import datetime
from decimal import Decimal
from typing import List
from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI(title="CounterStock API")

DATABASE_URL = os.environ.get("DATABASE_URL")
EXPECTED_TOKEN = os.environ.get("API_TOKEN", "secret_counterstock_key")

def get_db():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    try:
        yield conn
    finally:
        conn.close()

def verify_token(x_api_token: str = Header(None, alias="X-API-Token"), x_api_key: str = Header(None, alias="X-API-Key")):
    token = x_api_token or x_api_key
    if not token or token != EXPECTED_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid or missing API Key")

class OrderItemInput(BaseModel):
    menu_item_id: int
    quantity: int

class OrderCreate(BaseModel):
    staff_id: int = 1
    items: List[OrderItemInput]

class RestockInput(BaseModel):
    amount: float

@app.get("/menu")
def get_menu(conn=Depends(get_db)):
    query = """
    SELECT 
        m.id, m.name, m.category, m.price,
        COALESCE(FLOOR(MIN(i.stock_quantity / r.quantity_required)), 0)::INT AS available
    FROM menu_items m
    JOIN recipes r ON m.id = r.menu_item_id
    JOIN ingredients i ON r.ingredient_id = i.id
    WHERE m.active = TRUE
    GROUP BY m.id, m.name, m.category, m.price
    ORDER BY m.id;
    """
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()

@app.get("/ingredients/low-stock")
def get_low_stock(conn=Depends(get_db)):
    query = """
    SELECT id, name, unit, stock_quantity, reorder_threshold
    FROM ingredients
    WHERE stock_quantity <= reorder_threshold
    ORDER BY name;
    """
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()

@app.get("/orders/{order_id}")
def get_order(order_id: int, conn=Depends(get_db)):
    with conn.cursor() as cur:
        cur.execute("SELECT id, staff_id, order_time, status FROM orders WHERE id = %s;", (order_id,))
        order = cur.fetchone()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        cur.execute("""
            SELECT oi.menu_item_id, m.name, oi.quantity, oi.subtotal
            FROM order_items oi
            JOIN menu_items m ON oi.menu_item_id = m.id
            WHERE oi.order_id = %s;
        """, (order_id,))
        order["items"] = cur.fetchall()

        cur.execute("SELECT COALESCE(SUM(subtotal), 0) AS total FROM order_items WHERE order_id = %s;", (order_id,))
        order["total"] = cur.fetchone()["total"]
        return order

@app.post("/orders", dependencies=[Depends(verify_token)])
def create_order(payload: OrderCreate, conn=Depends(get_db)):
    if not payload.items:
        raise HTTPException(status_code=400, detail="Order cannot be empty")

    with conn:
        with conn.cursor() as cur:
            # 1. Aggregate required ingredients across all items
            item_counts = {}
            for it in payload.items:
                item_counts[it.menu_item_id] = item_counts.get(it.menu_item_id, 0) + it.quantity

            menu_ids = list(item_counts.keys())
            cur.execute("""
                SELECT menu_item_id, ingredient_id, quantity_required 
                FROM recipes 
                WHERE menu_item_id = ANY(%s);
            """, (menu_ids,))
            recipes = cur.fetchall()

            required_ingredients = {}
            for r in recipes:
                ing_id = r["ingredient_id"]
                needed = Decimal(str(r["quantity_required"])) * Decimal(item_counts[r["menu_item_id"]])
                required_ingredients[ing_id] = required_ingredients.get(ing_id, Decimal("0.0")) + needed

            # 2. Lock ingredient rows to eliminate race conditions
            ing_ids = list(required_ingredients.keys())
            cur.execute("""
                SELECT id, name, stock_quantity 
                FROM ingredients 
                WHERE id = ANY(%s) 
                FOR UPDATE;
            """, (ing_ids,))
            current_stocks = {row["id"]: row for row in cur.fetchall()}

            # 3. Verify stock availability (safe Decimal to Decimal comparison)
            for ing_id, needed in required_ingredients.items():
                current = current_stocks.get(ing_id)
                if not current or Decimal(str(current["stock_quantity"])) < needed:
                    raise HTTPException(
                        status_code=409, 
                        detail=f"Insufficient stock for {current['name'] if current else 'Ingredient'}"
                    )

            # 4. Deduct ingredient inventory
            for ing_id, needed in required_ingredients.items():
                cur.execute("""
                    UPDATE ingredients 
                    SET stock_quantity = stock_quantity - %s 
                    WHERE id = %s;
                """, (needed, ing_id))

            # 5. Insert order
            cur.execute("""
                INSERT INTO orders (staff_id, order_time, status) 
                VALUES (%s, %s, 'completed') RETURNING id;
            """, (payload.staff_id, datetime.now()))
            new_order_id = cur.fetchone()["id"]

            # 6. Insert order items
            cur.execute("SELECT id, price FROM menu_items WHERE id = ANY(%s);", (menu_ids,))
            prices = {row["id"]: row["price"] for row in cur.fetchall()}

            for m_id, qty in item_counts.items():
                subtotal = Decimal(str(prices[m_id])) * Decimal(qty)
                cur.execute("""
                    INSERT INTO order_items (order_id, menu_item_id, quantity, subtotal) 
                    VALUES (%s, %s, %s, %s);
                """, (new_order_id, m_id, qty, subtotal))

            return {"status": "success", "order_id": new_order_id}

@app.post("/ingredients/{ingredient_id}/restock", dependencies=[Depends(verify_token)])
def restock_ingredient(ingredient_id: int, payload: RestockInput, conn=Depends(get_db)):
    if payload.amount <= 0:
        raise HTTPException(status_code=400, detail="Restock amount must be positive")

    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE ingredients 
                SET stock_quantity = stock_quantity + %s 
                WHERE id = %s RETURNING id, name, stock_quantity;
            """, (Decimal(str(payload.amount)), ingredient_id))
            updated = cur.fetchone()
            if not updated:
                raise HTTPException(status_code=404, detail="Ingredient not found")
            return updated
