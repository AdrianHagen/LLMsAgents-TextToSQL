import chardet
import os

with open(
    os.path.join(
        os.getenv("DB_DIRECTORY"), "codebase_community/database_description/badges.csv"
    ),
    "rb",
) as file:
    result = chardet.detect(file.read())
print(result)
