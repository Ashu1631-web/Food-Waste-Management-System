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

# ---------------- COLUMN DETECTION ----------------
def get_col(df, names):
    for col in df.columns:
        if col.lower() in [n.lower() for n in names]:
            return col
    return None

city_f = get_col(food_df, ["city", "location"])
qty = get_col(food_df, ["quantity", "qty"])
city_p = get_col(providers_df, ["city"])
city_r = get_col(receivers_df, ["city"])

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
    ### Bridging the Gap Between Surplus and Shortage

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

    data_map = {
        "Providers": providers_df,
        "Receivers": receivers_df,
        "Food Listings": food_df,
        "Claims": claims_df
    }

    table = st.selectbox("Select Table", list(data_map.keys()))
    df = data_map[table]

    if "City" in df.columns:
        city = st.selectbox("Filter by City", ["All"] + list(df["City"].dropna().unique()))
        if city != "All":
            df = df[df["City"] == city]

    st.dataframe(df)

    st.markdown("## 📊 Visual Insights")

    col1,col2 = st.columns(2)

    with col1:
        if "City" in df.columns:
            st.plotly_chart(px.bar(df, x="City", title="City Distribution"))
            st.plotly_chart(px.pie(df, names="City", title="City Share"))
            st.plotly_chart(px.histogram(df, x="City", title="City Frequency"))

    with col2:
        if "Quantity" in df.columns:
            st.plotly_chart(px.box(df, y="Quantity", title="Quantity Spread"))
            st.plotly_chart(px.line(df, y="Quantity", title="Quantity Trend"))
            st.plotly_chart(px.scatter(df, x="Quantity", y="Quantity", title="Quantity Scatter"))

# ---------------- DATA ----------------
elif menu == "Data":
    st.title("📂 Data Tables")

    for name, df in {
        "Providers": providers_df,
        "Receivers": receivers_df,
        "Food Listings": food_df,
        "Claims": claims_df
    }.items():
        st.markdown(f"### {name}")
        st.dataframe(df)

# ---------------- SQL QUERIES ----------------
elif menu == "Queries":
    st.title("📊 SQL Queries (30 Advanced)")

    queries = {
        "1. Total Food Quantity": ("SUM", lambda: food_df[qty].sum()),
        "2. Avg Food Quantity": ("AVG", lambda: food_df[qty].mean()),
        "3. Max Food Quantity": ("MAX", lambda: food_df[qty].max()),
        "4. Min Food Quantity": ("MIN", lambda: food_df[qty].min()),
        "5. Food by City": ("GROUP BY", lambda: food_df.groupby(city_f)[qty].sum()),
        "6. Providers Count": ("COUNT", lambda: len(providers_df)),
        "7. Receivers Count": ("COUNT", lambda: len(receivers_df)),
        "8. Claims Count": ("COUNT", lambda: len(claims_df)),
        "9. Providers by City": ("GROUP BY", lambda: providers_df.groupby(city_p).size()),
        "10. Receivers by City": ("GROUP BY", lambda: receivers_df.groupby(city_r).size()),
        "11. Top City Food": ("SORT DESC", lambda: food_df.groupby(city_f)[qty].sum().sort_values(ascending=False)),
        "12. Lowest City Food": ("SORT ASC", lambda: food_df.groupby(city_f)[qty].sum().sort_values()),
        "13. Food > 50": ("FILTER", lambda: food_df[food_df[qty] > 50]),
        "14. Food < 50": ("FILTER", lambda: food_df[food_df[qty] < 50]),
        "15. Unique Cities": ("DISTINCT", lambda: food_df[city_f].unique()),
        "16. Total Records": ("COUNT", lambda: len(food_df)),
        "17. Providers + Receivers Join":
            ("JOIN", lambda: pd.merge(providers_df, receivers_df, on=city_p)),
        "18. Food Sorted Desc": ("ORDER BY DESC", lambda: food_df.sort_values(by=qty, ascending=False)),
        "19. Food Sorted Asc": ("ORDER BY ASC", lambda: food_df.sort_values(by=qty)),
        "20. Top 5 Food": ("LIMIT", lambda: food_df.head()),
        "21. Last 5 Food": ("LIMIT", lambda: food_df.tail()),
        "22. City Frequency": ("COUNT GROUP", lambda: food_df[city_f].value_counts()),
        "23. Avg per City": ("AVG GROUP", lambda: food_df.groupby(city_f)[qty].mean()),
        "24. Sum per City": ("SUM GROUP", lambda: food_df.groupby(city_f)[qty].sum()),
        "25. Median Quantity": ("MEDIAN", lambda: food_df[qty].median()),
        "26. Std Dev Quantity": ("STD", lambda: food_df[qty].std()),
        "27. Duplicate Cities": ("DUPLICATE", lambda: food_df[city_f][food_df[city_f].duplicated()]),
        "28. Non Null Records": ("NOT NULL", lambda: food_df.dropna()),
        "29. Claim Status Count":
            ("GROUP BY", lambda: claims_df.groupby(get_col(claims_df, ["status"])).size()
             if get_col(claims_df, ["status"]) else "No Status Column"),
        "30. Combined Data":
            ("JOIN", lambda: pd.merge(food_df, providers_df, left_on=city_f, right_on=city_p))
    }

    selected = st.selectbox("Select Question", list(queries.keys()))

    st.markdown("### ❓ Question")
    st.write(selected)

    st.markdown("### 🧠 SQL Logic")
    st.code(queries[selected][0])

    if st.button("Run Query"):
        try:
            result = queries[selected][1]()
            st.success("Result")
            st.write(result)
        except Exception as e:
            st.error(f"Error: {e}")
