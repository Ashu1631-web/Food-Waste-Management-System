import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Food Waste System", layout="wide")

# ---------------- LOAD DATA ----------------
def load_clean(file):
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip()
    df.columns = df.columns.str.title()
    return df

providers_df = load_clean("providers_data.csv")
receivers_df = load_clean("receivers_data.csv")
food_df = load_clean("food_listings_data.csv")
claims_df = load_clean("claims_data.csv")

data_map = {
    "Providers": providers_df,
    "Receivers": receivers_df,
    "Food Listings": food_df,
    "Claims": claims_df
}

# ---------------- HELPER ----------------
def get_col(df, names):
    for col in df.columns:
        if col.lower() in [n.lower() for n in names]:
            return col
    return None

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

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if u == "admin" and p == "1234":
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
## 🌍 Bridging the Gap Between Surplus and Shortage

A smart platform connecting providers & receivers using analytics.
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

    # -------- FILTER BY TYPE --------
    type_col = None
    for col in df.columns:
        if col.lower() in ["type", "food_type", "meal_type"]:
            type_col = col
            break

    if type_col:
        val = st.selectbox("Filter by Type", ["All"] + list(df[type_col].dropna().unique()))
        if val != "All":
            df = df[df[type_col] == val]

    st.dataframe(df, use_container_width=True)

    # -------- SAFE GRAPHS --------
    st.markdown("## 📊 Visual Insights")

    city_col = get_col(df, ["city", "location"])
    qty_col = get_col(df, ["quantity"])

    try:
        if city_col:
            st.plotly_chart(px.bar(df, x=city_col, title="City Distribution"), use_container_width=True)
            st.plotly_chart(px.pie(df, names=city_col, title="City Share"), use_container_width=True)
            st.plotly_chart(px.histogram(df, x=city_col, title="City Frequency"), use_container_width=True)

        if qty_col:
            st.plotly_chart(px.box(df, y=qty_col, title="Quantity Spread"), use_container_width=True)
            st.plotly_chart(px.line(df, y=qty_col, title="Quantity Trend"), use_container_width=True)
            st.plotly_chart(px.scatter(df, x=qty_col, y=qty_col, title="Quantity Scatter"), use_container_width=True)

    except Exception as e:
        st.warning("Graphs not available for this dataset")

# ---------------- DATA ----------------
elif menu == "Data":
    st.title("📂 Data Management")

    table = st.selectbox("Select Dataset", list(data_map.keys()))
    df = data_map[table]

    st.dataframe(df, use_container_width=True)

    # -------- ADD RECORD --------
    st.markdown("## ➕ Add Record")

    new_data = {}
    for col in df.columns:
        new_data[col] = st.text_input(col)

    if st.button("Add Record"):
        df.loc[len(df)] = list(new_data.values())
        st.success("Record Added")

    # -------- DELETE RECORD --------
    st.markdown("## ❌ Delete Record")

    id_col = df.columns[0]
    delete_id = st.selectbox("Select ID", df[id_col])

    if st.button("Delete Record"):
        df = df[df[id_col] != delete_id]
        st.success("Record Deleted")

# ---------------- SQL ----------------
elif menu == "Queries":
    st.title("📊 SQL Queries")

    city_f = get_col(food_df, ["city", "location"])
    qty = get_col(food_df, ["quantity"])

    queries = {
        "Total Quantity":
            ("SELECT SUM(Quantity) FROM food_listings;",
             lambda: food_df[qty].sum() if qty else "Missing Column"),

        "Food by City":
            ("SELECT City, SUM(Quantity) FROM food_listings GROUP BY City;",
             lambda: food_df.groupby(city_f)[qty].sum() if city_f and qty else "Missing Column"),

        "Providers Count":
            ("SELECT COUNT(*) FROM providers;",
             lambda: len(providers_df))
    }

    q = st.selectbox("Select Question", list(queries.keys()))

    st.markdown("### ❓ Question")
    st.write(q)

    st.markdown("### 🧠 SQL Query")
    st.code(queries[q][0])

    if st.button("Run"):
        st.write(queries[q][1]())
