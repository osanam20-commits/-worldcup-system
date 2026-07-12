import telebot
import requests
import time
import threading
from flask import Flask, request

TOKEN = "8689943788:AAHOD6jINGiV_g8wHYJ8eZ5SwO6_OLngoYE"
CHANNEL_ID = "-1004372754611"
NEWS_API_KEY = "3ceaa7be00msha38c948056a4052p1fd973jsn92dcc1392590"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- دالة جلب ونشر الأخبار ---
def auto_post_news():
    while True:
        url = "https://nfl-football-api.p.rapidapi.com/nfl-leagueinfo"
        headers = {
            "x-rapidapi-key": NEWS_API_KEY,
            "x-rapidapi-host": "nfl-football-api.p.rapidapi.com"
        }
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                league_name = data.get('displayName', 'غير معروف')
                msg = f"⚽ تحديث تلقائي للدوري:\nالدوري: {league_name}"
                bot.send_message(CHANNEL_ID, msg)
        except Exception as e:
            print(f"خطأ في النشر التلقائي: {e}")
        
        # ينشر كل 3600 ثانية (ساعة واحدة). يمكنك تغيير الرقم حسب الرغبة.
        time.sleep(3600) 

# --- المسارات ---
@app.route('/')
def home():
    return "البوت يعمل (نظام النشر التلقائي نشط)!"

@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

# إعداد الويب هوك
bot.remove_webhook()
bot.set_webhook(url='https://wor-ldcup-system.onrender.com/' + TOKEN)

if __name__ == '__main__':
    # تشغيل النشر التلقائي في خيط منفصل (Thread)
    threading.Thread(target=auto_post_news, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
