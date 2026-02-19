import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

from database import create_tables, load_csv_data
from queries import queries

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Food Waste Management", layout="wide")

DB_NAME = "food_waste.db"

# Reload Database
create_tables()
load_csv_data()


def get_conn():
    return sqlite3.connect(DB_NAME)


# ---------------- SIDEBAR ----------------
st.sidebar.title("🍲 Food Wastage System")

menu = st.sidebar.radio(
    "Navigation",
    ["Dashboard (15 Graphs)", "Food Listings", "SQL Queries (15 Questions)"]
)

# ======================================================
# 📊 DASHBOARD WITH 15 GRAPHS
# ======================================================
if menu == "Dashboard (15 Graphs)":

    st.title("📊 Food Wastage Dashboard (15 Graphs)")

    conn = get_conn()

    food_df = pd.read_sql("SELECT * FROM food_listings", conn)
    claims_df = pd.read_sql("SELECT * FROM claims", conn)
    providers_df = pd.read_sql("SELECT * FROM providers", conn)
    receivers_df = pd.read_sql("SELECT * FROM receivers", conn)

    conn.close()

    # Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("🍱 Total Food Items", len(food_df))
    col2.metric("📌 Total Claims", len(claims_df))
    col3.metric("🏢 Total Providers", len(providers_df))

    st.divider()
    st.subheader("📍 Food & Claims Insights (15 Charts)")

    # 1 Listings by City
    st.write("### 1. Food Listings by City")
    st.bar_chart(food_df["Location"].value_counts())

    # 2 Food Type
    st.write("### 2. Food Type Distribution")
    st.bar_chart(food_df["Food_Type"].value_counts())

    # 3 Meal Type
    st.write("### 3. Meal Type Distribution")
    st.bar_chart(food_df["Meal_Type"].value_counts())

    # 4 Providers by City
    st.write("### 4. Providers by City")
    st.bar_chart(providers_df["City"].value_counts())

    # 5 Provider Type
    st.write("### 5. Provider Type Contribution")
    st.bar_chart(food_df["Provider_Type"].value_counts())

    # 6 Claims Status
    st.write("### 6. Claims Status Breakdown")
    st.bar_chart(claims_df["Status"].value_counts())

    # 7 Quantity Trend
    st.write("### 7. Quantity Trend")
    st.line_chart(food_df["Quantity"])

    # 8 Top Foods
    st.write("### 8. Top 10 Food Items")
    st.bar_chart(food_df["Food_Name"].value_counts().head(10))

    # 9 Claims by City
    st.write("### 9. Claims by City")
    merged = claims_df.merge(food_df, on="Food_ID")
    st.bar_chart(merged["Location"].value_counts())

    # 10 Expiry Trend
    st.write("### 10. Expiry Month Trend")
    food_df["Expiry_Date"] = pd.to_datetime(food_df["Expiry_Date"])
    expiry = food_df.groupby(food_df["Expiry_Date"].dt.month).size()
    st.line_chart(expiry)

    # 11 Receivers by City
    st.write("### 11. Receivers by City")
    st.bar_chart(receivers_df["City"].value_counts())

    # 12 Top Receivers Claims
    st.write("### 12. Top Receivers by Claims")
    st.bar_chart(claims_df["Receiver_ID"].value_counts().head(10))

    # 13 Top Providers Listings
    st.write("### 13. Top Providers by Listings")
    st.bar_chart(food_df["Provider_ID"].value_counts().head(10))

    # 14 Pie Chart Claims Status
    st.write("### 14. Claims Status Pie Chart")
    status = claims_df["Status"].value_counts()
    fig, ax = plt.subplots()
    ax.pie(status, labels=status.index, autopct="%1.1f%%")
    st.pyplot(fig)

    # 15 Quantity Donated by City
    st.write("### 15. Total Quantity Donated by City")
    qty_city = food_df.groupby("Location")["Quantity"].sum()
    st.bar_chart(qty_city)

    st.success("✅ Dashboard with 15 Graphs Completed!")

# ======================================================
# FOOD LISTINGS PAGE
# ======================================================
elif menu == "Food Listings":
    st.title("🍲 Food Listings Table")

    conn = get_conn()
    df = pd.read_sql("SELECT * FROM food_listings", conn)
    conn.close()

    st.dataframe(df)

# ======================================================
# SQL QUERIES (15 QUESTIONS)
# ======================================================
elif menu == "SQL Queries (15 Questions)":

    st.title("📌 SQL Queries Output (15 Questions)")

    st.write("Select any query below to see output:")

    selected_query = st.selectbox("Choose Query", list(queries.keys()))

    conn = get_conn()
    result = pd.read_sql(queries[selected_query], conn)
    conn.close()

    st.subheader("Query Result")
    st.dataframe(result)
