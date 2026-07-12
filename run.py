import telebot
import requests
import time
import threading
import logging
from flask import Flask, request
from datetime import datetime
import json
import os

# --- إعدادات التسجيل ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- الإعدادات ---
TOKEN = "8689943788:AAHOD6jINGiV_g8wHYJ8eZ5SwO6_OLngoYE"
CHANNEL_ID = "-1004372754611"
NEWS_API_KEY = "3ceaa7be00msha38c948056a4052p1fd973jsn92dcc1392590"

# --- تهيئة البوت والتطبيق ---
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- متغيرات التحكم ---
posting_active = True
last_post_time = 0

# --- دالة جلب الأحداث الرياضية ---
def get_sports_events():
    """جلب الأحداث الرياضية مع معالجة الأخطاء"""
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    querystring = {
        "league": "39",
        "season": "2025",
        "live": "all"
    }
    headers = {
        "x-rapidapi-key": NEWS_API_KEY,
        "x-rapidapi-host": "api-football-v1.p.rapidapi.com"
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if not data.get('response'):
            return "⚽ **لا توجد مباريات مباشرة حالياً** في الدوري الإنجليزي."

        matches = data['response']
        if not matches:
            return "⚽ **لا توجد مباريات مباشرة حالياً** في الدوري الإنجليزي."

        msg = f"⚽ **أحداث رياضية مباشرة**\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n{'='*30}\n\n"
        
        for match in matches[:5]:
            home_team = match['teams']['home']['name']
            away_team = match['teams']['away']['name']
            home_goals = match['goals']['home'] if match['goals']['home'] is not None else 0
            away_goals = match['goals']['away'] if match['goals']['away'] is not None else 0
            status = match['fixture']['status']['short']
            elapsed = match['fixture']['status'].get('elapsed', 0)
            
            if status == 'HT':
                status_text = "⏸️ استراحة"
            elif status == 'FT':
                status_text = "🏁 انتهت"
            elif status == 'PST':
                status_text = "⏰ مؤجلة"
            else:
                status_text = f"⏱️ الدقيقة {elapsed}" if elapsed > 0 else "🎯 جارية"
            
            msg += f"🏟️ **{home_team}** vs **{away_team}**\n"
            msg += f"⚽ النتيجة: {home_goals} - {away_goals}\n"
            msg += f"📊 الحالة: {status_text}\n\n"
        
        msg += "🔄 **سيتم التحديث تلقائياً**"
        return msg
        
    except Exception as e:
        logger.error(f"خطأ في جلب البيانات: {e}")
        return f"❌ **خطأ في جلب البيانات**\n{str(e)}"

# --- دالة النشر التلقائي ---
def auto_post_news():
    """النشر التلقائي للمباريات"""
    global last_post_time
    
    logger.info("بدء خدمة النشر التلقائي...")
    time.sleep(5)
    
    while posting_active:
        try:
            news = get_sports_events()
            
            # محاولة النشر مع إعادة المحاولة
            for attempt in range(3):
                try:
                    bot.send_message(
                        CHANNEL_ID, 
                        news, 
                        parse_mode="Markdown",
                        disable_web_page_preview=True
                    )
                    last_post_time = time.time()
                    logger.info("تم النشر بنجاح")
                    break
                except Exception as e:
                    logger.warning(f"محاولة {attempt + 1} فشلت: {e}")
                    if attempt < 2:
                        time.sleep(5)
                    else:
                        raise
            
        except Exception as e:
            logger.error(f"خطأ في دورة النشر: {e}")
        
        logger.info("انتظار 30 دقيقة...")
        time.sleep(1800)

# --- مسارات Flask ---
@app.route('/')
def home():
    return {
        "status": "online",
        "message": "البوت يعمل بنجاح",
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

@app.route('/health')
def health_check():
    return {
        "status": "healthy",
        "last_post": datetime.fromtimestamp(last_post_time).strftime("%Y-%m-%d %H:%M:%S") if last_post_time > 0 else "Never"
    }

@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    try:
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "OK", 200
    except Exception as e:
        logger.error(f"خطأ في الويب هوك: {e}")
        return "Error", 500

# --- أوامر البوت ---
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, """
🤖 **مرحباً بك في بوت المباريات!**

📋 **الأوامر المتاحة:**
/start - عرض هذه الرسالة
/help - عرض المساعدة
/live - عرض المباريات المباشرة

⚽ **استمتع بمتابعة المباريات!**
""", parse_mode="Markdown")

@bot.message_handler(commands=['live'])
def send_live_matches(message):
    news = get_sports_events()
    bot.reply_to(message, news, parse_mode="Markdown")

# --- التشغيل الرئيسي ---
if __name__ == '__main__':
    # إعداد الويب هوك
    server_url = os.environ.get('RENDER_URL', 'https://wor-ldcup-system.onrender.com')
    webhook_url = f"{server_url}/{TOKEN}"
    
    try:
        bot.remove_webhook()
        bot.set_webhook(url=webhook_url)
        logger.info(f"تم تعيين الويب هوك: {webhook_url}")
        
        # تشغيل خيط النشر التلقائي
        threading.Thread(target=auto_post_news, daemon=True).start()
        
        # تشغيل التطبيق
        port = int(os.environ.get('PORT', 10000))
        app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
        
    except Exception as e:
        logger.error(f"خطأ في التشغيل: {e}")
