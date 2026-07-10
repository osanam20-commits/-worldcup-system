import telebot
import requests
from flask import Flask
from threading import Thread
import time

TOKEN = "8689943788:AAFfmE62a4h-eLXYAcOXvSUgmkLs5KZZwts"
CHANNEL_ID = "-1004372754611"
# استخدم مفتاحاً خاصاً بـ API أخبار بدلاً من API التوقعات
NEWS_API_KEY = "3ceaa7be00msha38c948056a4052p1fd973jsn92dcc1392590' "

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "البوت يعمل بكفاءة!"

def get_sports_news():
    # هذا الرابط كمثال، يجب تغييره حسب الـ API الذي ستختاره من RapidAPI
    url = "https://sport-news-api.p.rapidapi.com/get-news"
    headers = {
        "x-rapidapi-key": NEWS_API_KEY,
        "x-rapidapi-host": "sport-news-api.p.rapidapi.com"
    }
    try:
        response = requests.get(url, headers=headers)
        return response.json()
    except Exception as e:
        print(f"خطأ في جلب الأخبار: {e}")
        return None

def auto_post_news():
    while True:
        data = get_sports_news()
        if data and 'articles' in data:
            # نشر أول خبر في القائمة
            article = data['articles'][0]
            msg = f"📰 {article['title']}\n\n{article['summary']}\n\nالمصدر: {article['url']}"
            bot.send_message(CHANNEL_ID, msg)
        
        # النشر كل ساعتين (7200 ثانية)
        time.sleep(7200)

def run_bot():
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)

if __name__ == '__main__':
    Thread(target=run_bot).start()
    Thread(target=auto_post_news).start()
    app.run(host='0.0.0.0', port=10000)
