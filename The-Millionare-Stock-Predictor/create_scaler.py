# create_scaler.py
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import joblib

# Path to your training CSV
csv_path = "D:/DIVINE_GENERAL/EURUSD_1min.csv"  # Make sure this CSV exists and is correct

# Load the dataset
df = pd.read_csv(csv_path)

# Reshape close prices for scaling
close_data = df["close"].values.reshape(-1, 1)

# Fit the scaler
scaler = MinMaxScaler()
scaler.fit(close_data)

# Save the scaler
scaler_path = "D:/DIVINE_GENERAL/scaler.gz"
joblib.dump(scaler, scaler_path)

print("✅ Scaler saved successfully at:", scaler_path)
