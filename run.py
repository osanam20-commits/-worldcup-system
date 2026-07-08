import os
import telebot
import threading
from flask import Flask

# 1. الإعدادات
TOKEN = "8689943788:AAFfmE62a4h-eLXYAcOXvSUgmkLs5KZZwts"
CHANNEL_ID = "-1004372754611"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# 2. هذه الصفحة تجعل Render ترى أن الموقع يعمل (تمنع التايم أوت)
@app.route('/')
def home():
    return "البوت والقناة يعملان هنا!"

# 3. أوامر البوت
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "✅ البوت والموقع يعملان معاً!")

# 4. تشغيل البوت في الخلفية
def run_bot():
    bot.infinity_polling()

if __name__ == '__main__':
    # تشغيل البوت كـ Thread
    threading.Thread(target=run_bot, daemon=True).start()
    
    # ربط Flask بالبورت الذي تطلبه Render (وهذا هو سر الحل)
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
