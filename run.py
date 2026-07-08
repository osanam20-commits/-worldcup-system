import os
import logging
import threading
from flask import Flask, render_template_string
from datetime import datetime
import telebot

# إعدادات التطبيق
app = Flask(__name__)
# ضع التوكن الخاص بك هنا بين علامات التنصيص
BOT_TOKEN = "8689943788:AAFfmE62a4h-eLXYAcOXvSUgmkLs5KZZwts"
CHANNEL_ID = "-1004372754611"

bot = telebot.TeleBot(BOT_TOKEN)

# دالة بسيطة لتنسيق جدول المباريات
def get_match_text():
    return "⚽ *جدول مباريات اليوم*\n\n✅ البوت يعمل بشكل ممتاز!\n\nيمكنك تخصيص هذا الجدول كما تريد."

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "مرحباً! البوت يعمل الآن.")

@bot.message_handler(commands=['today'])
def today(message):
    bot.reply_to(message, get_match_text(), parse_mode='Markdown')

@bot.message_handler(commands=['send'])
def send(message):
    try:
        bot.send_message(CHANNEL_ID, get_match_text(), parse_mode='Markdown')
        bot.reply_to(message, "✅ تم النشر في القناة بنجاح!")
    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ: {e}")

# صفحة ويب لكي لا تتوقف Render عن العمل
@app.route('/')
def home():
    return "<h1>Bot is running!</h1>"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    # تشغيل Flask في الخلفية
    threading.Thread(target=run_flask, daemon=True).start()
    # تشغيل البوت
    print("Bot is starting...")
    bot.infinity_polling()
