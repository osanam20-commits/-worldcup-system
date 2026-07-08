import os
import threading
import telebot
from flask import Flask

# 1. الإعدادات
TOKEN = "8689943788:AAFfmE62a4h-eLXYAcOXvSUgmkLs5KZZwts"
CHANNEL_ID = "-1004372754611"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# 2. كود الموقع (يظهر عند زيارة رابط Render)
@app.route('/')
def home():
    return "<h1>البوت والقناة يعملان هنا!</h1>"

# 3. أوامر البوت
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "✅ البوت والموقع يعملان معاً!")

@bot.message_handler(commands=['today'])
def today(message):
    bot.reply_to(message, "⚽ لا توجد مباريات.")

# 4. تشغيل الموقع والبوت معاً باستخدام الخيوط (Threading)
def run_bot():
    bot.infinity_polling()

if __name__ == '__main__':
    # تشغيل البوت في خيط منفصل (Background)
    threading.Thread(target=run_bot, daemon=True).start()
    
    # تشغيل الموقع (الذي يحتاجه Render ليعتبر الخدمة حية)
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
