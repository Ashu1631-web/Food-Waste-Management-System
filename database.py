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
        Food_Type TEXT,
        Meal_Type TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE claims (
        Claim_ID INTEGER,
        Food_ID INTEGER,
        Receiver_ID INTEGER,
        Status TEXT,
        Timestamp TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE providers (
        Provider_ID INTEGER,
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

    # Load CSV correctly
    food_listings = pd.read_csv(os.path.join(DATA_DIR, "food_listings_data.csv"))
    claims = pd.read_csv(os.path.join(DATA_DIR, "claims_data.csv"))
    providers = pd.read_csv(os.path.join(DATA_DIR, "providers_data.csv"))

    # Insert Data Properly
    food_listings.to_sql("food_listings", conn, if_exists="append", index=False)
    claims.to_sql("claims", conn, if_exists="append", index=False)
    providers.to_sql("providers", conn, if_exists="append", index=False)

    conn.close()
