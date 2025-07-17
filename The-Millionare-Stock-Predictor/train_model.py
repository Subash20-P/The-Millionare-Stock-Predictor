import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import joblib
import os

print("📦 Starting full training pipeline...")

# Step 1: Initialize MT5
symbol = "EURUSDm"
if not mt5.initialize():
    print("❌ MT5 initialization failed")
    quit()

# Step 2: Download 10 years of M1 data
data_dir = "D:/DIVINE_GENERAL/"
os.makedirs(data_dir, exist_ok=True)
yearly_data = []

print("📡 Downloading M1 data for 2015–2024...")
for year in range(2015, 2025):
    from_date = datetime(year, 1, 1)
    to_date = datetime(year, 12, 31)
    rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M1, from_date, to_date)

    if rates is not None and len(rates) > 0:
        df_year = pd.DataFrame(rates)
        df_year.to_csv(f"{data_dir}data_m1_{year}.csv", index=False)
        yearly_data.append(df_year)
        print(f"✅ {year} - {len(df_year)} rows")
    else:
        print(f"❌ {year} - No data received")

mt5.shutdown()

# Step 3: Combine all data
print("🧩 Merging all yearly CSVs...")
all_df = pd.concat(yearly_data, ignore_index=True)
all_df.to_csv(f"{data_dir}EURUSDm_10yr_M1.csv", index=False)
print(f"📁 Combined dataset saved with {len(all_df)} rows")

# Step 4: Preprocess (focus on Close price)
close_prices = all_df['close'].values.reshape(-1, 1)
scaler = MinMaxScaler()
scaled = scaler.fit_transform(close_prices)
joblib.dump(scaler, f"{data_dir}scaler.save")
print("📊 Data normalized & scaler saved")

# Step 5: Prepare training data
X = []
y = []
sequence_len = 50

for i in range(sequence_len, len(scaled)):
    X.append(scaled[i-sequence_len:i])
    y.append(scaled[i])

X, y = np.array(X), np.array(y)
print(f"📦 Training set: {X.shape[0]} samples")

# Step 6: Build & train LSTM model
model = Sequential()
model.add(LSTM(64, return_sequences=True, input_shape=(X.shape[1], 1)))
model.add(LSTM(64))
model.add(Dense(1))

model.compile(optimizer='adam', loss='mean_squared_error')
print("🚀 Training model...")
model.fit(X, y, epochs=5, batch_size=64)

# Step 7: Save model
model.save(f"{data_dir}forex_model.h5")
print("🎉 Model training complete and saved!")

