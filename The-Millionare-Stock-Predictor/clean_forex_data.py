import pandas as pd

# Load raw CSV
df = pd.read_csv("EURUSD_1M_2014_2024.csv")

# Drop rows with any NaN values
df.dropna(inplace=True)

# Reset index if necessary
df.reset_index(drop=True, inplace=True)

# Rename columns to match your AI project expectation
df.rename(columns={
    'open': 'open',
    'high': 'high',
    'low': 'low',
    'close': 'close'
}, inplace=True)

# Ensure datetime column is in datetime format
df['datetime'] = pd.to_datetime(df['datetime'])

# Reorder columns for consistency
df = df[['datetime', 'open', 'high', 'low', 'close']]

# Save the cleaned version
df.to_csv("EURUSDm_1M.csv", index=False)

print("✅ Cleaned data saved as EURUSDm_1M.csv")
