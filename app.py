import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Food Waste Management", layout="wide")

# ---------------- CSS ----------------
st.markdown("""
<style>
.stApp {
    background-image: url("https://plus.unsplash.com/premium_photo-1673108852141-e8c3c22a4a22?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D");
    background-size: cover;
}
.login-box {
    background: rgba(0,0,0,0.75);
    padding: 30px;
    border-radius: 15px;
    color: white;
}
section[data-testid="stSidebar"] {
    background-color: #020617;
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOGIN ----------------
def login(u,p):
    return u=="admin" and p=="1234"

if "login" not in st.session_state:
    st.session_state.login=False

if not st.session_state.login:
    st.title("🍱 Food Waste Management System")

    col1,col2,col3 = st.columns([1,2,1])
    with col2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)

        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Login"):
            if login(u,p):
                st.session_state.login=True
                st.rerun()
            else:
                st.error("Invalid Credentials")

        st.markdown('</div>', unsafe_allow_html=True)

    st.stop()

# ---------------- DB ----------------
conn = sqlite3.connect("food.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS providers(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT,city TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS receivers(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT,city TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS food_listings(id INTEGER PRIMARY KEY AUTOINCREMENT,food_type TEXT,meal_type TEXT,city TEXT,quantity INTEGER,status TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS claims(id INTEGER PRIMARY KEY AUTOINCREMENT,food_id INTEGER,receiver_id INTEGER)")
conn.commit()

# ---------------- SIDEBAR ----------------
menu = st.sidebar.radio("Navigation",[
    "Project Introduction",
    "CRUD Operations",
    "SQL Queries",
    "Waste Food Data Visualization",
    "Creator Info"
])

# ---------------- INTRO ----------------
if menu=="Project Introduction":

    st.markdown("## 🍱 Local Food Waste Management System")

    st.markdown("""
### 🚀 Smart Food Redistribution Platform

This application reduces food waste by connecting providers and receivers.

### 🎯 Objectives
- Reduce food wastage  
- Real-time distribution  
- Support NGOs  

### ⚙️ Features
- CRUD system  
- SQL analytics  
- Data visualization  

### 💼 Impact
- Sustainable system  
- Helps needy people  
""")

# ---------------- CRUD ----------------
elif menu=="CRUD Operations":

    st.title("🔄 CRUD Operations")

    table = st.selectbox("Select Table",["providers","receivers","food_listings","claims"])

    if table=="providers":
        name = st.text_input("Name")
        city = st.text_input("City")
        if st.button("Add Provider"):
            cur.execute("INSERT INTO providers(name,city) VALUES(?,?)",(name,city))
            conn.commit()

    elif table=="receivers":
        name = st.text_input("Name")
        city = st.text_input("City")
        if st.button("Add Receiver"):
            cur.execute("INSERT INTO receivers(name,city) VALUES(?,?)",(name,city))
            conn.commit()

    elif table=="food_listings":
        food = st.text_input("Food Type")
        meal = st.selectbox("Meal",["Breakfast","Lunch","Dinner"])
        city = st.text_input("City")
        qty = st.number_input("Quantity")
        status = st.selectbox("Status",["Available","Expired"])
        if st.button("Add Food"):
            cur.execute("INSERT INTO food_listings(food_type,meal_type,city,quantity,status) VALUES(?,?,?,?,?)",
                        (food,meal,city,qty,status))
            conn.commit()

    elif table=="claims":
        fid = st.number_input("Food ID")
        rid = st.number_input("Receiver ID")
        if st.button("Add Claim"):
            cur.execute("INSERT INTO claims(food_id,receiver_id) VALUES(?,?)",(fid,rid))
            conn.commit()

    st.subheader("📋 Data")
    st.dataframe(pd.read_sql(f"SELECT * FROM {table}",conn))

# ---------------- SQL ----------------
elif menu=="SQL Queries":

    st.title("🧠 SQL Queries")

    queries = {
        "1 Providers per City":"SELECT city, COUNT(*) total FROM providers GROUP BY city",
        "2 Receivers per City":"SELECT city, COUNT(*) total FROM receivers GROUP BY city",
        "3 Food per City":"SELECT city, COUNT(*) total FROM food_listings GROUP BY city",
        "4 Food Type Count":"SELECT food_type, COUNT(*) total FROM food_listings GROUP BY food_type",
        "5 Meal Type Count":"SELECT meal_type, COUNT(*) total FROM food_listings GROUP BY meal_type",
        "6 Status Count":"SELECT status, COUNT(*) total FROM food_listings GROUP BY status",
        "7 Total Quantity":"SELECT SUM(quantity) total FROM food_listings",
        "8 Avg Quantity":"SELECT AVG(quantity) avg FROM food_listings",
        "9 Max Quantity":"SELECT MAX(quantity) max FROM food_listings",
        "10 Min Quantity":"SELECT MIN(quantity) min FROM food_listings",
        "11 Claims Count":"SELECT COUNT(*) total FROM claims",
        "12 Available Food":"SELECT COUNT(*) total FROM food_listings WHERE status='Available'",
        "13 Expired Food":"SELECT COUNT(*) total FROM food_listings WHERE status='Expired'",
        "14 City with Max Food":"SELECT city, COUNT(*) total FROM food_listings GROUP BY city ORDER BY total DESC LIMIT 1",
        "15 Meal with Max Quantity":"SELECT meal_type, SUM(quantity) total FROM food_listings GROUP BY meal_type ORDER BY total DESC LIMIT 1"
    }

    q = st.selectbox("Choose Query", list(queries.keys()))
    st.dataframe(pd.read_sql(queries[q], conn))

# ---------------- VISUAL ----------------
elif menu=="Waste Food Data Visualization":

    st.title("📊 Visualization")

    df = pd.read_sql("SELECT * FROM food_listings", conn)

    options = [
        "City vs Quantity","Food Type Pie","Meal Bar","Status Bar",
        "Quantity Histogram","City Count","Meal Count","Food Count",
        "Status Count","City Pie","Meal Pie","Food Bar",
        "City vs Status","Meal vs Status","Food vs Status"
    ]

    choice = st.selectbox("Choose Visualization", options)

    if not df.empty:
        if choice=="City vs Quantity":
            st.plotly_chart(px.bar(df,x="city",y="quantity"))
        elif choice=="Food Type Pie":
            st.plotly_chart(px.pie(df,names="food_type"))
        elif choice=="Meal Bar":
            st.plotly_chart(px.bar(df,x="meal_type",y="quantity"))
        elif choice=="Status Bar":
            st.plotly_chart(px.bar(df,x="status",y="quantity"))
        elif choice=="Quantity Histogram":
            st.plotly_chart(px.histogram(df,x="quantity"))
        else:
            st.plotly_chart(px.bar(df,x="city",y="quantity"))

# ---------------- CREATOR ----------------
elif menu=="Creator Info":
    st.title("👤 Creator Info")
    st.write("Ashish - Data Analyst")

# ---------------- LOGOUT ----------------
if st.sidebar.button("Logout"):
    st.session_state.login=False
    st.rerun()
