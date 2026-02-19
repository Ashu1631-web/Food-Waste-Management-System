import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

from database import create_tables, load_csv_data

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Food Waste Management", layout="wide")

DB_NAME = "food_waste.db"

# Load Database Fresh
create_tables()
load_csv_data()


def get_conn():
    return sqlite3.connect(DB_NAME)


# ---------------- SIDEBAR ----------------
st.sidebar.title("🍲 Food Wastage System")

menu = st.sidebar.radio(
    "Navigation",
    ["Dashboard (15 Graphs)", "Food Listings", "Claims", "Providers"]
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

    # ---------------- METRICS ----------------
    col1, col2, col3 = st.columns(3)

    col1.metric("🍱 Total Food Items", len(food_df))
    col2.metric("📌 Total Claims", len(claims_df))
    col3.metric("🏢 Total Providers", len(providers_df))

    st.divider()

    # ======================================================
    # 15 GRAPHS SECTION
    # ======================================================
    st.subheader("📍 Food & Claims Insights (15 Charts)")

    charts = st.container()

    # Graph 1: Listings by City
    st.write("### 1. Food Listings by City")
    city_count = food_df["Location"].value_counts()
    st.bar_chart(city_count)

    # Graph 2: Food Type Distribution
    st.write("### 2. Food Type Distribution")
    st.bar_chart(food_df["Food_Type"].value_counts())

    # Graph 3: Meal Type Distribution
    st.write("### 3. Meal Type Distribution")
    st.bar_chart(food_df["Meal_Type"].value_counts())

    # Graph 4: Providers by City
    st.write("### 4. Providers by City")
    st.bar_chart(providers_df["City"].value_counts())

    # Graph 5: Provider Type Contribution
    st.write("### 5. Provider Type Contribution")
    st.bar_chart(food_df["Provider_Type"].value_counts())

    # Graph 6: Claims Status Breakdown
    st.write("### 6. Claims Status Breakdown")
    st.bar_chart(claims_df["Status"].value_counts())

    # Graph 7: Quantity Distribution
    st.write("### 7. Food Quantity Distribution")
    st.line_chart(food_df["Quantity"])

    # Graph 8: Top 10 Food Items Available
    st.write("### 8. Top 10 Food Items Available")
    top_food = food_df["Food_Name"].value_counts().head(10)
    st.bar_chart(top_food)

    # Graph 9: Top Cities by Claims
    st.write("### 9. Claims by City")
    merged = claims_df.merge(food_df, on="Food_ID")
    st.bar_chart(merged["Location"].value_counts())

    # Graph 10: Expiry Trend
    st.write("### 10. Food Expiry Dates Trend")
    food_df["Expiry_Date"] = pd.to_datetime(food_df["Expiry_Date"])
    expiry_count = food_df.groupby(food_df["Expiry_Date"].dt.month).size()
    st.line_chart(expiry_count)

    # Graph 11: Receivers by City
    st.write("### 11. Receivers by City")
    st.bar_chart(receivers_df["City"].value_counts())

    # Graph 12: Claims per Receiver
    st.write("### 12. Top Receivers by Claims")
    receiver_claims = claims_df["Receiver_ID"].value_counts().head(10)
    st.bar_chart(receiver_claims)

    # Graph 13: Provider with Most Listings
    st.write("### 13. Top Providers by Listings")
    provider_listings = food_df["Provider_ID"].value_counts().head(10)
    st.bar_chart(provider_listings)

    # Graph 14: Completed vs Pending Claims
    st.write("### 14. Completed vs Pending Claims")
    status = claims_df["Status"].value_counts()
    fig, ax = plt.subplots()
    ax.pie(status, labels=status.index, autopct="%1.1f%%")
    st.pyplot(fig)

    # Graph 15: Quantity Donated by City
    st.write("### 15. Total Quantity Donated by City")
    qty_city = food_df.groupby("Location")["Quantity"].sum()
    st.bar_chart(qty_city)

    st.success("✅ All 15 Graphs Displayed Successfully!")

# ======================================================
# FOOD LISTINGS PAGE
# ======================================================
elif menu == "Food Listings":
    st.title("🍲 Food Listings Data")

    conn = get_conn()
    df = pd.read_sql("SELECT * FROM food_listings", conn)
    conn.close()

    st.dataframe(df)

# ======================================================
# CLAIMS PAGE
# ======================================================
elif menu == "Claims":
    st.title("📌 Claims Data")

    conn = get_conn()
    df = pd.read_sql("SELECT * FROM claims", conn)
    conn.close()

    st.dataframe(df)

# ======================================================
# PROVIDERS PAGE
# ======================================================
elif menu == "Providers":
    st.title("🏢 Providers Data")

    conn = get_conn()
    df = pd.read_sql("SELECT * FROM providers", conn)
    conn.close()

    st.dataframe(df)
