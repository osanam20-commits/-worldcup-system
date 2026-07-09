import os
import telebot
import requests
from flask import Flask
from threading import Thread
import time

# --- الإعدادات (ضع التوكن والمفتاح هنا) ---
TOKEN = "8689943788:AAFfmE62a4h-eLXYAcOXvSUgmkLs5KZZwts"
CHANNEL_ID = "-1004372754611"
API_KEY = "https://football-prediction-api.p.rapidapi.com/api/v2/predictions?market=classic&iso_date=2018-12-01&federation=UEFA" 

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- المسار الأساسي (لضمان عمل الرابط) ---
@app.route('/')
def home():
    return "البوت يعمل بكفاءة!"

# --- دالة جلب التوقعات من API ---
def get_football_predictions():
    url = "https://football-prediction-api.p.rapidapi.com/api/v2/predictions"
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "football-prediction-api.p.rapidapi.com"
    }
    # تاريخ اليوم 2026-07-09
    params = {"market": "classic", "iso_date": "2026-07-09"}
    try:
        response = requests.get(url, headers=headers, params=params)
        return response.json()
    except Exception as e:
        print(f"خطأ في الاتصال بـ API: {e}")
        return None

# --- دالة النشر في القناة ---
def auto_post():
    while True:
        data = get_football_predictions()
        if data and 'data' in data and len(data['data']) > 0:
            match = data['data'][0]
            msg = f"⚽ **توقعات اليوم:**\n\n{match.get('home_team')} vs {match.get('away_team')}\nالنتيجة المتوقعة: {match.get('prediction')}"
            bot.send_message(CHANNEL_ID, msg)
        else:
            print("لم يتم العثور على مباريات اليوم.")
        
        # النشر كل 6 ساعات (21600 ثانية)
        time.sleep(21600)

# --- تشغيل البوت ---
def run_bot():
    bot.infinity_polling()

if __name__ == '__main__':
    # تشغيل مهام البوت في خلفية مستقلة
    Thread(target=run_bot).start()
    Thread(target=auto_post).start()
    # تشغيل سيرفر Flask
    app.run(host='0.0.0.0', port=10000)
