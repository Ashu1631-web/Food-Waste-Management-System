import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Food Waste System", layout="wide")

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------------- BACKGROUND ----------------
def login_bg():
    st.markdown("""
    <style>
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1504674900247-0877df9cc836");
        background-size: cover;
    }
    </style>
    """, unsafe_allow_html=True)

def clear_bg():
    st.markdown("""
    <style>
    .stApp {
        background-color: #0E1117;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------- LOGIN ----------------
if not st.session_state.logged_in:
    login_bg()
    st.title("🔐 Login")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if user == "admin" and pwd == "1234":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid Credentials")

    st.stop()

# ---------------- MAIN APP ----------------
clear_bg()

# ---------------- SIDEBAR ----------------
menu = st.sidebar.radio("Go to", [
    "Dashboard", "Queries", "CRUD", "Data", "About"
])

# ---------------- SAMPLE DATA ----------------
df = pd.DataFrame({
    "City": ["Delhi","Mumbai","Pune","Delhi"],
    "Food_Type": ["Veg","Non-Veg","Veg","Veg"],
    "Quantity": [50,30,20,40]
})

# ---------------- DASHBOARD ----------------
if menu == "Dashboard":
    st.title("📊 Dashboard")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Food", df["Quantity"].sum())
    col2.metric("Cities", df["City"].nunique())
    col3.metric("Records", len(df))

    st.markdown("### Visualizations")

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(px.bar(df, x="City", y="Quantity"), use_container_width=True)
    with c2:
        st.plotly_chart(px.pie(df, names="Food_Type"), use_container_width=True)

# ---------------- QUERIES ----------------
elif menu == "Queries":
    st.title("📊 SQL Queries")

    queries = {
        "Total Food": "SELECT SUM(Quantity) FROM Food",
        "City Count": "SELECT City, COUNT(*) FROM Food GROUP BY City"
    }

    q = st.selectbox("Select Query", list(queries.keys()))

    st.code(queries[q], language="sql")

    if st.button("Run Query"):
        st.success("Executed ✅")
        st.dataframe(df)

# ---------------- CRUD ----------------
elif menu == "CRUD":
    st.title("🛠️ CRUD Operations")

    st.dataframe(df, use_container_width=True)

    with st.expander("➕ Add"):
        city = st.text_input("City")
        qty = st.number_input("Quantity")
        if st.button("Add"):
            df.loc[len(df)] = [city, "Veg", qty]
            st.success("Added")

    with st.expander("✏️ Update"):
        idx = st.number_input("Index", 0, len(df)-1)
        new_city = st.text_input("New City")
        if st.button("Update"):
            df.loc[idx, "City"] = new_city
            st.success("Updated")

    with st.expander("🗑️ Delete"):
        idx = st.number_input("Delete Index", 0, len(df)-1)
        if st.button("Delete"):
            df.drop(idx, inplace=True)
            st.success("Deleted")

# ---------------- DATA ----------------
elif menu == "Data":
    st.title("📂 Data & Analytics")

    with st.expander("Food Data"):

        city = st.selectbox("Filter City", ["All"] + list(df["City"].unique()))
        temp = df if city == "All" else df[df["City"] == city]

        st.dataframe(temp)

        st.download_button("Download CSV", temp.to_csv().encode(), "data.csv")

        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(px.bar(temp, x="City", y="Quantity"), use_container_width=True)
            st.plotly_chart(px.histogram(temp, x="City"), use_container_width=True)
        with c2:
            st.plotly_chart(px.pie(temp, names="Food_Type"), use_container_width=True)
            st.plotly_chart(px.box(temp, y="Quantity"), use_container_width=True)

# ---------------- ABOUT ----------------
elif menu == "About":
    st.title("ℹ️ About")

    st.markdown("""
    ### 🌿 Food Waste Management System

    This project helps reduce food wastage by connecting providers and receivers.

    ### 🚀 Features
    - CRUD operations
    - SQL queries
    - Dashboard analytics
    - Data insights

    ### 🛠 Tech Stack
    - Python
    - Streamlit
    - SQL
    - Plotly

    ### 🔮 Future Scope
    - AI prediction
    - Maps integration
    """)

    st.image("https://images.unsplash.com/photo-1551288049-bebda4e38f71")
