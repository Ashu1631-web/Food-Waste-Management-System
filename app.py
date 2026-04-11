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

A smart platform connecting food providers & receivers using analytics.

### 📌 Project Mission
Our platform acts as a digital bridge to reduce food waste and feed those in need.

### 🚀 Core Features
- 📊 Real-time analytics dashboard  
- 🛠️ CRUD operations  
- 📈 Smart visual insights  
- 🔍 SQL query engine  

### 🛠️ Tech Stack
- Streamlit  
- Pandas  
- Plotly  
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

    # -------- GRAPHS --------
    st.markdown("## 📊 Visual Insights")

    city_col = get_col(df, ["city", "location"])
    qty_col = get_col(df, ["quantity"])

    try:
        if city_col:
            st.plotly_chart(px.bar(df, x=city_col, title="City Distribution"), use_container_width=True)
            st.plotly_chart(px.pie(df, names=city_col, title="City Share"), use_container_width=True)

        if qty_col:
            st.plotly_chart(px.box(df, y=qty_col, title="Quantity Spread"), use_container_width=True)
            st.plotly_chart(px.line(df, y=qty_col, title="Quantity Trend"), use_container_width=True)
            st.plotly_chart(px.histogram(df, x=qty_col, title="Quantity Histogram"), use_container_width=True)
            st.plotly_chart(px.scatter(df, x=qty_col, y=qty_col, title="Quantity Scatter"), use_container_width=True)

    except:
        st.warning("Graphs not supported for this dataset")

# ---------------- DATA ----------------
elif menu == "Data":
    st.title("📂 Data Management")

    table = st.selectbox("Select Dataset", list(data_map.keys()))
    df = data_map[table]

    st.dataframe(df, use_container_width=True)

    # -------- ADD --------
    st.markdown("## ➕ Add Record")

    new_data = {}
    for col in df.columns:
        new_data[col] = st.text_input(col)

    if st.button("Add Record"):
        df.loc[len(df)] = list(new_data.values())
        st.success("Record Added")

    # -------- DELETE --------
    st.markdown("## ❌ Delete Record")

    id_col = df.columns[0]
    delete_id = st.selectbox("Select ID", df[id_col])

    if st.button("Delete Record"):
        df = df[df[id_col] != delete_id]
        st.success("Record Deleted")

# ---------------- SQL ----------------
elif menu == "Queries":
    st.title("📊 SQL Queries")

    city = get_col(food_df, ["city", "location"])
    qty = get_col(food_df, ["quantity"])
    food_type = get_col(food_df, ["food_type", "type"])
    provider_type = get_col(providers_df, ["type"])

    queries = {

    "Total Providers":
        ("SELECT COUNT(*) FROM providers;",
         lambda: len(providers_df)),

    "Total Receivers":
        ("SELECT COUNT(*) FROM receivers;",
         lambda: len(receivers_df)),

    "Total Food Listings":
        ("SELECT COUNT(*) FROM food_listings;",
         lambda: len(food_df)),

    "Total Claims":
        ("SELECT COUNT(*) FROM claims;",
         lambda: len(claims_df)),

    "Total Quantity":
        ("SELECT SUM(quantity) FROM food_listings;",
         lambda: food_df[qty].sum() if qty else "Missing Column"),

    "Average Quantity":
        ("SELECT AVG(quantity) FROM food_listings;",
         lambda: food_df[qty].mean() if qty else "Missing Column"),

    "Food by City":
        ("SELECT city, SUM(quantity) FROM food_listings GROUP BY city;",
         lambda: food_df.groupby(city)[qty].sum() if city and qty else "Missing Column"),

    "Food Count by Type":
        ("SELECT food_type, COUNT(*) FROM food_listings GROUP BY food_type;",
         lambda: food_df[food_type].value_counts() if food_type else "Missing Column"),

    "Providers by Type":
        ("SELECT type, COUNT(*) FROM providers GROUP BY type;",
         lambda: providers_df[provider_type].value_counts() if provider_type else "Missing Column"),

    "High Quantity (>50)":
        ("SELECT * FROM food_listings WHERE quantity > 50;",
         lambda: food_df[food_df[qty] > 50] if qty else "Missing Column"),

    "Low Quantity (<10)":
        ("SELECT * FROM food_listings WHERE quantity < 10;",
         lambda: food_df[food_df[qty] < 10] if qty else "Missing Column"),

    "Top 5 Highest":
        ("SELECT * FROM food_listings ORDER BY quantity DESC LIMIT 5;",
         lambda: food_df.sort_values(qty, ascending=False).head(5) if qty else "Missing Column"),

    "Bottom 5":
        ("SELECT * FROM food_listings ORDER BY quantity ASC LIMIT 5;",
         lambda: food_df.sort_values(qty).head(5) if qty else "Missing Column"),

    "Unique Cities":
        ("SELECT DISTINCT city FROM food_listings;",
         lambda: food_df[city].unique() if city else "Missing Column"),

    "Unique Food Types":
        ("SELECT DISTINCT food_type FROM food_listings;",
         lambda: food_df[food_type].unique() if food_type else "Missing Column"),

    "Food + Provider Join":
        ("SELECT f.*, p.name FROM food_listings f JOIN providers p ON f.provider_id = p.provider_id;",
         lambda: food_df.merge(providers_df, on="Provider_Id", how="left")),

    "Claims + Food Join":
        ("SELECT c.*, f.food_name FROM claims c JOIN food_listings f ON c.food_id = f.food_id;",
         lambda: claims_df.merge(food_df, on="Food_Id", how="left")),

    "City with Max Food":
        ("SELECT city FROM food_listings GROUP BY city ORDER BY SUM(quantity) DESC LIMIT 1;",
         lambda: food_df.groupby(city)[qty].sum().idxmax() if city and qty else "Missing Column"),

    "Claims per City":
        ("SELECT city, COUNT(*) FROM claims GROUP BY city;",
         lambda: claims_df.groupby(city).size() if city else "Missing Column"),

    "All Quantities":
        ("SELECT quantity FROM food_listings;",
         lambda: food_df[qty] if qty else "Missing Column")
    }

    selected = st.selectbox("Select Question", list(queries.keys()))

    st.markdown("### ❓ Question")
    st.write(selected)

    st.markdown("### 🧠 SQL Query")
    st.code(queries[selected][0], language="sql")

    if st.button("Run Query"):
        result = queries[selected][1]()

        st.markdown("### ✅ Output")
        if isinstance(result, pd.DataFrame) or isinstance(result, pd.Series):
            st.dataframe(result, use_container_width=True)
        else:
            st.success(result)
