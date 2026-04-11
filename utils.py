import sqlite3
import pandas as pd

def get_connection():
    return sqlite3.connect("database.db", check_same_thread=False)

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS providers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        city TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS receivers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        city TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS food (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT,
        city TEXT,
        quantity INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS claims (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city TEXT,
        status TEXT
    )
    """)

    conn.commit()

def fetch_data(table):
    conn = get_connection()
    return pd.read_sql(f"SELECT * FROM {table}", conn)

def insert_data(table, values):
    conn = get_connection()
    cursor = conn.cursor()

    placeholders = ",".join(["?"] * len(values))
    cursor.execute(f"INSERT INTO {table} VALUES (NULL, {placeholders})", values)

    conn.commit()

def delete_data(table, id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {table} WHERE id=?", (id,))
    conn.commit()
