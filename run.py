import os
import logging
import threading
from flask import Flask, render_template_string
from datetime import datetime
import telebot

# ========== إعدادات البوت والقناة ==========
app = Flask(__name__)

# ضع التوكن ومعرف القناة هنا (أو عبر المتغيرات البيئية)
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8689943788:AAFfmE62a4h-eLXYAcOXvSUgmkLs5KZZwts")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "-1004372754611")

# تهيئة البوت بالمكتبة الجديدة
bot = telebot.TeleBot(BOT_TOKEN)

# ========== قاعدة البيانات ==========
matches_db = []
match_id = 1

def add_match(home, away, home_flag="🏴", away_flag="🏴", stadium="غير محدد", 
              time="00:00", stage="مباراة دورية", tournament="بطولة", 
              channel="beIN Sports", commentator="غير محدد"):
    global match_id
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

# ========== توليد المباريات ==========
def load_today_matches():
    global matches_db, match_id
    matches_db = []
    match_id = 1
    
    add_match("ريال مدريد", "مانشستر سيتي", "🇪🇸", "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "سانتياغو برنابيو", "22:00", "نصف النهائي", "دوري أبطال أوروبا", "beIN Sports 1", "عصام الشوالي")
    add_match("بايرن ميونخ", "أرسنال", "🇩🇪", "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "أليانز أرينا", "22:00", "نصف النهائي", "دوري أبطال أوروبا", "beIN Sports 2", "حفيظ دراجي")
    add_match("ليفربول", "تشيلسي", "🔴", "🔵", "أنفيلد", "18:30", "الجولة 30", "الدوري الإنجليزي", "beIN Sports 1", "خليل البلوشي")
    add_match("برشلونة", "أتلتيكو مدريد", "🔵🔴", "🔴⚪", "مونتجويك", "23:00", "الجولة 30", "الدوري الإسباني", "beIN Sports 3", "علي محمد علي")
    add_match("يوفنتوس", "ميلان", "⚫⚪", "🔴⚫", "أليانز ستاديوم", "21:45", "الجولة 30", "الدوري الإيطالي", "AD Sports Premium 1", "فارس عوض")
    add_match("بوروسيا دورتموند", "لايبزيج", "🟡⚫", "⚪🔴", "سيغنال إيدونا بارك", "19:30", "الجولة 30", "الدوري الألماني", "beIN Sports 5", "حسن العيدروس")
    add_match("باريس سان جيرمان", "مارسيليا", "🔵🔴", "⚪🔵", "حديقة الأمراء", "22:00", "الجولة 30", "الدوري الفرنسي", "beIN Sports 4", "جواد بدة")
    add_match("أهلي صنعاء", "وحدة صنعاء", "🔴", "🔵", "ملعب الثورة", "16:00", "ديربي العاصمة", "الدوري اليمني", "قناة السعيدة", "علي النونو")

def get_today_matches():
    today = datetime.now().strftime("%Y-%m-%d")
    return [m for m in matches_db if m['date'] == today]

def create_full_schedule():
    matches = get_today_matches()
    if not matches:
        return "📭 لا توجد مباريات اليوم"
    
    today_str = datetime.now().strftime("%d/%m/%Y")
    
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
    
    for tournament, games in tournaments.items():
        schedule += f"🏆 *{tournament}* \n"
        schedule += f"━━━━━━━━━━━━━━━━━━\n"
        for m in games:
            schedule += f"*🔹️ {m['home_flag']} {m['home']} × {m['away']} {m['away_flag']} 🔸️*\n"
            schedule += f"⌚️ {m['time']} | 📺 {m['channel']} | 🎙 {m['commentator']}\n\n"
        
    schedule += f"────────────────\n"
    return schedule

# ========== أوامر البوت ==========
@bot.message_handler(commands=['start'])
def start_command(message):
    bot.reply_to(message, "🎉 مرحباً بك في بوت جدول المباريات!\n\n📌 الأوامر المتاحة:\n/today - عرض مباريات اليوم هنا\n/send - 📢 نشر جدول اليوم في القناة")

@bot.message_handler(commands=['today'])
def today_command(message):
    load_today_matches() 
    schedule = create_full_schedule()
    bot.reply_to(message, schedule, parse_mode='Markdown')

@bot.message_handler(commands=['send'])
def send_command(message):
    load_today_matches() 
    schedule = create_full_schedule()
    
    try:
        bot.send_message(chat_id=CHANNEL_ID, text=schedule, parse_mode='Markdown')
        bot.reply_to(message, "✅ تم نشر جدول مباريات اليوم في القناة بنجاح!")
    except Exception as e:
        bot.reply_to(message, f"❌ فشل النشر في القناة.\nتأكد من أن البوت مشرف في القناة وأن المعرف ({CHANNEL_ID}) صحيح.\nالخطأ: {e}")

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
        logging.warning("⚠️ BOT_TOKEN غير مضبوط! قم بتعديله.")
        return
    
    try:
        load_today_matches()
        logging.info("🤖 البوت متصل ويعمل الآن...")
        bot.infinity_polling()
    except Exception as e:
        logging.error(f"❌ خطأ في تشغيل البوت: {e}")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
