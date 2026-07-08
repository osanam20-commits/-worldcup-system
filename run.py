import os
import telebot
import threading
from flask import Flask

# إعداد البوت
TOKEN = "8689943788:AAFfmE62a4h-eLXYAcOXvSUgmkLs5KZZwts"
bot = telebot.TeleBot(TOKEN)

# إعداد موقع وهمي لإرضاء Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running"

# تشغيل البوت
def run_bot():
    bot.infinity_polling()

if __name__ == '__main__':
    # تشغيل البوت في الخلفية
    threading.Thread(target=run_bot, daemon=True).start()
    # تشغيل الموقع (هذا السطر يمنع Render من إغلاق الخدمة)
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
