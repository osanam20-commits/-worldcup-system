import os
import telebot
import threading
from flask import Flask

# --- الإعدادات ---
TOKEN = "8689943788:AAFfmE62a4h-eLXYAcOXvSUgmkLs5KZZwts"
CHANNEL_ID = "-1004372754611"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- وظيفة تشغيل البوت ---
def run_bot():
    try:
        bot.remove_webhook()
        bot.infinity_polling(none_stop=True)
    except Exception as e:
        print(f"Error in polling: {e}")

# تشغيل البوت في خيط (Thread) منفصل
threading.Thread(target=run_bot, daemon=True).start()

# --- أوامر البوت ---

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "مرحباً! أنا بوت إدارة القناة. أرسل /help لرؤية الأوامر.")

@bot.message_handler(commands=['help'])
def help_cmd(message):
    help_text = """
📋 قائمة الأوامر:
/broadcast [النص] - نشر خبر في القناة
/leagues - عرض قائمة البطولات
/poll [السؤال] - إنشاء استطلاع رأي
/channel - رابط القناة
"""
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    text = message.text.replace('/broadcast', '').strip()
    if text:
        try:
            bot.send_message(CHANNEL_ID, f"📢 {text}")
            bot.reply_to(message, "✅ تم النشر في القناة بنجاح!")
        except Exception as e:
            bot.reply_to(message, f"❌ خطأ: تأكد أن البوت مشرف في القناة.\nالخطأ: {e}")
    else:
        bot.reply_to(message, "⚠️ يرجى كتابة الخبر بعد الأمر.")

@bot.message_handler(commands=['leagues'])
def leagues_list(message):
    text = "🏆 **البطولات المتاحة:**\n/wc - كأس العالم\n/yemen - الدوري اليمني\n/epl - الدوري الإنجليزي\n/ucl - أبطال أوروبا"
    bot.reply_to(message, text, parse_mode="Markdown")

@bot.message_handler(commands=['poll'])
def poll(message):
    bot.send_poll(message.chat.id, "ما توقعك للمباراة القادمة؟", ["فوز", "خسارة", "تعادل"])

@bot.message_handler(commands=['channel'])
def channel(message):
    bot.reply_to(message, f"🔗 رابط القناة: https://t.me/c/{str(CHANNEL_ID)[4:]}")

# --- جزء الـ Flask للويب ---
@app.route('/')
def home():
    return "Bot is running perfectly!"
