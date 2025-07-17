import pandas as pd

# Load the prediction log
log_path = "D:/DIVINE_GENERAL/prediction_log.csv"

try:
    df = pd.read_csv(log_path)

    if df.empty:
        print("⚠️ The prediction log is empty.")
    else:
        total_trades = df[df['signal'].isin(['buy', 'sell'])].shape[0]
        total_profit = df[df['result'] == 'profit'].shape[0]
        total_loss = df[df['result'] == 'loss'].shape[0]
        total_hold = df[df['result'] == 'hold'].shape[0]

        # Success rate
        if total_trades > 0:
            success_rate = (total_profit / total_trades) * 100
        else:
            success_rate = 0

        print("\n📊 TRADE PERFORMANCE SUMMARY")
        print("="*40)
        print(f"🔢 Total Trades     : {total_trades}")
        print(f"✅ Profitable Trades: {total_profit}")
        print(f"❌ Loss Trades      : {total_loss}")
        print(f"⏸️ Hold/Skipped     : {total_hold}")
        print(f"📈 Success Rate     : {success_rate:.2f}%")
        print("="*40)

except FileNotFoundError:
    print("❌ prediction_log.csv not found.")
