import os
import time
import requests
from flask import Flask
from telegram import Bot
from threading import Thread

app = Flask(__name__)

# 🔑 Твої токени
TELEGRAM_TOKEN = "8041021589:AAFuD-HElQI4yehKOJ328-V50XFhk9XQWfQ"
CHAT_ID = "2066686801"
API_KEY = "4d43adc405084d9fa68103c42afaaaa7"

bot = Bot(token=TELEGRAM_TOKEN)

# Валютні пари
PAIRS = [
    "EUR/USD", "CAD/CHF", "USD/JPY", "GBP/USD",
    "AUD/CHF", "EUR/GBP", "NZD/USD", "USD/CAD"
]

@app.route("/")
def home():
    return "Pocket Option Signal Bot is running!"

def analyze_and_send():
    for pair in PAIRS:
        symbol = pair.replace("/", "")
        url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=1min&apikey={API_KEY}&outputsize=2"
        try:
            r = requests.get(url)
            data = r.json()
            values = data.get("values", [])
            if len(values) < 2:
                continue

            last = float(values[0]["close"])
            prev = float(values[1]["close"])

            if last > prev:
                signal, probability = "📈 Купувати", 92
            elif last < prev:
                signal, probability = "📉 Продавати", 91
            else:
                signal, probability = "⏸ Очікувати", 50

            if probability >= 90:
                bot.send_message(
                    chat_id=CHAT_ID,
                    text=f"🔔 Сигнал по {pair}\n{signal}\nЙмовірність: {probability}%"
                )
        except Exception as e:
            print("Error for", pair, e)

def run_loop():
    while True:
        analyze_and_send()
        time.sleep(300)

if __name__ == "__main__":
    t = Thread(target=run_loop)
    t.daemon = True
    t.start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
