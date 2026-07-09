import os
import telebot
import requests
from flask import Flask
from threading import Thread

# إعداداتك
TOKEN = "8689943788:AAFfmE62a4h-eLXYAcOXvSUgmkLs5KZZwts" # ضع التوكن الخاص بك هنا
CHANNEL_ID = "-1004372754611"
API_KEY = "curl --request GET \
	--url 'https://football-prediction-api.p.rapidapi.com/api/v2/predictions?market=classic&iso_date=2018-12-01&federation=UEFA' \
	--header 'Content-Type: application/json' \
	--header 'x-rapidapi-host: football-prediction-api.p.rapidapi.com' \
	--header 'x-rapidapi-key: 3ceaa7be00msha38c948056a4052p1fd973jsn92dcc1392590'"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# مسار لجعل Render سعيداً (يمنع الخطأ 502)
@app.route('/')
def home():
    return "البوت يعمل بنجاح!"

# دالة لجلب البيانات
def fetch_football_data():
    url = "https://football-prediction-api.p.rapidapi.com/api/v2/predictions"
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "football-prediction-api.p.rapidapi.com"
    }
    # جلب توقعات اليوم
    params = {"market": "classic", "iso_date": "2026-07-09"}
    try:
        response = requests.get(url, headers=headers, params=params)
        return response.json()
    except:
        return None

# دالة تشغيل البوت
def run_bot():
    bot.infinity_polling()

if __name__ == '__main__':
    # تشغيل البوت في مسار منفصل
    Thread(target=run_bot).start()
    # تشغيل خادم Flask
    app.run(host='0.0.0.0', port=10000)
