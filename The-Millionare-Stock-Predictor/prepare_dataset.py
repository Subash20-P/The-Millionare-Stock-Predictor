import pandas as pd

# Path to raw CSV
file_path = "D:/DIVINE_GENERAL/EURUSD_Candlestick_1_M_BID_01.01.2024-30.06.2024.csv"

# Load and rename columns
df = pd.read_csv(file_path)
df.rename(columns={
    "Gmt time": "datetime",
    "Open": "open",
    "High": "high",
    "Low": "low",
    "Close": "close",
    "Volume": "volume"
}, inplace=True)

# Convert datetime with correct format
df['datetime'] = pd.to_datetime(df['datetime'], format="%d.%m.%Y %H:%M:%S.%f")

# Reorder and save cleaned dataset
df = df[['datetime', 'open', 'high', 'low', 'close', 'volume']]
df.to_csv("D:/DIVINE_GENERAL/EURUSDm_1M.csv", index=False)

print("✅ Dataset prepared and saved as 'EURUSDm_1M.csv'")
