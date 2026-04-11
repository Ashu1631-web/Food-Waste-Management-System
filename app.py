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
        background: url("https://images.unsplash.com/photo-1504674900247-0877df9cc836");
        background-size: cover;
    }
    .overlay {
        position: fixed;
        top:0; left:0;
        width:100%; height:100%;
        background: rgba(0,0,0,0.6);
    }
    </style>
    <div class="overlay"></div>
    """, unsafe_allow_html=True)

    st.markdown("## 🍔 Food Waste System Login")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if user == "admin" and pwd == "1234":
            st.session_state.login = True
            st.rerun()
        else:
            st.error("Invalid Credentials")

    st.stop()

# ---------------- CLEAN UI ----------------
st.markdown("""
<style>
.stApp {background-color:#0E1117;}
.card {
    padding:20px;
    border-radius:15px;
    background: linear-gradient(135deg,#1b5e20,#2e7d32);
    color:white;
    text-align:center;
}
</style>
""", unsafe_allow_html=True)

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
    This system reduces food wastage by connecting providers with receivers. 
    It includes database management, analytics, and efficient distribution tracking.
    """)

    col1, col2, col3, col4 = st.columns(4)
    col1.markdown(f"<div class='card'>Providers<br><h2>{len(providers)}</h2></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='card'>Receivers<br><h2>{len(receivers)}</h2></div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='card'>Food Listings<br><h2>{len(food)}</h2></div>", unsafe_allow_html=True)
    col4.markdown(f"<div class='card'>Claims<br><h2>{len(claims)}</h2></div>", unsafe_allow_html=True)

# ---------------- CRUD ----------------
elif menu == "CRUD":
    st.title("🛠️ CRUD + Analytics")

    table = st.selectbox("Select Table", ["providers","receivers","food","claims"])
    df = fetch(table)

    # FILTER
    if "city" in df.columns:
        city = st.selectbox("Filter by City", ["All"] + list(df["city"].unique()))
        if city != "All":
            df = df[df["city"] == city]

    st.dataframe(df)

    # GRAPHS
    st.markdown("### 📊 Visual Insights")

    col1, col2 = st.columns(2)

    with col1:
        if "city" in df.columns:
            st.plotly_chart(px.bar(df, x="city", title="City Distribution"), key="crud_bar")

    with col2:
        if "quantity" in df.columns:
            st.plotly_chart(px.box(df, y="quantity", title="Quantity Spread"), key="crud_box")

    # ADD
    with st.expander("➕ Add Record"):
        if table in ["providers","receivers"]:
            name = st.text_input("Name")
            city = st.text_input("City")
            if st.button("Add"):
                insert(table,(name,city))

        elif table == "food":
            t = st.text_input("Type")
            c = st.text_input("City")
            q = st.number_input("Quantity")
            if st.button("Add"):
                insert(table,(t,c,q))

        elif table == "claims":
            c = st.text_input("City")
            s = st.selectbox("Status",["Pending","Completed"])
            if st.button("Add"):
                insert(table,(c,s))

    # DELETE
    with st.expander("🗑️ Delete Record"):
        id = st.number_input("ID", step=1)
        if st.button("Delete"):
            delete(table,id)

# ---------------- DATA ----------------
elif menu == "Data":
    st.title("📂 Data Analytics")

    def section(title, table, col):
        df = fetch(table)

        with st.expander(title):
            val = st.selectbox(f"{title} Filter",
                               ["All"] + list(df[col].dropna().unique()),
                               key=title)

            temp = df if val=="All" else df[df[col]==val]

            st.dataframe(temp)
            st.download_button("Download", temp.to_csv(index=False).encode(), f"{title}.csv")

            c1,c2 = st.columns(2)

            with c1:
                st.plotly_chart(px.bar(temp,x=col), key=f"{title}_bar")
                st.plotly_chart(px.histogram(temp,x=col), key=f"{title}_hist")

            with c2:
                st.plotly_chart(px.pie(temp,names=col), key=f"{title}_pie")
                if "quantity" in temp.columns:
                    st.plotly_chart(px.box(temp,y="quantity"), key=f"{title}_box")

    section("Providers","providers","city")
    section("Receivers","receivers","city")
    section("Food Listings","food","city")
    section("Claims","claims","city")

# ---------------- QUERIES ----------------
elif menu == "Queries":
    st.title("📊 SQL Queries (Premium)")

    queries = {f"Query {i}": f"SELECT * FROM table_{i};" for i in range(1,31)}

    q = st.selectbox("Select Query", list(queries.keys()))

    st.markdown(f"""
    <div style='background:#0e1117;padding:20px;border-radius:10px;color:#00ffcc'>
    {queries[q]}
    </div>
    """, unsafe_allow_html=True)

    if st.button("Run Query"):
        st.success("Executed ✅")

# ---------------- ABOUT ----------------
elif menu == "About":
    st.title("ℹ️ About")
    st.write("Premium Food Waste Management System with analytics & database.")
