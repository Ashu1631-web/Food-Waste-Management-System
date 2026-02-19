queries = {

"1. Providers per City":
"""
SELECT City, COUNT(*) AS Total_Providers
FROM providers
GROUP BY City;
""",

"2. Receivers per City":
"""
SELECT City, COUNT(*) AS Total_Receivers
FROM receivers
GROUP BY City;
""",

"3. Top Provider Type Contribution":
"""
SELECT Provider_Type, SUM(Quantity) AS Total_Food
FROM food_listings
GROUP BY Provider_Type
ORDER BY Total_Food DESC;
""",

"4. Contact Providers in City":
"""
SELECT Name, Contact, City
FROM providers
WHERE City = 'Chennai';
""",

"5. Receiver claimed most food":
"""
SELECT r.Name, COUNT(c.Claim_ID) AS Total_Claims
FROM claims c
JOIN receivers r ON c.Receiver_ID = r.Receiver_ID
GROUP BY r.Name
ORDER BY Total_Claims DESC
LIMIT 5;
""",

"6. Total Quantity Available":
"""
SELECT SUM(Quantity) AS Total_Food_Available
FROM food_listings;
""",

"7. City with Highest Listings":
"""
SELECT Location, COUNT(*) AS Total_Listings
FROM food_listings
GROUP BY Location
ORDER BY Total_Listings DESC;
""",

"8. Most Common Food Types":
"""
SELECT Food_Type, COUNT(*) AS Count
FROM food_listings
GROUP BY Food_Type
ORDER BY Count DESC;
""",

"9. Claims per Food Item":
"""
SELECT Food_Name, COUNT(c.Claim_ID) AS Total_Claims
FROM claims c
JOIN food_listings f ON c.Food_ID = f.Food_ID
GROUP BY Food_Name;
""",

"10. Provider with Highest Successful Claims":
"""
SELECT p.Name, COUNT(*) AS Successful_Claims
FROM claims c
JOIN food_listings f ON c.Food_ID = f.Food_ID
JOIN providers p ON f.Provider_ID = p.Provider_ID
WHERE c.Status='Completed'
GROUP BY p.Name
ORDER BY Successful_Claims DESC;
""",

"11. Claim Status Percentage":
"""
SELECT Status,
COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims) AS Percentage
FROM claims
GROUP BY Status;
""",

"12. Avg Quantity Claimed per Receiver":
"""
SELECT r.Name, AVG(f.Quantity) AS Avg_Quantity
FROM claims c
JOIN receivers r ON c.Receiver_ID=r.Receiver_ID
JOIN food_listings f ON c.Food_ID=f.Food_ID
GROUP BY r.Name;
""",

"13. Most Claimed Meal Type":
"""
SELECT Meal_Type, COUNT(*) AS Total_Claims
FROM food_listings f
JOIN claims c ON f.Food_ID=c.Food_ID
GROUP BY Meal_Type
ORDER BY Total_Claims DESC;
""",

"14. Total Quantity Donated by Provider":
"""
SELECT p.Name, SUM(f.Quantity) AS Total_Donated
FROM food_listings f
JOIN providers p ON f.Provider_ID=p.Provider_ID
GROUP BY p.Name;
""",

"15. Expiring Soon Food Items":
"""
SELECT Food_Name, Expiry_Date, Location
FROM food_listings
ORDER BY Expiry_Date ASC
LIMIT 10;
"""
}
