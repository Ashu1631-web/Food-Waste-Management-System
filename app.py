import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.linear_model import LinearRegression
import sqlite3
import os

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Food Waste Dashboard", layout="wide")

# ---------------- CSS ----------------
st.markdown("""
<style>
.stApp {
    background-image: url("https://images.unsplash.com/photo-1504674900247-0877df9cc836");
    background-size: cover;
    background-attachment: fixed;
}

[data-testid="stHeader"] {background: transparent;}

.stTextInput>div>div>input:focus {
    box-shadow: none !important;
    border: 1px solid #555 !important;
}

.glass {
    background: rgba(0,0,0,0.65);
    padding: 30px;
    border-radius: 20px;
    backdrop-filter: blur(12px);
    color: white;
}

.kpi {
    background: linear-gradient(135deg,#00C9A7,#007CF0);
    padding:20px;
    border-radius:15px;
    color:white;
    text-align:center;
    font-weight:bold;
}

h1,h2,h3,label {color:white !important;}
</style>
""", unsafe_allow_html=True)

# ---------------- LOGIN FIX (NO DB) ----------------
def login(username, password):
    if username == "admin" and password == "1234":
        return True
    return False

# SESSION
if "login" not in st.session_state:
    st.session_state.login = False

# ---------------- LOGIN PAGE ----------------
if not st.session_state.login:

    st.markdown("<h1 style='text-align:center;'>🍱 Food Waste Management</h1>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    # OVERVIEW
    with col1:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.subheader("📌 Project Overview")
        st.write("""
✔ Reduce food waste  
✔ Connect providers & receivers  
✔ SQL analytics dashboard  
✔ 12 advanced charts  
✔ ML demand prediction  
✔ Admin control system  
        """)
        st.markdown('</div>', unsafe_allow_html=True)

    # LOGIN
    with col2:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.subheader("🔐 Login")

        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Login"):
            if login(u, p):
                st.session_state.login = True
                st.session_state.role = "admin"
                st.success("Login Successful ✅")
                st.rerun()
            else:
                st.error("Invalid username or password ❌")

        st.markdown('</div>', unsafe_allow_html=True)

    st.stop()

# ---------------- DATABASE (ONLY FOR DATA) ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "food_waste.db")

conn = sqlite3.connect(db_path, check_same_thread=False)
cur = conn.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS providers (id INTEGER PRIMARY KEY, name TEXT, city TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS receivers (id INTEGER PRIMARY KEY, name TEXT, type TEXT)")
cur.execute("""CREATE TABLE IF NOT EXISTS food_listings (
id INTEGER PRIMARY KEY, food_name TEXT, quantity INTEGER,
food_type TEXT, meal_type TEXT, city TEXT,
expiry_date DATE, status TEXT, provider_id INTEGER)""")
cur.execute("CREATE TABLE IF NOT EXISTS claims (id INTEGER PRIMARY KEY, food_id INTEGER, receiver_id INTEGER)")

# SAMPLE DATA
if cur.execute("SELECT COUNT(*) FROM providers").fetchone()[0] == 0:
    cur.execute("INSERT INTO providers VALUES (1,'Hotel Taj','Delhi'),(2,'Food Hub','Mumbai')")
if cur.execute("SELECT COUNT(*) FROM receivers").fetchone()[0] == 0:
    cur.execute("INSERT INTO receivers VALUES (1,'NGO','NGO'),(2,'Shelter','Shelter')")
if cur.execute("SELECT COUNT(*) FROM food_listings").fetchone()[0] == 0:
    cur.execute("""
    INSERT INTO food_listings VALUES
    (1,'Rice',10,'Veg','Lunch','Delhi','2026-04-10','Available',1),
    (2,'Bread',5,'Veg','Breakfast','Noida','2026-04-08','Expired',1),
    (3,'Chicken',8,'Non-Veg','Dinner','Mumbai','2026-04-11','Available',2)
    """)

conn.commit()

# ---------------- SIDEBAR ----------------
menu = st.sidebar.radio("📊 Menu", ["🏠 Dashboard","🤖 ML","🛠 Admin"])

# ---------------- DASHBOARD ----------------
if menu == "🏠 Dashboard":

    st.title("📊 Dashboard")

    c1, c2, c3, c4 = st.columns(4)

    total_food = pd.read_sql("SELECT COUNT(*) FROM food_listings", conn).iloc[0,0]
    total_prov = pd.read_sql("SELECT COUNT(*) FROM providers", conn).iloc[0,0]
    total_recv = pd.read_sql("SELECT COUNT(*) FROM receivers", conn).iloc[0,0]
    total_claim = pd.read_sql("SELECT COUNT(*) FROM claims", conn).iloc[0,0]

    c1.markdown(f"<div class='kpi'>🍱<br>{total_food}<br>Total Food</div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='kpi'>🏢<br>{total_prov}<br>Providers</div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='kpi'>👥<br>{total_recv}<br>Receivers</div>", unsafe_allow_html=True)
    c4.markdown(f"<div class='kpi'>📦<br>{total_claim}<br>Claims</div>", unsafe_allow_html=True)

    st.subheader("📈 Charts")

    df1 = pd.read_sql("SELECT city, COUNT(*) as total FROM providers GROUP BY city", conn)
    st.plotly_chart(px.bar(df1, x="city", y="total"))

    df2 = pd.read_sql("SELECT food_type, COUNT(*) as total FROM food_listings GROUP BY food_type", conn)
    st.plotly_chart(px.pie(df2, names="food_type", values="total"))

    df3 = pd.read_sql("SELECT meal_type, COUNT(*) as total FROM food_listings GROUP BY meal_type", conn)
    st.plotly_chart(px.pie(df3, names="meal_type", values="total"))

# ---------------- ML ----------------
elif menu == "🤖 ML":

    st.title("🤖 Demand Prediction")

    df = pd.read_sql("SELECT quantity, food_type, city FROM food_listings", conn)
    df = pd.get_dummies(df)

    X = df.drop("quantity", axis=1)
    y = df["quantity"]

    model = LinearRegression()
    model.fit(X, y)

    food = st.selectbox("Food", [c for c in X.columns if "food_type" in c])
    city = st.selectbox("City", [c for c in X.columns if "city" in c])

    if st.button("Predict"):
        inp = pd.DataFrame([0]*len(X.columns)).T
        inp.columns = X.columns
        inp[food] = 1
        inp[city] = 1
        st.success(f"Prediction: {round(model.predict(inp)[0],2)}")

# ---------------- ADMIN ----------------
elif menu == "🛠 Admin":

    st.title("Admin Panel")

    if st.button("Delete Expired Food"):
        conn.execute("DELETE FROM food_listings WHERE expiry_date < DATE('now')")
        conn.commit()
        st.success("Deleted")

# ---------------- LOGOUT ----------------
if st.sidebar.button("Logout"):
    st.session_state.login = False
    st.rerun()
