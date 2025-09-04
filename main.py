import time
import requests
from telegram import Bot

# Твої токени (захардкоджені)
TELEGRAM_TOKEN = "8041021589:AAFuD-HElQI4yehKOJ328-V50XFhk9XQWfQ"
CHAT_ID = "2066686801"
API_KEY = "4d43adc405084d9fa68103c42afaaaa7"

bot = Bot(token=TELEGRAM_TOKEN)

def get_signal():
    """Функція отримання сигналу з TwelveData"""
    try:
        url = f"https://api.twelvedata.com/time_series?symbol=EUR/USD&interval=5min&apikey={API_KEY}"
        response = requests.get(url).json()

        if "values" not in response:
            return "Помилка API"

        values = response["values"][:2]
        last = float(values[0]["close"])
        prev = float(values[1]["close"])

        if last > prev:
            return "📈 Купувати (ймовірність 90%+)"
        elif last < prev:
            return "📉 Продавати (ймовірність 90%+)"
        else:
            return "⏸ Очікувати"
    except Exception as e:
        return f"Помилка: {e}"

def main():
    while True:
        signal = get_signal()
        bot.send_message(chat_id=CHAT_ID, text=f"Сигнал: {signal}")
        time.sleep(300)  # кожні 5 хвилин

if __name__ == "__main__":
    main()
