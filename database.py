import sqlite3
import pandas as pd
import os

DB_NAME = "food_waste.db"

# Correct Paths for Streamlit Cloud
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


# اتصال Database
def get_connection():
    return sqlite3.connect(DB_NAME)


# Create Tables
def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # Drop old tables to reload fresh data
    cursor.execute("DROP TABLE IF EXISTS food_listings")
    cursor.execute("DROP TABLE IF EXISTS claims")
    cursor.execute("DROP TABLE IF EXISTS providers")

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

    conn.commit()
    conn.close()


# Load CSV Data
def load_csv_data():
    conn = get_connection()

    # File Paths
    food_path = os.path.join(DATA_DIR, "food_listings_data.csv")
    claims_path = os.path.join(DATA_DIR, "claims_data.csv")
    providers_path = os.path._
