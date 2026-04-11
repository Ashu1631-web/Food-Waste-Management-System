import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Food Waste System", layout="wide")

# ---------------- DATABASE ----------------
conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

# CREATE TABLES
cursor.execute("CREATE TABLE IF NOT EXISTS providers (id INTEGER PRIMARY KEY, name TEXT, city TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS receivers (id INTEGER PRIMARY KEY, name TEXT, city TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS food (id INTEGER PRIMARY KEY, type TEXT, city TEXT, quantity INTEGER)")
cursor.execute("CREATE TABLE IF NOT EXISTS claims (id INTEGER PRIMARY KEY, city TEXT, status TEXT)")

# ---------------- INSERT SAMPLE DATA ----------------
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

# ---------------- FUNCTIONS ----------------
def fetch(table):
    return pd.read_sql(f"SELECT * FROM {table}", conn)

def insert(table, values):
    cursor.execute(f"INSERT INTO {table} VALUES (NULL,{','.join(['?']*len(values))})", values)
    conn.commit()

def delete(table, id):
    cursor.execute(f"DELETE FROM {table} WHERE id=?", (id,))
    conn.commit()

# ---------------- LOGIN ----------------
if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    st.markdown("""
    <style>
    .stApp {
        background:url("https://images.unsplash.com/photo-1504674900247-0877df9cc836");
        background-size:cover;
    }
    .overlay {
        position:fixed;
        width:100%;
        height:100%;
        background:rgba(0,0,0,0.6);
    }
    </style>
    <div class="overlay"></div>
    """, unsafe_allow_html=True)

    st.title("🍔 Login")

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if u=="admin" and p=="1234":
            st.session_state.login=True
            st.rerun()

    st.stop()

# ---------------- SIDEBAR ----------------
menu = st.sidebar.radio("Navigation", ["Dashboard","CRUD","Data","Queries","About"])

# ---------------- DASHBOARD ----------------
if menu=="Dashboard":
    st.title("📊 Dashboard")

    st.markdown("## 📌 Project Overview")
    st.info("""
    Food Waste Management System connects providers and receivers to reduce food wastage 
    using data-driven insights and efficient distribution.
    """)

    p = fetch("providers")
    r = fetch("receivers")
    f = fetch("food")
    c = fetch("claims")

    col1,col2,col3,col4 = st.columns(4)
    col1.metric("Providers",len(p))
    col2.metric("Receivers",len(r))
    col3.metric("Food Listings",len(f))
    col4.metric("Claims",len(c))

    st.markdown("## 📋 Food Data")
    st.dataframe(f)

# ---------------- CRUD ----------------
elif menu=="CRUD":
    st.title("🛠️ CRUD")

    table = st.selectbox("Select Table",["providers","receivers","food","claims"])
    df = fetch(table)

    if "city" in df.columns:
        city = st.selectbox("Filter City",["All"]+list(df["city"].unique()))
        if city!="All":
            df = df[df["city"]==city]

    st.dataframe(df)

    st.markdown("### 📊 Graphs")
    if "city" in df.columns:
        st.plotly_chart(px.bar(df,x="city",title="City Distribution"))

    if "quantity" in df.columns:
        st.plotly_chart(px.box(df,y="quantity",title="Quantity Spread"))

    # ADD
    with st.expander("➕ Add"):
        if table in ["providers","receivers"]:
            name=st.text_input("Name")
            city=st.text_input("City")
            if st.button("Add"):
                insert(table,(name,city))

        elif table=="food":
            t=st.text_input("Type")
            c=st.text_input("City")
            q=st.number_input("Quantity")
            if st.button("Add"):
                insert(table,(t,c,q))

        elif table=="claims":
            c=st.text_input("City")
            s=st.selectbox("Status",["Pending","Completed"])
            if st.button("Add"):
                insert(table,(c,s))

    # DELETE
    with st.expander("🗑️ Delete"):
        id=st.number_input("ID",step=1)
        if st.button("Delete"):
            delete(table,id)

# ---------------- DATA ----------------
elif menu=="Data":
    st.title("📂 Data")

    for table in ["providers","receivers","food","claims"]:
        df = fetch(table)
        st.markdown(f"### {table.title()}")
        st.dataframe(df)

# ---------------- QUERIES ----------------
elif menu=="Queries":
    st.title("📊 SQL Queries")

    queries = {
        "Total Food Quantity":"SELECT SUM(quantity) FROM food",
        "Providers Count":"SELECT COUNT(*) FROM providers",
        "Food by City":"SELECT city,SUM(quantity) FROM food GROUP BY city"
    }

    q = st.selectbox("Select Question", list(queries.keys()))

    st.markdown("### 🧠 Query (Formula)")
    st.code(queries[q])

    if st.button("Run Query"):
        result = pd.read_sql(queries[q], conn)
        st.success("Result")
        st.dataframe(result)

# ---------------- ABOUT ----------------
elif menu=="About":
    st.title("ℹ️ About")

    st.write("""
    **Food Waste Management System**

    Developed by: **Ashish**

    This project helps reduce food wastage using:
    - Data Analytics
    - CRUD Operations
    - SQL Queries
    - Visualization

    Built using Python, Streamlit, SQLite.
    """)
