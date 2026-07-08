import os
import telebot
from flask import Flask

# 1. إعدادات البوت
TOKEN = "8689943788:AAFfmE62a4h-eLXYAcOXvSUgmkLs5KZZwts"
CHANNEL_ID = "-1004372754611"
bot = telebot.TeleBot(TOKEN)

# 2. إعدادات الموقع
app = Flask(__name__)

@app.route('/')
def home():
    return "البوت يعمل الآن!"

# 3. أوامر البوت
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "✅ البوت يعمل من داخل Render!")

@bot.message_handler(commands=['today'])
def today(message):
    bot.reply_to(message, "⚽ لا توجد مباريات اليوم.")

@bot.message_handler(commands=['send'])
def send(message):
    try:
        bot.send_message(CHANNEL_ID, "📢 اختبار نشر من البوت.")
        bot.reply_to(message, "✅ تم النشر!")
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ: {e}")

# 4. التشغيل المدمج (هذا هو سر النجاح)
if __name__ == '__main__':
    # تشغيل البوت في الخلفية
    import threading
    threading.Thread(target=bot.infinity_polling, daemon=True).start()
    
    # تشغيل الموقع (الذي يمنع إغلاق السيرفر)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
