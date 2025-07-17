import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf
from candlestick import apply_all_patterns
import time
import pyttsx3  # 🔊 Text-to-Speech

# === MT5 Account Info ===
account = 240294352
password = "sTrR?&jL?Bu*GE5"
server = "Exness-MT5Trial6"
symbol = "EURUSDm"
timeframe = mt5.TIMEFRAME_M1
num_candles = 100

# === Initialize MT5 ===
if not mt5.initialize():
    print("❌ MT5 initialization failed")
    quit()

if not mt5.login(account, password=password, server=server):
    print("❌ Login failed")
    quit()

print("✅ Logged in to MT5")

# === Setup Plotting ===
plt.ion()
fig, ax = plt.subplots(figsize=(12, 8))

# === Setup Voice Engine ===
engine = pyttsx3.init()
engine.setProperty('rate', 160)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # 0: Male, 1: Female

# === Fetch Candle Data Function ===
def fetch_data():
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, num_candles)

    if rates is None or len(rates) == 0:
        print("❌ No data received from MetaTrader 5. Check your login, symbol, or internet connection.")
        return pd.DataFrame()

    df = pd.DataFrame(rates)

    if 'time' not in df.columns:
        print("❌ 'time' column missing in data. Full columns are:", df.columns)
        return pd.DataFrame()

    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.rename(columns={
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'tick_volume': 'Volume'
    }, inplace=True)
    df.set_index('time', inplace=True)
    return df[['Open', 'High', 'Low', 'Close', 'Volume']]

# === Live Chart Loop ===
while True:
    df = fetch_data()
    if df.empty:
        time.sleep(60)
        continue

    df = apply_all_patterns(df)

    df['pattern_marker'] = np.nan
    df['pattern_label'] = None
    df['expected_direction'] = None

    pattern_cols = [col for col in df.columns if col not in ['Open', 'High', 'Low', 'Close', 'Volume', 'pattern_marker', 'pattern_label', 'expected_direction']]

    for i in range(len(df)):
        for pattern in pattern_cols:
            if df[pattern].iloc[i]:
                df.at[df.index[i], 'pattern_marker'] = df['High'].iloc[i] + 0.0003
                df.at[df.index[i], 'pattern_label'] = pattern

                # Speak pattern name 🗣️
                print(f"🔔 Pattern Detected: {pattern}")
                engine.say(f"{pattern} detected")
                engine.runAndWait()

                # Predict expected movement
                if "Bullish" in pattern:
                    df.at[df.index[i], 'expected_direction'] = 'up'
                elif "Bearish" in pattern:
                    df.at[df.index[i], 'expected_direction'] = 'down'

    # === Clear & Plot ===
    plt.clf()

    fig, axes = mpf.plot(
        df,
        type='candle',
        style='charles',
        addplot=[
            mpf.make_addplot(df['pattern_marker'], type='scatter', markersize=100, marker='^', color='lime')
        ],
        warn_too_much_data=10000,
        returnfig=True
    )

    ax = axes[0]

    for i in range(len(df)):
        if pd.notna(df['pattern_label'].iloc[i]):
            ax.text(df.index[i], df['High'].iloc[i] + 0.0006,
                    df['pattern_label'].iloc[i],
                    fontsize=7, rotation=45, color='blue')

        direction = df['expected_direction'].iloc[i]
        if direction == 'up':
            ax.annotate('↑', (df.index[i], df['High'].iloc[i] + 0.0009),
                        color='green', fontsize=15, ha='center')
            ax.text(df.index[i], df['High'].iloc[i] + 0.0012, 'Expected Up', fontsize=8, color='green', ha='center')
        elif direction == 'down':
            ax.annotate('↓', (df.index[i], df['Low'].iloc[i] - 0.0009),
                        color='red', fontsize=15, ha='center')
            ax.text(df.index[i], df['Low'].iloc[i] - 0.0012, 'Expected Down', fontsize=8, color='red', ha='center')

    plt.pause(60)  # Refresh every 1 minute
