import sqlite3
import json

# Load data from JSON file
with open("data/dev/dev.json", "r", encoding="utf-8") as dev_file:
    data = json.load(dev_file)

pred = "SELECT surname FROM drivers JOIN Qualifying ON Drivers.driver_id = Qualifying.driver_id WHERE Qualifying.race_number = 19 AND Qualifying.qualifying_period = 2 ORDER BY Qualifying.best_lap_time ASC LIMIT 1"
actual = "SELECT T2.surname FROM qualifying AS T1 INNER JOIN drivers AS T2 ON T2.driverId = T1.driverId WHERE T1.raceId = 19 ORDER BY T1.q2 ASC LIMIT 1"

# Initialize database connection
current_db_id = "formula_1"

connection = sqlite3.connect(
    f"data/dev/dev_databases/{current_db_id}/{current_db_id}.sqlite"
)
cursor = connection.cursor()
cursor.execute(pred)
results = cursor.fetchall()
print(f"Results of the predicted query: {results}")
cursor.execute(actual)
results = cursor.fetchall()
print(f"Results of the actual query: {results}")
connection.close()
