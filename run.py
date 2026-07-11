import telebot
import requests
from flask import Flask, request

TOKEN = "8689943788:AAHOD6jINGiV_g8wHYJ8eZ5SwO6_OLngoYE"
CHANNEL_ID = "-1004372754611"
NEWS_API_KEY = "https://wor-ldcup-system.onrender.com/"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- دالة جلب الأخبار ---
def fetch_news():
    url = "https://nfl-football-api.p.rapidapi.com/nfl-leagueinfo"
    headers = {
        "x-rapidapi-key": NEWS_API_KEY,
        "x-rapidapi-host": "nfl-football-api.p.rapidapi.com"
    }
    try:
        response = requests.get(url, headers=headers)
        # طباعة حالة الـ API في الـ Logs لمعرفة سبب فشل النشر
        print(f"API Response Status: {response.status_code}")
        return response.json()
    except Exception as e:
        print(f"API Error: {e}")
        return None

# --- الرد على الأوامر ---
@bot.message_handler(commands=['wc'])
def send_news(message):
    bot.reply_to(message, "جاري جلب البيانات من الـ API...")
    news_data = fetch_news()
    if news_data:
        try:
            # هنا يمكنك تنسيق النص كما تحب
            msg = f"⚽ معلومات الدوري:\n{str(news_data)[:1000]}" # قص النص ليناسب تيليجرام
            bot.send_message(CHANNEL_ID, msg)
            bot.reply_to(message, "تم النشر في القناة بنجاح!")
        except Exception as e:
            bot.reply_to(message, f"خطأ في النشر للقناة: {e}")
    else:
        bot.reply_to(message, "فشل جلب الأخبار من موقع الـ API.")

# --- المسارات ---
@app.route('/')
def home():
    return "البوت يعمل بنظام Webhook!"

@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

# إعداد الويب هوك عند التشغيل
bot.remove_webhook()
bot.set_webhook(url='https://wor-ldcup-system.onrender.com/' + TOKEN)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
