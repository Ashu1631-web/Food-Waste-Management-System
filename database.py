def load_csv_data():
    conn = get_connection()

    # सही File Paths
    food_path = os.path.join(DATA_DIR, "food_listings_data.csv")
    claims_path = os.path.join(DATA_DIR, "claims_data.csv")
    providers_path = os.path.join(DATA_DIR, "providers_data.csv")

    # File Check
    if not os.path.exists(food_path):
        raise FileNotFoundError("Missing file: food_listings_data.csv inside data folder")

    if not os.path.exists(claims_path):
        raise FileNotFoundError("Missing file: claims_data.csv inside data folder")

    if not os.path.exists(providers_path):
        raise FileNotFoundError("Missing file: providers_data.csv inside data folder")

    # Read CSV
    food_listings = pd.read_csv(food_path)
    claims = pd.read_csv(claims_path)
    providers = pd.read_csv(providers_path)

    # Insert into DB
    food_listings.to_sql("food_listings", conn, if_exists="append", index=False)
    claims.to_sql("claims", conn, if_exists="append", index=False)
    providers.to_sql("providers", conn, if_exists="append", index=False)

    conn.close()
