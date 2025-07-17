import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

pnl_file = "D:/DIVINE_GENERAL/pnl.csv"

def animate(i):
    try:
        df = pd.read_csv(pnl_file, header=None)
        df.columns = ["Time", "Direction", "Entry", "Exit", "PnL"]
        df["Time"] = pd.to_datetime(df["Time"])
        df["Cumulative PnL"] = df["PnL"].cumsum()

        plt.cla()
        plt.plot(df["Time"], df["Cumulative PnL"], color='green', linewidth=2)
        plt.xlabel("Time")
        plt.ylabel("Cumulative Profit/Loss ($)")
        plt.title("💹 Forex Bot Live PnL Tracker")
        plt.grid(True)
    except Exception as e:
        print(f"Error reading or plotting: {e}")

# Plot setup
fig = plt.figure(figsize=(10, 5))
ani = FuncAnimation(fig, animate, interval=5000)  # Update every 5 seconds
plt.tight_layout()
plt.show()
