import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import numpy as np
import random

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Food Waste Dashboard", layout="wide")

# ---------------- CSS (ANIMATION) ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(to right,#0f2027,#203a43,#2c5364);
}
.kpi {
    background: linear-gradient(135deg,#00C9A7,#007CF0);
    padding:20px;
    border-radius:15px;
    color:white;
    text-align:center;
    font-weight:bold;
    animation: fadeIn 1s ease-in;
}
@keyframes fadeIn {
    from {opacity:0; transform:translateY(10px);}
    to {opacity:1; transform:translateY(0);}
}
h1,h2,h3 {color:white;}
</style>
""", unsafe_allow_html=True)

# ---------------- LOGIN ----------------
def login(u,p):
    return u=="admin" and p=="1234"

if "login" not in st.session_state:
    st.session_state.login=False

if not st.session_state.login:
    st.title("🔐 Login")
    u=st.text_input("Username")
    p=st.text_input("Password", type="password")

    if st.button("Login"):
        if login(u,p):
            st.session_state.login=True
            st.rerun()
        else:
            st.error("Invalid Login")
    st.stop()

# ---------------- DB ----------------
conn = sqlite3.connect("food_waste.db", check_same_thread=False)

# ---------------- AUTO DATA (1000 ROWS) ----------------
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS food_listings (
id INTEGER PRIMARY KEY,
food_type TEXT,
meal_type TEXT,
city TEXT,
quantity INTEGER,
status TEXT
)""")

if cur.execute("SELECT COUNT(*) FROM food_listings").fetchone()[0] < 1000:

    cities = ["Delhi","Mumbai","Noida","Bangalore","Pune"]
    food_types = ["Veg","Non-Veg"]
    meals = ["Breakfast","Lunch","Dinner"]
    status = ["Available","Expired"]

    for i in range(1000):
        cur.execute("INSERT INTO food_listings VALUES (?,?,?,?,?,?)",(
            i,
            random.choice(food_types),
            random.choice(meals),
            random.choice(cities),
            random.randint(1,50),
            random.choice(status)
        ))

    conn.commit()

# ---------------- LOAD DATA ----------------
df = pd.read_sql("SELECT * FROM food_listings", conn)

# ---------------- FILTERS ----------------
st.sidebar.header("🔍 Filters")

city_filter = st.sidebar.multiselect("City", df["city"].unique(), default=df["city"].unique())
food_filter = st.sidebar.multiselect("Food Type", df["food_type"].unique(), default=df["food_type"].unique())

df = df[(df["city"].isin(city_filter)) & (df["food_type"].isin(food_filter))]

# ---------------- KPI ----------------
st.title("📊 Food Waste Dashboard")

c1,c2,c3 = st.columns(3)

c1.markdown(f"<div class='kpi'>🍱<br>{len(df)}<br>Total Records</div>", unsafe_allow_html=True)
c2.markdown(f"<div class='kpi'>🏙️<br>{df['city'].nunique()}<br>Cities</div>", unsafe_allow_html=True)
c3.markdown(f"<div class='kpi'>🍴<br>{df['food_type'].nunique()}<br>Food Types</div>", unsafe_allow_html=True)

# ---------------- OVERVIEW ----------------
st.info("AI-powered dashboard to reduce food waste with real-time filtering & analytics")

# ---------------- CHARTS ----------------
st.subheader("📈 Analytics")

col1,col2 = st.columns(2)

with col1:
    st.plotly_chart(px.bar(df.groupby("city").size().reset_index(name="count"), x="city", y="count", title="City Distribution"))
    st.plotly_chart(px.pie(df, names="food_type", title="Food Type"))
    st.plotly_chart(px.histogram(df, x="quantity", title="Quantity Distribution"))

with col2:
    st.plotly_chart(px.line(df.groupby("city")["quantity"].mean().reset_index(), x="city", y="quantity", title="Avg Quantity"))
    st.plotly_chart(px.bar(df.groupby("meal_type").size().reset_index(name="count"), x="meal_type", y="count", title="Meal Type"))
    st.plotly_chart(px.bar(df.groupby("status").size().reset_index(name="count"), x="status", y="count", title="Status"))

# ---------------- LOGOUT ----------------
if st.sidebar.button("Logout"):
    st.session_state.login=False
    st.rerun()
