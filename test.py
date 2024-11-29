import os
import chardet
import pandas as pd
from pprint import pprint


def retrieve_column_names(database_name: str, tables: list):
    table_descriptions = {}
    descriptions_path = os.path.join(
        os.getenv("DB_DIRECTORY"), database_name, "database_description"
    )

    for table_name in tables:
        file_path = os.path.join(descriptions_path, f"{table_name}.csv")
        if os.path.exists(file_path):
            # Detect encoding dynamically since it can vary from file to file
            with open(file_path, "rb") as file:
                result = chardet.detect(file.read())
                detected_encoding = (
                    result["encoding"] if result["encoding"] else "utf-8"
                )

            # Use the detected encoding to read the file
            table_data = pd.read_csv(file_path, encoding=detected_encoding)

            # Extract column descriptions
            columns = table_data[["original_column_name", "column_description"]]
            table_descriptions[table_name] = [
                f"Column name: {column.original_column_name}, Column description: {column.column_description}"
                for column in columns.itertuples()
            ]

    return table_descriptions


pprint(
    retrieve_column_names(
        "card_games",
        ["cards", "foreign_data", "legalities", "rulings", "set_translations", "sets"],
    )
)
