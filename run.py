import telebot
import requests
from flask import Flask, request

# --- الإعدادات ---
TOKEN = "8689943788:AAHOD6jINGiV_g8wHYJ8eZ5SwO6_OLngoYE"
CHANNEL_ID = "-1004372754611"
NEWS_API_KEY = "3ceaa7be00msha38c948056a4052p1fd973jsn92dcc1392590" # ضع مفتاحك بدقة

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- دالة جلب الأخبار المعدلة ---
def fetch_news():
    url = "https://nfl-football-api.p.rapidapi.com/nfl-leagueinfo"
    headers = {
        "x-rapidapi-key": NEWS_API_KEY,
        "x-rapidapi-host": "nfl-football-api.p.rapidapi.com"
    }
    
    try:
        response = requests.get(url, headers=headers)
        # طباعة تفاصيل الطلب في الـ Logs
        print(f"--- حالة الاتصال: {response.status_code} ---")
        print(f"--- نص الرد: {response.text} ---")
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        print(f"خطأ في الاتصال: {e}")
        return None

# --- الأوامر ---
@bot.message_handler(commands=['wc'])
def send_news(message):
    bot.reply_to(message, "جاري محاولة الاتصال بالخادم...")
    news_data = fetch_news()
    
    if news_data:
        msg = f"⚽ أخبار الدوري:\n{str(news_data)[:1000]}"
        bot.send_message(CHANNEL_ID, msg)
        bot.reply_to(message, "تم النشر في القناة بنجاح!")
    else:
        bot.reply_to(message, "فشل جلب الأخبار. تأكد من الـ Logs في Render لرؤية سبب الخطأ.")

@app.route('/')
def home():
    return "البوت يعمل بنظام Webhook!"

@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

# --- تشغيل البوت ---
bot.remove_webhook()
bot.set_webhook(url='https://wor-ldcup-system.onrender.com/' + TOKEN)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
