queries={
"Total Quantity Available":"SELECT SUM(Quantity) AS Total_Food FROM food_listings;",
"City with Highest Listings":"SELECT Location,COUNT(*) AS Listings FROM food_listings GROUP BY Location ORDER BY Listings DESC;"
}
