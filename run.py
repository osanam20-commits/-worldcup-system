import telebot
import requests
from flask import Flask
from threading import Thread
import time
from datetime import datetime # مكتبة لجلب التاريخ تلقائياً

# --- الإعدادات ---
TOKEN = "8689943788:AAFfmE62a4h-eLXYAcOXvSUgmkLs5KZZwts"
CHANNEL_ID = "-1004372754611"
API_KEY = "https://football-prediction-api.p.rapidapi.com/api/v2/predictions?market=classic&iso_date=2026-07-09&federation=UEFA" 

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "البوت يعمل بكفاءة!"

# --- دالة جلب التوقعات بتاريخ اليوم تلقائياً ---
def get_football_predictions():
    # جلب تاريخ اليوم تلقائياً بصيغة YYYY-MM-DD
    today = datetime.now().strftime('%Y-%m-%d')
    
    url = "https://football-prediction-api.p.rapidapi.com/api/v2/predictions"
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "football-prediction-api.p.rapidapi.com"
    }
    params = {"market": "classic", "iso_date": today}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        return response.json()
    except Exception as e:
        print(f"خطأ في الاتصال بـ API: {e}")
        return None

# --- دالة النشر التلقائي ---
def auto_post():
    while True:
        data = get_football_predictions()
        if data and 'data' in data and len(data['data']) > 0:
            match = data['data'][0]
            msg = f"⚽ **توقعات اليوم {datetime.now().strftime('%Y-%m-%d')}:**\n\n{match.get('home_team')} vs {match.get('away_team')}"
            bot.send_message(CHANNEL_ID, msg)
        
        # النوم لمدة 24 ساعة ثم التكرار
        time.sleep(86400) 

def run_bot():
    bot.infinity_polling()

if __name__ == '__main__':
    Thread(target=run_bot).start()
    Thread(target=auto_post).start()
    app.run(host='0.0.0.0', port=10000)
