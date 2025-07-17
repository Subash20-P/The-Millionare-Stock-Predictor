import pandas as pd
import matplotlib.pyplot as plt

log_file = "D:/DIVINE_GENERAL/prediction_log.csv"

df = pd.read_csv(log_file)

plt.figure(figsize=(10,6))
plt.plot(df['actual_price'], label='Actual Price', color='blue')
plt.plot(df['predicted_price'], label='Predicted Price', color='orange')
plt.title('Actual vs Predicted Forex Prices')
plt.xlabel('Time')
plt.ylabel('Price')
plt.legend()
plt.grid(True)
plt.show()
