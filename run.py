import telebot
import requests
import time
import threading
from flask import Flask, request

TOKEN = "8689943788:AAHOD6jINGiV_g8wHYJ8eZ5SwO6_OLngoYE"
CHANNEL_ID = "-1004372754611"
NEWS_API_KEY = "3ceaa7be00msha38c948056a4052p1fd973jsn92dcc1392590" # تأكد أنه مفتاح API-Football

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

def get_sports_events():
    # هذا الرابط يجلب مباريات اليوم للدوري الإنجليزي كمثال (يمكنك تغيير league)
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    querystring = {"league":"39","season":"2025","live":"all"} # live="all" يجلب المباريات المباشرة
    headers = {
        "x-rapidapi-key": NEWS_API_KEY,
        "x-rapidapi-host": "api-football-v1.p.rapidapi.com"
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring)
        data = response.json()
        
        if not data['response']:
            return "⚽ لا توجد مباريات مباشرة حالياً."

        # تنسيق الخبر بشكل احترافي
        msg = "⚽ **أحداث رياضية مباشرة:**\n\n"
        for match in data['response'][:3]: # يجلب أول 3 مباريات فقط لعدم إطالة الرسالة
            home = match['teams']['home']['name']
            away = match['teams']['away']['name']
            status = match['fixture']['status']['short']
            msg += f"🏟 {home} vs {away}\nالنتيجة: {match['goals']['home']} - {match['goals']['away']}\nالحالة: {status}\n\n"
        return msg
    except Exception as e:
        return f"خطأ في جلب البيانات: {e}"

def auto_post_news():
    while True:
        news = get_sports_events()
        bot.send_message(CHANNEL_ID, news, parse_mode="Markdown")
        time.sleep(3600) # ينشر كل ساعة

# --- إعدادات الويب هوك ---
@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

bot.remove_webhook()
bot.set_webhook(url='https://wor-ldcup-system.onrender.com/' + TOKEN)

if __name__ == '__main__':
    threading.Thread(target=auto_post_news, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
