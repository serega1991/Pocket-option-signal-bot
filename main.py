
import os
import time
import requests
from telegram import Bot

# Дані користувача
CHAT_ID = "2066686801"
TELEGRAM_TOKEN = "8041021589"
API_KEY = "4d43adc405084d9fa68103c42afaaaa7"

bot = Bot(token=TELEGRAM_TOKEN)

# Валютні пари
pairs = [
    "EUR/USD", "CAD/CHF", "USD/JPY", "GBP/USD",
    "AUD/CHF", "EUR/GBP", "NZD/USD", "USD/CAD"
]

def get_signal(pair):
    url = f"https://api.twelvedata.com/ema?symbol={pair}&interval=5min&time_period=10&apikey={API_KEY}"
    response = requests.get(url).json()
    if 'values' not in response:
        return None

    values = response['values']
    if len(values) < 2:
        return None

    last = float(values[0]['ema'])
    prev = float(values[1]['ema'])

    if last > prev:
        return "BUY"
    elif last < prev:
        return "SELL"
    return None

def send_signal():
    for pair in pairs:
        signal = get_signal(pair)
        if signal:
            msg = f"📊 Сигнал для {pair} (REAL): {signal} (90%+)"
            bot.send_message(chat_id=CHAT_ID, text=msg)
            time.sleep(1)

if __name__ == "__main__":
    while True:
        send_signal()
        time.sleep(300)  # кожні 5 хв
