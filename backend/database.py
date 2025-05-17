import mysql.connector
from mysql.connector import pooling

db_config = {
    "host": "localhost",
    "user": "your_user",
    "password": "your_password",
    "database": "your_db"
}

pool = pooling.MySQLConnectionPool(pool_name="mypool", pool_size=5, **db_config)

def get_db():
    conn = pool.get_connection()
    try:
        yield conn
    finally:
        conn.close()

def create_tables():
    conn = pool.get_connection()
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        memberId VARCHAR(10) PRIMARY KEY,
        tier VARCHAR(20),
        email VARCHAR(100) UNIQUE,
        password VARCHAR(100),
        isAdmin BOOLEAN
    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS events (
        id VARCHAR(10) PRIMARY KEY,
        title VARCHAR(100),
        date DATE,
        maxSeats INT,
        seatsBooked INT,
        tier VARCHAR(20),
        description TEXT,
        imageUrl TEXT
    )""")
    conn.commit()
    cursor.close()
    conn.close()