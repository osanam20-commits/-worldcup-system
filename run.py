import os
import logging
import threading
from flask import Flask, render_template_string
from datetime import datetime
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# ========== إعدادات البوت والقناة ==========
app = Flask(__name__)

# ضع التوكن ومعرف القناة هنا (أو استخدم متغيرات البيئة)
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8689943788:AAFfmE62a4h-eLXYAcOXvSUgmkLs5KZZwts")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@lvFaax5HzsxOTU0")

# ========== قاعدة البيانات ==========
matches_db = []
match_id = 1

def add_match(home, away, home_flag="🏴", away_flag="🏴", stadium="غير محدد", 
              time="00:00", stage="مباراة دورية", tournament="بطولة", 
              channel="beIN Sports", commentator="غير محدد"):
    global match_id
    
    # تحديد تاريخ المباراة ليكون تاريخ "اليوم" تلقائياً
    today_date = datetime.now().strftime("%Y-%m-%d")
    
    match = {
        'id': match_id,
        'home': home,
        'away': away,
        'home_flag': home_flag,
        'away_flag': away_flag,
        'stadium': stadium,
        'date': today_date,
        'time': time,
        'stage': stage,
        'tournament': tournament,
        'channel': channel,
        'commentator': commentator,
    }
    matches_db.append(match)
    match_id += 1
    return match

# ========== توليد المباريات (تتجدد برمجياً لتاريخ اليوم) ==========
def load_today_matches():
    global matches_db, match_id
    matches_db = []
    match_id = 1
    
    # 🏆 دوري أبطال أوروبا
    add_match("ريال مدريد", "مانشستر سيتي", "🇪🇸", "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "سانتياغو برنابيو", "22:00", "نصف النهائي", "دوري أبطال أوروبا", "beIN Sports 1", "عصام الشوالي")
    add_match("بايرن ميونخ", "أرسنال", "🇩🇪", "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "أليانز أرينا", "22:00", "نصف النهائي", "دوري أبطال أوروبا", "beIN Sports 2", "حفيظ دراجي")

    # 🏴󠁧󠁢󠁥󠁮󠁧󠁿 الدوري الإنجليزي الممتاز
    add_match("ليفربول", "تشيلسي", "🔴", "🔵", "أنفيلد", "18:30", "الجولة 30", "الدوري الإنجليزي", "beIN Sports 1", "خليل البلوشي")

    # 🇪🇸 الدوري الإسباني
    add_match("برشلونة", "أتلتيكو مدريد", "🔵🔴", "🔴⚪", "مونتجويك", "23:00", "الجولة 30", "الدوري الإسباني", "beIN Sports 3", "علي محمد علي")

    # 🇮🇹 الدوري الإيطالي
    add_match("يوفنتوس", "ميلان", "⚫⚪", "🔴⚫", "أليانز ستاديوم", "21:45", "الجولة 30", "الدوري الإيطالي", "AD Sports Premium 1", "فارس عوض")

    # 🇩🇪 الدوري الألماني
    add_match("بوروسيا دورتموند", "لايبزيج", "🟡⚫", "⚪🔴", "سيغنال إيدونا بارك", "19:30", "الجولة 30", "الدوري الألماني", "beIN Sports 5", "حسن العيدروس")

    # 🇫🇷 الدوري الفرنسي
    add_match("باريس سان جيرمان", "مارسيليا", "🔵🔴", "⚪🔵", "حديقة الأمراء", "22:00", "الجولة 30", "الدوري الفرنسي", "beIN Sports 4", "جواد بدة")

    # 🇾🇪 الدوري اليمني
    add_match("أهلي صنعاء", "وحدة صنعاء", "🔴", "🔵", "ملعب الثورة", "16:00", "ديربي العاصمة", "الدوري اليمني", "قناة السعيدة", "علي النونو")

# ========== دوال المساعدة للجدول ==========
def get_today_matches():
    today = datetime.now().strftime("%Y-%m-%d")
    return [m for m in matches_db if m['date'] == today]

def create_full_schedule():
    """إنشاء جدول كامل مجمع حسب البطولات"""
    matches = get_today_matches()
    if not matches:
        return "📭 لا توجد مباريات اليوم"
    
    today_str = datetime.now().strftime("%d/%m/%Y")
    
    # تجميع المباريات حسب البطولة
    tournaments = {}
    for match in matches:
        t = match['tournament']
        if t not in tournaments:
            tournaments[t] = []
        tournaments[t].append(match)

    schedule = f"────────────────\n"
    schedule += f"♦ *جدول مباريات اليوم* |\n"
    schedule += f"📆 {today_str}\n"
    schedule += f"────────────────\n\n"
    
    # بناء نص الجدول المجمع
    for tournament, games in tournaments.items():
        schedule += f"🏆 *{tournament}* \n"
        schedule += f"━━━━━━━━━━━━━━━━━━\n"
        for m in games:
            schedule += f"*🔹️ {m['home_flag']} {m['home']} × {m['away']} {m['away_flag']} 🔸️*\n"
            schedule += f"⌚️ {m['time']} | 📺 {m['channel']} | 🎙 {m['commentator']}\n\n"
        
    schedule += f"────────────────\n"
    return schedule

# ========== أوامر البوت ==========
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "🎉 مرحباً بك في بوت جدول المباريات!\n\n"
        "📌 الأوامر المتاحة:\n"
        "/today - عرض مباريات اليوم هنا\n"
        "/send - 📢 نشر جدول اليوم في القناة"
    )

def today_command(update: Update, context: CallbackContext):
    # تحديث المباريات لتاريخ اليوم قبل العرض
    load_today_matches() 
    schedule = create_full_schedule()
    update.message.reply_text(schedule, parse_mode='Markdown')

def send_command(update: Update, context: CallbackContext):
    # تحديث المباريات لتاريخ اليوم قبل النشر
    load_today_matches() 
    schedule = create_full_schedule()
    
    try:
        context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=schedule,
            parse_mode='Markdown'
        )
        update.message.reply_text("✅ تم نشر جدول مباريات اليوم في القناة بنجاح!")
    except Exception as e:
        update.message.reply_text(
            f"❌ فشل النشر في القناة.\n"
            f"تأكد من:\n"
            f"1. البوت مضاف كـ (مشرف/Admin) في القناة.\n"
            f"2. معرف القناة ({CHANNEL_ID}) صحيح.\n"
            f"الخطأ التقني: {e}"
        )

# ========== صفحة الموقع (لاستضافة Flask) ==========
HTML = """
<!DOCTYPE html>
<html dir="rtl">
<head><title>🏆 بوت المباريات</title></head>
<body style="background:#0a0e1a;color:#fff;font-family:Arial;text-align:center;padding:50px;">
<h1 style="color:#ffd700;">🏆 بوت جدول المباريات يعمل بنجاح</h1>
<p>✅ البوت متصل وجاهز لتلقي الأوامر عبر التليجرام.</p>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML)

# ========== تشغيل البوت ==========
def run_bot():
    if not BOT_TOKEN or BOT_TOKEN == "PUT_YOUR_BOT_TOKEN_HERE":
        logging.warning("⚠️ BOT_TOKEN غير مضبوط! قم بتعديله في الكود.")
        return
    
    try:
        updater = Updater(BOT_TOKEN)
        dp = updater.dispatcher
        
        # تحميل المباريات عند التشغيل
        load_today_matches()
        
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(CommandHandler("today", today_command))
        dp.add_handler(CommandHandler("send", send_command))
        
        logging.info("🤖 البوت متصل ويعمل الآن...")
        updater.start_polling()
        updater.idle()
    except Exception as e:
        logging.error(f"❌ خطأ في تشغيل البوت: {e}")

# ========== التشغيل الرئيسي ==========
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    # تشغيل البوت في مسار (Thread) منفصل
    threading.Thread(target=run_bot, daemon=True).start()
    
    # تشغيل خادم Flask
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
