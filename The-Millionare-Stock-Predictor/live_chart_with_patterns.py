import MetaTrader5 as mt5
import pandas as pd
import mplfinance as mpf
import time
from candlestick import apply_all_patterns

# Login to MT5
mt5.initialize()
account = 240294352
password = "sTrR?&jL?Bu*GE5"
server = "Exness-MT5Trial"
mt5.login(account, password=password, server=server)

symbol = "EURUSDm"
timeframe = mt5.TIMEFRAME_M1
num_candles = 100

def fetch_data():
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, num_candles)
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'tick_volume': 'Volume'}, inplace=True)
    df.set_index('time', inplace=True)
    return df[['Open', 'High', 'Low', 'Close', 'Volume']]

def detect_patterns(df):
    df = apply_all_patterns(df)
    return df

def draw_chart(df):
    df['pattern_marker'] = None
    markers = []

    for i in range(len(df)):
        for col in df.columns:
            if df[col].iloc[i] == True:
                if "bullish" in col.lower() or "morning" in col.lower() or "white_soldiers" in col.lower() or "inverted_hammer" in col.lower():
                    df.at[df.index[i], 'pattern_marker'] = df['Low'].iloc[i] - 0.0003
                    markers.append(("buy", df.index[i]))
                    break
                elif "bearish" in col.lower() or "evening" in col.lower() or "black_crows" in col.lower() or "shooting_star" in col.lower():
                    df.at[df.index[i], 'pattern_marker'] = df['High'].iloc[i] + 0.0003
                    markers.append(("sell", df.index[i]))
                    break

    ap = mpf.make_addplot(df['pattern_marker'], type='scatter', markersize=100,
                          marker='^', color='purple', panel=0)

    mpf.plot(df, type='candle', style='yahoo',
             title=f'{symbol} - All Candlestick Patterns',
             ylabel='Price',
             addplot=[ap],
             warn_too_much_data=10000)

while True:
    df = fetch_data()
    df = detect_patterns(df)
    draw_chart(df)
    time.sleep(60)
