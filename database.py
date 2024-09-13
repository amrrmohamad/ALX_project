import sqlite3
import os

def get_db_connection():
    db_path = os.getenv('DATABASE', 'users.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn
# Create a data base and tables to storage data "users.db"
# you can comment this function i you don't want delete database
def init_db():
    try:
        with get_db_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    email TEXT NOT NULL
                )
            ''')
            conn.commit()
            print(" Database and tables created successfully.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")


