import telebot
import requests
from flask import Flask, request

TOKEN = "8689943788:AAHOD6jINGiV_g8wHYJ8eZ5SwO6_OLngoYE"
CHANNEL_ID = "-1004372754611" # تأكد أنه يبدأ بـ -100
NEWS_API_KEY = "curl --request GET \
	--url https://nfl-football-api.p.rapidapi.com/nfl-leagueinfo \
	--header 'Content-Type: application/json' \
	--header 'x-rapidapi-host: nfl-football-api.p.rapidapi.com' \
	--header 'x-rapidapi-key: 3ceaa7be00msha38c948056a4052p1fd973jsn92dcc1392590'" # تأكد من وضعه هنا

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- دالة جلب الأخبار ---
def fetch_news():
    url = "https://nfl-football-api.p.rapidapi.com/nfl-leagueinfo" # رابط الـ API
    headers = {
        "x-rapidapi-key": NEWS_API_KEY,
        "x-rapidapi-host": "nfl-football-api.p.rapidapi.com"
    }
    try:
        response = requests.get(url, headers=headers)
        return response.json()
    except Exception as e:
        return None

# --- دالة الأمر /wc ---
@bot.message_handler(commands=['wc'])
def send_news(message):
    bot.reply_to(message, "جاري جلب آخر الأخبار ونشرها في القناة...")
    news_data = fetch_news()
    if news_data:
        # هنا تضع صيغة الخبر حسب ما يرجعه الـ API الخاص بك
        news_text = f"⚽ خبر جديد:\n{str(news_data)}" 
        bot.send_message(CHANNEL_ID, news_text)
    else:
        bot.reply_to(message, "فشل جلب الأخبار، تأكد من مفتاح الـ API.")

# --- إعداد الويب هوك ---
@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

bot.remove_webhook()
bot.set_webhook(url='https://wor-ldcup-system.onrender.com/' + TOKEN)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
