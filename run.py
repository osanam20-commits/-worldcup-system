import os
import telebot
import requests
import time
from flask import Flask
from threading import Thread

# --- الإعدادات (يفضل وضعها في Environment Variables في Render) ---
TOKEN = "8689943788:AAFfmE62a4h-eLXYAcOXvSUgmkLs5KZZwts"
CHANNEL_ID = "-1004372754611"
# استخدم مفتاحك الخاص بـ API الأخبار
NEWS_API_KEY = "curl --request GET \
	--url https://nfl-football-api.p.rapidapi.com/nfl-leagueinfo \
	--header 'Content-Type: application/json' \
	--header 'x-rapidapi-host: nfl-football-api.p.rapidapi.com' \
	--header 'x-rapidapi-key: 3ceaa7be00msha38c948056a4052p1fd973jsn92dcc1392590'"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "البوت يعمل بكفاءة!"

# --- دالة جلب الأخبار ---
def get_sports_news():
    # هذا رابط مثال، استبدله بالرابط الموثق من موقع API الأخبار الذي اشتركت فيه
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

# --- دالة النشر التلقائي ---
def auto_post_news():
    while True:
        data = get_sports_news()
        if data and 'articles' in data and len(data['articles']) > 0:
            article = data['articles'][0]
            msg = f"📰 {article.get('title', 'خبر رياضي')}\n\n{article.get('summary', 'تفاصيل الخبر متاحة عبر الرابط')}\n\n🔗 {article.get('url', '')}"
            try:
                bot.send_message(CHANNEL_ID, msg)
                print("تم نشر خبر جديد!")
            except Exception as e:
                print(f"خطأ في النشر (تأكد أن البوت Admin): {e}")
        
        # الانتظار ساعتين قبل النشر مرة أخرى
        time.sleep(7200)

# --- دالة تشغيل البوت (مضادة للتعارض) ---
def run_bot():
    print("جاري تشغيل البوت...")
    # إزالة أي Webhook قديم أو اتصالات معلقة
    try:
        bot.delete_webhook()
    except:
        pass
    # skip_pending=True هي السر في منع خطأ 409
    bot.infinity_polling(none_stop=True, skip_pending=True)

if __name__ == '__main__':
    # تشغيل البوت والنشر في مسارات منفصلة
    Thread(target=run_bot).start()
    Thread(target=auto_post_news).start()
    app.run(host='0.0.0.0', port=10000)
