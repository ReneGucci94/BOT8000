import os
import requests
import zipfile
import time
from pathlib import Path
from typing import List
from tqdm import tqdm

def download_file(url: str, dest_path: Path, max_retries: int = 3) -> bool:
    """Download a file with retry logic and progress bar."""
    if dest_path.exists():
        return True # Skip if raw zip exists (though usually we clean it up)

    for attempt in range(max_retries):
        try:
            response = requests.get(url, stream=True, timeout=10)
            if response.status_code == 404:
                return False # Not found (e.g. future month)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            with open(dest_path, 'wb') as f, tqdm(
                desc=dest_path.name,
                total=total_size,
                unit='iB',
                unit_scale=True,
                unit_divisor=1024,
                leave=False
            ) as bar:
                for data in response.iter_content(chunk_size=1024):
                    size = f.write(data)
                    bar.update(size)
            return True
            
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(1) # Backoff
            else:
                print(f"Failed to download {url}: {e}")
                if dest_path.exists():
                    dest_path.unlink() # Cleanup partial
                return False
    return False

def download_binance_data(
    pairs: List[str],
    timeframes: List[str],
    years: List[int],
    months: List[int],
    data_dir: str = "data/raw"
):
    """
    Downloads monthly CSVs for the specified permutations.
    """
    base_url = "https://data.binance.vision/data/spot/monthly/klines"
    Path(data_dir).mkdir(parents=True, exist_ok=True)
    
    print(f"--- Checking Logic: Data Availability ({len(pairs)} pairs, {len(timeframes)} tfs, {len(years)} years) ---")
    
    for pair in pairs:
        for tf in timeframes:
            for year in years:
                for month in months:
                    # Target CSV naming convention: BTCUSDT-1h-2024-01.csv
                    # Binance ZIP naming: BTCUSDT-1h-2024-01.zip
                    month_str = f"{month:02d}"
                    file_base = f"{pair}-{tf}-{year}-{month_str}"
                    target_csv = Path(data_dir) / f"{file_base}.csv"
                    
                    # 1. Check if CSV exists and is valid
                    if target_csv.exists() and target_csv.stat().st_size > 100:
                        continue # Skip
                        
                    # 2. Download ZIP
                    zip_name = f"{file_base}.zip"
                    url = f"{base_url}/{pair}/{tf}/{zip_name}"
                    temp_zip = Path(data_dir) / zip_name
                    
                    # print(f"Downloading {zip_name}...")
                    success = download_file(url, temp_zip)
                    
                    if success:
                        # 3. Extract
                        try:
                            with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
                                # Binance zip usually contains one file with the same name as the zip but .csv
                                zip_ref.extractall(data_dir)
                            
                            # Cleanup
                            temp_zip.unlink()
                            
                            # Verify extraction
                            if not target_csv.exists():
                                print(f"Warning: Extraction did not produce expected file {target_csv}")
                                
                        except zipfile.BadZipFile:
                            print(f"Error: Corrupted zip file {zip_name}")
                            temp_zip.unlink()
                    else:
                        # 404 or fail, just continue
                        pass

if __name__ == "__main__":
    # Test
    download_binance_data(["BTCUSDT"], ["4h"], [2024], [1])
