import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Food Waste System", layout="wide")

# ---------------- LOAD CSV DATA ----------------
providers_df = pd.read_csv("providers_data.csv")
receivers_df = pd.read_csv("receivers_data.csv")
food_df = pd.read_csv("food_listings_data.csv")
claims_df = pd.read_csv("claims_data.csv")

# ---------------- LOGIN ----------------
if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:

    st.markdown("""
    <style>
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1504674900247-0877df9cc836");
        background-size: cover;
    }

    .overlay {
        position: fixed;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.4); /* lighter = clear image */
    }

    .center-box {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 300px;
    }
    </style>

    <div class="overlay"></div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='center-box'>", unsafe_allow_html=True)

    st.title("🍔 Login")

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

    st.markdown("## 📌 Project Overview")
    st.info("Food Waste Management System reduces food wastage using smart analytics.")

    col1,col2,col3,col4 = st.columns(4)

    col1.markdown(f"<div class='card'>Providers<br><h2>{len(providers_df)}</h2></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='card'>Receivers<br><h2>{len(receivers_df)}</h2></div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='card'>Food<br><h2>{len(food_df)}</h2></div>", unsafe_allow_html=True)
    col4.markdown(f"<div class='card'>Claims<br><h2>{len(claims_df)}</h2></div>", unsafe_allow_html=True)

# ---------------- CRUD ----------------
elif menu == "CRUD":
    st.title("🛠️ CRUD + Analytics")

    table = st.selectbox("Select Table",
                         ["Providers","Receivers","Food Listings","Claims"])

    data_map = {
        "Providers": providers_df,
        "Receivers": receivers_df,
        "Food Listings": food_df,
        "Claims": claims_df
    }

    df = data_map[table]

    if "City" in df.columns:
        city = st.selectbox("Filter City", ["All"] + list(df["City"].unique()))
        if city != "All":
            df = df[df["City"] == city]

    st.dataframe(df)

    st.markdown("### 📊 Visual Insights")

    if "City" in df.columns:
        st.plotly_chart(px.bar(df, x="City", color="City", title="City Distribution"))

    if "Quantity" in df.columns:
        st.plotly_chart(px.box(df, y="Quantity", title="Quantity Spread"))

# ---------------- DATA ----------------
elif menu == "Data":
    st.title("📂 Data Tables")

    st.markdown("### Providers")
    st.dataframe(providers_df)

    st.markdown("### Receivers")
    st.dataframe(receivers_df)

    st.markdown("### Food Listings")
    st.dataframe(food_df)

    st.markdown("### Claims")
    st.dataframe(claims_df)

# ---------------- QUERIES ----------------
elif menu == "Queries":
    st.title("📊 SQL Queries")

    queries = {
        "Total Food Quantity":"SUM(Quantity)",
        "Providers Count":"COUNT(Providers)",
        "Food by City":"GROUP BY City"
    }

    q = st.selectbox("Select Question", list(queries.keys()))

    st.markdown("### 🧠 Logic")
    st.code(queries[q])

    if st.button("Run"):
        if q == "Total Food Quantity":
            st.write(food_df["Quantity"].sum())

        elif q == "Providers Count":
            st.write(len(providers_df))

        elif q == "Food by City":
            st.dataframe(food_df.groupby("City")["Quantity"].sum())

# ---------------- ABOUT ----------------
elif menu == "About":
    st.title("ℹ️ About")

    st.write("""
    Developed by **Ashish**

    Food Waste Management System with:
    - CSV Data Handling
    - Analytics Dashboard
    - CRUD Interface
    """)
