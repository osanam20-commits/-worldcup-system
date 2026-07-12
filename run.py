import telebot
import requests
import time
import threading
from flask import Flask, request

# --- الإعدادات ---
TOKEN = "8689943788:AAHOD6jINGiV_g8wHYJ8eZ5SwO6_OLngoYE"
CHANNEL_ID = "-1004372754611"
NEWS_API_KEY = "3ceaa7be00msha38c948056a4052p1fd973jsn92dcc1392590" 

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- المسار الرئيسي (لمنع خطأ 404) ---
@app.route('/')
def home():
    return "البوت يعمل بنجاح ومستعد للنشر!"

# --- مسار الويب هوك لاستقبال أوامر تيليجرام ---
@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

# --- دالة جلب الأحداث الرياضية ---
def get_sports_events():
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    querystring = {"league":"39","season":"2025","live":"all"} 
    headers = {
        "x-rapidapi-key": NEWS_API_KEY,
        "x-rapidapi-host": "api-football-v1.p.rapidapi.com"
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring)
        data = response.json()
        
        if not data.get('response'):
            return "⚽ لا توجد مباريات مباشرة حالياً في الدوري الإنجليزي."

        msg = "⚽ **أحداث رياضية مباشرة:**\n\n"
        for match in data['response'][:3]: 
            home = match['teams']['home']['name']
            away = match['teams']['away']['name']
            home_goals = match['goals']['home']
            away_goals = match['goals']['away']
            status = match['fixture']['status']['short']
            msg += f"🏟 {home} vs {away}\nالنتيجة: {home_goals} - {away_goals}\nالحالة: {status}\n\n"
        return msg
    except Exception as e:
        return f"خطأ في جلب البيانات: {e}"

# --- دالة النشر التلقائي ---
def auto_post_news():
    while True:
        try:
            news = get_sports_events()
            bot.send_message(CHANNEL_ID, news, parse_mode="Markdown")
        except Exception as e:
            print(f"خطأ في النشر التلقائي: {e}")
        time.sleep(3600) # ينشر كل ساعة

# --- التشغيل ---
if __name__ == '__main__':
    # إعداد الويب هوك
    bot.remove_webhook()
    bot.set_webhook(url='https://wor-ldcup-system.onrender.com/' + TOKEN)
    
    # تشغيل خيط النشر التلقائي في الخلفية
    threading.Thread(target=auto_post_news, daemon=True).start()
    
    # تشغيل تطبيق Flask
    app.run(host='0.0.0.0', port=10000)
