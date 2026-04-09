import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from sklearn.linear_model import LinearRegression
import os

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(page_title="Food Waste Dashboard", layout="wide")

# ---------------------------
# PREMIUM CSS
# ---------------------------
st.markdown("""
<style>
body {
    background-color: #0E1117;
}
.kpi-card {
    background: linear-gradient(135deg, #00C9A7, #007CF0);
    padding:20px;
    border-radius:15px;
    color:white;
    text-align:center;
    box-shadow:0px 4px 15px rgba(0,0,0,0.3);
}
.card {
    background:#1E1E1E;
    padding:20px;
    border-radius:15px;
}
button {
    background: linear-gradient(90deg,#00C9A7,#007CF0);
    color:white !important;
    border:none !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# DATABASE
# ---------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "food_waste.db")

conn = sqlite3.connect(db_path, check_same_thread=False)
cursor = conn.cursor()

# ---------------------------
# CREATE TABLES
# ---------------------------
cursor.execute("""CREATE TABLE IF NOT EXISTS providers (provider_id INTEGER PRIMARY KEY, name TEXT, city TEXT)""")
cursor.execute("""CREATE TABLE IF NOT EXISTS receivers (receiver_id INTEGER PRIMARY KEY, name TEXT, type TEXT)""")
cursor.execute("""CREATE TABLE IF NOT EXISTS food_listings (
food_id INTEGER PRIMARY KEY, food_name TEXT, quantity INTEGER, food_type TEXT,
meal_type TEXT, city TEXT, expiry_date DATE, status TEXT, provider_id INTEGER)""")
cursor.execute("""CREATE TABLE IF NOT EXISTS claims (claim_id INTEGER PRIMARY KEY, food_id INTEGER, receiver_id INTEGER, claim_date DATE)""")
cursor.execute("""CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)""")

# ---------------------------
# SAMPLE DATA
# ---------------------------
if cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
    cursor.execute("INSERT INTO users VALUES (1,'admin','admin123','admin'),(2,'user1','user123','user')")

if cursor.execute("SELECT COUNT(*) FROM providers").fetchone()[0] == 0:
    cursor.execute("INSERT INTO providers VALUES (1,'Hotel Taj','Delhi'),(2,'Food Hub','Mumbai')")

if cursor.execute("SELECT COUNT(*) FROM receivers").fetchone()[0] == 0:
    cursor.execute("INSERT INTO receivers VALUES (1,'NGO A','NGO'),(2,'Shelter B','Shelter')")

if cursor.execute("SELECT COUNT(*) FROM food_listings").fetchone()[0] == 0:
    cursor.execute("""INSERT INTO food_listings VALUES
    (1,'Rice',10,'Veg','Lunch','Delhi','2026-04-10','Available',1),
    (2,'Bread',5,'Veg','Breakfast','Noida','2026-04-08','Expired',1)
    """)

conn.commit()

# ---------------------------
# LOGIN
# ---------------------------
def login(u,p):
    return conn.execute("SELECT * FROM users WHERE username=? AND password=?", (u,p)).fetchone()

if "logged" not in st.session_state:
    st.session_state.logged=False
    st.session_state.role=None

# ---------------------------
# LOGIN PAGE
# ---------------------------
if not st.session_state.logged:

    col1,col2=st.columns([1,1])

    with col1:
        st.markdown("## 🍱 Food Waste System")
        st.write("""
- Reduce food waste  
- Smart analytics dashboard  
- ML demand prediction  
- Admin control system  
        """)

    with col2:
        st.markdown("### 🔐 Login")
        u=st.text_input("Username")
        p=st.text_input("Password",type="password")

        if st.button("Login"):
            user=login(u,p)
            if user:
                st.session_state.logged=True
                st.session_state.role=user[3]
                st.rerun()
            else:
                st.error("Invalid")

    st.stop()

# ---------------------------
# SIDEBAR
# ---------------------------
st.sidebar.title("📊 Dashboard")
menu = st.sidebar.radio("Menu", ["🏠 Dashboard","🤖 ML","🛠 Admin"])

# ---------------------------
# DASHBOARD
# ---------------------------
if menu=="🏠 Dashboard":

    st.title("📊 Analytics Dashboard")

    # KPI CARDS
    col1,col2,col3,col4=st.columns(4)

    total_food = pd.read_sql("SELECT COUNT(*) as x FROM food_listings", conn).iloc[0,0]
    total_providers = pd.read_sql("SELECT COUNT(*) FROM providers", conn).iloc[0,0]
    total_receivers = pd.read_sql("SELECT COUNT(*) FROM receivers", conn).iloc[0,0]
    total_claims = pd.read_sql("SELECT COUNT(*) FROM claims", conn).iloc[0,0]

    col1.markdown(f"<div class='kpi-card'>🍱<br>{total_food}<br>Total Food</div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='kpi-card'>🏢<br>{total_providers}<br>Providers</div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='kpi-card'>👥<br>{total_receivers}<br>Receivers</div>", unsafe_allow_html=True)
    col4.markdown(f"<div class='kpi-card'>📦<br>{total_claims}<br>Claims</div>", unsafe_allow_html=True)

    st.markdown("---")

    # CHARTS
    df1=pd.read_sql("SELECT city, COUNT(*) as total FROM providers GROUP BY city",conn)
    st.plotly_chart(px.bar(df1,x="city",y="total",title="Providers by City"))

    df2=pd.read_sql("SELECT food_type, COUNT(*) as total FROM food_listings GROUP BY food_type",conn)
    st.plotly_chart(px.pie(df2,names="food_type",values="total"))

# ---------------------------
# ML
# ---------------------------
elif menu=="🤖 ML":

    st.title("🤖 Demand Prediction")

    df=pd.read_sql("SELECT quantity, food_type, city FROM food_listings",conn)
    df=pd.get_dummies(df)

    X=df.drop("quantity",axis=1)
    y=df["quantity"]

    model=LinearRegression()
    model.fit(X,y)

    food=st.selectbox("Food",[c for c in X.columns if "food_type" in c])
    city=st.selectbox("City",[c for c in X.columns if "city" in c])

    if st.button("Predict"):
        inp=pd.DataFrame([0]*len(X.columns)).T
        inp.columns=X.columns
        inp[food]=1
        inp[city]=1
        pred=model.predict(inp)[0]
        st.success(f"Prediction: {round(pred,2)}")

# ---------------------------
# ADMIN
# ---------------------------
elif menu=="🛠 Admin":

    if st.session_state.role!="admin":
        st.error("No Access")
        st.stop()

    st.title("Admin Panel")

    if st.button("Delete Expired"):
        conn.execute("DELETE FROM food_listings WHERE expiry_date < DATE('now')")
        conn.commit()
        st.success("Deleted")

# ---------------------------
# LOGOUT
# ---------------------------
if st.sidebar.button("Logout"):
    st.session_state.logged=False
    st.rerun()
