import sqlite3, pandas as pd, os
DB_NAME="food_waste.db"
BASE_DIR=os.path.dirname(os.path.abspath(__file__))
DATA_DIR=os.path.join(BASE_DIR,"data")

def get_connection():
    return sqlite3.connect(DB_NAME)

def create_tables():
    conn=get_connection()
    cur=conn.cursor()
    cur.execute("DROP TABLE IF EXISTS food_listings")
    cur.execute("CREATE TABLE food_listings (Food_ID INTEGER,Food_Name TEXT,Quantity INTEGER,Expiry_Date TEXT,Provider_ID INTEGER,Provider_Type TEXT,Location TEXT,Food_Type TEXT,Meal_Type TEXT)")
    conn.commit()
    conn.close()

def load_csv_data():
    conn=get_connection()
    food=pd.read_csv(os.path.join(DATA_DIR,'food_listings_data.csv'))
    food.to_sql('food_listings',conn,if_exists='replace',index=False)
    conn.close()
