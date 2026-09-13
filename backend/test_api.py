import pytest
import requests

BASE_URL = "http://localhost:8000"
VALID_HEADERS = {"X-API-Key": "secret_counterstock_key"}
INVALID_HEADERS = {"X-API-Key": "invalid_or_wrong_token"}

def test_get_menu_structure_and_availability():
    """Verify GET /menu returns status 200, valid structure, and computed portion count."""
    res = requests.get(f"{BASE_URL}/menu")
    assert res.status_code == 200
    menu = res.json()
    assert isinstance(menu, list)
    assert len(menu) > 0

    item = menu[0]
    expected_fields = {"id", "name", "category", "price", "available"}
    assert expected_fields.issubset(item.keys())
    assert isinstance(item["available"], int)
    assert item["available"] >= 0

def test_auth_rejection_on_protected_endpoints():
    """Verify POST /orders rejects requests with missing or invalid authentication (401)."""
    payload = {"staff_id": 1, "items": [{"menu_item_id": 1, "quantity": 1}]}

    # 1. Missing Header
    res_missing = requests.post(f"{BASE_URL}/orders", json=payload)
    assert res_missing.status_code == 401

    # 2. Invalid API Key
    res_invalid = requests.post(f"{BASE_URL}/orders", json=payload, headers=INVALID_HEADERS)
    assert res_invalid.status_code == 401

def test_insufficient_stock_rejection():
    """Verify ordering more than current inventory raises 409 Conflict."""
    oversized_order = {
        "staff_id": 1,
        "items": [{"menu_item_id": 1, "quantity": 99999}]
    }
    res = requests.post(f"{BASE_URL}/orders", json=oversized_order, headers=VALID_HEADERS)
    assert res.status_code == 409
    assert "Insufficient stock" in res.json().get("detail", "")

def test_successful_order_placement_and_deduction():
    """Verify a valid order decrements ingredient stock and creates an order record."""
    # Read initial portions
    menu_before = {m["id"]: m["available"] for m in requests.get(f"{BASE_URL}/menu").json()}
    initial_available = menu_before[1]

    # Ensure there is at least 1 portion available to test happy path
    if initial_available == 0:
        requests.post(f"{BASE_URL}/ingredients/1/restock", json={"amount": 20.0}, headers=VALID_HEADERS)
        requests.post(f"{BASE_URL}/ingredients/2/restock", json={"amount": 20.0}, headers=VALID_HEADERS)
        requests.post(f"{BASE_URL}/ingredients/3/restock", json={"amount": 20.0}, headers=VALID_HEADERS)

    order_payload = {
        "staff_id": 1,
        "items": [{"menu_item_id": 1, "quantity": 1}]
    }
    res = requests.post(f"{BASE_URL}/orders", json=order_payload, headers=VALID_HEADERS)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    order_id = data["order_id"]

    # Verify order lookup endpoint (GET /orders/{id})
    order_res = requests.get(f"{BASE_URL}/orders/{order_id}")
    assert order_res.status_code == 200
    order_data = order_res.json()
    assert order_data["id"] == order_id
    assert len(order_data["items"]) > 0

def test_low_stock_and_restock_workflow():
    """Verify restock endpoint updates quantity and returns 200."""
    restock_payload = {"amount": 10.0}
    res = requests.post(f"{BASE_URL}/ingredients/1/restock", json=restock_payload, headers=VALID_HEADERS)
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == 1
    assert "stock_quantity" in data

    # Verify low-stock list endpoint format
    low_res = requests.get(f"{BASE_URL}/ingredients/low-stock")
    assert low_res.status_code == 200
    assert isinstance(low_res.json(), list)
