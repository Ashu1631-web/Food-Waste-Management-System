import sqlite3
import pandas as pd
import os

DB_NAME = "food_waste.db"

# ✅ CSV files root folder में हैं
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = BASE_DIR   # <-- Final Fix


# ---------------- Connection ----------------
def get_connection():
    return sqlite3.connect(DB_NAME)


# ---------------- Create Tables ----------------
def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # पुराने tables हटाओ
    cursor.execute("DROP TABLE IF EXISTS food_listings")
    cursor.execute("DROP TABLE IF EXISTS claims")
    cursor.execute("DROP TABLE IF EXISTS providers")
    cursor.execute("DROP TABLE IF EXISTS receivers")

    # Food Listings Table
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

    # Claims Table
    cursor.execute("""
        CREATE TABLE claims (
            Claim_ID INTEGER,
            Food_ID INTEGER,
            Receiver_ID INTEGER,
            Status TEXT,
            Timestamp TEXT
        )
    """)

    # Providers Table
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

    # Receivers Table
    cursor.execute("""
        CREATE TABLE receivers (
            Receiver_ID INTEGER,
            Name TEXT,
            Type TEXT,
            City TEXT,
            Contact TEXT
        )
    """)

    conn.commit()
    conn.close()


# ---------------- Load CSV Data ----------------
def load_csv_data():
    conn = get_connection()

    # ✅ Root CSV Paths
    food_path = os.path.join(DATA_DIR, "food_listings_data.csv")
    claims_path = os.path.join(DATA_DIR, "claims_data.csv")
    providers_path = os.path.join(DATA_DIR, "providers_data.csv")
    receivers_path = os.path.join(DATA_DIR, "receivers_data.csv")

    # Read CSV Files
    food_listings = pd.read_csv(food_path)
    claims = pd.read_csv(claims_path)
    providers = pd.read_csv(providers_path)
    receivers = pd.read_csv(receivers_path)

    # Insert into Database
    food_listings.to_sql("food_listings", conn, if_exists="replace", index=False)
    claims.to_sql("claims", conn, if_exists="replace", index=False)
    providers.to_sql("providers", conn, if_exists="replace", index=False)
    receivers.to_sql("receivers", conn, if_exists="replace", index=False)

    conn.close()
