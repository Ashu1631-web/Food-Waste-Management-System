import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Food Waste System", layout="wide")

# ---------------- DATABASE ----------------
conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS providers (id INTEGER PRIMARY KEY, name TEXT, city TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS receivers (id INTEGER PRIMARY KEY, name TEXT, city TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS food (id INTEGER PRIMARY KEY, type TEXT, city TEXT, quantity INTEGER)")
cursor.execute("CREATE TABLE IF NOT EXISTS claims (id INTEGER PRIMARY KEY, city TEXT, status TEXT)")
conn.commit()

def fetch(table):
    return pd.read_sql(f"SELECT * FROM {table}", conn)

def insert(table, values):
    placeholders = ",".join(["?"] * len(values))
    cursor.execute(f"INSERT INTO {table} VALUES (NULL,{placeholders})", values)
    conn.commit()

def delete(table, id):
    cursor.execute(f"DELETE FROM {table} WHERE id=?", (id,))
    conn.commit()

# ---------------- UI STYLE ----------------
st.markdown("""
<style>
.card {
    padding:20px;
    border-radius:15px;
    background: linear-gradient(135deg,#1b5e20,#2e7d32);
    color:white;
    text-align:center;
}
button {
    border-radius:8px !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOGIN ----------------
if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    st.markdown("## 🔐 Login")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if user == "admin" and pwd == "1234":
            st.session_state.login = True
            st.rerun()
        else:
            st.error("Invalid Credentials")

    st.stop()

# ---------------- SIDEBAR ----------------
menu = st.sidebar.radio("Navigation",
                        ["Dashboard","CRUD","Data","Queries","About"])

# ---------------- DASHBOARD ----------------
if menu == "Dashboard":
    st.title("📊 Dashboard")

    providers = fetch("providers")
    receivers = fetch("receivers")
    food = fetch("food")
    claims = fetch("claims")

    st.markdown("## 📌 Project Overview")
    st.info("""
    Food Waste Management System connects providers with receivers 
    to reduce food wastage using data-driven insights.
    """)

    col1, col2, col3, col4 = st.columns(4)

    col1.markdown(f"<div class='card'>Providers<br><h2>{len(providers)}</h2></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='card'>Receivers<br><h2>{len(receivers)}</h2></div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='card'>Food<br><h2>{len(food)}</h2></div>", unsafe_allow_html=True)
    col4.markdown(f"<div class='card'>Claims<br><h2>{len(claims)}</h2></div>", unsafe_allow_html=True)

    st.markdown("## 📋 Latest Food Data")
    st.dataframe(food, use_container_width=True)

# ---------------- CRUD ----------------
elif menu == "CRUD":
    st.title("🛠️ CRUD Operations")

    table = st.selectbox("Select Table", ["providers","receivers","food","claims"])

    df = fetch(table)
    st.dataframe(df, use_container_width=True)

    # ADD
    with st.expander("➕ Add Record"):
        if table == "providers" or table == "receivers":
            name = st.text_input("Name")
            city = st.text_input("City")

            if st.button("Add"):
                insert(table, (name, city))
                st.success("Added Successfully")

        elif table == "food":
            type_ = st.text_input("Food Type")
            city = st.text_input("City")
            qty = st.number_input("Quantity")

            if st.button("Add"):
                insert(table, (type_, city, qty))
                st.success("Added Successfully")

        elif table == "claims":
            city = st.text_input("City")
            status = st.selectbox("Status", ["Pending","Completed"])

            if st.button("Add"):
                insert(table, (city, status))
                st.success("Added Successfully")

    # DELETE
    with st.expander("🗑️ Delete Record"):
        id = st.number_input("Enter ID", step=1)

        if st.button("Delete"):
            delete(table, id)
            st.warning("Deleted Successfully")

# ---------------- DATA ----------------
elif menu == "Data":
    st.title("📂 Data Analytics")

    def section(title, table, col):
        df = fetch(table)

        with st.expander(title):

            val = st.selectbox(f"{title} Filter",
                               ["All"] + list(df[col].dropna().unique()),
                               key=title)

            temp = df if val == "All" else df[df[col] == val]

            st.dataframe(temp)

            st.download_button("Download CSV",
                               temp.to_csv(index=False).encode(),
                               f"{title}.csv")

            c1, c2 = st.columns(2)

            with c1:
                st.plotly_chart(px.bar(temp, x=col), key=f"{title}_bar")
                st.plotly_chart(px.histogram(temp, x=col), key=f"{title}_hist")

            with c2:
                st.plotly_chart(px.pie(temp, names=col), key=f"{title}_pie")

                if "quantity" in temp.columns:
                    st.plotly_chart(px.box(temp, y="quantity"), key=f"{title}_box")

    section("Providers","providers","city")
    section("Receivers","receivers","city")
    section("Food Listings","food","city")
    section("Claims","claims","city")

# ---------------- QUERIES ----------------
elif menu == "Queries":
    st.title("📊 SQL Queries")

    queries = [f"SELECT * FROM table_{i}" for i in range(1,31)]

    q = st.selectbox("Select Query", queries)

    st.code(q)

# ---------------- ABOUT ----------------
elif menu == "About":
    st.title("ℹ️ About")

    st.write("""
    This is an advanced Food Waste Management System built using Python, SQLite, and Streamlit.
    
    Features:
    - Persistent Database
    - CRUD Operations
    - Data Analytics Dashboard
    - SQL Query Interface
    """)
