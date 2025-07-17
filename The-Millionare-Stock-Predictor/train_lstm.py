import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import EarlyStopping
import joblib
from datetime import datetime

# 📂 Load 1-minute historical data
data_path = "D:/DIVINE_GENERAL/EURUSDm_1M.csv"
df = pd.read_csv(data_path)
df['datetime'] = pd.to_datetime(df['datetime'])
df.set_index('datetime', inplace=True)

# 🎯 Target: classify next move: Buy (1), Sell (2), Hold (0)
threshold = 0.0002

# 🏷️ Labeling logic
def generate_labels(close_prices):
    labels = []
    for i in range(len(close_prices)-2):
        now = close_prices[i]
        future = close_prices[i+1]
        diff = future - now
        if diff > threshold:
            labels.append(1)  # Buy
        elif diff < -threshold:
            labels.append(2)  # Sell
        else:
            labels.append(0)  # Hold
    labels.append(0)
    labels.append(0)
    return np.array(labels)

# 🧼 Prepare features
df['label'] = generate_labels(df['close'].values)
scaler = MinMaxScaler()
df['scaled_close'] = scaler.fit_transform(df[['close']])

# 🪄 Generate sequences
def create_sequences(data, labels, seq_length=50):
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i:i+seq_length])
        y.append(labels[i+seq_length])
    return np.array(X), np.array(y)

X, y = create_sequences(df['scaled_close'].values, df['label'].values)
y_cat = to_categorical(y, num_classes=3)

# 🧪 Split
tX, vX, ty, vy = train_test_split(X, y_cat, test_size=0.2, shuffle=False)

# 🧠 Build model
model = Sequential([
    LSTM(64, input_shape=(50, 1), return_sequences=True),
    Dropout(0.2),
    LSTM(32),
    Dropout(0.2),
    Dense(32, activation='relu'),
    Dense(3, activation='softmax')
])

model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# 🛑 Early stopping
early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

# 🏋️‍♂️ Train
model.fit(tX, ty, validation_data=(vX, vy), epochs=50, batch_size=64, callbacks=[early_stop])

# 📊 Evaluation
val_loss, val_acc = model.evaluate(vX, vy)
print(f"📊 Validation Accuracy: {val_acc:.4f}")

# 💾 Save with timestamp
model_name = f"D:/DIVINE_GENERAL/classifier_model_{datetime.now().strftime('%Y%m%d_%H%M%S')}.h5"
model.save(model_name)
joblib.dump(scaler, "D:/DIVINE_GENERAL/scaler_classifier.pkl")

print(f"✅ Model trained and saved as {model_name}!")
