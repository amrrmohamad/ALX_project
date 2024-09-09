import sqlite3

# Create a data base and tables to storage data "users.db"
# you can comment this function i you don't want delete database
def init_db():
    with sqlite3.connect('./users.db') as data:
        data.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                email TEXT NOT NULL
            )
        ''')
    print("Database and tables created successfully.")

# don't run file from here
if __name__ ==  "__name__":
    exit()