import os
import zipfile
import requests
from tqdm import tqdm

import os
import sys

# Check if the folder exists
if os.path.isdir("data/dev"):
    print("Data already downloaded. Exiting script.")
    sys.exit()

# URL of the BIRD dataset
BIRD_DATASET_URL = "https://bird-bench.oss-cn-beijing.aliyuncs.com/dev.zip"
DOWNLOADED_ZIP_PATH = "data/downloaded_file.zip"
CHUNK_SIZE = 1024  # Download in chunks of 1KB

# Download the BIRD dataset with a progress bar
response = requests.get(BIRD_DATASET_URL, stream=True, timeout=10)
total_size = int(response.headers.get('content-length', 0))

with open(DOWNLOADED_ZIP_PATH, "wb") as zip_file, tqdm(
    desc="Downloading BIRD dataset",
    total=total_size,
    unit='B',
    unit_scale=True,
    unit_divisor=1024
) as progress_bar:
    for data in response.iter_content(chunk_size=CHUNK_SIZE):
        zip_file.write(data)
        progress_bar.update(len(data))

# Extract the downloaded zip file while ignoring the __MACOSX folder
with zipfile.ZipFile(DOWNLOADED_ZIP_PATH, "r") as zip_ref:
    members = [m for m in zip_ref.namelist() if not m.startswith("__MACOSX/")]
    with tqdm(total=len(members), desc="Extracting BIRD dataset", unit="file") as progress_bar:
        for member in members:
            zip_ref.extract(member, "data")
            progress_bar.update(1)

# Rename the extracted folder from 'dev_20240627' to 'dev'
EXTRACTED_FOLDER_PATH = "data/dev_20240627"
os.rename(EXTRACTED_FOLDER_PATH, "data/dev")

# Extract the databases zip file within the 'dev' folder
DATABASES_ZIP_PATH = "data/dev/dev_databases.zip"
with zipfile.ZipFile(DATABASES_ZIP_PATH, "r") as zip_ref:
    members = [m for m in zip_ref.namelist() if not m.startswith("__MACOSX/")]
    with tqdm(total=len(members), desc="Extracting databases", unit="file") as progress_bar:
        for member in members:
            zip_ref.extract(member, "data/dev")
            progress_bar.update(1)

# Remove the downloaded zip files after extraction
os.remove(DOWNLOADED_ZIP_PATH)
os.remove(DATABASES_ZIP_PATH)
