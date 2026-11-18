import sqlite3
import pytest
from fastapi.testclient import TestClient
import main


@pytest.fixture
def client(tmp_path, monkeypatch):

    # Create a temporary database for testing
    db_path = tmp_path / "test_inventory.db"

    connection = sqlite3.connect(db_path)

    connection.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL
        )
    """)

    connection.commit()
    connection.close()

    # Create a connection to the temporary database
    def get_test_connection():
        connection = sqlite3.connect(db_path)
        connection.row_factory = sqlite3.Row
        return connection

    # Replace the application's database connection for this test
    monkeypatch.setattr(main, "get_connection", get_test_connection)

    return TestClient(main.app)


def test_home_endpoint(client):

    response = client.get("/")

    assert response.status_code == 200

    assert response.json() == {
        "message": "Welcome to Inventory Management System"
    }


def test_get_products_empty(client):

    response = client.get("/products")

    assert response.status_code == 200

    assert response.json() == []

def test_add_product(client):

    product_data = {
        "name": "Laptop",
        "price": 55000,
        "quantity": 10
    }

    response = client.post(
        "/products",
        json=product_data
    )

    assert response.status_code == 200

    assert response.json()["name"] == "Laptop"
    assert response.json()["price"] == 55000
    assert response.json()["quantity"] == 10

def test_get_products_after_adding(client):

    product_data = {
        "name": "Monitor",
        "price": 15000,
        "quantity": 5
    }

    # First, add a product
    client.post("/products", json=product_data)

    # Now retrieve all products
    response = client.get("/products")

    assert response.status_code == 200

    products = response.json()

    assert len(products) == 1

    assert products[0]["name"] == "Monitor"
    assert products[0]["price"] == 15000
    assert products[0]["quantity"] == 5


def test_update_product(client):

    # First, create a product
    product_data = {
        "name": "Laptop",
        "price": 55000,
        "quantity": 10
    }

    create_response = client.post(
        "/products",
        json=product_data
    )

    # Get the ID of the newly created product
    product_id = create_response.json()["id"]

    # Prepare updated product information
    updated_data = {
        "name": "Gaming Laptop",
        "price": 75000,
        "quantity": 8
    }

    # Send PUT request
    response = client.put(
        f"/products/{product_id}",
        json=updated_data
    )

    # Verify the response
    assert response.status_code == 200
    assert response.json()["id"] == product_id
    assert response.json()["name"] == "Gaming Laptop"
    assert response.json()["price"] == 75000
    assert response.json()["quantity"] == 8


def test_delete_product(client):

    # First, create a product
    product_data = {
        "name": "Keyboard",
        "price": 2500,
        "quantity": 20
    }

    create_response = client.post(
        "/products",
        json=product_data
    )

    product_id = create_response.json()["id"]

    # Delete the product
    response = client.delete(
        f"/products/{product_id}"
    )

    # Verify deletion response
    assert response.status_code == 200

    assert response.json()["message"] == "Product deleted successfully"

    assert response.json()["product"]["id"] == product_id

    # Verify that the product no longer exists
    get_response = client.get("/products")

    assert get_response.status_code == 200

    assert get_response.json() == []

