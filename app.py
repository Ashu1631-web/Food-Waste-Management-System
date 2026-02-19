import streamlit as st
import pandas as pd
import sqlite3
import os

from database import create_tables, load_csv_data
from queries import queries

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Food Waste Management", layout="wide")

DB_NAME = "food_waste.db"

# ---------------- FINAL FIX DATABASE INITIALIZATION ----------------
# Streamlit Cloud हर बार restart पर database reset करता है
# इसलिए हमेशा fresh tables बनाओ और CSV data load करो

create_tables()
load_csv_data()

# ---------------- CONNECTION FUNCTION ----------------
def get_conn():
    return sqlite3.connect(DB_NAME)
