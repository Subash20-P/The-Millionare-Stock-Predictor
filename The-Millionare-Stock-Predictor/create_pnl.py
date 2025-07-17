import csv
import os

path = "D:/DIVINE_GENERAL/pnl.csv"

# Create file only if it doesn't exist
if not os.path.exists(path):
    with open(path, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Optional dummy entry to test the graph
        writer.writerow(["2025-04-09 22:15:10", "BUY", 1.1031, 1.1035, 0.0004])
    print("✅ pnl.csv created with dummy data.")
else:
    print("✅ pnl.csv already exists.")
