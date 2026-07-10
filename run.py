import os
import telebot
from flask import Flask, request

TOKEN = "8689943788:AAHOD6jINGiV_g8wHYJ8eZ5SwO6_OLngoYE"
CHANNEL_ID = "-1004372754611"
URL = "https://wor-ldcup-system.onrender.com/" # استبدل اسم-مشروعك برابط موقعك الحقيقي على Render

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- دالة استقبال الرسائل ---
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "تم استلام رسالتك!")
@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

# --- إعداد الويب هوك ---
bot.remove_webhook()
bot.set_webhook(url=URL + TOKEN)

@app.route('/')
def home():
    return "البوت يعمل بنظام Webhook!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
