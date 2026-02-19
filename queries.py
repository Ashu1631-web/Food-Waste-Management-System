queries = {

"1. Providers per City":
"""
SELECT City, COUNT(*) AS Total_Providers
FROM providers
GROUP BY City;
""",

"2. Total Quantity Available":
"""
SELECT SUM(Quantity) AS Total_Food
FROM food_listings;
""",

"3. City with Highest Listings":
"""
SELECT Location, COUNT(*) AS Listings
FROM food_listings
GROUP BY Location
ORDER BY Listings DESC;
""",

"4. Most Common Food Types":
"""
SELECT Food_Type, COUNT(*) AS Count
FROM food_listings
GROUP BY Food_Type
ORDER BY Count DESC;
""",

"5. Claims Status Summary":
"""
SELECT Status, COUNT(*) AS Total
FROM claims
GROUP BY Status;
"""
}
