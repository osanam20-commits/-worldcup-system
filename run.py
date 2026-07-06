import os
import logging
import threading
from flask import Flask, render_template_string
from datetime import datetime
from telegram import Update
from telegram.ext import Updater, CommandHandler

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8689943788:AAFfmE62a4h-eLXYAcOXvSUgmkLs5KZZwts")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@lvFaax5HzsxOTU0")

matches_db = []
match_id = 1

def add_match(home, away, home_flag="🏴", away_flag="🏴", stadium="", 
              date="", time="", stage="", tournament=""):
    global match_id
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    if not time:
        time = "20:00"
    
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
        'status': 'upcoming'
    }
    matches_db.append(match)
    match_id += 1
    return match

# ========== كأس العالم 2026 ==========
add_match("فرنسا", "باراغواي", "🇫🇷", "🇵🇾", "ملعب أمريكا", "2026-07-04", "18:00", "دور الـ16", "كأس العالم")
add_match("المغرب", "كندا", "🇲🇦", "🇨🇦", "ملعب أمريكا", "2026-07-04", "21:00", "دور الـ16", "كأس العالم")
add_match("البرازيل", "النرويج", "🇧🇷", "🇳🇴", "ملعب أمريكا", "2026-07-05", "16:00", "دور الـ16", "كأس العالم")
add_match("المكسيك", "إنجلترا", "🇲🇽", "🏴", "ملعب أمريكا", "2026-07-05", "20:00", "دور الـ16", "كأس العالم")
add_match("البرتغال", "إسبانيا", "🇵🇹", "🇪🇸", "ملعب أمريكا", "2026-07-06", "15:00", "دور الـ16", "كأس العالم")
add_match("أمريكا", "بلجيكا", "🇺🇸", "🇧🇪", "ملعب أمريكا", "2026-07-06", "20:00", "دور الـ16", "كأس العالم")
add_match("الأرجنتين", "مصر", "🇦🇷", "🇪🇬", "ملعب أمريكا", "2026-07-07", "12:00", "دور الـ16", "كأس العالم")
add_match("سويسرا", "كولومبيا", "🇨🇭", "🇨🇴", "ملعب أمريكا", "2026-07-07", "16:00", "دور الـ16", "كأس العالم")
add_match("فرنسا", "المغرب", "🇫🇷", "🇲🇦", "ملعب أمريكا", "2026-07-09", "18:00", "ربع النهائي", "كأس العالم")
add_match("البرتغال/إسبانيا", "أمريكا/بلجيكا", "🇵🇹", "🇺🇸", "ملعب أمريكا", "2026-07-10", "18:00", "ربع النهائي", "كأس العالم")
add_match("البرازيل/النرويج", "المكسيك/إنجلترا", "🇧🇷", "🇲🇽", "ملعب أمريكا", "2026-07-11", "16:00", "ربع النهائي", "كأس العالم")
add_match("الأرجنتين/مصر", "سويسرا/كولومبيا", "🇦🇷", "🇨🇭", "ملعب أمريكا", "2026-07-11", "20:00", "ربع النهائي", "كأس العالم")
add_match("الفائز ربع الأول", "الفائز ربع الثاني", "🏆", "🏆", "أرلينغتون", "2026-07-14", "18:00", "نصف النهائي", "كأس العالم")
add_match("الفائز ربع الثالث", "الفائز ربع الرابع", "🏆", "🏆", "أتلانتا", "2026-07-15", "18:00", "نصف النهائي", "كأس العالم")
add_match("المركز الثالث", "المركز الثالث", "🥉", "🥉", "ميامي", "2026-07-18", "17:00", "المركز الثالث", "كأس العالم")
add_match("النهائي", "النهائي", "🏆", "🏆", "ملعب ميتلايف", "2026-07-19", "15:00", "النهائي", "كأس العالم")

# ========== الدوريات الخمسة ==========
add_match("مانشستر سيتي", "آرسنال", "🏴", "🏴", "الاتحاد", "2026-08-10", "18:30", "الجولة 1", "الدوري الإنجليزي")
add_match("ليفربول", "تشيلسي", "🏴", "🏴", "أنفيلد", "2026-08-10", "21:00", "الجولة 1", "الدوري الإنجليزي")
add_match("ريال مدريد", "برشلونة", "🇪🇸", "🇪🇸", "سانتياغو برنابيو", "2026-08-11", "22:00", "الجولة 1", "الدوري الإسباني")
add_match("يوفنتوس", "ميلان", "🇮🇹", "🇮🇹", "أليانز", "2026-08-12", "20:45", "الجولة 1", "الدوري الإيطالي")
add_match("بايرن ميونخ", "بوروسيا", "🇩🇪", "🇩🇪", "أليانز أرينا", "2026-08-13", "20:30", "الجولة 1", "الدوري الألماني")
add_match("باريس سان جيرمان", "مارسيليا", "🇫🇷", "🇫🇷", "بارك دي برينس", "2026-08-14", "21:00", "الجولة 1", "الدوري الفرنسي")

# ========== الدوري اليمني ==========
add_match("أهلي صنعاء", "الوحدة", "🇾🇪", "🇾🇪", "ملعب صنعاء", "2026-08-15", "16:00", "الجولة 1", "الدوري اليمني")
add_match("شعب إب", "التلال", "🇾🇪", "🇾🇪", "ملعب إب", "2026-08-15", "18:00", "الجولة 1", "الدوري اليمني")
add_match("اليرموك", "حسان", "🇾🇪", "🇾🇪", "ملعب عدن", "2026-08-16", "16:00", "الجولة 1", "الدوري اليمني")

def get_today_matches():
    today = datetime.now().strftime("%Y-%m-%d")
    return [m for m in matches_db if m['date'] == today]

def get_all_matches():
    return matches_db

HTML = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🏆 كأس العالم 2026</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{background:linear-gradient(135deg,#0a0e1a,#1a1f35);color:#fff;font-family:Arial;padding:20px;}
.container{max-width:1200px;margin:0 auto;}
.header{text-align:center;padding:40px;background:#1a1f35;border-radius:20px;margin-bottom:30px;border:1px solid #ffd70033;}
.header h1{font-size:3em;color:#ffd700;}
.header p{color:#aaa;font-size:1.2em;}
.btn{display:inline-block;padding:12px 30px;background:linear-gradient(135deg,#ffd700,#f5a623);color:#1a1f35;text-decoration:none;border-radius:30px;font-weight:bold;margin:5px;}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:20px;margin:30px 0;}
.stat-box{background:#1a1f35;padding:20px;border-radius:15px;text-align:center;border:1px solid #2a3f5f;}
.stat-box .number{font-size:2.5em;color:#ffd700;font-weight:bold;}
.stat-box .label{color:#aaa;}
.section-title{font-size:2em;color:#ffd700;margin:30px 0 20px;padding-bottom:10px;border-bottom:2px solid rgba(255,215,0,0.2);}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:25px;margin-bottom:40px;}
.card{background:#1a1f35;padding:25px;border-radius:18px;border:1px solid #2a3f5f;text-align:center;transition:0.3s;}
.card:hover{border-color:#ffd700;transform:translateY(-5px);}
.card .tournament{color:#ffd700;font-size:0.9em;}
.card .stage{background:rgba(255,215,0,0.15);color:#ffd700;padding:3px 15px;border-radius:20px;font-size:0.8em;display:inline-block;}
.card .teams{font-size:1.5em;font-weight:bold;margin:15px 0;}
.card .teams .home{color:#2ecc71;}
.card .teams .away{color:#e74c3c;}
.card .teams .vs{color:#ffd700;margin:0 10px;}
.card .info{color:#aaa;line-height:1.8;}
.card .info span{color:#fff;}
.filter-buttons{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:20px;}
.filter-btn{padding:8px 20px;background:#1a1f35;color:#aaa;border:1px solid #2a3f5f;border-radius:25px;text-decoration:none;transition:0.3s;}
.filter-btn:hover,.filter-btn.active{background:#ffd700;color:#1a1f35;}
.footer{text-align:center;padding:30px;color:#555;border-top:1px solid #2a3f5f;margin-top:40px;}
.footer a{color:#ffd700;text-decoration:none;}
@media(max-width:600px){.header h1{font-size:2em;}.card .teams{font-size:1.2em;}}
</style>
</head>
<body>
<div class="container">
<div class="header">
<h1>🏆 كأس العالم 2026</h1>
<p>جميع البطولات - جميع المباريات</p>
<div style="margin-top:15px;"><a href="https://t.me/Ali_worldcup_bot" class="btn">🤖 البوت على تليجرام</a></div>
</div>
<div class="stats">
<div class="stat-box"><div class="number">{{ total }}</div><div class="label">كل المباريات</div></div>
<div class="stat-box"><div class="number">{{ today_count }}</div><div class="label">مباريات اليوم</div></div>
<div class="stat-box"><div class="number">{{ tournaments }}</div><div class="label">بطولات</div></div>
</div>
<div class="filter-buttons">
<a href="/" class="filter-btn active">🏆 الكل</a>
<a href="/?t=كأس%20العالم" class="filter-btn">🌍 كأس العالم</a>
<a href="/?t=الدوري%20الإنجليزي" class="filter-btn">🏴 إنجلترا</a>
<a href="/?t=الدوري%20الإسباني" class="filter-btn">🇪🇸 إسبانيا</a>
<a href="/?t=الدوري%20الإيطالي" class="filter-btn">🇮🇹 إيطاليا</a>
<a href="/?t=الدوري%20الألماني" class="filter-btn">🇩🇪 ألمانيا</a>
<a href="/?t=الدوري%20الفرنسي" class="filter-btn">🇫🇷 فرنسا</a>
<a href="/?t=الدوري%20اليمني" class="filter-btn">🇾🇪 اليمن</a>
</div>
<h2 class="section-title">⚽ المباريات</h2>
<div class="cards">
{% for match in matches %}
<div class="card">
<div class="tournament">🏆 {{ match.tournament }}</div>
<div class="stage">{{ match.stage }}</div>
<div class="teams">
<span class="home">{{ match.home_flag }} {{ match.home }}</span>
<span class="vs">⚔️</span>
<span class="away">{{ match.away_flag }} {{ match.away }}</span>
</div>
<div class="info">
📍 <span>{{ match.stadium }}</span><br>
📅 <span>{{ match.date }}</span> | 🕒 <span>{{ match.time }}</span>
</div>
</div>
{% else %}
<div class="card" style="grid-column:1/-1;padding:40px;"><p>📭 لا توجد مباريات</p></div>
{% endfor %}
</div>
<div class="footer"><p>🏆 كأس العالم 2026 - جميع الحقوق محفوظة</p></div>
</div>
</body>
</html>
"""

@app.route('/')
def home():
    t = request.args.get('t')
    if t:
        matches = [m for m in matches_db if m['tournament'] == t]
    else:
        matches = matches_db
    total = len(matches_db)
    tournaments = len(set(m['tournament'] for m in matches_db))
    today_count = len(get_today_matches())
    return render_template_string(HTML, matches=matches, total=total, tournaments=tournaments, today_count=today_count)

# ========== البوت ==========
def start(update, context):
    update.message.reply_text("🎉 مرحباً بك في بوت كأس العالم 2026!\n/today - مباريات اليوم\n/matches - جميع المباريات")

def today(update, context):
    matches = get_today_matches()
    if not matches:
        update.message.reply_text("📭 لا توجد مباريات اليوم")
        return
    text = "📅 مباريات اليوم:\n\n"
    for m in matches:
        text += f"{m['home_flag']} {m['home']} 🆚 {m['away_flag']} {m['away']}\n🏆 {m['tournament']} | 🕒 {m['time']}\n\n"
    update.message.reply_text(text)

def matches(update, context):
    text = "📋 جميع المباريات:\n\n"
    for m in matches_db[:20]:
        text += f"{m['home_flag']} {m['home']} 🆚 {m['away_flag']} {m['away']}\n🏆 {m['tournament']} | 📅 {m['date']}\n\n"
    update.message.reply_text(text)

def worldcup(update, context):
    matches = [m for m in matches_db if m['tournament'] == "كأس العالم"]
    if not matches:
        update.message.reply_text("📭 لا توجد مباريات")
        return
    text = "🌍 كأس العالم 2026:\n\n"
    for m in matches:
        text += f"{m['home_flag']} {m['home']} 🆚 {m['away_flag']} {m['away']}\n📌 {m['stage']} | 📅 {m['date']}\n\n"
    update.message.reply_text(text)

def leagues(update, context):
    leagues = ["الدوري الإنجليزي", "الدوري الإسباني", "الدوري الإيطالي", "الدوري الألماني", "الدوري الفرنسي"]
    text = "🏆 الدوريات الخمسة:\n\n"
    for l in leagues:
        count = len([m for m in matches_db if m['tournament'] == l])
        text += f"🏆 {l} - {count} مباراة\n"
    update.message.reply_text(text)

def yemen(update, context):
    matches = [m for m in matches_db if m['tournament'] == "الدوري اليمني"]
    if not matches:
        update.message.reply_text("📭 لا توجد مباريات")
        return
    text = "🇾🇪 الدوري اليمني:\n\n"
    for m in matches:
        text += f"{m['home_flag']} {m['home']} 🆚 {m['away_flag']} {m['away']}\n📍 {m['stadium']} | 🕒 {m['time']}\n\n"
    update.message.reply_text(text)

def send(update, context):
    try:
        today_matches = get_today_matches()
        if not today_matches:
            update.message.reply_text("📭 لا توجد مباريات اليوم")
            return
        for match in today_matches:
            text = f"🏆 **{match['tournament']}**\n📌 {match['stage']}\n\n{match['home_flag']} {match['home']} ⚔️ {match['away_flag']} {match['away']}\n📍 {match['stadium']} | 🕒 {match['time']}"
            context.bot.send_message(chat_id=CHANNEL_ID, text=text, parse_mode='Markdown')
            time.sleep(1)
        update.message.reply_text(f"✅ تم نشر {len(today_matches)} مباراة في القناة!")
    except Exception as e:
        update.message.reply_text(f"❌ خطأ: {e}")

def run_bot():
    if not BOT_TOKEN or BOT_TOKEN == "PUT_YOUR_BOT_TOKEN_HERE":
        return
    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("today", today))
    dp.add_handler(CommandHandler("matches", matches))
    dp.add_handler(CommandHandler("worldcup", worldcup))
    dp.add_handler(CommandHandler("leagues", leagues))
    dp.add_handler(CommandHandler("yemen", yemen))
    dp.add_handler(CommandHandler("send", send))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    from flask import request
    import time
    logging.basicConfig(level=logging.INFO)
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
