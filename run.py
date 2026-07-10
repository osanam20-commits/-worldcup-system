import telebot
import requests
import threading
from flask import Flask
from time import sleep
from datetime import datetime

# --- الإعدادات ---
TOKEN = "8689943788:AAFfmE62a4h-eLXYAcOXvSUgmkLs5KZZwts"
CHANNEL_ID = "-1004372754611"
API_KEY = "https://football-prediction-api.p.rapidapi.com/api/v2/predictions?market=classic&iso_date=2026-07-09&federation=UEFA"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- المسار لـ Render ---
@app.route('/')
def home():
    return "البوت يعمل بكفاءة!"

# --- أمر للتأكد من عمل البوت ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك! أنا جاهز لنشر التوقعات الرياضية.")

# --- دالة جلب البيانات من API ---
def get_predictions():
    url = "https://football-prediction-api.p.rapidapi.com/api/v2/predictions"
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "football-prediction-api.p.rapidapi.com"
    }
    params = {"market": "classic", "iso_date": datetime.now().strftime('%Y-%m-%d')}
    try:
        response = requests.get(url, headers=headers, params=params)
        return response.json()
    except Exception as e:
        print(f"خطأ API: {e}")
        return None

# --- مهمة النشر التلقائي ---
def auto_post_task():
    while True:
        data = get_predictions()
        if data and 'data' in data and len(data['data']) > 0:
            match = data['data'][0]
            msg = f"⚽ توقعات اليوم:\n{match['home_team']} vs {match['away_team']}\nالنتيجة: {match.get('prediction', 'غير متوفرة')}"
            try:
                bot.send_message(CHANNEL_ID, msg)
                print("تم النشر بنجاح!")
            except Exception as e:
                print(f"خطأ في النشر (تأكد أن البوت Admin في القناة): {e}")
        
        sleep(21600) # النشر كل 6 ساعات

# --- التشغيل ---
def run_bot():
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)

if __name__ == '__main__':
    threading.Thread(target=run_bot).start()
    threading.Thread(target=auto_post_task).start()
    app.run(host='0.0.0.0', port=10000)
