
import os
import sys
import zipfile
import io
import requests

# Set target directory
DATA_DIR = os.path.join(os.getcwd(), 'data', 'raw')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

BASE_URL = "https://data.binance.vision/data/spot/monthly/klines/BTCUSDT"

def download_and_extract(timeframe, month):
    filename = f"BTCUSDT-{timeframe}-2024-{month:02d}.zip"
    url = f"{BASE_URL}/{timeframe}/{filename}"
    print(f"Downloading {url}...")
    
    try:
        r = requests.get(url)
        if r.status_code == 200:
            z = zipfile.ZipFile(io.BytesIO(r.content))
            z.extractall(DATA_DIR)
            print(f"Extracted to {DATA_DIR}")
            
            # Rename extracted file to match project convention (usually extracted as BTCUSDT-1h-2024-05.csv)
            extracted_name = f"BTCUSDT-{timeframe}-2024-{month:02d}.csv"
            # Binance zip contains a csv with same name usually
            if os.path.exists(os.path.join(DATA_DIR, extracted_name)):
                print(f"Verified {extracted_name} exists.")
            else:
                print(f"Warning: Expected {extracted_name} not found after extraction.")
        else:
            print(f"Failed to download {url}: Status {r.status_code}")
    except Exception as e:
        print(f"Error downloading {filename}: {e}")

if __name__ == "__main__":
    # Download May 2024 (Month 5) for 4h (strategy timeframe) and 15m/1h/5m if needed
    # Top strategies use 4h.
    import argparse
    
    download_and_extract("4h", 5)
    download_and_extract("1h", 5)
    download_and_extract("15m", 5)
    download_and_extract("5m", 5)
