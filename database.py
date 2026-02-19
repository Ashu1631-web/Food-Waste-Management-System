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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS food_listings (
        Food_ID INTEGER PRIMARY KEY,
        Food_Name TEXT,
        Quantity INTEGER,
        Expiry_Date TEXT,
        Location TEXT,
        Food_Type TEXT,
        Meal_Type TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS claims (
        Claim_ID INTEGER PRIMARY KEY,
        Food_ID INTEGER,
        Receiver_ID INTEGER,
        Status TEXT,
        Timestamp TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS providers (
        Provider_ID INTEGER PRIMARY KEY,
        Name TEXT,
        Type TEXT,
        Address TEXT,
        City TEXT,
        Contact TEXT
    )
    """)

    conn.commit()
    conn.close()


def load_csv_data():
    conn = get_connection()

    food_listings = pd.read_csv(os.path.join(DATA_DIR, "food_listings_data.csv"))
    claims = pd.read_csv(os.path.join(DATA_DIR, "claims_data.csv"))
    providers = pd.read_csv(os.path.join(DATA_DIR, "providers_data.csv"))

    food_listings.to_sql("food_listings", conn, if_exists="replace", index=False)
    claims.to_sql("claims", conn, if_exists="replace", index=False)
    providers.to_sql("providers", conn, if_exists="replace", index=False)

    conn.close()
