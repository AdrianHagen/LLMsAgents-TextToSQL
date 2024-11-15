import sqlite3
import json

# Load data from JSON file
with open("data/dev/dev.json", "r", encoding="utf-8") as dev_file:
    data = json.load(dev_file)

print(f"Number of examples: {len(data)}")
print(data[0]["question"])
print(data[1]["SQL"])

# Initialize database connection
current_db_id = data[0]["db_id"]
connection = sqlite3.connect(
    f"data/dev/dev_databases/{current_db_id}/{current_db_id}.sqlite"
)
cursor = connection.cursor()
cursor.execute(data[0]["SQL"])
results = cursor.fetchall()
print(results)
connection.close()
