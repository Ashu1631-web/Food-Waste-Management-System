import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

# ---------------------------
# DATABASE CONNECTION
# ---------------------------
conn = sqlite3.connect("food_waste.db", check_same_thread=False)

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(page_title="Food Waste Management System", layout="wide")

# ---------------------------
# LOGIN FUNCTION (SECURE)
# ---------------------------
def login(username, password):
    query = "SELECT * FROM users WHERE username=? AND password=?"
    return conn.execute(query, (username, password)).fetchone()

# ---------------------------
# SESSION STATE
# ---------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None

# ---------------------------
# LOGIN UI
# ---------------------------
if not st.session_state.logged_in:
    st.title("🔐 Login System")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = login(username, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.role = user[3]
            st.session_state.username = username
            st.success(f"Welcome {username} ({user[3]})")
            st.rerun()
        else:
            st.error("Invalid Credentials")

    st.stop()

# ---------------------------
# SIDEBAR
# ---------------------------
st.sidebar.title("📌 Navigation")

if st.session_state.role == "admin":
    st.sidebar.success("Admin Access")
else:
    st.sidebar.info("User Access")

menu = st.sidebar.radio("Go to", ["Dashboard", "ML Prediction", "Admin Panel"])

# ---------------------------
# COMMON FUNCTION
# ---------------------------
def run_query(query):
    return pd.read_sql(query, conn)

# =========================================================
# 📊 DASHBOARD
# =========================================================
if menu == "Dashboard":

    st.title("🍱 Food Waste Management Dashboard")

    # ---------------------------
    # 15 SQL Queries
    # ---------------------------
    queries = {
        "1. Total Food Items":
        "SELECT COUNT(*) AS total_food FROM food_listings",

        "2. Providers by City":
        "SELECT city, COUNT(*) as total FROM providers GROUP BY city",

        "3. Receivers by Type":
        "SELECT type, COUNT(*) FROM receivers GROUP BY type",

        "4. Food Status":
        "SELECT status, COUNT(*) FROM food_listings GROUP BY status",

        "5. Top Providers":
        """SELECT p.name, COUNT(*) as total 
           FROM providers p 
           JOIN food_listings f ON p.provider_id=f.provider_id
           GROUP BY p.name ORDER BY total DESC LIMIT 5""",

        "6. Most Common Food Type":
        "SELECT food_type, COUNT(*) as total FROM food_listings GROUP BY food_type ORDER BY total DESC",

        "7. Food by City":
        "SELECT city, COUNT(*) as total FROM food_listings GROUP BY city",

        "8. Total Claims":
        "SELECT COUNT(*) FROM claims",

        "9. Available Food":
        "SELECT * FROM food_listings WHERE status='Available'",

        "10. Providers without Donations":
        """SELECT p.name FROM providers p 
           LEFT JOIN food_listings f ON p.provider_id=f.provider_id
           WHERE f.provider_id IS NULL""",

        "11. Top Receivers":
        """SELECT r.name, COUNT(*) as total 
           FROM receivers r 
           JOIN claims c ON r.receiver_id=c.receiver_id
           GROUP BY r.name ORDER BY total DESC LIMIT 5""",

        "12. Avg Quantity":
        "SELECT AVG(quantity) FROM food_listings",

        "13. Expired Food":
        "SELECT * FROM food_listings WHERE expiry_date < DATE('now')",

        "14. Meal Type Distribution":
        "SELECT meal_type, COUNT(*) FROM food_listings GROUP BY meal_type",

        "15. Full Join Data":
        """SELECT p.name as provider, r.name as receiver, f.food_name
           FROM claims c
           JOIN food_listings f ON c.food_id=f.food_id
           JOIN providers p ON f.provider_id=p.provider_id
           JOIN receivers r ON c.receiver_id=r.receiver_id"""
    }

    selected_query = st.selectbox("📊 Select SQL Query", list(queries.keys()))
    df = run_query(queries[selected_query])
    st.dataframe(df, use_container_width=True)

    # ---------------------------
    # CHARTS (12)
    # ---------------------------
    st.markdown("## 📈 Data Visualizations")

    df1 = run_query("SELECT city, COUNT(*) as total FROM providers GROUP BY city")
    st.plotly_chart(px.bar(df1, x="city", y="total", title="Providers by City"))

    df2 = run_query("SELECT type, COUNT(*) as total FROM receivers GROUP BY type")
    st.plotly_chart(px.pie(df2, names="type", values="total", title="Receivers Distribution"))

    df3 = run_query("SELECT food_type, COUNT(*) as total FROM food_listings GROUP BY food_type")
    st.plotly_chart(px.bar(df3, x="food_type", y="total", title="Food Type"))

    df4 = run_query("SELECT meal_type, COUNT(*) as total FROM food_listings GROUP BY meal_type")
    st.plotly_chart(px.pie(df4, names="meal_type", values="total", title="Meal Type"))

    df5 = run_query("SELECT status, COUNT(*) as total FROM food_listings GROUP BY status")
    st.plotly_chart(px.bar(df5, x="status", y="total", title="Food Status"))

    df6 = run_query("""
    SELECT p.name, COUNT(*) as total 
    FROM providers p JOIN food_listings f 
    ON p.provider_id=f.provider_id 
    GROUP BY p.name ORDER BY total DESC LIMIT 5
    """)
    st.plotly_chart(px.bar(df6, x="name", y="total", title="Top Providers"))

    df7 = run_query("""
    SELECT r.name, COUNT(*) as total 
    FROM receivers r JOIN claims c 
    ON r.receiver_id=c.receiver_id 
    GROUP BY r.name ORDER BY total DESC LIMIT 5
    """)
    st.plotly_chart(px.bar(df7, x="name", y="total", title="Top Receivers"))

    df8 = run_query("SELECT COUNT(*) as total FROM claims")
    st.metric("Total Claims", df8.iloc[0,0])

    df9 = run_query("SELECT COUNT(*) as total FROM food_listings WHERE expiry_date < DATE('now')")
    st.metric("Expired Food Items", df9.iloc[0,0])

    df10 = run_query("SELECT AVG(quantity) FROM food_listings")
    st.metric("Avg Quantity", round(df10.iloc[0,0],2))

    df11 = run_query("SELECT city, COUNT(*) as total FROM food_listings GROUP BY city")
    st.plotly_chart(px.line(df11, x="city", y="total", title="Food by City"))

    df12 = run_query("SELECT food_type, status, COUNT(*) as total FROM food_listings GROUP BY food_type, status")
    st.plotly_chart(px.bar(df12, x="food_type", y="total", color="status", title="Food Type vs Status"))

# =========================================================
# 🤖 ML PREDICTION
# =========================================================
elif menu == "ML Prediction":

    st.title("🤖 Food Demand Prediction")

    df_ml = pd.read_sql("SELECT quantity, food_type, city FROM food_listings", conn)

    df_ml = pd.get_dummies(df_ml, columns=["food_type", "city"])

    X = df_ml.drop("quantity", axis=1)
    y = df_ml["quantity"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    model = LinearRegression()
    model.fit(X_train, y_train)

    food_cols = [col for col in X.columns if "food_type" in col]
    city_cols = [col for col in X.columns if "city" in col]

    selected_food = st.selectbox("Select Food Type", food_cols)
    selected_city = st.selectbox("Select City", city_cols)

    if st.button("Predict Demand"):
        input_data = pd.DataFrame([0]*len(X.columns)).T
        input_data.columns = X.columns

        input_data[selected_food] = 1
        input_data[selected_city] = 1

        prediction = model.predict(input_data)[0]

        st.success(f"Predicted Demand: {round(prediction,2)}")

# =========================================================
# 🛠 ADMIN PANEL
# =========================================================
elif menu == "Admin Panel":

    if st.session_state.role != "admin":
        st.error("Access Denied")
        st.stop()

    st.title("🛠 Admin Panel")

    if st.button("Delete Expired Food"):
        conn.execute("DELETE FROM food_listings WHERE expiry_date < DATE('now')")
        conn.commit()
        st.success("Expired food deleted")

    if st.button("View Users"):
        df_users = pd.read_sql("SELECT * FROM users", conn)
        st.dataframe(df_users)

# ---------------------------
# LOGOUT
# ---------------------------
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()
