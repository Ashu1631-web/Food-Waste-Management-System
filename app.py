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
file_map = {
    "Providers": "providers_data.csv",
    "Receivers": "receivers_data.csv",
    "Food Listings": "food_listings_data.csv",
    "Claims": "claims_data.csv"
}

# Load function (NO CACHE → live update)
def load_clean(file):
    if os.path.exists(file):
        df = pd.read_csv(file)
        df.columns = df.columns.str.strip().str.title()
        return df
    else:
        return pd.DataFrame()

# Load all datasets
providers_df = load_clean(file_map["Providers"])
receivers_df = load_clean(file_map["Receivers"])
food_df = load_clean(file_map["Food Listings"])
claims_df = load_clean(file_map["Claims"])

# Store in dictionary (used in app)
data_map = {
    "Providers": providers_df,
    "Receivers": receivers_df,
    "Food Listings": food_df,
    "Claims": claims_df,
}

# Utility function (column detection)
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
        background-image: url("https://wallpaperaccess.com/full/767252.jpg");
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
    df_orig = data_map[table].copy()

    # ── Smart column detection ──
    city_col   = get_col(df_orig, ["city", "location"])
    type_col   = get_col(df_orig, ["type", "food_type", "meal_type", "provider_type", "receiver_type"])
    status_col = get_col(df_orig, ["status", "claim_status"])
    qty_col    = get_col(df_orig, ["quantity", "quantity_claimed"])

    # All categorical cols (for fallback)
    all_cat = [c for c in df_orig.columns if df_orig[c].dtype == object]
    # All numeric cols (for fallback)
    all_num = [c for c in df_orig.columns if pd.api.types.is_numeric_dtype(df_orig[c])]

    # ── Resolve filter columns per table ──
    FILTER_CFG = {
        "Providers":     (type_col,   "🏪 Provider Type",  city_col,   "📍 City"),
        "Receivers":     (type_col,   "👥 Receiver Type",  city_col,   "📍 City"),
        "Food Listings": (type_col,   "🥘 Food Type",      city_col,   "📍 City"),
        "Claims":        (status_col, "🔖 Claim Status",
                          city_col or get_col(df_orig, ["provider_id", "receiver_id", "food_id"]),
                          "📍 City" if city_col else "🔗 Provider ID"),
    }
    col1, lbl1, col2, lbl2 = FILTER_CFG.get(table, (all_cat[0] if all_cat else None, "Filter 1",
                                                     all_cat[1] if len(all_cat) > 1 else None, "Filter 2"))

    f1, f2 = st.columns(2)
    df = df_orig.copy()

    with f1:
        if col1 and col1 in df.columns:
            opts = ["All"] + sorted(df[col1].dropna().astype(str).unique().tolist())
            sel1 = st.selectbox(lbl1, opts)
            if sel1 != "All":
                df = df[df[col1].astype(str) == sel1]
        else:
            st.info("No primary filter available.")

    with f2:
        if col2 and col2 in df.columns:
            opts2 = ["All"] + sorted(df[col2].dropna().astype(str).unique().tolist())
            sel2  = st.selectbox(lbl2, opts2)
            if sel2 != "All":
                df = df[df[col2].astype(str) == sel2]
        else:
            st.info("No secondary filter available.")

    if df.empty:
        st.warning("⚠️ No records match the selected filters.")
    else:
        st.dataframe(df, use_container_width=True)

    # ==================== 10 GRAPHS ====================
    st.markdown(f"## 📊 Visual Insights — {table}")

    if df.empty:
        st.info("Adjust filters to see charts.")
    else:
        # Re-detect on filtered df
        city_c   = get_col(df, ["city", "location"])
        type_c   = get_col(df, ["type", "food_type", "meal_type", "provider_type", "receiver_type"])
        status_c = get_col(df, ["status", "claim_status"])
        qty_c    = get_col(df, ["quantity", "quantity_claimed"])
        grp_c    = status_c if table == "Claims" else type_c
        grp_lbl  = "Status" if table == "Claims" else "Type"

        # Fallbacks
        cat_fallbacks = [c for c in df.columns if df[c].dtype == object
                         and c not in [city_c, type_c, status_c] and df[c].nunique() <= 40]
        num_fallbacks = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])
                         and c != qty_c]
        num_c = qty_c or (num_fallbacks[0] if num_fallbacks else None)
        num_lbl = "Quantity" if qty_c else (num_fallbacks[0] if num_fallbacks else "Value")
        cat_extra = cat_fallbacks[0] if cat_fallbacks else (grp_c or city_c)

        # Helper: safe bar
        def cat_bar(col, title, top=20):
            t = df[col].value_counts().nlargest(top).reset_index()
            t.columns = [col, "Count"]
            return apply_theme(px.bar(t, x=col, y="Count", color=col,
                               color_discrete_sequence=COLOR_SEQ,
                               labels={col: col, "Count": "Records"}), title)

        try:
            # ── Graph 1: Top Cities / primary-cat bar ──
            g1_col = city_c or grp_c or cat_extra
            g1_lbl = "City" if g1_col == city_c else (grp_lbl if g1_col == grp_c else g1_col)
            st.plotly_chart(cat_bar(g1_col, f"📍 Top {g1_lbl}s — {table}"), use_container_width=True)

            # ── Graph 2: City / primary-cat pie ──
            t2 = df[g1_col].value_counts().nlargest(10).reset_index()
            t2.columns = [g1_col, "Count"]
            fig2 = px.pie(t2, names=g1_col, values="Count",
                          color_discrete_sequence=COLOR_SEQ, hole=0.38)
            fig2.update_traces(textposition="inside", textinfo="percent+label", textfont_size=11)
            st.plotly_chart(apply_theme(fig2, f"🗺️ {g1_lbl} Share (Top 10) — {table}"), use_container_width=True)

            # ── Graph 3: grp_col bar (type/status) ──
            g3_col = grp_c or (city_c if city_c != g1_col else cat_extra)
            g3_lbl = grp_lbl if g3_col == grp_c else (g3_col or "Category")
            if g3_col and g3_col != g1_col:
                st.plotly_chart(cat_bar(g3_col, f"🏷️ Distribution by {g3_lbl} — {table}"), use_container_width=True)
            else:
                # Treemap fallback
                t3 = df[g1_col].value_counts().reset_index(); t3.columns = [g1_col, "Count"]
                fig3 = px.treemap(t3, path=[g1_col], values="Count", color_discrete_sequence=COLOR_SEQ)
                st.plotly_chart(apply_theme(fig3, f"🏷️ {g1_lbl} Treemap — {table}"), use_container_width=True)

            # ── Graph 4: grp_col donut ──
            g4_col = g3_col or g1_col
            g4_lbl = g3_lbl or g1_lbl
            t4 = df[g4_col].value_counts().reset_index(); t4.columns = [g4_col, "Count"]
            fig4 = px.pie(t4, names=g4_col, values="Count",
                          color_discrete_sequence=COLOR_SEQ, hole=0.45)
            fig4.update_traces(textposition="inside", textinfo="percent+label", textfont_size=11)
            st.plotly_chart(apply_theme(fig4, f"🥧 {g4_lbl} Share — {table}"), use_container_width=True)

            # ── Graph 5: Status Funnel OR stacked bar (city × type) ──
            if status_c:
                t5 = df[status_c].value_counts().reset_index(); t5.columns = ["Status", "Count"]
                fig5 = px.funnel(t5, x="Count", y="Status",
                                 color="Status", color_discrete_sequence=COLOR_SEQ)
                st.plotly_chart(apply_theme(fig5, f"🔻 Status Funnel — {table}"), use_container_width=True)
            elif city_c and type_c and city_c != type_c:
                cross5 = df.groupby([city_c, type_c]).size().unstack(fill_value=0)
                fig5 = px.bar(cross5.reset_index(), x=city_c, y=cross5.columns.tolist(),
                              color_discrete_sequence=COLOR_SEQ, barmode="stack",
                              labels={city_c: "City"})
                st.plotly_chart(apply_theme(fig5, f"🔻 {grp_lbl} by City (Stacked) — {table}"), use_container_width=True)
            else:
                t5 = df[g1_col].value_counts().reset_index(); t5.columns = [g1_col, "Count"]
                fig5 = px.funnel(t5.head(8), x="Count", y=g1_col,
                                 color=g1_col, color_discrete_sequence=COLOR_SEQ)
                st.plotly_chart(apply_theme(fig5, f"🔻 {g1_lbl} Funnel — {table}"), use_container_width=True)

            # ── Graph 6: Qty / num box ──
            if num_c:
                fig6 = px.box(df, y=num_c, color_discrete_sequence=COLOR_SEQ,
                              labels={num_c: num_lbl})
                fig6.update_traces(marker_color="#7F77DD", line_color="#a09cff")
                st.plotly_chart(apply_theme(fig6, f"📦 {num_lbl} Spread — {table}"), use_container_width=True)
            else:
                # Records KPI card
                fig6 = go.Figure(go.Indicator(
                    mode="number", value=len(df),
                    title={"text": f"Total {table} Records", "font": {"color": "#a09cff"}},
                    number={"font": {"color": "#c9c3ff", "size": 72}},
                ))
                fig6.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                                   margin=dict(t=60, b=40))
                st.plotly_chart(apply_theme(fig6, f"📦 Record Count — {table}"), use_container_width=True)

            # ── Graph 7: Qty / num histogram OR cross-tab bar ──
            if num_c:
                fig7 = px.histogram(df, x=num_c, nbins=25,
                                    color_discrete_sequence=["#1D9E75"],
                                    labels={num_c: num_lbl, "count": "Frequency"})
                st.plotly_chart(apply_theme(fig7, f"📊 {num_lbl} Distribution — {table}"), use_container_width=True)
            elif grp_c and city_c:
                cross7 = pd.crosstab(df[grp_c].fillna("?"), df[city_c].fillna("?"))
                fig7 = px.imshow(cross7, color_continuous_scale="Purples",
                                 labels=dict(color="Count"),
                                 aspect="auto")
                st.plotly_chart(apply_theme(fig7, f"📊 {grp_lbl} × City Heatmap — {table}"), use_container_width=True)
            else:
                fig7 = px.bar(df[g1_col].value_counts().reset_index().rename(
                              columns={g1_col: g1_lbl, "count": "Count"}),
                              x=g1_lbl, y="Count", color_discrete_sequence=["#1D9E75"])
                st.plotly_chart(apply_theme(fig7, f"📊 {g1_lbl} Count Bars — {table}"), use_container_width=True)

            # ── Graph 8: Total Qty by City OR records by city ──
            if city_c:
                if qty_c:
                    g8 = df.groupby(city_c)[qty_c].sum().nlargest(15).reset_index()
                    g8.columns = ["City", "Total Qty"]
                    fig8 = px.bar(g8, x="City", y="Total Qty", color="City",
                                  color_discrete_sequence=COLOR_SEQ,
                                  labels={"City": "City", "Total Qty": "Total Quantity"})
                    st.plotly_chart(apply_theme(fig8, f"🏙️ Total Quantity by City — {table}"), use_container_width=True)
                else:
                    g8 = df.groupby(city_c).size().nlargest(15).reset_index()
                    g8.columns = ["City", "Count"]
                    fig8 = px.bar(g8, x="City", y="Count", color="City",
                                  color_discrete_sequence=COLOR_SEQ)
                    st.plotly_chart(apply_theme(fig8, f"🏙️ Records by City — {table}"), use_container_width=True)
            else:
                # Treemap of grp_col
                t8 = df[grp_c or g1_col].value_counts().reset_index()
                t8.columns = ["Cat", "Count"]
                fig8 = px.treemap(t8, path=["Cat"], values="Count", color_discrete_sequence=COLOR_SEQ)
                st.plotly_chart(apply_theme(fig8, f"🏙️ {grp_lbl} Treemap — {table}"), use_container_width=True)

            # ── Graph 9: Avg Qty by Type OR grouped bar ──
            if num_c and grp_c:
                g9 = df.groupby(grp_c)[num_c].mean().reset_index()
                g9.columns = [grp_lbl, f"Avg {num_lbl}"]
                g9[f"Avg {num_lbl}"] = g9[f"Avg {num_lbl}"].round(1)
                fig9 = px.bar(g9, x=f"Avg {num_lbl}", y=grp_lbl, orientation="h",
                              color=grp_lbl, color_discrete_sequence=COLOR_SEQ,
                              labels={grp_lbl: grp_lbl, f"Avg {num_lbl}": f"Avg {num_lbl}"})
                st.plotly_chart(apply_theme(fig9, f"📈 Avg {num_lbl} by {grp_lbl} — {table}"), use_container_width=True)
            elif grp_c and city_c:
                g9 = df.groupby([grp_c, city_c]).size().unstack(fill_value=0)
                fig9 = px.bar(g9.reset_index(), x=grp_c, y=g9.columns.tolist(),
                              barmode="group", color_discrete_sequence=COLOR_SEQ)
                st.plotly_chart(apply_theme(fig9, f"📈 {grp_lbl} Count by City — {table}"), use_container_width=True)
            else:
                top9_col = cat_extra or g1_col
                t9 = df[top9_col].value_counts().nlargest(15).reset_index()
                t9.columns = [top9_col, "Count"]
                fig9 = px.bar(t9, x=top9_col, y="Count", color=top9_col,
                              orientation="v", color_discrete_sequence=COLOR_SEQ)
                st.plotly_chart(apply_theme(fig9, f"📈 Top {top9_col} Values — {table}"), use_container_width=True)

            # ── Graph 10: Qty trend line OR cumulative area ──
            df_r = df.reset_index(drop=True).reset_index()
            if num_c:
                fig10 = px.line(df_r, x="index", y=num_c,
                                color_discrete_sequence=["#7F77DD"],
                                labels={"index": "Record #", num_c: num_lbl})
                fig10.update_traces(line_width=1.8)
                st.plotly_chart(apply_theme(fig10, f"📉 {num_lbl} Trend — {table}"), use_container_width=True)
            else:
                df_r["Cumulative"] = range(1, len(df_r) + 1)
                fig10 = px.area(df_r, x="index", y="Cumulative",
                                color_discrete_sequence=["#7F77DD"],
                                labels={"index": "Record #", "Cumulative": "Cumulative Count"})
                fig10.update_traces(line_width=1.8)
                st.plotly_chart(apply_theme(fig10, f"📉 Cumulative Records — {table}"), use_container_width=True)

            st.caption(f"✅ 10 charts rendered for **{table}**")

        except Exception as e:
            st.warning(f"⚠️ Some charts could not be rendered: {e}")

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
    new_df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)

    # SAVE to CSV
    new_df.to_csv(file_map[table], index=False)

    st.success("✅ Record Added & Saved")
    st.rerun()

    st.markdown("## ❌ Delete Record")
    id_col    = df.columns[0]
    delete_id = st.selectbox("Select ID to Delete", df[id_col])
if st.button("Delete Record"):
    new_df = df[df[id_col] != delete_id]

    # SAVE to CSV
    new_df.to_csv(file_map[table], index=False)

    st.success("🗑️ Record Deleted & Saved")
    st.rerun()

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
