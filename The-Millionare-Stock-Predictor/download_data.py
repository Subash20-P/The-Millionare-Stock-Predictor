from datetime import datetime
import MetaTrader5 as mt5
import pandas as pd

symbol = "EURUSDm"

# Initialize connection
if not mt5.initialize():
    print("❌ Failed to initialize MT5")
    quit()

# Approx minutes in 10 years: 10*365*24*60 = 5,256,000
n_minutes = 525600

print(f"📡 Fetching {n_minutes} minutes of M1 data for {symbol}...")

# Download historical data
rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, n_minutes)

if rates is None or len(rates) == 0:
    print("❌ No data received. Check symbol or broker's data limits.")
else:
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.to_csv("D:/DIVINE_GENERAL/EURUSDm_M1_10yrs.csv", index=False)
    print("✅ 10 years of M1 data saved to EURUSDm_M1_10yrs.csv")

mt5.shutdown()
