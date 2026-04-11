import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Food Waste System", layout="wide")

# ---------------- LOAD DATA ----------------
providers_df = pd.read_csv("providers_data.csv")
receivers_df = pd.read_csv("receivers_data.csv")
food_df = pd.read_csv("food_listings_data.csv")
claims_df = pd.read_csv("claims_data.csv")

data_map = {
    "Providers": providers_df,
    "Receivers": receivers_df,
    "Food Listings": food_df,
    "Claims": claims_df
}

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
    </style>
    """, unsafe_allow_html=True)

    st.title("🍔 Local Food Management Analysis")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if user == "admin" and pwd == "1234":
            st.session_state.login = True
            st.rerun()

    st.stop()

# ---------------- SIDEBAR ----------------
menu = st.sidebar.radio("Navigation",
                        ["Project Dashboard & Overview","CRUD","Data","Queries","About"])

# ---------------- DASHBOARD ----------------
if menu == "Project Dashboard & Overview":
    st.title("🥗 Food Waste Management System")

    st.markdown("""
    ### "Bridging the Gap Between Surplus and Shortage"

    ## 📌 Project Mission
    Our platform serves as a digital bridge connecting food donors with organizations in need. 
    By leveraging data analytics, we aim to transform potential waste into valuable resources.

    ## 🚀 Core Pillars
    - **Real-time Analytics** → Visualizing food trends  
    - **Inventory Control** → Managing food listings  
    - **Claim Management** → Tracking donations  
    - **City-wise Insights** → Supply-demand tracking  

    ## 🛠️ Technical Architecture
    - Streamlit UI  
    - Pandas Data Engine  
    - Plotly Visuals  
    - Secure Login System  

    ## 💡 How the System Works
    1. Donation → Providers list food  
    2. Aggregation → Categorized by city  
    3. Claiming → Receivers claim food  
    4. Reporting → Dashboard insights  

    ## 👤 Developer Credits
    Developed by **Ashish**
    """)

    st.markdown("## 📊 Quick Stats")
    col1,col2,col3,col4 = st.columns(4)
    col1.metric("Providers", len(providers_df))
    col2.metric("Receivers", len(receivers_df))
    col3.metric("Food Listings", len(food_df))
    col4.metric("Claims", len(claims_df))

# ---------------- CRUD ----------------
elif menu == "CRUD":
    st.title("🛠️ CRUD")

    table = st.selectbox("Select Table", list(data_map.keys()))
    df = data_map[table]

    st.dataframe(df)

# ---------------- DATA ----------------
elif menu == "Data":
    st.title("📂 Data Management")

    table = st.selectbox("Select Dataset", list(data_map.keys()))
    df = data_map[table]

    st.dataframe(df)

    # ADD RECORD
    st.markdown("### ➕ Add Record")
    new_data = {}

    for col in df.columns:
        new_data[col] = st.text_input(col)

    if st.button("Add Data"):
        df.loc[len(df)] = list(new_data.values())
        st.success("Data Added")

    # GRAPHS
    st.markdown("### 📊 Visual Insights")

    if "City" in df.columns:
        st.plotly_chart(px.bar(df, x="City", color="City", title="City Distribution"))

    if "Quantity" in df.columns:
        st.plotly_chart(px.box(df, y="Quantity", title="Quantity Spread"))

# ---------------- QUERIES ----------------
elif menu == "Queries":
    st.title("📊 SQL Queries")

    queries = {
        f"Q{i}": f"SELECT * FROM table_{i}" for i in range(1,31)
    }

    selected = st.selectbox("Select Question", list(queries.keys()))

    st.markdown("### ❓ Question")
    st.write(f"Question {selected}")

    st.markdown("### 🧠 Query")
    st.code(queries[selected])

    if st.button("Run Query"):
        st.success("Executed (Demo Result)")
        st.dataframe(food_df.head())

# ---------------- ABOUT ----------------
elif menu == "About":
    st.title("ℹ️ About")

    st.write("""
    Developed by **Ashish**

    A smart system to reduce food waste using analytics, data, and technology.
    """)
