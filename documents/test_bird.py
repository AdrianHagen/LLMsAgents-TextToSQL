import sqlite3
import json

with open("data/bird/dev.json", "r", encoding="utf-8") as dev_file:
    data = json.load(dev_file)

print(f"Number of examples: {len(data)}")
print(type(data[0]))
print(data[0]["question"])
print(data[1]["SQL"])

curr_db_id = data[0]["db_id"]
conn = sqlite3.connect(f"data/bird/dev_databases/{curr_db_id}/{curr_db_id}.sqlite")
cursor = conn.cursor()

for element in data:
    if element["db_id"] != curr_db_id:
        curr_db_id = element["db_id"]
        print(curr_db_id)
        conn.close()
        conn = sqlite3.connect(
            f"data/bird/dev_databases/{curr_db_id}/{curr_db_id}.sqlite"
        )
        cursor = conn.cursor()

    cursor.execute(element["SQL"])
    results = cursor.fetchall()

conn.close()
