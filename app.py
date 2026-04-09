import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Food Waste App", layout="wide")

# ---------------- DB ----------------
conn = sqlite3.connect("food.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS food_listings (
id INTEGER PRIMARY KEY AUTOINCREMENT,
food_type TEXT,
meal_type TEXT,
city TEXT,
quantity INTEGER,
status TEXT
)
""")

conn.commit()

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
            st.error("Invalid")
    st.stop()

# ---------------- SIDEBAR ----------------
menu = st.sidebar.radio("Navigation",[
    "Project Introduction",
    "CRUD Operations",
    "SQL Queries",
    "Waste Food Data Visualization"
])

# ---------------- INTRO ----------------
if menu=="Project Introduction":
    st.title("🍱 Food Waste Management")
    st.info("System to reduce food waste using analytics")

# ---------------- CRUD ----------------
elif menu=="CRUD Operations":

    st.title("🛠 CRUD Operations")

    # ADD
    st.subheader("Add Food")
    food = st.text_input("Food Type")
    meal = st.selectbox("Meal",["Breakfast","Lunch","Dinner"])
    city = st.text_input("City")
    qty = st.number_input("Quantity",0,100)
    status = st.selectbox("Status",["Available","Expired"])

    if st.button("Add"):
        cur.execute("INSERT INTO food_listings (food_type,meal_type,city,quantity,status) VALUES (?,?,?,?,?)",
                    (food,meal,city,qty,status))
        conn.commit()
        st.success("Added")

    # VIEW
    df = pd.read_sql("SELECT * FROM food_listings",conn)
    st.subheader("All Data")
    st.dataframe(df)

    # DELETE
    delete_id = st.number_input("Delete ID",0,1000)
    if st.button("Delete"):
        cur.execute("DELETE FROM food_listings WHERE id=?", (delete_id,))
        conn.commit()
        st.success("Deleted")

# ---------------- SQL ----------------
elif menu=="SQL Queries":

    st.title("🧠 SQL Queries")

    query = st.selectbox("Select Query",[
        "Providers per City",
        "Food Type Count",
        "Meal Type Count",
        "Status Count"
    ])

    if query=="Providers per City":
        df = pd.read_sql("SELECT city, COUNT(*) as total FROM food_listings GROUP BY city",conn)

    elif query=="Food Type Count":
        df = pd.read_sql("SELECT food_type, COUNT(*) as total FROM food_listings GROUP BY food_type",conn)

    elif query=="Meal Type Count":
        df = pd.read_sql("SELECT meal_type, COUNT(*) as total FROM food_listings GROUP BY meal_type",conn)

    elif query=="Status Count":
        df = pd.read_sql("SELECT status, COUNT(*) as total FROM food_listings GROUP BY status",conn)

    st.dataframe(df)

# ---------------- VISUAL ----------------
elif menu=="Waste Food Data Visualization":

    st.title("📈 Visualization")

    df = pd.read_sql("SELECT * FROM food_listings",conn)

    if df.empty:
        st.warning("No Data Available")
    else:
        st.plotly_chart(px.bar(df, x="city", y="quantity", color="food_type"))
        st.plotly_chart(px.pie(df, names="food_type"))
        st.plotly_chart(px.bar(df, x="meal_type", y="quantity"))
        st.plotly_chart(px.bar(df, x="status", y="quantity"))

# ---------------- LOGOUT ----------------
if st.sidebar.button("Logout"):
    st.session_state.login=False
    st.rerun()
