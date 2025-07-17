import pandas as pd
from datetime import datetime
import os
import MetaTrader5 as mt5

# Connect to MetaTrader 5
if not mt5.initialize():
    print("❌ MT5 Initialization failed:", mt5.last_error())
    quit()

# Settings
symbol = "EURUSDm"
entry_price = 1.0845  # Replace with your actual entry price
order_type = "buy"     # or "sell"
log_path = "D:/DIVINE_GENERAL/trade_log.csv"

# Get current market price
tick = mt5.symbol_info_tick(symbol)
if tick is None:
    print("❌ Failed to get market price.")
    mt5.shutdown()
    quit()

# Decide exit price based on type
exit_price = tick.bid if order_type == "sell" else tick.ask

# Determine profit/loss
is_profit = (exit_price > entry_price) if order_type == "buy" else (exit_price < entry_price)
result = "profit" if is_profit else "loss"

# Log trade
trade_result = {
    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "entry_price": entry_price,
    "exit_price": exit_price,
    "type": order_type,
    "result": result
}

# Load or create the CSV
if os.path.exists(log_path):
    df = pd.read_csv(log_path)
else:
    df = pd.DataFrame(columns=["time", "entry_price", "exit_price", "type", "result"])

# Append and save
df = pd.concat([df, pd.DataFrame([trade_result])], ignore_index=True)
df.to_csv(log_path, index=False)

# Calculate success rate
total_trades = len(df)
profitable_trades = len(df[df["result"] == "profit"])
loss_trades = total_trades - profitable_trades
success_rate = (profitable_trades / total_trades) * 100

# Show summary
print("📊 Trade Summary")
print(f"✅ Profitable Trades: {profitable_trades}")
print(f"❌ Loss Trades: {loss_trades}")
print(f"🔁 Total Trades: {total_trades}")
print(f"💯 Success Rate: {success_rate:.2f}%")

mt5.shutdown()
