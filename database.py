import sqlite3
import pandas as pd
import os

DB_NAME = "food_waste.db"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


def get_connection():
    return sqlite3.connect(DB_NAME)


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS food_listings;")
    cursor.execute("DROP TABLE IF EXISTS claims;")
    cursor.execute("DROP TABLE IF EXISTS providers;")

    cursor.execute("""
    CREATE TABLE food_listings (
        Food_ID INTEGER,
        Food_Name TEXT,
        Quantity INTEGER,
        Expiry_Date TEXT,
        Provider_ID INTEGER,
        Provider_Type TEXT,
        Location TEXT,
