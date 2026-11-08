import sqlite3

def get_connection():
    connection = sqlite3.connect("inventory.db")
    connection.row_factory = sqlite3.Row
    return connection

def create_table():
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL
        )
    """)

    connection.commit()
    connection.close()

create_table()