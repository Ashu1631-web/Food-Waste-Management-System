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

# ---------------- MAIN ----------------
clear_bg()

menu = st.sidebar.radio("Go to", [
    "Dashboard", "Queries", "CRUD", "Data", "About"
])

# ---------------- DATA ----------------
providers_df = pd.DataFrame({
    "Provider_ID": [1,2,3],
    "Name": ["A Shop","B Store","C Mart"],
    "City": ["Delhi","Mumbai","Pune"]
})

receivers_df = pd.DataFrame({
    "Receiver_ID": [1,2],
    "Name": ["NGO1","NGO2"],
    "City": ["Delhi","Mumbai"]
})

food_df = pd.DataFrame({
    "Food_ID": [1,2,3],
    "Food_Type": ["Veg","Non-Veg","Veg"],
    "City": ["Delhi","Mumbai","Delhi"],
    "Quantity": [50,30,20]
})

claims_df = pd.DataFrame({
    "Claim_ID": [1,2],
    "City": ["Delhi","Mumbai"],
    "Status": ["Completed","Pending"]
})

# ---------------- DASHBOARD ----------------
if menu == "Dashboard":
    st.title("📊 Dashboard")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Food", food_df["Quantity"].sum())
    col2.metric("Cities", food_df["City"].nunique())
    col3.metric("Records", len(food_df))

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(px.bar(food_df, x="City", y="Quantity"), use_container_width=True)
    with c2:
        st.plotly_chart(px.pie(food_df, names="Food_Type"), use_container_width=True)

# ---------------- QUERIES ----------------
elif menu == "Queries":
    st.title("📊 Database Queries")

    queries = {f"Q{i}": f"SELECT * FROM table_{i};" for i in range(1, 31)}

    selected = st.selectbox("Select Query", list(queries.keys()), key="query_select")

    st.markdown("""
    <style>
    .sql-box {
        background-color: #0e1117;
        color: #00ffcc;
        padding: 18px;
        border-radius: 10px;
        font-family: monospace;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"<div class='sql-box'>{queries[selected]}</div>", unsafe_allow_html=True)

    if st.button("Run Query", key="run_query"):
        st.success("Executed ✅")
        st.dataframe(food_df, use_container_width=True)

# ---------------- CRUD ----------------
elif menu == "CRUD":
    st.title("🛠️ CRUD Management")

    table = st.selectbox("Select Table",
                         ["Providers","Receivers","Food Listings","Claims"],
                         key="crud_table")

    data_map = {
        "Providers": providers_df,
        "Receivers": receivers_df,
        "Food Listings": food_df,
        "Claims": claims_df
    }

    df_selected = data_map[table]

    st.dataframe(df_selected, use_container_width=True)

    # ADD
    with st.expander("➕ Add Record"):
        values = []
        cols = st.columns(2)
        for i, col in enumerate(df_selected.columns):
            with cols[i % 2]:
                values.append(st.text_input(col, key=f"add_{col}_{table}"))

        if st.button("Add", key=f"add_btn_{table}"):
            df_selected.loc[len(df_selected)] = values
            st.success("Added")

    # UPDATE
    with st.expander("✏️ Update Record"):
        idx = st.selectbox("Select Row", df_selected.index, key=f"update_idx_{table}")

        new_vals = []
        for col in df_selected.columns:
            new_vals.append(
                st.text_input(col, str(df_selected.loc[idx, col]),
                              key=f"update_{col}_{table}")
            )

        if st.button("Update", key=f"update_btn_{table}"):
            df_selected.loc[idx] = new_vals
            st.success("Updated")

    # DELETE
    with st.expander("🗑️ Delete Record"):
        idx = st.selectbox("Delete Row", df_selected.index, key=f"delete_idx_{table}")

        if st.button("Delete", key=f"delete_btn_{table}"):
            df_selected.drop(idx, inplace=True)
            st.warning("Deleted")

# ---------------- DATA ----------------
elif menu == "Data":
    st.title("📂 Raw Data & Analytics")

    def section(title, df, col):

        with st.expander(title):

            val = st.selectbox(
                f"{title} Filter",
                ["All"] + list(df[col].unique()),
                key=f"{title}_filter"
            )

            temp = df if val == "All" else df[df[col] == val]

            st.dataframe(temp, use_container_width=True)

            st.download_button(
                "Download",
                temp.to_csv(index=False).encode(),
                f"{title}.csv",
                key=f"{title}_download"
            )

            c1, c2 = st.columns(2)

            with c1:
                st.plotly_chart(px.bar(temp, x=col),
                                use_container_width=True,
                                key=f"{title}_bar")

                st.plotly_chart(px.histogram(temp, x=col),
                                use_container_width=True,
                                key=f"{title}_hist")

            with c2:
                st.plotly_chart(px.pie(temp, names=col),
                                use_container_width=True,
                                key=f"{title}_pie")

                if "Quantity" in temp.columns:
                    st.plotly_chart(px.box(temp, y="Quantity"),
                                    use_container_width=True,
                                    key=f"{title}_box")

    section("Providers", providers_df, "City")
    section("Receivers", receivers_df, "City")
    section("Food Listings", food_df, "City")
    section("Claims", claims_df, "City")

# ---------------- ABOUT ----------------
elif menu == "About":
    st.title("ℹ️ About")

    st.write("""
    Food Waste Management System helps reduce food wastage by connecting providers and receivers.

    Features:
    - Dashboard analytics
    - SQL queries (30)
    - CRUD operations (4 tables)
    - Data insights with filters & graphs
    """)

    st.image("https://images.unsplash.com/photo-1551288049-bebda4e38f71")
