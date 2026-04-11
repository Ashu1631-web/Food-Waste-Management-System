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
                        ["Project Dashboard & Overview","CRUD","Data","Queries"])

# ---------------- DASHBOARD ----------------
if menu == "Project Dashboard & Overview":
    st.title("🥗 Food Waste Management System")

    st.markdown("""
    ### Bridging the Gap Between Surplus and Shortage

    A data-driven platform connecting food providers and receivers 
    to minimize food wastage and maximize resource utilization.
    """)

    col1,col2,col3,col4 = st.columns(4)
    col1.metric("Providers", len(providers_df))
    col2.metric("Receivers", len(receivers_df))
    col3.metric("Food Listings", len(food_df))
    col4.metric("Claims", len(claims_df))

# ---------------- CRUD ----------------
elif menu == "CRUD":
    st.title("🛠️ CRUD + Analytics")

    table = st.selectbox("Select Table", list(data_map.keys()))
    df = data_map[table]

    # FILTER
    if "City" in df.columns:
        city = st.selectbox("Filter by City", ["All"] + list(df["City"].dropna().unique()))
        if city != "All":
            df = df[df["City"] == city]

    st.dataframe(df, use_container_width=True)

    st.markdown("## 📊 Visual Insights")

    col1, col2 = st.columns(2)

    with col1:
        if "City" in df.columns:
            st.plotly_chart(px.bar(df, x="City", title="📍 City Distribution"),
                            use_container_width=True)

        if "City" in df.columns:
            st.plotly_chart(px.pie(df, names="City", title="🥧 City Share"),
                            use_container_width=True)

        if "Quantity" in df.columns:
            st.plotly_chart(px.box(df, y="Quantity", title="📦 Quantity Spread"),
                            use_container_width=True)

    with col2:
        if "City" in df.columns:
            st.plotly_chart(px.histogram(df, x="City", title="📊 City Frequency"),
                            use_container_width=True)

        if "Quantity" in df.columns:
            st.plotly_chart(px.line(df, y="Quantity", title="📈 Quantity Trend"),
                            use_container_width=True)

        if "Quantity" in df.columns:
            st.plotly_chart(px.scatter(df, x="Quantity", y="Quantity",
                                      title="🔍 Quantity Scatter"),
                            use_container_width=True)

# ---------------- DATA ----------------
elif menu == "Data":
    st.title("📂 Data Tables")

    for name, df in data_map.items():
        st.markdown(f"### {name}")
        st.dataframe(df, use_container_width=True)

# ---------------- QUERIES ----------------
elif menu == "Queries":
    st.title("📊 SQL Queries (30 Questions)")

    queries = {
        "1. Total Food Quantity": ("SELECT SUM(Quantity) FROM food", lambda: food_df["Quantity"].sum()),
        "2. Total Providers": ("SELECT COUNT(*) FROM providers", lambda: len(providers_df)),
        "3. Total Receivers": ("SELECT COUNT(*) FROM receivers", lambda: len(receivers_df)),
        "4. Total Claims": ("SELECT COUNT(*) FROM claims", lambda: len(claims_df)),
        "5. Food by City": ("SELECT City, SUM(Quantity) GROUP BY City",
                           lambda: food_df.groupby("City")["Quantity"].sum()),
        "6. Providers by City": ("SELECT City, COUNT(*) GROUP BY City",
                                lambda: providers_df.groupby("City").size()),
        "7. Receivers by City": ("SELECT City, COUNT(*) GROUP BY City",
                                lambda: receivers_df.groupby("City").size()),
        "8. Avg Food Quantity": ("SELECT AVG(Quantity) FROM food",
                                lambda: food_df["Quantity"].mean()),
        "9. Max Food Quantity": ("SELECT MAX(Quantity) FROM food",
                                lambda: food_df["Quantity"].max()),
        "10. Min Food Quantity": ("SELECT MIN(Quantity) FROM food",
                                 lambda: food_df["Quantity"].min())
    }

    selected = st.selectbox("Select Question", list(queries.keys()))

    st.markdown("### ❓ Question")
    st.write(selected)

    st.markdown("### 🧠 SQL Formula")
    st.code(queries[selected][0])

    if st.button("Run Query"):
        result = queries[selected][1]()
        st.success("Result")
        st.write(result)
