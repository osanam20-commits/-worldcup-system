import telebot
import requests
import time
import threading
import logging
from flask import Flask, request
from datetime import datetime
import json
import os

# --- إعدادات التسجيل (Logging) ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- الإعدادات ---
TOKEN = "8689943788:AAHOD6jINGiV_g8wHYJ8eZ5SwO6_OLngoYE"
CHANNEL_ID = "-1004372754611"  # تأكد من أن البوت مشرف في القناة
NEWS_API_KEY = "3ceaa7be00msha38c948056a4052p1fd973jsn92dcc1392590"

# --- تهيئة البوت والتطبيق ---
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- متغيرات التحكم ---
posting_active = True
last_post_time = 0

# --- دالة التحقق من صحة الإعدادات ---
def validate_settings():
    """التحقق من صحة الإعدادات قبل بدء التشغيل"""
    errors = []
    
    if TOKEN == "توكن_بوتك":
        errors.append("❌ لم يتم تعيين توكن البوت")
    
    if NEWS_API_KEY == "مفتاحك_الخاص":
        errors.append("❌ لم يتم تعيين مفتاح API")
    
    if not CHANNEL_ID.startswith("-100"):
        errors.append("⚠️ تأكد من أن معرف القناة صحيح (يبدأ بـ -100)")
    
    if errors:
        for error in errors:
            logger.error(error)
        return False
    return True

# --- المسار الرئيسي ---
@app.route('/')
def home():
    return {
        "status": "online",
        "message": "البوت يعمل بنجاح!",
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "version": "2.0"
    }

# --- مسار التحقق من صحة البوت ---
@app.route('/health')
def health_check():
    return {
        "status": "healthy",
        "bot": "running",
        "webhook": "active",
        "last_post": datetime.fromtimestamp(last_post_time).strftime("%Y-%m-%d %H:%M:%S") if last_post_time > 0 else "Never"
    }

# --- مسار الويب هوك ---
@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    try:
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "OK", 200
    except Exception as e:
        logger.error(f"خطأ في معالجة الويب هوك: {e}")
        return "Error", 500

# --- دالة جلب الأحداث الرياضية (مطورة) ---
def get_sports_events():
    """جلب الأحداث الرياضية مع معالجة أفضل للأخطاء"""
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    querystring = {
        "league": "39",  # الدوري الإنجليزي
        "season": "2025",
        "live": "all"
    }
    headers = {
        "x-rapidapi-key": NEWS_API_KEY,
        "x-rapidapi-host": "api-football-v1.p.rapidapi.com"
    }
    
    try:
        logger.info("جاري جلب البيانات من API...")
        response = requests.get(url, headers=headers, params=querystring, timeout=30)
        response.raise_for_status()  # رفع استثناء للكود غير 200
        
        data = response.json()
        
        if not data.get('response'):
            return "⚽ **لا توجد مباريات مباشرة حالياً** في الدوري الإنجليزي.\n\n🔄 سيتم التحديث تلقائياً."

        matches = data['response']
        if not matches:
            return "⚽ **لا توجد مباريات مباشرة حالياً** في الدوري الإنجليزي.\n\n🔄 سيتم التحديث تلقائياً."

        # تنسيق الرسالة
        msg = f"⚽ **أحداث رياضية مباشرة**\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n{'='*30}\n\n"
        
        for match in matches[:5]:  # عرض أول 5 مباريات
            home_team = match['teams']['home']['name']
            away_team = match['teams']['away']['name']
            home_goals = match['goals']['home'] if match['goals']['home'] is not None else 0
            away_goals = match['goals']['away'] if match['goals']['away'] is not None else 0
            status = match['fixture']['status']['short']
            elapsed = match['fixture']['status']['elapsed'] if match['fixture']['status'].get('elapsed') else 0
            
            # تحديد حالة المباراة
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
        
        msg += "🔄 **سيتم التحديث تلقائياً بعد 30 دقيقة**"
        logger.info(f"تم جلب {len(matches)} مباريات بنجاح")
        return msg
        
    except requests.exceptions.Timeout:
        error_msg = "⏰ **انتهى وقت الاتصال**\nيرجى المحاولة لاحقاً."
        logger.error("Timeout في جلب البيانات")
        return error_msg
        
    except requests.exceptions.RequestException as e:
        error_msg = f"❌ **خطأ في الاتصال**\n{str(e)}"
        logger.error(f"خطأ في الاتصال: {e}")
        return error_msg
        
    except json.JSONDecodeError as e:
        error_msg = "❌ **خطأ في تحليل البيانات**"
        logger.error(f"خطأ في تحليل JSON: {e}")
        return error_msg
        
    except Exception as e:
        error_msg = f"❌ **خطأ غير متوقع**\n{str(e)}"
        logger.error(f"خطأ غير متوقع: {e}")
        return error_msg

# --- دالة النشر التلقائي (مطورة) ---
def auto_post_news():
    """النشر التلقائي مع تحسينات"""
    global posting_active, last_post_time
    
    logger.info("بدء خدمة النشر التلقائي...")
    
    # انتظار ثواني قبل البدء
    time.sleep(10)
    
    while posting_active:
        try:
            logger.info("جاري نشر التحديث...")
            
            # جلب البيانات
            news = get_sports_events()
            
            # محاولة النشر مع إعادة المحاولة
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    bot.send_message(
                        CHANNEL_ID, 
                        news, 
                        parse_mode="Markdown",
                        disable_web_page_preview=True
                    )
                    last_post_time = time.time()
                    logger.info(f"تم النشر بنجاح (المحاولة {attempt + 1})")
                    break
                except Exception as e:
                    logger.warning(f"محاولة النشر {attempt + 1} فشلت: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(5)  # انتظار قبل إعادة المحاولة
                    else:
                        raise
            
        except Exception as e:
            logger.error(f"خطأ في دورة النشر: {e}")
            # إرسال رسالة خطأ إلى القناة
            try:
                error_msg = f"⚠️ **حدث خطأ في تحديث المباريات**\n\nسيتم المحاولة مرة أخرى في 30 دقيقة."
                bot.send_message(CHANNEL_ID, error_msg, parse_mode="Markdown")
            except:
                pass
        
        # انتظار 30 دقيقة بدلاً من ساعة للتحديث الأسرع
        logger.info("انتظار 30 دقيقة للنشر التالي...")
        time.sleep(1800)  # 30 دقيقة

# --- أوامر البوت ---
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = """
🤖 **مرحباً بك في بوت المباريات!**

📋 **الأوامر المتاحة:**
/start - عرض هذه الرسالة
/help - عرض المساعدة
/live - عرض المباريات المباشرة
/status - حالة البوت

📊 **مميزات البوت:**
• تحديث تلقائي كل 30 دقيقة
• عرض المباريات المباشرة في الدوري الإنجليزي
• إشعارات فورية للأهداف والبطاقات

⚽ **استمتع بمتابعة المباريات!**
"""
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(commands=['live'])
def send_live_matches(message):
    """إرسال المباريات المباشرة عند الطلب"""
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        news = get_sports_events()
        bot.reply_to(message, news, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"خطأ في أمر live: {e}")
        bot.reply_to(message, "❌ حدث خطأ في جلب البيانات، حاول مرة أخرى.")

@bot.message_handler(commands=['status'])
def send_status(message):
    """عرض حالة البوت"""
    status_text = f"""
📊 **حالة البوت**

✅ الحالة: يعمل
📅 آخر تحديث: {datetime.fromtimestamp(last_post_time).strftime('%Y-%m-%d %H:%M:%S') if last_post_time > 0 else 'لم يتم النشر بعد'}
🔄 النشر التلقائي: نشط
⏰ التالي: خلال 30 دقيقة
📡 عدد المتابعين: {bot.get_chat_members_count(CHANNEL_ID)}
"""
    bot.reply_to(message, status_text, parse_mode="Markdown")

# --- التشغيل الرئيسي ---
if __name__ == '__main__':
    # التحقق من الإعدادات
    if not validate_settings():
        logger.error("فشل التحقق من الإعدادات. تأكد من تعيين جميع المتغيرات.")
        exit(1)
    
    # الحصول على رابط السيرفر (من متغيرات البيئة أو استخدام القيمة الافتراضية)
    server_url = os.environ.get('RENDER_URL', 'https://wor-ldcup-system.onrender.com')
    
    try:
        # إعداد الويب هوك
        logger.info("جاري إعداد الويب هوك...")
        bot.remove_webhook()
        webhook_url = f"{server_url}/{TOKEN}"
        bot.set_webhook(url=webhook_url)
        logger.info(f"تم تعيين الويب هوك على: {webhook_url}")
        
        # تشغيل خيط النشر التلقائي
        posting_thread = threading.Thread(target=auto_post_news, daemon=True)
        posting_thread.start()
        logger.info("تم بدء خيط النشر التلقائي")
        
        # تشغيل التطبيق
        port = int(os.environ.get('PORT', 10000))
        logger.info(f"تشغيل التطبيق على المنفذ {port}")
        app.run(host='0.0.0.0', port=port, debug=False)
        
    except Exception as e:
        logger.error(f"خطأ في تشغيل البوت: {e}")
        exit(1)
