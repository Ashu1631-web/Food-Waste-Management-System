import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Food Waste System", layout="wide")

# ---------------- DATABASE ----------------
conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS providers (id INTEGER PRIMARY KEY, name TEXT, city TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS receivers (id INTEGER PRIMARY KEY, name TEXT, city TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS food (id INTEGER PRIMARY KEY, type TEXT, city TEXT, quantity INTEGER)")
cursor.execute("CREATE TABLE IF NOT EXISTS claims (id INTEGER PRIMARY KEY, city TEXT, status TEXT)")
conn.commit()

# ---------------- SAMPLE DATA ----------------
def insert_sample():
    if pd.read_sql("SELECT * FROM providers", conn).empty:
        cursor.execute("INSERT INTO providers (name,city) VALUES ('Restaurant A','Delhi')")
        cursor.execute("INSERT INTO providers (name,city) VALUES ('Store B','Mumbai')")

    if pd.read_sql("SELECT * FROM receivers", conn).empty:
        cursor.execute("INSERT INTO receivers (name,city) VALUES ('NGO A','Delhi')")
        cursor.execute("INSERT INTO receivers (name,city) VALUES ('NGO B','Pune')")

    if pd.read_sql("SELECT * FROM food", conn).empty:
        cursor.execute("INSERT INTO food (type,city,quantity) VALUES ('Veg','Delhi',50)")
        cursor.execute("INSERT INTO food (type,city,quantity) VALUES ('Non-Veg','Mumbai',30)")

    if pd.read_sql("SELECT * FROM claims", conn).empty:
        cursor.execute("INSERT INTO claims (city,status) VALUES ('Delhi','Completed')")
        cursor.execute("INSERT INTO claims (city,status) VALUES ('Mumbai','Pending')")

    conn.commit()

insert_sample()

def fetch(table):
    return pd.read_sql(f"SELECT * FROM {table}", conn)

# ---------------- LOGIN ----------------
if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:

    st.markdown("""
    <style>
    .stApp {
        background: url("https://images.unsplash.com/photo-1504674900247-0877df9cc836");
        background-size: cover;
    }

    .overlay {
        position: fixed;
        top:0; left:0;
        width:100%; height:100%;
        backdrop-filter: blur(8px);
        background: rgba(0,0,0,0.6);
    }

    .login-card {
        position: absolute;
        top:50%; left:50%;
        transform: translate(-50%, -50%);
        background: rgba(255,255,255,0.08);
        padding: 40px;
        border-radius: 15px;
        backdrop-filter: blur(15px);
        width: 350px;
    }

    </style>

    <div class="overlay"></div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='login-card'>", unsafe_allow_html=True)
    st.markdown("## 🍔 Login")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if user == "admin" and pwd == "1234":
            st.session_state.login = True
            st.rerun()
        else:
            st.error("Invalid Credentials")

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ---------------- MAIN UI ----------------
st.markdown("""
<style>
.stApp {background-color:#0E1117;}
.card {
    padding:20px;
    border-radius:15px;
    background: linear-gradient(135deg,#00c853,#64dd17);
    color:white;
    text-align:center;
}
</style>
""", unsafe_allow_html=True)

menu = st.sidebar.radio("Navigation", ["Dashboard","CRUD","Data","Queries","About"])

# ---------------- DASHBOARD ----------------
if menu == "Dashboard":
    st.title("📊 Dashboard")

    p = fetch("providers")
    r = fetch("receivers")
    f = fetch("food")
    c = fetch("claims")

    st.markdown("## 📌 Project Overview")
    st.info("Food Waste Management System reduces food wastage using smart analytics.")

    col1,col2,col3,col4 = st.columns(4)
    col1.markdown(f"<div class='card'>👨‍🍳 Providers<br><h2>{len(p)}</h2></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='card'>🤝 Receivers<br><h2>{len(r)}</h2></div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='card'>🍱 Food<br><h2>{len(f)}</h2></div>", unsafe_allow_html=True)
    col4.markdown(f"<div class='card'>📦 Claims<br><h2>{len(c)}</h2></div>", unsafe_allow_html=True)

# ---------------- CRUD ----------------
elif menu == "CRUD":
    st.title("🛠️ CRUD + Analytics")

    table = st.selectbox("Select Table", ["providers","receivers","food","claims"])
    df = fetch(table)

    if "city" in df.columns:
        city = st.selectbox("Filter City", ["All"] + list(df["city"].unique()))
        if city != "All":
            df = df[df["city"] == city]

    st.dataframe(df)

    st.markdown("### 📊 Visual Insights")

    if "city" in df.columns:
        st.plotly_chart(px.bar(df, x="city", color="city",
                                      title="🏙️ City Distribution"))

    if "quantity" in df.columns:
        st.plotly_chart(px.box(df, y="quantity",
                                      title="📦 Quantity Spread"))

# ---------------- DATA ----------------
elif menu == "Data":
    st.title("📂 Data")

    for table in ["providers","receivers","food","claims"]:
        df = fetch(table)
        st.markdown(f"### {table.title()}")
        st.dataframe(df)

# ---------------- QUERIES ----------------
elif menu == "Queries":
    st.title("📊 SQL Queries")

    queries = {
        "Total Food Quantity":"SELECT SUM(quantity) FROM food",
        "Providers Count":"SELECT COUNT(*) FROM providers",
        "Food by City":"SELECT city,SUM(quantity) FROM food GROUP BY city"
    }

    q = st.selectbox("Select Question", list(queries.keys()))

    st.markdown("### 🧠 Query")
    st.code(queries[q])

    if st.button("Run"):
        result = pd.read_sql(queries[q], conn)
        st.dataframe(result)

# ---------------- ABOUT ----------------
elif menu == "About":
    st.title("ℹ️ About")

    st.write("""
    Developed by **Ashish**

    Food Waste Management System with:
    - Analytics
    - CRUD
    - SQL Queries
    """)
