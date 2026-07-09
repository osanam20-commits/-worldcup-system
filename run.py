import telebot
import requests
import schedule
import time
import threading
from flask import Flask

# إعداداتك
TOKEN = "8689943788:AAFfmE62a4h-eLXYAcOXvSUgmkLs5KZZwts"
API_KEY = "https://football-prediction-api.p.rapidapi.com/api/v2/predictions?market=classic&iso_date=2018-12-01&federation=UEFA" # ضع المفتاح الكامل الذي نسخته هنا
CHANNEL_ID = "-1004372754611"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

def get_live_scores():
    # هذا الرابط هو الخاص بـ RapidAPI
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures?live=all"
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "api-football-v1.p.rapidapi.com"
    }
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        
        # التأكد من وجود مباريات
        if not data.get('response'):
            return None
            
        msg = "⚽ **نتائج المباريات الحية الآن:**\n\n"
        for fixture in data['response']:
            home = fixture['teams']['home']['name']
            away = fixture['teams']['away']['name']
            score = f"{fixture['goals']['home']} - {fixture['goals']['away']}"
            msg += f"• {home} {score} {away}\n"
        return msg
    except:
        return None

def auto_post():
    news = get_live_scores()
    if news:
        bot.send_message(CHANNEL_ID, news)

# جدول النشر (كل 30 دقيقة مثلاً)
schedule.every(30).minutes.do(auto_post)

def scheduler_thread():
    while True:
        schedule.run_pending()
        time.sleep(1)

# تشغيل المجدول في الخلفية
threading.Thread(target=scheduler_thread, daemon=True).start()

@app.route('/')
def home():
    return "البوت يعمل بكفاءة مع RapidAPI!"

if __name__ == '__main__':
    bot.infinity_polling()
