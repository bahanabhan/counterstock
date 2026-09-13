import requests

BASE_URL = "http://localhost:8000"
HEADERS = {}

def get_menu():
    r = requests.get(f"{BASE_URL}/menu", timeout=5)
    r.raise_for_status()
    return r.json()

def get_low_stock():
    r = requests.get(f"{BASE_URL}/ingredients/low-stock", timeout=5)
    r.raise_for_status()
    return r.json()

def place_order(menu_item_id: int, quantity: int):
    payload = {
        "staff_id": 1,
        "items": [{"menu_item_id": menu_item_id, "quantity": quantity}]
    }
    r = requests.post(f"{BASE_URL}/orders", json=payload, headers=HEADERS, timeout=5)
    if r.status_code != 200:
        try:
            detail = r.json().get("detail", r.text)
        except Exception:
            detail = r.text
        raise ValueError(f"HTTP {r.status_code}: {detail}")
    return r.json()

def restock_ingredient(ingredient_id: int, amount: float = 20.0):
    payload = {"amount": amount}
    r = requests.post(f"{BASE_URL}/ingredients/{ingredient_id}/restock", json=payload, headers=HEADERS, timeout=5)
    if r.status_code != 200:
        try:
            detail = r.json().get("detail", r.text)
        except Exception:
            detail = r.text
        raise ValueError(f"HTTP {r.status_code}: {detail}")
    return r.json()
