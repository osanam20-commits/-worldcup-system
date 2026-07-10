import os
import telebot
import requests
import time
from flask import Flask
from threading import Thread

# الإعدادات
TOKEN = "8689943788:AAHOD6jINGiV_g8wHYJ8eZ5SwO6_OLngoYE"
CHANNEL_ID = "-1004372754611"
API_KEY = "curl --request GET \
	--url 'https://football-prediction-api.p.rapidapi.com/api/v2/predictions?market=classic&iso_date=2018-12-01&federation=UEFA' \
	--header 'Content-Type: application/json' \
	--header 'x-rapidapi-host: football-prediction-api.p.rapidapi.com' \
	--header 'x-rapidapi-key: 3ceaa7be00msha38c948056a4052p1fd973jsn92dcc1392590'"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "البوت يعمل!"

# دالة اختبار للرد السريع
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "أنا متصل وأعمل!")
    print("تم تلقي أمر start والرد عليه")

def check_bot():
    # هذا السطر يجبر البوت على مسح أي جلسة معلقة في تيليجرام
    bot.remove_webhook()
    print("تم حذف الويب هوك القديم")
    
    # حلقة التشغيل الأساسية
    bot.infinity_polling(none_stop=True, skip_pending=True)

if __name__ == '__main__':
    # تشغيل البوت في مسار منفصل
    Thread(target=check_bot).start()
    # تشغيل خادم Flask
    app.run(host='0.0.0.0', port=10000)
