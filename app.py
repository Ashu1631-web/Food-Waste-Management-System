import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Food Waste System", layout="wide")

PLOTLY_THEME = dict(
    template="plotly_white",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", size=13),
    margin=dict(l=40, r=20, t=50, b=40),
    title_font_size=16,
    title_x=0.5,
)

COLOR_SEQ = ["#7F77DD", "#1D9E75", "#D85A30", "#378ADD", "#D4537E", "#BA7517", "#639922"]

# ---------------- LOAD DATA ----------------
def load_clean(file):
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip().str.title()
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

def styled_chart(fig, title=""):
    fig.update_layout(**PLOTLY_THEME)
    if title:
        fig.update_layout(title_text=title)
    return fig

# ---------------- LOGIN ----------------
if "login" not in st.session_state:
    st.session_state.login = False
if "login_error" not in st.session_state:
    st.session_state.login_error = False

if not st.session_state.login:
    st.markdown("""
    <style>
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1504674900247-0877df9cc836");
        background-size: cover;
        background-attachment: fixed;
    }
    .login-box {
        background: rgba(255,255,255,0.92);
        backdrop-filter: blur(12px);
        border-radius: 20px;
        padding: 2.5rem 2rem;
        max-width: 420px;
        margin: 5vh auto;
        box-shadow: 0 8px 32px rgba(0,0,0,0.18);
    }
    .login-title {
        font-size: 2rem;
        font-weight: 700;
        color: #3C3489;
        text-align: center;
        margin-bottom: 0.25rem;
    }
    .login-sub {
        text-align: center;
        color: #888;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }
    .error-msg {
        background: #FCEBEB;
        border: 1px solid #F09595;
        border-radius: 10px;
        color: #A32D2D;
        padding: 0.6rem 1rem;
        font-size: 0.9rem;
        margin-bottom: 1rem;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown('<div class="login-title">🥗 FoodWise</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-sub">Local Food Management Analysis</div>', unsafe_allow_html=True)

        if st.session_state.login_error:
            st.markdown('<div class="error-msg">❌ Invalid username or password. Please try again.</div>', unsafe_allow_html=True)

        u = st.text_input("Username", placeholder="Enter username")
        p = st.text_input("Password", type="password", placeholder="Enter password")

        if st.button("🔐 Login", use_container_width=True):
            if u == "admin" and p == "1234":
                st.session_state.login = True
                st.session_state.login_error = False
                st.rerun()
            else:
                st.session_state.login_error = True
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("## 🥗 FoodWise")
menu = st.sidebar.radio("Navigation",
    ["Project Dashboard & Overview", "CRUD", "Data", "Queries"])

# ==================== DASHBOARD ====================
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
- Streamlit · Pandas · Plotly
""")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Providers", len(providers_df))
    col2.metric("Receivers", len(receivers_df))
    col3.metric("Food Listings", len(food_df))
    col4.metric("Claims", len(claims_df))

# ==================== CRUD ====================
elif menu == "CRUD":
    st.title("🛠️ CRUD + Analytics")

    table = st.selectbox("Select Table", list(data_map.keys()))
    df = data_map[table].copy()

    # -------- FILTER LOGIC --------
    if table == "Claims":
        status_col = get_col(df, ["status", "claim_status"])
        if status_col:
            status_options = ["All"] + sorted(df[status_col].dropna().unique().tolist())
            selected_status = st.selectbox("Filter by Status", status_options)
            if selected_status != "All":
                df = df[df[status_col] == selected_status]
    else:
        type_col = get_col(df, ["type", "food_type", "meal_type"])
        if type_col:
            val = st.selectbox("Filter by Type", ["All"] + list(df[type_col].dropna().unique()))
            if val != "All":
                df = df[df[type_col] == val]

    st.dataframe(df, use_container_width=True)

    # -------- GRAPHS --------
    st.markdown("## 📊 Visual Insights")

    city_col = get_col(df, ["city", "location"])
    qty_col = get_col(df, ["quantity"])
    status_col = get_col(df, ["status", "claim_status"])
    type_col = get_col(df, ["type", "food_type", "meal_type", "provider_type"])
    name_col = get_col(df, ["name", "food_name", "provider_name", "receiver_name"])

    try:
        # City distribution
        if city_col and len(df[city_col].dropna()) > 0:
            city_counts = df[city_col].value_counts().reset_index()
            city_counts.columns = [city_col, "Count"]

            fig1 = px.bar(city_counts, x=city_col, y="Count",
                          color=city_col, color_discrete_sequence=COLOR_SEQ,
                          labels={city_col: "City", "Count": "Number of Records"})
            st.plotly_chart(styled_chart(fig1, f"📍 Distribution by City — {table}"),
                            use_container_width=True)

            fig2 = px.pie(city_counts, names=city_col, values="Count",
                          color_discrete_sequence=COLOR_SEQ,
                          hole=0.35)
            st.plotly_chart(styled_chart(fig2, f"🗺️ City Share — {table}"),
                            use_container_width=True)

        # Type distribution
        if type_col and len(df[type_col].dropna()) > 0:
            type_counts = df[type_col].value_counts().reset_index()
            type_counts.columns = [type_col, "Count"]

            fig3 = px.bar(type_counts, x=type_col, y="Count",
                          color=type_col, color_discrete_sequence=COLOR_SEQ,
                          labels={type_col: "Type", "Count": "Count"})
            st.plotly_chart(styled_chart(fig3, f"🏷️ Distribution by Type — {table}"),
                            use_container_width=True)

            fig4 = px.pie(type_counts, names=type_col, values="Count",
                          color_discrete_sequence=COLOR_SEQ, hole=0.35)
            st.plotly_chart(styled_chart(fig4, f"🥧 Type Share — {table}"),
                            use_container_width=True)

        # Status distribution (Claims)
        if status_col and len(df[status_col].dropna()) > 0:
            status_counts = df[status_col].value_counts().reset_index()
            status_counts.columns = [status_col, "Count"]

            fig5 = px.bar(status_counts, x=status_col, y="Count",
                          color=status_col, color_discrete_sequence=COLOR_SEQ,
                          labels={status_col: "Status", "Count": "Count"})
            st.plotly_chart(styled_chart(fig5, f"📋 Claims by Status — {table}"),
                            use_container_width=True)

            fig6 = px.pie(status_counts, names=status_col, values="Count",
                          color_discrete_sequence=COLOR_SEQ, hole=0.35)
            st.plotly_chart(styled_chart(fig6, f"📊 Status Share — {table}"),
                            use_container_width=True)

        # Quantity charts
        if qty_col and len(df[qty_col].dropna()) > 0:
            fig7 = px.box(df, y=qty_col, color_discrete_sequence=COLOR_SEQ,
                          labels={qty_col: "Quantity (units)"})
            st.plotly_chart(styled_chart(fig7, f"📦 Quantity Spread — {table}"),
                            use_container_width=True)

            fig8 = px.histogram(df, x=qty_col, nbins=20,
                                color_discrete_sequence=COLOR_SEQ,
                                labels={qty_col: "Quantity", "count": "Frequency"})
            st.plotly_chart(styled_chart(fig8, f"📊 Quantity Frequency Distribution — {table}"),
                            use_container_width=True)

            fig9 = px.line(df.reset_index(), x="index", y=qty_col,
                           color_discrete_sequence=COLOR_SEQ,
                           labels={"index": "Record #", qty_col: "Quantity"})
            st.plotly_chart(styled_chart(fig9, f"📈 Quantity Trend — {table}"),
                            use_container_width=True)

            if city_col:
                city_qty = df.groupby(city_col)[qty_col].sum().reset_index()
                fig10 = px.bar(city_qty, x=city_col, y=qty_col,
                               color=city_col, color_discrete_sequence=COLOR_SEQ,
                               labels={city_col: "City", qty_col: "Total Quantity"})
                st.plotly_chart(styled_chart(fig10, f"🏙️ Total Quantity by City — {table}"),
                                use_container_width=True)

    except Exception as e:
        st.warning(f"Some graphs could not be rendered: {e}")

# ==================== DATA ====================
elif menu == "Data":
    st.title("📂 Data Management")

    table = st.selectbox("Select Dataset", list(data_map.keys()))
    df = data_map[table]

    st.dataframe(df, use_container_width=True)

    st.markdown("## ➕ Add Record")
    new_data = {}
    for col in df.columns:
        new_data[col] = st.text_input(col)

    if st.button("Add Record"):
        df.loc[len(df)] = list(new_data.values())
        st.success("✅ Record Added")

    st.markdown("## ❌ Delete Record")
    id_col = df.columns[0]
    delete_id = st.selectbox("Select ID", df[id_col])

    if st.button("Delete Record"):
        data_map[table] = df[df[id_col] != delete_id]
        st.success("🗑️ Record Deleted")

# ==================== QUERIES ====================
elif menu == "Queries":
    st.title("📊 SQL Queries")

    city = get_col(food_df, ["city", "location"])
    qty = get_col(food_df, ["quantity"])
    food_type = get_col(food_df, ["food_type", "type"])
    provider_type = get_col(providers_df, ["type"])
    claim_city = get_col(claims_df, ["city", "location"])

    queries = {
        "Total Providers": (
            "SELECT COUNT(*) FROM providers;",
            lambda: len(providers_df)),
        "Total Receivers": (
            "SELECT COUNT(*) FROM receivers;",
            lambda: len(receivers_df)),
        "Total Food Listings": (
            "SELECT COUNT(*) FROM food_listings;",
            lambda: len(food_df)),
        "Total Claims": (
            "SELECT COUNT(*) FROM claims;",
            lambda: len(claims_df)),
        "Total Quantity": (
            "SELECT SUM(quantity) FROM food_listings;",
            lambda: food_df[qty].sum() if qty else "Missing Column"),
        "Average Quantity": (
            "SELECT AVG(quantity) FROM food_listings;",
            lambda: round(food_df[qty].mean(), 2) if qty else "Missing Column"),
        "Food by City": (
            "SELECT city, SUM(quantity) FROM food_listings GROUP BY city;",
            lambda: food_df.groupby(city)[qty].sum() if city and qty else "Missing Column"),
        "Food Count by Type": (
            "SELECT food_type, COUNT(*) FROM food_listings GROUP BY food_type;",
            lambda: food_df[food_type].value_counts() if food_type else "Missing Column"),
        "Providers by Type": (
            "SELECT type, COUNT(*) FROM providers GROUP BY type;",
            lambda: providers_df[provider_type].value_counts() if provider_type else "Missing Column"),
        "High Quantity (>50)": (
            "SELECT * FROM food_listings WHERE quantity > 50;",
            lambda: food_df[food_df[qty] > 50] if qty else "Missing Column"),
        "Low Quantity (<10)": (
            "SELECT * FROM food_listings WHERE quantity < 10;",
            lambda: food_df[food_df[qty] < 10] if qty else "Missing Column"),
        "Top 5 Highest": (
            "SELECT * FROM food_listings ORDER BY quantity DESC LIMIT 5;",
            lambda: food_df.sort_values(qty, ascending=False).head(5) if qty else "Missing Column"),
        "Bottom 5": (
            "SELECT * FROM food_listings ORDER BY quantity ASC LIMIT 5;",
            lambda: food_df.sort_values(qty).head(5) if qty else "Missing Column"),
        "Unique Cities": (
            "SELECT DISTINCT city FROM food_listings;",
            lambda: food_df[city].unique() if city else "Missing Column"),
        "Unique Food Types": (
            "SELECT DISTINCT food_type FROM food_listings;",
            lambda: food_df[food_type].unique() if food_type else "Missing Column"),
        "Food + Provider Join": (
            "SELECT f.*, p.name FROM food_listings f JOIN providers p ON f.provider_id = p.provider_id;",
            lambda: food_df.merge(providers_df, on="Provider_Id", how="left")),
        "Claims + Food Join": (
            "SELECT c.*, f.food_name FROM claims c JOIN food_listings f ON c.food_id = f.food_id;",
            lambda: claims_df.merge(food_df, on="Food_Id", how="left")),
        "City with Max Food": (
            "SELECT city FROM food_listings GROUP BY city ORDER BY SUM(quantity) DESC LIMIT 1;",
            lambda: food_df.groupby(city)[qty].sum().idxmax() if city and qty else "Missing Column"),
        "Claims per City": (
            "SELECT city, COUNT(*) FROM claims GROUP BY city;",
            lambda: claims_df.groupby(claim_city).size() if claim_city else "Missing Column"),
        "All Quantities": (
            "SELECT quantity FROM food_listings;",
            lambda: food_df[qty] if qty else "Missing Column"),
    }

    selected = st.selectbox("Select Question", list(queries.keys()))

    st.markdown("### ❓ Question")
    st.write(selected)

    st.markdown("### 🧠 SQL Query")
    st.code(queries[selected][0], language="sql")

    if st.button("▶️ Run Query"):
        result = queries[selected][1]()
        st.markdown("### ✅ Output")
        if isinstance(result, (pd.DataFrame, pd.Series)):
            st.dataframe(result, use_container_width=True)
        else:
            st.success(str(result))
