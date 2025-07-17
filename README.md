# 💸 The-Millionare-Stock-Predictor

**The-Millionare-Stock-Predictor** is a professional-grade AI-powered Forex trading bot that leverages deep learning (LSTM) and MetaTrader 5 to predict real-time EURUSDm price movements on a 1-minute timeframe. Built for research and demo trading, this system automates trading decisions, logs profit/loss accurately from MT5, and integrates candlestick pattern recognition for enhanced strategy execution.

---

## 📌 Key Features

* 🔮 **LSTM Neural Network**: Predicts short-term price trends using 1-minute historical data.
* 🛒 **Automated Trade Execution**: Sends buy/sell orders via MetaTrader 5 based on predicted signals.
* 🕯️ **Candlestick Pattern Detection**: Recognizes key patterns like Doji, Engulfing, Hammer, etc.
* 💰 **Smart Exit Logic**: Trades are closed only when in profit.
* 📊 **Real MT5 Profit/Loss Logging**: Tracks actual trade outcome using MT5 order history.
* 🧪 **Designed for Demo Trading**: Ensures zero-risk AI trading experimentation.

---

## 📂 Project Structure

```
The-Millionare-Stock-Predictor/
├── EURUSD_Candlestick_1_M_BID_01.01.2024-30.06.2024.csv   # Training dataset (1-minute)
├── EURUSDm_1M.csv                                         # Live price data feed
├── train_lstm.py                                          # Model training script
├── bot.py                                                 # Real-time AI trading bot
├── prediction_log.csv                                     # Trade logs with P/L
├── model/                                                 # Saved LSTM model and scaler
│   ├── lstm_model.h5
│   └── scaler.pkl
```

---

## ⚙️ Installation & Setup

### 1. Create Conda Environment

```bash
conda create -n forex_env python=3.10
conda activate forex_env
```

### 2. Install Required Packages

```bash
pip install tensorflow numpy pandas scikit-learn matplotlib MetaTrader5 pyttsx3 ta joblib
```

### 3. MetaTrader 5 Setup

* Install MT5 platform and log in using a demo account.
* Ensure symbol **EURUSDm** is visible and active.

---

## 🧠 Train the Model

Ensure your historical data file is located at:
`The-Millionare-Stock-Predictor/EURUSD_Candlestick_1_M_BID_01.01.2024-30.06.2024.csv`

Then run:

```bash
python train_lstm.py
```

This will save the trained model and scaler to `model/`.

---

## 🤖 Run the Bot (Live Prediction + Trading)

```bash
python bot.py
```

**Functionality:**

* Fetches latest 1M price data for EURUSDm
* Predicts next price movement using LSTM
* Executes BUY/SELL based on signal
* Detects candlestick patterns
* Closes open trades **only when in profit**
* Logs full trade results to `prediction_log.csv`

> ✅ MT5 terminal must remain open with market hours active.

---

## 📁 Trade Log Format (`prediction_log.csv`)

| Timestamp           | Signal | Entry Price | Exit Price | Profit  | Pattern           | Result |
| ------------------- | ------ | ----------- | ---------- | ------- | ----------------- | ------ |
| 2024-07-15 13:41:00 | BUY    | 1.08210     | 1.08250    | 0.00040 | Bullish Engulfing | Profit |

---

## 📉 Strategy Notes

* The LSTM model is trained on 6 months of 1-minute EURUSDm data.
* Entry and exit thresholds can be adjusted in `bot.py` for better optimization.
* Focuses on micro scalping techniques with high-frequency predictions.

---

## ⚠️ Disclaimer

> This bot is intended for **educational and research** purposes only. Do **not** use this system on live accounts with real money. Market risk is high and unpredictable. The authors are not liable for any financial losses.

---

## 🔄 Planned Enhancements

* 🧮 Integration of technical indicators (MACD, RSI, Bollinger Bands)
* 📲 Telegram/Email alert system for trades
* 🧠 Advanced hyperparameter tuning (Bayesian optimization)
* 🖥️ Real-time web dashboard using FastAPI + React
* 💼 Multi-symbol and multi-timeframe support

---

## 👨‍💻 Author

Made with 🔥 by **Subash P.**
*For queries or collaboration, raise an issue or pull request.*

