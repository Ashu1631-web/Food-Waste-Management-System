import streamlit as st
import pandas as pd
import sqlite3
from database import create_tables, load_csv_data
from queries import queries

DB_NAME = "food_waste.db"

# ---------------- INIT ----------------
st.set_page_config(page_title="Food Wastage Management", layout="wide")

create_tables()
load_csv_data()


# Connection
def get_conn():
    return sqlite3.connect(DB_NAME)


# ---------------- UI ----------------
st.title("🍲 Local Food Wastage Management System")

menu = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "SQL Query Results", "Food Listings CRUD"]
)

# ---------------- DASHBOARD ----------------
if menu == "Dashboard":
    st.header("📊 Food Wastage Insights Dashboard")

    conn = get_conn()

    total_food = pd.read_sql("SELECT SUM(Quantity) AS Total FROM food_listings", conn)
    total_claims = pd.read_sql("SELECT COUNT(*) AS Claims FROM claims", conn)
    total_providers = pd.read_sql("SELECT COUNT(*) AS Providers FROM providers", conn)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Food Available", int(total_food["Total"][0]))
    col2.metric("Total Claims Made", int(total_claims["Claims"][0]))
    col3.metric("Total Providers", int(total_providers["Providers"][0]))

    st.subheader("📍 Food Listings by City")
    city_data = pd.read_sql("""
        SELECT Location, COUNT(*) AS Listings
        FROM food_listings
        GROUP BY Location
    """, conn)

    st.bar_chart(city_data.set_index("Location"))

    conn.close()


# ---------------- SQL QUERIES ----------------
elif menu == "SQL Query Results":
    st.header("📌 15 SQL Query Outputs")

    selected_query = st.selectbox("Choose Query", list(queries.keys()))

    conn = get_conn()
    df = pd.read_sql(queries[selected_query], conn)
    conn.close()

    st.dataframe(df)


# ---------------- CRUD ----------------
elif menu == "Food Listings CRUD":
    st.header("🛠 Manage Food Listings (CRUD)")

    conn = get_conn()

    food_df = pd.read_sql("SELECT * FROM food_listings", conn)
    st.dataframe(food_df)

    st.subheader("➕ Add New Food Listing")

    with st.form("add_food"):
        food_name = st.text_input("Food Name")
        qty = st.number_input("Quantity", min_value=1)
        expiry = st.date_input("Expiry Date")
        location = st.text_input("City Location")
        food_type = st.selectbox("Food Type", ["Vegetarian", "Non-Vegetarian", "Vegan"])
        meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snacks"])

        submitted = st.form_submit_button("Add Food")

        if submitted:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO food_listings
            (Food_Name, Quantity, Expiry_Date, Location, Food_Type, Meal_Type)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (food_name, qty, expiry, location, food_type, meal_type))

            conn.commit()
            st.success("✅ Food Listing Added Successfully!")

    conn.close()
