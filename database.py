import sqlite3
import pandas as pd

DB_NAME = "food_waste.db"


# اتصال DB
def get_connection():
    return sqlite3.connect(DB_NAME)


# Table Creation
def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS receivers (
        Receiver_ID INTEGER PRIMARY KEY,
        Name TEXT,
        Type TEXT,
        City TEXT,
        Contact TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS food_listings (
        Food_ID INTEGER PRIMARY KEY,
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
    CREATE TABLE IF NOT EXISTS claims (
        Claim_ID INTEGER PRIMARY KEY,
        Food_ID INTEGER,
        Receiver_ID INTEGER,
        Status TEXT,
        Timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()


# Load CSV into DB
def load_csv_data():
    conn = get_connection()

    providers = pd.read_csv("data/providers_data.csv")
    receivers = pd.read_csv("data/receivers_data.csv")
    food_listings = pd.read_csv("data/food_listings_data.csv")
    claims = pd.read_csv("data/claims_data.csv")

    providers.to_sql("providers", conn, if_exists="replace", index=False)
    receivers.to_sql("receivers", conn, if_exists="replace", index=False)
    food_listings.to_sql("food_listings", conn, if_exists="replace", index=False)
    claims.to_sql("claims", conn, if_exists="replace", index=False)

    conn.close()
