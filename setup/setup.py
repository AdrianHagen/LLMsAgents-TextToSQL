import os
import zipfile
import subprocess

import requests

# Download the BIRD dataset from the specified URL
response = requests.get("https://bird-bench.oss-cn-beijing.aliyuncs.com/dev.zip")
DOWNLOADED_ZIP_PATH = "data/downloaded_file.zip"

# Save the downloaded zip file to the specified path
with open(DOWNLOADED_ZIP_PATH, "wb") as zip_file:
    zip_file.write(response.content)

# Extract the downloaded zip file while ignoring the __MACOSX folder
with zipfile.ZipFile(DOWNLOADED_ZIP_PATH, "r") as zip_ref:
    for member in zip_ref.namelist():
        if not member.startswith("__MACOSX/"):
            zip_ref.extract(member, "data")

# Rename the extracted folder from 'dev_20240627' to 'dev'
EXTRACTED_FOLDER_PATH = "data/dev_20240627"
os.rename(EXTRACTED_FOLDER_PATH, "data/dev")

# Extract the databases zip file within the 'dev' folder
DATABASES_ZIP_PATH = "data/dev/dev_databases.zip"
with zipfile.ZipFile(DATABASES_ZIP_PATH, "r") as zip_ref:
    for member in zip_ref.namelist():
        if not member.startswith("__MACOSX/"):
            zip_ref.extract(member, "data/dev")

# Remove the downloaded zip files after extraction
os.remove(DOWNLOADED_ZIP_PATH)
os.remove(DATABASES_ZIP_PATH)

# Run the test script to verify the dataset
subprocess.run(["python", "setup/test_bird.py"], check=True)
