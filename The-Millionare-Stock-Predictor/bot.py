# import MetaTrader5 as mt5
# import pandas as pd
# import numpy as np
# import joblib
# import pyttsx3
# from tensorflow.keras.models import load_model
# from datetime import datetime
# import time
# from candlestick import apply_all_patterns

# # TTS init for candlestick patterns
# engine = pyttsx3.init()
# engine.setProperty('rate', 170)

# # Load trained model and scaler
# model = load_model("D:/DIVINE_GENERAL/lstm_model.h5")
# scaler = joblib.load("D:/DIVINE_GENERAL/scaler.pkl")

# # Constants
# symbol = "EURUSD"
# lot = 0.1
# prediction_log = "D:/DIVINE_GENERAL/prediction_log.csv"
# open_trades = []

# # Initialize MT5
# if not mt5.initialize():
#     print("❌ MT5 initialization failed")
#     quit()

# info = mt5.symbol_info(symbol)
# if info is None or not info.visible:
#     if not mt5.symbol_select(symbol, True):
#         print(f"❌ Failed to select symbol {symbol}")
#         quit()

# # Load or create log
# try:
#     df_log = pd.read_csv(prediction_log)
# except:
#     df_log = pd.DataFrame(columns=["datetime", "actual_price", "predicted_price", "signal", "result", "profit_loss"])

# def get_recent_data():
#     """Fetches the last 50 M1 candles."""
#     rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 50)
#     if rates is None or len(rates) < 50:
#         return None
#     df = pd.DataFrame(rates)
#     df['time'] = pd.to_datetime(df['time'], unit='s')
#     return df[['time', 'close']]

# def place_order(signal):
#     """Places a trade order based on the signal, with inverted logic."""
#     # 🔄 INVERTED LOGIC: BUY SIGNAL → SELL TRADE, SELL SIGNAL → BUY TRADE
#     order_type = mt5.ORDER_TYPE_SELL if signal == "buy" else mt5.ORDER_TYPE_BUY

#     # Get the latest tick information to ensure we have the correct bid/ask prices
#     tick = mt5.symbol_info_tick(symbol)
#     if tick is None:
#         print("❌ Failed to get tick information")
#         return False, None

#     # Determine the correct price based on the order type
#     # For a BUY order, use the ASK price. For a SELL order, use the BID price.
#     price = tick.ask if order_type == mt5.ORDER_TYPE_BUY else tick.bid

#     if price == 0:
#         print(f"❌ Invalid price (0) for order type {order_type}. Tick: {tick}")
#         return False, None

#     request = {
#         "action": mt5.TRADE_ACTION_DEAL,
#         "symbol": symbol,
#         "volume": lot,
#         "type": order_type,
#         "price": price,
#         "deviation": 10,
#         "magic": 234000,
#         "comment": "AI Trade (Inverted)",
#         "type_time": mt5.ORDER_TIME_GTC,
#         "type_filling": mt5.ORDER_FILLING_IOC,
#     }

#     result = mt5.order_send(request)
#     print(result)

#     if result and result.retcode == mt5.TRADE_RETCODE_DONE:
#         ticket = result.order
#         open_trades.append({
#             "ticket": ticket,
#             "signal": signal,
#             "entry_price": result.price, # Log the actual execution price
#             "open_time": datetime.now()
#         })
#         return True, ticket
#     else:
#         print(f"❌ Order failed: retcode={result.retcode} - {result.comment}")
#         return False, None

# def monitor_open_trades():
#     """Monitors open trades and closes them only when they are in profit."""
#     global open_trades
#     updated_trades = []
#     for trade in open_trades:
#         positions = mt5.positions_get(ticket=trade["ticket"])
#         if positions and len(positions) > 0:
#             pos = positions[0]
            
#             # --- MODIFIED LOGIC ---
#             # Check if the current position is profitable.
#             if pos.profit > 0:
#                 # If the trade is profitable, close it.
#                 order_type = mt5.ORDER_TYPE_SELL if pos.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
#                 price = mt5.symbol_info_tick(symbol).bid if order_type == mt5.ORDER_TYPE_SELL else mt5.symbol_info_tick(symbol).ask
                
#                 close_request = {
#                     "action": mt5.TRADE_ACTION_DEAL,
#                     "symbol": symbol,
#                     "volume": pos.volume,
#                     "type": order_type,
#                     "position": pos.ticket,
#                     "price": price,
#                     "deviation": 10,
#                     "magic": 234000,
#                     "comment": "Auto Close on Profit",
#                     "type_time": mt5.ORDER_TIME_GTC,
#                     "type_filling": mt5.ORDER_FILLING_IOC,
#                 }
#                 result = mt5.order_send(close_request)
#                 if result and result.retcode == mt5.TRADE_RETCODE_DONE:
#                     profit = pos.profit
#                     print(f"✅ PROFITABLE TRADE #{pos.ticket} CLOSED | PROFIT: {profit:.2f}")
#                     log_profit_loss(pos.ticket, profit)
#                 else:
#                     # If closing fails for some reason, keep it in the list to retry
#                     print(f"❌ Failed to close profitable trade {pos.ticket}, will retry.")
#                     updated_trades.append(trade)
#             else:
#                 # If the trade is not profitable, hold it and keep monitoring.
#                 updated_trades.append(trade)
#         else:
#             # If position is not found, it might have been closed manually.
#             print(f"⚠️ Trade {trade['ticket']} not found in open positions.")
            
#     open_trades = updated_trades

# def log_profit_loss(ticket, profit):
#     """Logs the profit or loss for a closed trade."""
#     global df_log
#     # Find the last 'open' log entry to update it
#     idx = df_log[df_log["result"] == "open"].last_valid_index()
#     if idx is not None:
#         df_log.loc[idx, "result"] = "profit" if profit > 0 else "loss"
#         df_log.loc[idx, "profit_loss"] = round(profit, 2)
#         df_log.to_csv(prediction_log, index=False)

# def predict_price():
#     """Predicts the next price using the loaded LSTM model."""
#     df = get_recent_data()
#     if df is None or df.empty:
#         return None, None

#     close_prices = df['close'].values.reshape(-1, 1)
#     scaled = scaler.transform(close_prices)
#     X = np.array([scaled[-50:]])
#     prediction = model.predict(X, verbose=0)
#     predicted_scaled = prediction[0][0]
#     predicted_price = scaler.inverse_transform([[predicted_scaled]])[0][0]
#     return df['close'].values[-1], predicted_price

# def detect_and_plot_patterns():
#     """Detects and announces candlestick patterns from the latest data."""
#     rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 100)
#     if rates is None or len(rates) == 0:
#         return

#     df = pd.DataFrame(rates)
#     df['time'] = pd.to_datetime(df['time'], unit='s')
#     df.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'tick_volume': 'Volume'}, inplace=True)
#     df.set_index('time', inplace=True)

#     # Apply candlestick pattern recognition
#     df = apply_all_patterns(df)
#     detected = []

#     # Check the most recent candle for any detected patterns
#     for col in df.columns:
#         if "pattern" in col.lower() and df[col].iloc[-1]:
#             pattern_name = col.replace("_pattern", "").replace("_", " ").title()
#             detected.append(pattern_name)
#             engine.say(pattern_name)
#             engine.runAndWait()

#     if detected:
#         print("📊 Detected Patterns:", ", ".join(detected))

# # 🔁 Main trading loop
# try:
#     while True:
#         actual_price, predicted_price = predict_price()

#         if actual_price is None or predicted_price is None:
#             print("⚠️ Could not fetch data for prediction, waiting...")
#             time.sleep(10)
#             continue

#         diff = predicted_price - actual_price
#         # A small threshold to prevent trading on minor fluctuations
#         threshold = 0.0001 

#         # Signal generation based on prediction
#         # This logic remains the same; the inversion happens in place_order
#         if diff > threshold:
#             signal = "buy"  # Prediction is higher -> Buy signal
#         elif diff < -threshold:
#             signal = "sell" # Prediction is lower -> Sell signal
#         else:
#             signal = "hold"

#         placed = False
#         if signal != "hold":
#             placed, ticket = place_order(signal)

#         # Log the prediction and action
#         log_entry = {
#             "datetime": datetime.now(),
#             "actual_price": actual_price,
#             "predicted_price": predicted_price,
#             "signal": signal,
#             "result": "open" if placed else "hold",
#             "profit_loss": None
#         }
#         df_log = pd.concat([df_log, pd.DataFrame([log_entry])], ignore_index=True)
#         df_log.to_csv(prediction_log, index=False)

#         # Print status update
#         print("\n" + "="*100)
#         print(f"🕒 Time       : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
#         print(f"📈 Actual     : {actual_price:.5f}")
#         print(f"🤖 Predicted  : {predicted_price:.5f}")
#         print(f"📢 Signal     : {signal.upper()}")
#         print(f"🔄 Trade Type : {'SELL' if signal == 'buy' else ('BUY' if signal == 'sell' else 'NONE')} (Inverted)")
#         print(f"🚀 Trade      : {'✔️ Placed' if placed else '❌ Not Placed'}")
#         print("="*100)

#         # Run other monitoring tasks
#         detect_and_plot_patterns()
#         monitor_open_trades()
        
#         # Wait before the next cycle
#         time.sleep(10)

# except KeyboardInterrupt:
#     print("\n🛑 Bot stopped by user. Shutting down MT5 connection.")
#     mt5.shutdown()

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import joblib
import pyttsx3
from tensorflow.keras.models import load_model
from datetime import datetime
import time
from candlestick import apply_all_patterns

# =======================
# CONFIGURATIONS
# =======================
engine = pyttsx3.init()
engine.setProperty('rate', 170)

model = load_model("D:/DIVINE_GENERAL/lstm_model.h5")
scaler = joblib.load("D:/DIVINE_GENERAL/scaler.pkl")

symbol = "EURUSD"
lot = 0.1
prediction_log = "D:/DIVINE_GENERAL/prediction_log.csv"
profit_percent = 2.0  # ✅ Close trade when 2% profit is reached

open_trades = []

# =======================
# MT5 Initialization
# =======================
if not mt5.initialize():
    print("❌ MT5 initialization failed")
    quit()

info = mt5.symbol_info(symbol)
if info is None or not info.visible:
    if not mt5.symbol_select(symbol, True):
        print(f"❌ Failed to select symbol {symbol}")
        quit()

# =======================
# Load or Create Log File
# =======================
try:
    df_log = pd.read_csv(prediction_log)
except:
    df_log = pd.DataFrame(columns=["datetime", "actual_price", "predicted_price", "signal", "result", "profit_loss"])


def get_recent_data():
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 50)
    if rates is None or len(rates) < 50:
        return None
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    return df[['time', 'close']]


def place_order(signal):
    order_type = mt5.ORDER_TYPE_SELL if signal == "buy" else mt5.ORDER_TYPE_BUY
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        print("❌ Failed to get tick information")
        return False, None

    price = tick.ask if order_type == mt5.ORDER_TYPE_BUY else tick.bid
    if price == 0:
        print(f"❌ Invalid price for order type {order_type}")
        return False, None

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": order_type,
        "price": price,
        "deviation": 10,
        "magic": 234000,
        "comment": "AI Trade (Inverted)",
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
            "entry_price": result.price,
            "open_time": datetime.now()
        })
        return True, ticket
    else:
        print(f"❌ Order failed: retcode={result.retcode} - {result.comment}")
        return False, None


def monitor_open_trades():
    global open_trades
    updated_trades = []

    for trade in open_trades:
        positions = mt5.positions_get(ticket=trade["ticket"])
        if positions and len(positions) > 0:
            pos = positions[0]
            tick = mt5.symbol_info_tick(symbol)
            if not tick:
                continue

            current_price = tick.bid if pos.type == mt5.ORDER_TYPE_BUY else tick.ask
            entry_price = trade["entry_price"]

            if pos.type == mt5.ORDER_TYPE_BUY:
                target_price = entry_price * (1 + profit_percent / 100)
                is_profitable = current_price >= target_price
            else:
                target_price = entry_price * (1 - profit_percent / 100)
                is_profitable = current_price <= target_price

            if is_profitable:
                order_type = mt5.ORDER_TYPE_SELL if pos.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
                close_price = tick.bid if order_type == mt5.ORDER_TYPE_SELL else tick.ask

                close_request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": symbol,
                    "volume": pos.volume,
                    "type": order_type,
                    "position": pos.ticket,
                    "price": close_price,
                    "deviation": 10,
                    "magic": 234000,
                    "comment": f"Auto Close at {profit_percent}% Profit",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_IOC,
                }

                result = mt5.order_send(close_request)
                if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                    profit = pos.profit
                    print(f"✅ TRADE #{pos.ticket} CLOSED at {profit_percent}% PROFIT | PROFIT: {profit:.2f}")
                    log_profit_loss(pos.ticket, profit)
                else:
                    print(f"❌ Failed to close trade {pos.ticket}, retrying.")
                    updated_trades.append(trade)
            else:
                updated_trades.append(trade)
        else:
            print(f"⚠️ Trade {trade['ticket']} not found in open positions.")

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
            pattern_name = col.replace("_pattern", "").replace("_", " ").title()
            detected.append(pattern_name)
            engine.say(pattern_name)
            engine.runAndWait()
    if detected:
        print("📊 Detected Patterns:", ", ".join(detected))


try:
    while True:
        actual_price, predicted_price = predict_price()
        if actual_price is None or predicted_price is None:
            print("⚠️ Could not fetch data for prediction, waiting...")
            time.sleep(60)
            continue

        diff = predicted_price - actual_price
        threshold = 0.0001

        if diff > threshold:
            signal = "buy"
        elif diff < -threshold:
            signal = "sell"
        else:
            signal = "hold"

        placed = False
        if signal != "hold":
            placed, ticket = place_order(signal)

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

        print("\n" + "="*100)
        print(f"🕒 Time       : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📈 Actual     : {actual_price:.5f}")
        print(f"🤖 Predicted  : {predicted_price:.5f}")
        print(f"📢 Signal     : {signal.upper()}")
        print(f"🔄 Trade Type : {'SELL' if signal == 'buy' else ('BUY' if signal == 'sell' else 'NONE')} (Inverted)")
        print(f"🚀 Trade      : {'✔️ Placed' if placed else '❌ Not Placed'}")
        print("="*100)

        detect_and_plot_patterns()
        monitor_open_trades()
        time.sleep(60)

except KeyboardInterrupt:
    print("\n🛑 Bot stopped by user. Shutting down MT5 connection.")
    mt5.shutdown()
