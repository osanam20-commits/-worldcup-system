import os
import logging
import threading
import time
from flask import Flask, render_template_string
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8689943788:AAFfmE62a4h-eLXYAcOXvSUgmkLs5KZZwts")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@lvFaax5HzsxOTU0")

matches_db = []
match_id = 1

def add_match(home, away, home_flag="🏴", away_flag="🏴", stadium="", 
              date="", time="", stage="دور المجموعات", tournament="كأس العالم"):
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
        'status': 'upcoming',
        'home_score': 0,
        'away_score': 0
    }
    matches_db.append(match)
    match_id += 1
    return match

add_match("الهلال", "النصر", "🇸🇦", "🇸🇦", "ملعب الملك فهد", "2026-07-15", "20:00", "نهائي", "دوري روشن")

def get_today_matches():
    today = datetime.now().strftime("%Y-%m-%d")
    return [m for m in matches_db if m['date'] == today]

def get_live_matches():
    return [m for m in matches_db if m['status'] == 'live']

HTML = """
<!DOCTYPE html>
<html>
<head><title>🏆 كأس العالم 2026</title>
<style>
body{background:#0a0e1a;color:#fff;font-family:Arial;padding:20px;}
.container{max-width:1200px;margin:0 auto;}
.header{text-align:center;padding:40px;background:#1a1f35;border-radius:20px;margin-bottom:30px;}
.header h1{color:#ffd700;font-size:3em;}
.card{background:#1a1f35;padding:20px;border-radius:15px;margin:10px 0;border:1px solid #2a3f5f;}
.teams{font-size:1.5em;font-weight:bold;}
.home{color:#2ecc71;}
.away{color:#e74c3c;}
.vs{color:#ffd700;margin:0 10px;}
.info{color:#aaa;}
</style>
</head>
<body>
<div class="container">
<div class="header"><h1>🏆 كأس العالم 2026</h1></div>
<h2>⚽ مباريات اليوم</h2>
{% for match in today %}
<div class="card">
<div class="teams">
<span class="home">{{ match.home_flag }} {{ match.home }}</span>
<span class="vs">⚔️</span>
<span class="away">{{ match.away_flag }} {{ match.away }}</span>
</div>
<div class="info">📍 {{ match.stadium }} | 📅 {{ match.date }} | 🕒 {{ match.time }}</div>
</div>
{% else %}
<p>📭 لا توجد مباريات اليوم</p>
{% endfor %}
</div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML, today=get_today_matches())

def start(update, context):
    update.message.reply_text("🎉 مرحباً بك في بوت كأس العالم 2026!\n/today - مباريات اليوم")

def today_command(update, context):
    matches = get_today_matches()
    if not matches:
        update.message.reply_text("📭 لا توجد مباريات اليوم")
        return
    text = "📅 مباريات اليوم:\n\n"
    for m in matches:
        text += f"{m['home_flag']} {m['home']} 🆚 {m['away_flag']} {m['away']}\n"
        text += f"📍 {m['stadium']} | 🕒 {m['time']}\n\n"
    update.message.reply_text(text)

def run_bot():
    if not BOT_TOKEN or BOT_TOKEN == "PUT_YOUR_BOT_TOKEN_HERE":
        return
    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("today", today_command))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
