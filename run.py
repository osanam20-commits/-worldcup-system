import os
import telebot
import threading
from flask import Flask

TOKEN = "8689943788:AAFfmE62a4h-eLXYAcOXvSUgmkLs5KZZwts"
CHANNEL_ID = "-1004372754611"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- أوامر الإدارة ---

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "مرحباً بك في بوت إدارة القناة! استخدم /help لرؤية الأوامر.")

@bot.message_handler(commands=['help'])
def help_cmd(message):
    help_text = """
أوامر البوت:
/today - مباريات اليوم
/standings - ترتيب الفرق
/topscorers - هدافي البطولة
/next - المباراة القادمة
/news - آخر الأخبار
/channel - رابط القناة
/poll - إنشاء استطلاع رأي
/schedule - جدول المباريات القادمة
"""
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['today'])
def today(message):
    bot.reply_to(message, "⚽ جدول مباريات اليوم: لا توجد مباريات.")

@bot.message_handler(commands=['schedule'])
def schedule(message):
    # أمر عرض الجدول
    bot.reply_to(message, "📅 جدول المباريات القادمة:\n1. الفريق أ ضد الفريق ب - الساعة 8:00")

@bot.message_handler(commands=['poll'])
def poll(message):
    # أمر استطلاع الرأي
    bot.send_poll(message.chat.id, "من سيفوز في المباراة القادمة؟", ["الفريق أ", "الفريق ب", "تعادل"])

@bot.message_handler(commands=['news'])
def news(message):
    bot.reply_to(message, "📰 آخر الأخبار: البطولة تسير بشكل رائع!")

@bot.message_handler(commands=['channel'])
def channel(message):
    bot.reply_to(message, f"🔗 رابط القناة: https://t.me/c/{str(CHANNEL_ID)[4:]}")

# --- تشغيل البوت والموقع ---

@app.route('/')
def home():
    return "البوت يعمل!"

if __name__ == '__main__':
    threading.Thread(target=lambda: bot.infinity_polling(none_stop=True), daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
