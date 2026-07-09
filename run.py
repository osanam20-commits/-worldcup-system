import telebot
import os
from flask import Flask
from threading import Thread

# 1. إعدادات البوت
TOKEN = "8689943788:AAFfmE62a4h-eLXYAcOXvSUgmkLs5KZZwts" # ضع التوكن هنا مباشرة للتجربة
bot = telebot.TeleBot(TOKEN)

# 2. إعدادات Flask (الموقع الذي يمنع انطفاء البوت)
app = Flask(__name__)

@app.route('/')
def home():
    return "البوت يعمل بكفاءة!"

# 3. تشغيل البوت في مسار منفصل
def start_bot():
    bot.infinity_polling()

# 4. تشغيل الموقع في المسار الرئيسي
if __name__ == '__main__':
    Thread(target=start_bot).start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
