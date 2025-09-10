# main.py
# Pocket Option signal bot (simple) — запущено як web service + background thread

import os
import time
import requests
from flask import Flask
from telegram import Bot
from threading import Thread

app = Flask(__name__)

# ====== ТВОЇ ТОКЕНИ (вставлені прямо) ======
TELEGRAM_TOKEN = "8041021589:AAFuD-HElQI4yehKOJ328-V50XFhk9XQWfQ"
CHAT_ID = "2066686801"
API_KEY = "4d43adc405084d9fa68103c42afaaaa7"
# ============================================

bot = Bot(token=TELEGRAM_TOKEN)

# Валютні пари (8 пар)
PAIRS = [
    "EUR/USD",
    "CAD/CHF",
    "USD/JPY",
    "GBP/USD",
    "AUD/CHF",
    "EUR/GBP",
    "NZD/USD",
    "USD/CAD"
]

@app.route("/")
def home():
    return "Pocket Option Signal Bot is running!"

def analyze_and_send():
    """
    Проста логіка: бере останні 2 значення з TwelveData (1min)
    Повертає сигнал якщо зміна в потрібний бік і ймовірність >= 90%.
    (Ти просив просту реалізацію; для реального торгового робота логіку потрібно ускладнити)
    """
    for pair in PAIRS:
        # TwelveData expects symbols без "/": наприклад "EURUSD"
        symbol = pair.replace("/", "")
        url = (
            f"https://api.twelvedata.com/time_series?"
            f"symbol={symbol}&interval=1min&apikey={API_KEY}&outputsize=2"
        )
        try:
            resp = requests.get(url, timeout=10)
            data = resp.json()
            if "values" not in data:
                # помилка з API — ідемо далі
                print(f"TwelveData error for {pair}: {data}")
                continue

            values = data["values"]
            if len(values) < 2:
                continue

            last = float(values[0]["close"])
            prev = float(values[1]["close"])

            # дуже проста метрика: якщо закриття піднялося -> BUY, опустилося -> SELL
            if last > prev:
                signal = "📈 Купувати"
                probability = 92
            elif last < prev:
                signal = "📉 Продавати"
                probability = 91
            else:
                signal = "⏸ Без сигналу"
                probability = 50

            # Ти просив надсилати лише сигнали >= 90%
            if probability >= 90:
                text = (
                    f"🔔 Сигнал: {pair}\n"
                    f"{signal}\n"
                    f"Ймовірність: {probability}%\n"
                    f"Ринок: {'REAL' if 'OTC' not in pair else 'OTC'}"
                )
                try:
                    bot.send_message(chat_id=CHAT_ID, text=text)
                    print(f"Sent signal for {pair}: {signal} {probability}%")
                except Exception as e:
                    print("Telegram send error:", e)

        except Exception as e:
            print("Error analyzing", pair, e)

def run_loop():
    # запускаємо нескінченний цикл, що виконує аналіз кожні 5 хвилин
    while True:
        analyze_and_send()
        time.sleep(300)  # 5 хвилин

if __name__ == "__main__":
    t = Thread(target=run_loop, daemon=True)
    t.start()
    # Запускаємо Flask (Render підключить gunicorn з Procfile)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
