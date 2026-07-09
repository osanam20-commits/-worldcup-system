import os
import telebot
import threading
from flask import Flask

TOKEN = "8689943788:AAFfmE62a4h-eLXYAcOXvSUgmkLs5KZZwts"
CHANNEL_ID = "-1004372754611"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- أوامر الدوريات ---

@bot.message_handler(commands=['leagues'])
def leagues_list(message):
    text = """
🏆 **متابعة الدوريات والبطولات:**
/wc - أخبار كأس العالم
/yemen - الدوري اليمني
/epl - الدوري الإنجليزي
/laliga - الدوري الإسباني
/ucl - دوري أبطال أوروبا
"""
    bot.reply_to(message, text, parse_mode="Markdown")

@bot.message_handler(commands=['wc'])
def wc(message):
    bot.reply_to(message, "🌍 **كأس العالم:** \n(قم بتحديث هذه النتائج يدوياً في الكود)")

@bot.message_handler(commands=['yemen'])
def yemen(message):
    bot.reply_to(message, "⚽ **الدوري اليمني:** \n(تحديث النتائج...)")

@bot.message_handler(commands=['ucl'])
def ucl(message):
    bot.reply_to(message, "🏆 **دوري أبطال أوروبا:** \n(النتائج والمواجهات...)")

@bot.message_handler(commands=['epl'])
def epl(message):
    bot.reply_to(message, "🏴󠁧󠁢󠁥󠁮󠁧󠁿 **الدوري الإنجليزي:** \n(نتائج البريميرليج...)")

# --- أمر النشر الاحترافي ---

@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    text = message.text.replace('/broadcast', '').strip()
    if text:
        bot.send_message(CHANNEL_ID, f"📢 {text}")
        bot.reply_to(message, "✅ تم النشر!")
    else:
        bot.reply_to(message, "⚠️ اكتب الخبر بعد الأمر.")

# --- تشغيل الموقع ---
@app.route('/')
def home():
    return "البوت يعمل!"

if __name__ == '__main__':
    threading.Thread(target=lambda: bot.infinity_polling(none_stop=True), daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
