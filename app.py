import streamlit as st
import pandas as pd
import sqlite3
import os

from database import create_tables, load_csv_data
from queries import queries

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="🍲 Food Wastage Management System",
    layout="wide"
)

DB_NAME = "food_waste.db"

# ---------------- INIT DATABASE ----------------
if not os.path.exists(DB_NAME):
    create_tables()
    load_csv_data()


def get_conn():
    return sqlite3.connect(DB_NAME)


# ---------------- SIDEBAR MENU ----------------
st.sidebar.title("🍴 Navigation")

menu = st.sidebar.radio(
    "Select Option",
    ["Dashboard", "Food Listings", "CRUD Operations", "15 SQL Query Results"]
)

# ---------------- DASHBOARD ----------------
if menu == "Dashboard":
    st.title("📊 Local Food Wastage Management Dashboard")

    conn = get_conn()

    total_food = pd.read_sql("SELECT SUM(Quantity) AS Total FROM food_listings", conn)
    total_claims = pd.read_sql("SELECT COUNT(*) AS Total FROM claims", conn)
    total_providers = pd.read_sql("SELECT COUNT(*) AS Total FROM providers", conn)

    col1, col2, col3 = st.columns(3)

    col1.metric("🍱 Total Food Available", int(total_food["Total"][0]))
    col2.metric("📌 Total Claims Made", int(total_claims["Total"][0]))
    col3.metric("🏢 Total Providers", int(total_providers["Total"][0]))

    st.subheader("📍 Food Listings by City")

    city_df = pd.read_sql("""
        SELECT Location, COUNT(*) AS Listings
        FROM food_listings
        GROUP BY Location
        ORDER BY Listings DESC
    """, conn)

    st.bar_chart(city_df.set_index("Location"))

    conn.close()


# ---------------- FOOD LISTINGS + FILTERS ----------------
elif menu == "Food Listings":
    st.title("🍲 Available Food Listings")

    conn = get_conn()
    food_df = pd.read_sql("SELECT * FROM food_listings", conn)

    st.sidebar.subheader("🔍 Filters")

    city_filter = st.sidebar.selectbox(
        "Select City",
        ["All"] + sorted(food_df["Location"].unique())
    )

    foodtype_filter = st.sidebar.selectbox(
        "Select Food Type",
        ["All"] + sorted(food_df["Food_Type"].unique())
    )

    meal_filter = st.sidebar.selectbox(
        "Select Meal Type",
        ["All"] + sorted(food_df["Meal_Type"].unique())
    )

    if city_filter != "All":
        food_df = food_df[food_df["Location"] == city_filter]

    if foodtype_filter != "All":
        food_df = food_df[food_df["Food_Type"] == foodtype_filter]

    if meal_filter != "All":
        food_df = food_df[food_df["Meal_Type"] == meal_filter]

    st.dataframe(food_df)

    conn.close()


# ---------------- CRUD OPERATIONS ----------------
elif menu == "CRUD Operations":
    st.title("🛠 Manage Food Listings (CRUD)")

    conn = get_conn()
    cursor = conn.cursor()

    st.subheader("➕ Add New Food Listing")

    with st.form("add_food"):
        food_name = st.text_input("Food Name")
        qty = st.number_input("Quantity", min_value=1)
        expiry = st.date_input("Expiry Date")
        location = st.text_input("City Location")
        food_type = st.selectbox("Food Type", ["Vegetarian", "Non-Vegetarian", "Vegan"])
        meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snacks"])

        add_btn = st.form_submit_button("Add Food")

        if add_btn:
            cursor.execute("""
                INSERT INTO food_listings
                (Food_Name, Quantity, Expiry_Date, Location, Food_Type, Meal_Type)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (food_name, qty, expiry, location, food_type, meal_type))

            conn.commit()
            st.success("✅ Food Listing Added Successfully!")

    # ---------------- UPDATE ----------------
    st.subheader("✏ Update Existing Food Listing")

    food_ids = pd.read_sql("SELECT Food_ID FROM food_listings", conn)["Food_ID"].tolist()

    selected_id = st.selectbox("Select Food ID to Update", food_ids)

    if selected_id:
        record = pd.read_sql(f"SELECT * FROM food_listings WHERE Food_ID={selected_id}", conn)

        new_qty = st.number_input("New Quantity", value=int(record["Quantity"][0]))
        new_city = st.text_input("New City", value=record["Location"][0])

        if st.button("Update Record"):
            cursor.execute("""
                UPDATE food_listings
                SET Quantity=?, Location=?
                WHERE Food_ID=?
            """, (new_qty, new_city, selected_id))

            conn.commit()
            st.success("✅ Record Updated Successfully!")

    # ---------------- DELETE ----------------
    st.subheader("🗑 Delete Food Listing")

    delete_id = st.selectbox("Select Food ID to Delete", food_ids)

    if st.button("Delete Record"):
        cursor.execute("DELETE FROM food_listings WHERE Food_ID=?", (delete_id,))
        conn.commit()
        st.warning("❌ Record Deleted Successfully!")

    conn.close()


# ---------------- 15 SQL QUERY OUTPUTS ----------------
elif menu == "15 SQL Query Results":
    st.title("📌 15 SQL Queries Output")

    selected_query = st.selectbox("Select Query", list(queries.keys()))

    conn = get_conn()
    df = pd.read_sql(queries[selected_query], conn)
    conn.close()

    st.dataframe(df)
