import requests
import pandas as pd

API_KEY = "82e7b16bd62b42c9a4903daa5444846a"
symbol = "EUR/USD"
interval = "1min"
output_size = 1000  # Max allowed in free plan
url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={interval}&outputsize={output_size}&apikey={API_KEY}"

print("📡 Fetching data from Twelve Data...")

response = requests.get(url)
data = response.json()

if "values" not in data:
    print("❌ Error fetching data:", data.get("message", "Unknown error"))
    exit()

df = pd.DataFrame(data["values"])
df = df.rename(columns={"datetime": "time", "close": "close"})
df = df[["time", "close"]]
df["close"] = df["close"].astype(float)
df = df[::-1]  # oldest to newest

df.to_csv("D:/DIVINE_GENERAL/EURUSD_1min.csv", index=False)
print("✅ Data saved to EURUSD_1min.csv")
