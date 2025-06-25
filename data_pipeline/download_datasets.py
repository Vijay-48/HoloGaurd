 #!/usr/bin/env python3
# data_pipeline/download_datasets.py
import os
import gdown

FFPP_URL = "https://github.com/ondyari/FaceForensics"
DFDC_URL = "https://www.kaggle.com/c/deepfake-detection-challenge/data"

TARGET_DIR = os.path.expanduser("~/datasets/deepfake")

os.makedirs(TARGET_DIR, exist_ok=True)

def download(url, name):
    out = os.path.join(TARGET_DIR, name)
    if not os.path.exists(out):
        print(f"Downloading {name}...")
        gdown.download(url, out, quiet=False)
    else:
        print(f"{name} already exists, skipping.")

if __name__ == "__main__":
    download(FFPP_URL, "FaceForensicspp.zip")
    download(DFDC_URL, "DFDC.zip")
    print("All datasets downloaded to", TARGET_DIR)
