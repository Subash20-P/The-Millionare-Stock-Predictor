import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import joblib
import pyttsx3
from tensorflow.keras.models import load_model
from datetime import datetime
import time
from candlestick import apply_all_patterns

# TTS init for candlestick patterns
engine = pyttsx3.init()
engine.setProperty('rate', 170)

# Load trained model and scaler
model = load_model("D:/DIVINE_GENERAL/lstm_model.h5")
scaler = joblib.load("D:/DIVINE_GENERAL/scaler.pkl")

# Constants
symbol = "EURUSD"
lot = 0.1
prediction_log = "D:/DIVINE_GENERAL/prediction_log.csv"
open_trades = []

# Initialize MT5
if not mt5.initialize():
    print("❌ MT5 initialization failed")
    quit()

info = mt5.symbol_info(symbol)
if info is None or not info.visible:
    if not mt5.symbol_select(symbol, True):
        print(f"❌ Failed to select symbol {symbol}")
        quit()

# Load or create log
try:
    df_log = pd.read_csv(prediction_log)
except:
    df_log = pd.DataFrame(columns=["datetime", "actual_price", "predicted_price", "signal", "result", "profit_loss"])

def get_latest_price():
    tick = mt5.symbol_info_tick(symbol)
    return tick.bid if tick else None

def get_recent_data():
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 50)
    if rates is None or len(rates) < 50:
        return None
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    return df[['time', 'close']]

def place_order(signal):
    price = get_latest_price()
    if price is None:
        print("❌ Failed to get price")
        return False, None

    # ✅ NORMAL LOGIC: BUY → BUY, SELL → SELL
    order_type = mt5.ORDER_TYPE_BUY if signal == "buy" else mt5.ORDER_TYPE_SELL

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": order_type,
        "price": price,
        "deviation": 10,
        "magic": 234000,
        "comment": "AI Trade",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)
    print(result)

    if result and result.retcode == mt5.TRADE_RETCODE_DONE:
        ticket = result.order
        open_trades.append({
            "ticket": ticket,
            "signal": signal,
            "entry_price": price,
            "open_time": datetime.now()
        })
        return True, ticket
    else:
        print(f"❌ Order failed: {result.retcode}")
        return False, None

def monitor_open_trades():
    global open_trades
    updated_trades = []
    for trade in open_trades:
        positions = mt5.positions_get(ticket=trade["ticket"])
        if positions and len(positions) > 0:
            pos = positions[0]
            open_duration = datetime.now() - trade["open_time"]
            if open_duration.total_seconds() >= 60:
                order_type = mt5.ORDER_TYPE_SELL if pos.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
                price = mt5.symbol_info_tick(symbol).bid if order_type == mt5.ORDER_TYPE_SELL else mt5.symbol_info_tick(symbol).ask
                close_request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": symbol,
                    "volume": pos.volume,
                    "type": order_type,
                    "position": pos.ticket,
                    "price": price,
                    "deviation": 10,
                    "magic": 234000,
                    "comment": "Auto Close after 1 Minute",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_IOC,
                }
                result = mt5.order_send(close_request)
                if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                    profit = pos.profit
                    print(f"✅ TRADE #{pos.ticket} CLOSED | PROFIT/LOSS: {profit:.2f}")
                    log_profit_loss(pos.ticket, profit)
                else:
                    print(f"❌ Failed to close trade {pos.ticket}")
            else:
                updated_trades.append(trade)
        else:
            print(f"⚠️ Trade {trade['ticket']} not found")
    open_trades = updated_trades

def log_profit_loss(ticket, profit):
    global df_log
    idx = df_log[df_log["result"] == "open"].last_valid_index()
    if idx is not None:
        df_log.loc[idx, "result"] = "profit" if profit > 0 else "loss"
        df_log.loc[idx, "profit_loss"] = round(profit, 2)
        df_log.to_csv(prediction_log, index=False)

def predict_price():
    df = get_recent_data()
    if df is None or df.empty:
        return None, None

    close_prices = df['close'].values.reshape(-1, 1)
    scaled = scaler.transform(close_prices)
    X = np.array([scaled[-50:]])
    prediction = model.predict(X, verbose=0)
    predicted_scaled = prediction[0][0]
    predicted_price = scaler.inverse_transform([[predicted_scaled]])[0][0]
    return df['close'].values[-1], predicted_price

def detect_and_plot_patterns():
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 100)
    if rates is None or len(rates) == 0:
        return

    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'tick_volume': 'Volume'}, inplace=True)
    df.set_index('time', inplace=True)

    df = apply_all_patterns(df)
    detected = []

    for col in df.columns:
        if "pattern" in col.lower() and df[col].iloc[-1]:
            pattern_name = col
            detected.append(pattern_name)
            engine.say(pattern_name)
            engine.runAndWait()

    if detected:
        print("📊 Detected Patterns:", ", ".join(detected))

# 🔁 Main loop
try:
    while True:
        actual_price, predicted_price = predict_price()

        if actual_price is None or predicted_price is None:
            print("⚠️ No data")
            time.sleep(60)
            continue

        diff = predicted_price - actual_price
        threshold = 0.00001

        # ✅ NORMAL LOGIC
        if diff > threshold:
            signal = "buy"
        elif diff < -threshold:
            signal = "sell"
        else:
            signal = "hold"

        placed = False
        ticket = None
        if signal != "hold":
            placed, ticket = place_order(signal)

        # Log entry
        log_entry = {
            "datetime": datetime.now(),
            "actual_price": actual_price,
            "predicted_price": predicted_price,
            "signal": signal,
            "result": "open" if placed else "hold",
            "profit_loss": None
        }
        df_log = pd.concat([df_log, pd.DataFrame([log_entry])], ignore_index=True)
        df_log.to_csv(prediction_log, index=False)

        print("\n" + "="*60)
        print(f"🕒 Time       : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📈 Actual     : {actual_price:.5f}")
        print(f"🤖 Predicted  : {predicted_price:.5f}")
        print(f"📢 Signal     : {signal.upper()}")
        print(f"🚀 Trade      : {'✔️ Placed' if placed else '❌ Not Placed'}")
        print("="*60)

        detect_and_plot_patterns()
        monitor_open_trades()
        time.sleep(60)

except KeyboardInterrupt:
    print("🛑 Bot stopped by user")
    mt5.shutdown()
