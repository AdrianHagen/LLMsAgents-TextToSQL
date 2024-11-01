import sqlite3
import json

# Load data from JSON file
with open("data/dev/dev.json", "r", encoding="utf-8") as dev_file:
    data = json.load(dev_file)

print(f"Number of examples: {len(data)}")
print(type(data[0]))
print(data[0]["question"])
print(data[1]["SQL"])

# Initialize database connection
current_db_id = data[0]["db_id"]  # Renamed for clarity
connection = sqlite3.connect(
    f"data/dev/dev_databases/{current_db_id}/{current_db_id}.sqlite"
)  # Renamed for clarity
cursor = connection.cursor()

# Iterate through each element in the data
for element in data:
    # Check if the database ID has changed
    if element["db_id"] != current_db_id:
        current_db_id = element["db_id"]
        print(current_db_id)

        # Close the current database connection
        connection.close()  # Renamed for clarity

        # Open a new database connection
        connection = sqlite3.connect(  # Renamed for clarity
            f"data/dev/dev_databases/{current_db_id}/{current_db_id}.sqlite"
        )
        cursor = connection.cursor()  # Renamed for clarity

    # Execute the SQL command from the current element
    cursor.execute(element["SQL"])
    results = cursor.fetchall()

# Close the final database connection
connection.close()  # Renamed for clarity
