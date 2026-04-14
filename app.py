import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Food Waste System", layout="wide")

COLOR_SEQ = ["#7F77DD","#1D9E75","#D85A30","#378ADD","#D4537E","#BA7517",
             "#639922","#533AB7","#0F6E56","#993C1D"]

def apply_theme(fig, title=""):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(20,20,30,0.6)",
        font=dict(family="Inter, sans-serif", size=13, color="#e0e0e0"),
        margin=dict(l=50, r=30, t=60, b=50),
        title_text=title,
        title_font_size=15,
        title_x=0.5,
        title_font_color="#c9c3ff",
        legend=dict(bgcolor="rgba(0,0,0,0)", font_size=11),
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.07)", zeroline=False)
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.07)", zeroline=False)
    return fig

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_clean(file):
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip().str.title()
    return df

providers_df = load_clean("providers_data.csv")
receivers_df  = load_clean("receivers_data.csv")
food_df       = load_clean("food_listings_data.csv")
claims_df     = load_clean("claims_data.csv")

data_map = {
    "Providers":     providers_df,
    "Receivers":     receivers_df,
    "Food Listings": food_df,
    "Claims":        claims_df,
}

def get_col(df, names):
    for col in df.columns:
        if col.lower() in [n.lower() for n in names]:
            return col
    return None

# ==================== LOGIN ====================
if "login" not in st.session_state:
    st.session_state.login       = False
    st.session_state.login_error = False

if not st.session_state.login:
    st.markdown("""
    <style>
    .block-container { padding-top: 0 !important; padding-bottom: 0 !important; max-width: 100% !important; }
    [data-testid="stAppViewContainer"] {
        background-image: url("https://images.unsplash.com/photo-1606914501449-5a96b6ce24ca?q=80&w=870&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    [data-testid="stHeader"]          { background: transparent !important; }
    [data-testid="stMain"]            { background: transparent !important; }
    /* remove any white-box padding divs */
    div[data-testid="stMainBlockContainer"] { background: transparent !important; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <style>
    .login-card {
        background: rgba(18,18,28,0.90);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(127,119,221,0.40);
        border-radius: 22px;
        padding: 2.8rem 2.4rem 2.2rem;
        margin: 8vh auto 0;
        max-width: 400px;
        text-align: center;
    }
    .login-title { font-size:2rem; font-weight:700; color:#a09cff; margin-bottom:.2rem; }
    .login-sub   { font-size:.9rem; color:#888; margin-bottom:1.8rem; }
    .err-box {
        background: rgba(163,45,45,0.25);
        border: 1px solid #a32d2d;
        border-radius: 10px;
        color: #f09595;
        padding: .55rem 1rem;
        font-size: .88rem;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

    _, mid, _ = st.columns([1, 1.5, 1])
    with mid:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown('<div class="login-title">🥗 FoodWise</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-sub">Local Food Management Analysis</div>', unsafe_allow_html=True)

        if st.session_state.login_error:
            st.markdown('<div class="err-box">❌ Invalid username or password. Please try again.</div>',
                        unsafe_allow_html=True)

        u = st.text_input("Username", placeholder="Enter username")
        p = st.text_input("Password", type="password", placeholder="Enter password")

        if st.button("🔐 Login", use_container_width=True):
            if u == "admin" and p == "1234":
                st.session_state.login       = True
                st.session_state.login_error = False
                st.rerun()
            else:
                st.session_state.login_error = True
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==================== SIDEBAR ====================
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
Streamlit · Pandas · Plotly
""")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Providers",     len(providers_df))
    c2.metric("Receivers",     len(receivers_df))
    c3.metric("Food Listings", len(food_df))
    c4.metric("Claims",        len(claims_df))

# ==================== CRUD / EDA ====================
elif menu == "CRUD":
    st.title("🛠️ CRUD + Analytics")

    table = st.selectbox("Select Table", list(data_map.keys()))
    df = data_map[table].copy()

    city_col   = get_col(df, ["city","location"])
    type_col   = get_col(df, ["type","food_type","meal_type","provider_type"])
    status_col = get_col(df, ["status","claim_status"])
    qty_col    = get_col(df, ["quantity"])

    # --- 2 context-aware filters ---
    f1, f2 = st.columns(2)

    filter_labels = {
        "Providers":     ("🏪 Filter by Provider Type", "📍 Filter by City"),
        "Receivers":     ("👥 Filter by Receiver Type",  "📍 Filter by City"),
        "Food Listings": ("🥘 Filter by Food Type",      "📍 Filter by City"),
        "Claims":        ("🔖 Filter by Status",         "📍 Filter by City"),
    }
    lbl1, lbl2 = filter_labels.get(table, ("Filter 1","Filter 2"))

    with f1:
        col1 = status_col if table == "Claims" else type_col
        if col1:
            opts = ["All"] + sorted(df[col1].dropna().unique().tolist())
            sel1 = st.selectbox(lbl1, opts)
            if sel1 != "All":
                df = df[df[col1] == sel1]
        else:
            st.info("No type/status column found.")

    with f2:
        if city_col:
            opts2 = ["All"] + sorted(df[city_col].dropna().unique().tolist())
            sel2  = st.selectbox(lbl2, opts2)
            if sel2 != "All":
                df = df[df[city_col] == sel2]
        else:
            st.info("No city column found.")

    if df.empty:
        st.warning("⚠️ No records match the selected filters.")
    else:
        st.dataframe(df, use_container_width=True)

    # ---- 10 GRAPHS ----
    st.markdown("## 📊 Visual Insights")

    if df.empty:
        st.info("Adjust filters to see charts.")
    else:
        # re-detect on filtered df
        city_col   = get_col(df, ["city","location"])
        type_col   = get_col(df, ["type","food_type","meal_type","provider_type"])
        status_col = get_col(df, ["status","claim_status"])
        qty_col    = get_col(df, ["quantity"])
        drawn = 0

        try:
            # 1 – City Bar (top 20)
            if city_col:
                t = df[city_col].value_counts().nlargest(20).reset_index()
                t.columns = ["City","Count"]
                fig = px.bar(t, x="City", y="Count", color="City",
                             color_discrete_sequence=COLOR_SEQ,
                             labels={"City":"City","Count":"Records"})
                st.plotly_chart(apply_theme(fig, f"📍 Top Cities — {table}"), use_container_width=True)
                drawn += 1

            # 2 – City Pie (top 10 to avoid 0.1% mess)
            if city_col:
                t = df[city_col].value_counts().nlargest(10).reset_index()
                t.columns = ["City","Count"]
                fig = px.pie(t, names="City", values="Count",
                             color_discrete_sequence=COLOR_SEQ, hole=0.38)
                fig.update_traces(textposition="inside", textinfo="percent+label", textfont_size=11)
                st.plotly_chart(apply_theme(fig, f"🗺️ City Share (Top 10) — {table}"), use_container_width=True)
                drawn += 1

            # 3 – Type / Status Bar
            grp_col = status_col if table == "Claims" else type_col
            if grp_col:
                t = df[grp_col].value_counts().reset_index()
                t.columns = ["Group","Count"]
                label = "Status" if table == "Claims" else "Type"
                fig = px.bar(t, x="Group", y="Count", color="Group",
                             color_discrete_sequence=COLOR_SEQ,
                             labels={"Group": label,"Count":"Count"})
                st.plotly_chart(apply_theme(fig, f"🏷️ Distribution by {label} — {table}"), use_container_width=True)
                drawn += 1

            # 4 – Type / Status Donut
            if grp_col:
                t = df[grp_col].value_counts().reset_index()
                t.columns = ["Group","Count"]
                fig = px.pie(t, names="Group", values="Count",
                             color_discrete_sequence=COLOR_SEQ, hole=0.45)
                fig.update_traces(textposition="inside", textinfo="percent+label", textfont_size=11)
                st.plotly_chart(apply_theme(fig, f"🥧 {label} Share — {table}"), use_container_width=True)
                drawn += 1

            # 5 – Status Funnel (only for Claims)
            if status_col:
                t = df[status_col].value_counts().reset_index()
                t.columns = ["Status","Count"]
                fig = px.funnel(t, x="Count", y="Status",
                                color="Status", color_discrete_sequence=COLOR_SEQ)
                st.plotly_chart(apply_theme(fig, f"🔻 Status Funnel — {table}"), use_container_width=True)
                drawn += 1

            # 6 – Quantity Box
            if qty_col:
                fig = px.box(df, y=qty_col, color_discrete_sequence=COLOR_SEQ,
                             labels={qty_col:"Quantity (units)"})
                fig.update_traces(marker_color="#7F77DD", line_color="#a09cff")
                st.plotly_chart(apply_theme(fig, f"📦 Quantity Spread — {table}"), use_container_width=True)
                drawn += 1

            # 7 – Quantity Histogram
            if qty_col:
                fig = px.histogram(df, x=qty_col, nbins=25,
                                   color_discrete_sequence=["#1D9E75"],
                                   labels={qty_col:"Quantity","count":"Frequency"})
                st.plotly_chart(apply_theme(fig, f"📊 Quantity Frequency — {table}"), use_container_width=True)
                drawn += 1

            # 8 – Total Qty by City
            if qty_col and city_col:
                grp = df.groupby(city_col)[qty_col].sum().nlargest(15).reset_index()
                grp.columns = ["City","Total Qty"]
                fig = px.bar(grp, x="City", y="Total Qty", color="City",
                             color_discrete_sequence=COLOR_SEQ,
                             labels={"City":"City","Total Qty":"Total Quantity"})
                st.plotly_chart(apply_theme(fig, f"🏙️ Total Quantity by City — {table}"), use_container_width=True)
                drawn += 1

            # 9 – Avg Qty by Type (horizontal)
            if qty_col and type_col:
                grp = df.groupby(type_col)[qty_col].mean().reset_index()
                grp.columns = ["Type","Avg Qty"]
                grp["Avg Qty"] = grp["Avg Qty"].round(1)
                fig = px.bar(grp, x="Avg Qty", y="Type", orientation="h",
                             color="Type", color_discrete_sequence=COLOR_SEQ,
                             labels={"Type":"Type","Avg Qty":"Average Quantity"})
                st.plotly_chart(apply_theme(fig, f"📈 Avg Quantity by Type — {table}"), use_container_width=True)
                drawn += 1

            # 10 – Qty Trend line
            if qty_col:
                fig = px.line(df.reset_index(), x="index", y=qty_col,
                              color_discrete_sequence=["#7F77DD"],
                              labels={"index":"Record #", qty_col:"Quantity"})
                fig.update_traces(line_width=1.8)
                st.plotly_chart(apply_theme(fig, f"📉 Quantity Trend — {table}"), use_container_width=True)
                drawn += 1

            if drawn == 0:
                st.info("No graphable columns found for this table/filter combination.")

        except Exception as e:
            st.warning(f"Some charts could not be rendered: {e}")

# ==================== DATA ====================
elif menu == "Data":
    st.title("📂 Data Management")

    table = st.selectbox("Select Dataset", list(data_map.keys()))
    df    = data_map[table]
    st.dataframe(df, use_container_width=True)

    st.markdown("## ➕ Add Record")
    new_data = {}
    for col in df.columns:
        new_data[col] = st.text_input(col)

    if st.button("Add Record"):
        data_map[table] = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
        st.success("✅ Record Added")

    st.markdown("## ❌ Delete Record")
    id_col    = df.columns[0]
    delete_id = st.selectbox("Select ID to Delete", df[id_col])
    if st.button("Delete Record"):
        data_map[table] = df[df[id_col] != delete_id]
        st.success("🗑️ Record Deleted")

# ==================== QUERIES ====================
elif menu == "Queries":
    st.title("📊 SQL Queries")

    city       = get_col(food_df,      ["city","location"])
    qty        = get_col(food_df,      ["quantity"])
    food_type  = get_col(food_df,      ["food_type","type"])
    prov_type  = get_col(providers_df, ["type"])
    claim_city = get_col(claims_df,    ["city","location"])

    queries = {
        "Total Providers":      ("SELECT COUNT(*) FROM providers;",
                                  lambda: len(providers_df)),
        "Total Receivers":      ("SELECT COUNT(*) FROM receivers;",
                                  lambda: len(receivers_df)),
        "Total Food Listings":  ("SELECT COUNT(*) FROM food_listings;",
                                  lambda: len(food_df)),
        "Total Claims":         ("SELECT COUNT(*) FROM claims;",
                                  lambda: len(claims_df)),
        "Total Quantity":       ("SELECT SUM(quantity) FROM food_listings;",
                                  lambda: food_df[qty].sum() if qty else "Missing Column"),
        "Average Quantity":     ("SELECT AVG(quantity) FROM food_listings;",
                                  lambda: round(food_df[qty].mean(),2) if qty else "Missing Column"),
        "Food by City":         ("SELECT city, SUM(quantity) FROM food_listings GROUP BY city;",
                                  lambda: food_df.groupby(city)[qty].sum() if city and qty else "Missing Column"),
        "Food Count by Type":   ("SELECT food_type, COUNT(*) FROM food_listings GROUP BY food_type;",
                                  lambda: food_df[food_type].value_counts() if food_type else "Missing Column"),
        "Providers by Type":    ("SELECT type, COUNT(*) FROM providers GROUP BY type;",
                                  lambda: providers_df[prov_type].value_counts() if prov_type else "Missing Column"),
        "High Quantity (>50)":  ("SELECT * FROM food_listings WHERE quantity > 50;",
                                  lambda: food_df[food_df[qty]>50] if qty else "Missing Column"),
        "Low Quantity (<10)":   ("SELECT * FROM food_listings WHERE quantity < 10;",
                                  lambda: food_df[food_df[qty]<10] if qty else "Missing Column"),
        "Top 5 Highest":        ("SELECT * FROM food_listings ORDER BY quantity DESC LIMIT 5;",
                                  lambda: food_df.sort_values(qty,ascending=False).head(5) if qty else "Missing Column"),
        "Bottom 5":             ("SELECT * FROM food_listings ORDER BY quantity ASC LIMIT 5;",
                                  lambda: food_df.sort_values(qty).head(5) if qty else "Missing Column"),
        "Unique Cities":        ("SELECT DISTINCT city FROM food_listings;",
                                  lambda: food_df[city].unique() if city else "Missing Column"),
        "Unique Food Types":    ("SELECT DISTINCT food_type FROM food_listings;",
                                  lambda: food_df[food_type].unique() if food_type else "Missing Column"),
        "Food + Provider Join": ("SELECT f.*, p.name FROM food_listings f JOIN providers p ON f.provider_id=p.provider_id;",
                                  lambda: food_df.merge(providers_df, on="Provider_Id", how="left")),
        "Claims + Food Join":   ("SELECT c.*, f.food_name FROM claims c JOIN food_listings f ON c.food_id=f.food_id;",
                                  lambda: claims_df.merge(food_df, on="Food_Id", how="left")),
        "City with Max Food":   ("SELECT city FROM food_listings GROUP BY city ORDER BY SUM(quantity) DESC LIMIT 1;",
                                  lambda: food_df.groupby(city)[qty].sum().idxmax() if city and qty else "Missing Column"),
        "Claims per City":      ("SELECT city, COUNT(*) FROM claims GROUP BY city;",
                                  lambda: claims_df.groupby(claim_city).size() if claim_city else "Missing Column"),
        "All Quantities":       ("SELECT quantity FROM food_listings;",
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
