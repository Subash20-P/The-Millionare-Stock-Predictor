import os
import struct
import zlib
import requests
import pandas as pd
from datetime import datetime, timedelta
from tqdm import tqdm

def get_url(year, month, day, hour):
    return f"https://datafeed.dukascopy.com/datafeed/EURUSD/{year}/{month:02d}/{day:02d}/{hour:02d}h_ticks.bi5"

def download_and_extract(url):
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return None
        data = zlib.decompress(r.content)
        records = []
        for i in range(0, len(data), 20):
            chunk = data[i:i+20]
            if len(chunk) == 20:
                ms, ask, bid, ask_vol, bid_vol = struct.unpack('>IIIff', chunk)
                records.append((ms, ask / 100000.0, bid / 100000.0))
        return records
    except:
        return None  # ❌ Don't print anything, just return None

start_date = datetime(2014, 1, 1)
end_date = datetime(2024, 1, 1)

all_data = []
failed_urls = []

print("📥 Downloading EUR/USD 1-minute data from Dukascopy (2014–2024)...")

for day_offset in tqdm(range((end_date - start_date).days)):
    day_date = start_date + timedelta(days=day_offset)
    for hour in range(24):
        url = get_url(day_date.year, day_date.month, day_date.day, hour)
        result = download_and_extract(url)
        if result is None:
            failed_urls.append(url)
            continue
        for record in result:
            timestamp = day_date + timedelta(hours=hour, milliseconds=record[0])
            all_data.append([timestamp, record[1], record[2]])

# Save raw tick data
if not all_data:
    print("❌ No data downloaded.")
    exit()

df = pd.DataFrame(all_data, columns=["datetime", "ask", "bid"])
df["mid"] = (df["ask"] + df["bid"]) / 2
df["datetime"] = pd.to_datetime(df["datetime"])
df.set_index("datetime", inplace=True)

df_1m = df["mid"].resample("1T").ohlc().dropna()
df_1m.to_csv("EURUSD_1M_2014_2024.csv")

print(f"\n✅ Saved 1-minute data to EURUSD_1M_2014_2024.csv with {len(df_1m)} rows.")

if failed_urls:
    with open("failed_urls.txt", "w") as f:
        for url in failed_urls:
            f.write(url + "\n")
    print(f"⚠️ Skipped {len(failed_urls)} files. Logged in failed_urls.txt for future retry.")
else:
    print("🎉 All files downloaded successfully. No failures.")
