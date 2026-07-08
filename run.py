import os
import telebot
from flask import Flask, request

TOKEN = os.environ.get("8689943788:AAFfmE62a4h-eLXYAcOXvSUgmkLs5KZZwts") # تأكد من وضعه في Environment
CHANNEL_ID = "-1004372754611"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/' + TOKEN, methods=['POST'])
def get_message():
    json_str = request.stream.read().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

@app.route('/')
def home():
    return "Bot is running!"

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "✅ البوت متصل عبر Webhook ويعمل!")

# قم بتشغيل هذا الرابط مرة واحدة في المتصفح بعد الـ Deploy:
# https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://wor-ldcup-system.onrender.com/<TOKEN>

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
