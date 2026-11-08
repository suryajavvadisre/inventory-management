
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import get_connection

app = FastAPI()


class Product(BaseModel):
    name: str
    price: float
    quantity: int


@app.get("/")
def home():
    return {"message": "Welcome to Inventory Management System"}


# READ: Get all products
@app.get("/products")
def get_products():
    connection = get_connection()

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM products")

        products = cursor.fetchall()

        return [dict(product) for product in products]

    finally:
        connection.close()


# CREATE: Add a new product
@app.post("/products")
def add_product(product: Product):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO products (name, price, quantity)
            VALUES (?, ?, ?)
            """,
            (product.name, product.price, product.quantity)
        )

        connection.commit()

        new_id = cursor.lastrowid

        cursor.execute(
            "SELECT * FROM products WHERE id = ?",
            (new_id,)
        )

        new_product = cursor.fetchone()

        return dict(new_product)

    finally:
        connection.close()


# UPDATE: Update an existing product
@app.put("/products/{product_id}")
def update_product(product_id: int, updated_product: Product):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            "SELECT * FROM products WHERE id = ?",
            (product_id,)
        )

        existing_product = cursor.fetchone()

        if existing_product is None:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        cursor.execute(
            """
            UPDATE products
            SET name = ?, price = ?, quantity = ?
            WHERE id = ?
            """,
            (
                updated_product.name,
                updated_product.price,
                updated_product.quantity,
                product_id
            )
        )

        connection.commit()

        cursor.execute(
            "SELECT * FROM products WHERE id = ?",
            (product_id,)
        )

        updated_row = cursor.fetchone()

        return dict(updated_row)

    finally:
        connection.close()


# DELETE: Delete an existing product
@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            "SELECT * FROM products WHERE id = ?",
            (product_id,)
        )

        product = cursor.fetchone()

        if product is None:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        deleted_product = dict(product)

        cursor.execute(
            "DELETE FROM products WHERE id = ?",
            (product_id,)
        )

        connection.commit()

        return {
            "message": "Product deleted successfully",
            "product": deleted_product
        }

    finally:
        connection.close()
