import streamlit as st
import pandas as pd
import sqlite3
from database import create_tables, load_csv_data
from queries import queries

st.set_page_config(page_title="Food Waste Management", layout="wide")
DB_NAME="food_waste.db"

create_tables()
load_csv_data()

def get_conn():
    return sqlite3.connect(DB_NAME)

st.sidebar.title("🍲 Food Wastage System")
menu=st.sidebar.radio("Navigation",["Dashboard","Food Listings","SQL Query Results"])

if menu=="Dashboard":
    st.title("📊 Dashboard")
    conn=get_conn()
    total=pd.read_sql("SELECT SUM(Quantity) AS Total FROM food_listings",conn)
    val=total["Total"][0]
    if pd.isna(val): val=0
    st.metric("Total Food Available",int(val))
    conn.close()

elif menu=="Food Listings":
    st.title("🍲 Food Listings")
    conn=get_conn()
    df=pd.read_sql("SELECT * FROM food_listings",conn)
    st.dataframe(df)
    conn.close()

else:
    st.title("📌 Query Outputs")
    q=st.selectbox("Select Query",list(queries.keys()))
    conn=get_conn()
    out=pd.read_sql(queries[q],conn)
    st.dataframe(out)
    conn.close()
