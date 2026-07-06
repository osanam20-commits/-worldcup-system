import os
import logging
import threading
import time
from flask import Flask, render_template_string
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

# ========== إعدادات ==========
app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8689943788:AAFfmE62a4h-eLXYAcOXvSUgmkLs5KZZwts")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@lvFaax5HzsxOTU0")

# ========== قاعدة البيانات ==========
matches_db = []
match_id = 1

def add_match(home, away, home_flag="🏴", away_flag="🏴", stadium="", 
              date="", time="", stage="", tournament="", status="upcoming"):
    global match_id
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    if not time:
        time = datetime.now().strftime("%H:%M")
    
    match = {
        'id': match_id,
        'home': home,
        'away': away,
        'home_flag': home_flag,
        'away_flag': away_flag,
        'stadium': stadium,
        'date': date,
        'time': time,
        'stage': stage,
        'tournament': tournament,
        'status': status,
        'home_score': 0,
        'away_score': 0
    }
    matches_db.append(match)
    match_id += 1
    return match

# ========== مباريات اليوم (7 يوليو 2026) ==========
add_match("الأرجنتين", "مصر", "🇦🇷", "🇪🇬", "ملعب أمريكا", "2026-07-07", "12:00", "دور الـ16", "كأس العالم 2026")
add_match("سويسرا", "كولومبيا", "🇨🇭", "🇨🇴", "ملعب أمريكا", "2026-07-07", "16:00", "دور الـ16", "كأس العالم 2026")

# ========== دوال المساعدة ==========
def get_today_matches():
    today = datetime.now().strftime("%Y-%m-%d")
    return [m for m in matches_db if m['date'] == today]

def get_all_matches():
    return matches_db

def create_match_card(match):
    card = (
        f"🏆 **{match['tournament']}**\n"
        f"📌 **{match['stage']}**\n\n"
        f"{match['home_flag']} **{match['home']}**\n"
        f"⚔️ VS\n"
        f"{match['away_flag']} **{match['away']}**\n\n"
        f"📍 {match['stadium']}\n"
        f"📅 {match['date']} | 🕒 {match['time']}\n"
        f"🆔 #{match['id']}"
    )
    return card

def send_to_channel(context, text):
    try:
        context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=text,
            parse_mode='Markdown'
        )
        return True
    except Exception as e:
        logging.error(f"❌ خطأ: {e}")
        return False

def send_daily_matches(context):
    today_matches = get_today_matches()
    if not today_matches:
        send_to_channel(context, "📭 لا توجد مباريات اليوم")
        return
    
    for match in today_matches:
        card = create_match_card(match)
        send_to_channel(context, card)
        time.sleep(1)

# ========== أوامر البوت ==========
def start(update, context):
    update.message.reply_text(
        "🎉 مرحباً بك في بوت كأس العالم 2026!\n\n"
        "/today - مباريات اليوم\n"
        "/matches - جميع المباريات\n"
        "/send - نشر مباريات اليوم في القناة"
    )

def today_command(update, context):
    matches = get_today_matches()
    if not matches:
        update.message.reply_text("📭 لا توجد مباريات اليوم")
        return
    
    text = "📅 مباريات اليوم:\n\n"
    for m in matches:
        text += f"{m['home_flag']} {m['home']} 🆚 {m['away_flag']} {m['away']}\n"
        text += f"🏆 {m['tournament']} | 🕒 {m['time']}\n\n"
    update.message.reply_text(text)

def matches_command(update, context):
    if not matches_db:
        update.message.reply_text("📭 لا توجد مباريات")
        return
    
    text = "📋 جميع المباريات:\n\n"
    for m in matches_db:
        text += f"#{m['id']} {m['home_flag']} {m['home']} 🆚 {m['away_flag']} {m['away']}\n"
        text += f"🏆 {m['tournament']} | 📅 {m['date']} | 🕒 {m['time']}\n\n"
    update.message.reply_text(text)

def send_command(update, context):
    try:
        send_daily_matches(context)
        update.message.reply_text("✅ تم نشر مباريات اليوم في القناة!")
    except Exception as e:
        update.message.reply_text(f"❌ خطأ: {e}")

# ========== صفحة الموقع ==========
HTML = """
<!DOCTYPE html>
<html>
<head><title>🏆 كأس العالم 2026</title></head>
<body style="background:#0a0e1a;color:#fff;font-family:Arial;text-align:center;padding:50px;">
<h1 style="color:#ffd700;">🏆 كأس العالم 2026</h1>
<p>✅ البوت يعمل!</p>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML)

# ========== تشغيل البوت ==========
def run_bot():
    if not BOT_TOKEN or BOT_TOKEN == "PUT_YOUR_BOT_TOKEN_HERE":
        logging.warning("⚠️ BOT_TOKEN غير مضبوط")
        return
    
    try:
        updater = Updater(BOT_TOKEN)
        dp = updater.dispatcher
        
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(CommandHandler("today", today_command))
        dp.add_handler(CommandHandler("matches", matches_command))
        dp.add_handler(CommandHandler("send", send_command))
        
        logging.info("🤖 البوت يعمل...")
        updater.start_polling()
        updater.idle()
    except Exception as e:
        logging.error(f"❌ خطأ: {e}")

# ========== التشغيل ==========
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
