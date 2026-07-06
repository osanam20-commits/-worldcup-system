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
        'away_score': 0,
        'home_votes': 0,
        'away_votes': 0,
        'draw_votes': 0
    }
    matches_db.append(match)
    match_id += 1
    return match

# ========== مباريات تجريبية (كأس العالم 2026) ==========
add_match("فرنسا", "باراغواي", "🇫🇷", "🇵🇾", "ملعب أمريكا", "2026-07-04", "18:00", "دور الـ16", "كأس العالم 2026")
add_match("المغرب", "كندا", "🇲🇦", "🇨🇦", "ملعب أمريكا", "2026-07-04", "21:00", "دور الـ16", "كأس العالم 2026")
add_match("البرازيل", "النرويج", "🇧🇷", "🇳🇴", "ملعب أمريكا", "2026-07-05", "16:00", "دور الـ16", "كأس العالم 2026")
add_match("المكسيك", "إنجلترا", "🇲🇽", "🏴", "ملعب أمريكا", "2026-07-05", "20:00", "دور الـ16", "كأس العالم 2026")
add_match("البرتغال", "إسبانيا", "🇵🇹", "🇪🇸", "ملعب أمريكا", "2026-07-06", "15:00", "دور الـ16", "كأس العالم 2026")
add_match("أمريكا", "بلجيكا", "🇺🇸", "🇧🇪", "ملعب أمريكا", "2026-07-06", "20:00", "دور الـ16", "كأس العالم 2026")
add_match("الأرجنتين", "مصر", "🇦🇷", "🇪🇬", "ملعب أمريكا", "2026-07-07", "12:00", "دور الـ16", "كأس العالم 2026")
add_match("سويسرا", "كولومبيا", "🇨🇭", "🇨🇴", "ملعب أمريكا", "2026-07-07", "16:00", "دور الـ16", "كأس العالم 2026")

# ========== دوال المساعدة ==========
def get_today_matches():
    today = datetime.now().strftime("%Y-%m-%d")
    return [m for m in matches_db if m['date'] == today]

def get_live_matches():
    return [m for m in matches_db if m['status'] == 'live']

def get_all_matches():
    return matches_db

def get_upcoming_matches():
    today = datetime.now().strftime("%Y-%m-%d")
    return [m for m in matches_db if m['date'] >= today and m['status'] == 'upcoming']

def get_matches_by_tournament(tournament):
    return [m for m in matches_db if m['tournament'] == tournament]

def create_match_card(match):
    status_emoji = "🔴" if match['status'] == 'live' else "⏳" if match['status'] == 'upcoming' else "✅"
    status_text = "مباشر" if match['status'] == 'live' else "قادمة" if match['status'] == 'upcoming' else "انتهت"
    
    card = (
        f"🏆 **{match['tournament']}**\n"
        f"📌 **{match['stage']}**\n\n"
        f"{match['home_flag']} **{match['home']}**\n"
        f"⚔️ VS\n"
        f"{match['away_flag']} **{match['away']}**\n\n"
    )
    
    if match['status'] == 'live':
        card += f"⚽ **{match['home_score']} - {match['away_score']}**\n\n"
    
    card += (
        f"📍 {match['stadium']}\n"
        f"📅 {match['date']} | 🕒 {match['time']}\n"
        f"📊 الحالة: {status_text} {status_emoji}\n"
        f"🆔 #{match['id']}\n\n"
        f"🗳️ **من تتوقع الفائز؟**"
    )
    
    return card

def create_match_keyboard(match):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"🏠 {match['home']}", callback_data=f"vote_home_{match['id']}"),
            InlineKeyboardButton(f"⚽ تعادل", callback_data=f"vote_draw_{match['id']}")
        ],
        [
            InlineKeyboardButton(f"✈️ {match['away']}", callback_data=f"vote_away_{match['id']}")
        ]
    ])

# ========== دوال النشر ==========
def send_to_channel(context, text, keyboard=None):
    try:
        context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        logging.info("✅ تم إرسال الرسالة إلى القناة")
        return True
    except Exception as e:
        logging.error(f"❌ خطأ: {e}")
        return False

def send_match_to_channel(context, match):
    try:
        card = create_match_card(match)
        keyboard = create_match_keyboard(match)
        return send_to_channel(context, card, keyboard)
    except Exception as e:
        logging.error(f"❌ خطأ: {e}")
        return False

def send_daily_matches(context):
    today_matches = get_today_matches()
    if not today_matches:
        send_to_channel(context, "📭 لا توجد مباريات اليوم")
        return
    
    for match in today_matches:
        send_match_to_channel(context, match)
        time.sleep(1)
    
    logging.info(f"✅ تم نشر {len(today_matches)} مباراة اليوم")

def check_live_matches(context):
    """التحقق من المباريات المباشرة وإرسال إشعار"""
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    
    for match in matches_db:
        if match['status'] == 'upcoming' and match['date'] == today:
            match_time = datetime.strptime(f"{match['date']} {match['time']}", "%Y-%m-%d %H:%M")
            if match_time <= now <= match_time + timedelta(minutes=30):
                match['status'] = 'live'
                text = f"🔴 **المباراة أصبحت مباشرة!**\n\n{create_match_card(match)}"
                send_to_channel(context, text)

# ========== أوامر البوت ==========
def start(update, context):
    update.message.reply_text(
        "🎉 **مرحباً بك في بوت كأس العالم 2026!**\n\n"
        "📌 **الأوامر المتاحة:**\n"
        "/start - بدء البوت\n"
        "/help - المساعدة\n"
        "/today - مباريات اليوم\n"
        "/live - المباريات المباشرة\n"
        "/matches - جميع المباريات\n"
        "/send - نشر مباريات اليوم في القناة\n"
        "/add - إضافة مباراة\n\n"
        "🔗 **رابط القناة:**\n" + CHANNEL_ID,
        parse_mode='Markdown'
    )

def help_command(update, context):
    update.message.reply_text(
        "❓ **المساعدة:**\n\n"
        "/today - مباريات اليوم\n"
        "/live - المباريات المباشرة\n"
        "/matches - جميع المباريات\n"
        "/send - نشر مباريات اليوم في القناة\n\n"
        "📌 **للمشرفين:**\n"
        "/add الفريق1 الفريق2 الملعب التاريخ الوقت البطولة المرحلة\n"
        "/set_live معرف_المباراة\n"
        "/set_score معرف_المباراة هدف1 هدف2\n"
        "/delete معرف_المباراة",
        parse_mode='Markdown'
    )

def today_command(update, context):
    matches = get_today_matches()
    if not matches:
        update.message.reply_text("📭 لا توجد مباريات اليوم")
        return
    
    text = "📅 **مباريات اليوم:**\n\n"
    for m in matches:
        text += f"{m['home_flag']} {m['home']} 🆚 {m['away_flag']} {m['away']}\n"
        text += f"🏆 {m['tournament']} | 🕒 {m['time']}\n\n"
    update.message.reply_text(text, parse_mode='Markdown')

def live_command(update, context):
    matches = get_live_matches()
    if not matches:
        update.message.reply_text("🔴 لا توجد مباريات مباشرة")
        return
    
    text = "🔴 **المباريات المباشرة:**\n\n"
    for m in matches:
        text += f"{m['home_flag']} {m['home']} {m['home_score']} - {m['away_score']} {m['away_flag']} {m['away']}\n"
        text += f"🏆 {m['tournament']} | 📍 {m['stadium']}\n\n"
    update.message.reply_text(text, parse_mode='Markdown')

def matches_command(update, context):
    matches = get_all_matches()
    if not matches:
        update.message.reply_text("📭 لا توجد مباريات")
        return
    
    text = "📋 **جميع المباريات:**\n\n"
    for m in matches[:15]:
        text += f"#{m['id']} {m['home_flag']} {m['home']} 🆚 {m['away_flag']} {m['away']}\n"
        text += f"🏆 {m['tournament']} | 📅 {m['date']} | 🕒 {m['time']}\n\n"
    update.message.reply_text(text, parse_mode='Markdown')

def send_command(update, context):
    """نشر مباريات اليوم في القناة"""
    try:
        send_daily_matches(context)
        update.message.reply_text("✅ تم نشر مباريات اليوم في القناة!")
    except Exception as e:
        update.message.reply_text(f"❌ خطأ: {e}")

def add_command(update, context):
    """إضافة مباراة"""
    try:
        args = context.args
        if len(args) < 7:
            update.message.reply_text(
                "⚠️ الصيغة: /add الفريق1 الفريق2 الملعب التاريخ الوقت البطولة المرحلة\n"
                "مثال: /add الهلال النصر ملعب_الملك_فهد 2026-07-07 20:00 دوري_روشن نهائي"
            )
            return
        
        match = add_match(
            home=args[0],
            away=args[1],
            stadium=args[2],
            date=args[3],
            time=args[4],
            tournament=args[5],
            stage=args[6] if len(args) > 6 else "دور المجموعات"
        )
        
        update.message.reply_text(
            f"✅ تم إضافة المباراة:\n"
            f"{match['home']} 🆚 {match['away']}\n"
            f"🏆 {match['tournament']} | 📅 {match['date']} | 🕒 {match['time']}"
        )
        
        # نشر المباراة في القناة
        send_match_to_channel(context, match)
        
    except Exception as e:
        update.message.reply_text(f"❌ خطأ: {e}")

def set_live_command(update, context):
    """تفعيل مباراة كمباشرة"""
    try:
        match_id = int(context.args[0])
        for match in matches_db:
            if match['id'] == match_id:
                match['status'] = 'live'
                update.message.reply_text(f"✅ تم تفعيل المباراة #{match_id} كمباشرة")
                text = f"🔴 **المباراة أصبحت مباشرة!**\n\n{create_match_card(match)}"
                send_to_channel(context, text)
                return
        update.message.reply_text(f"❌ المباراة #{match_id} غير موجودة")
    except Exception as e:
        update.message.reply_text(f"❌ خطأ: {e}")

def set_score_command(update, context):
    """تحديث النتيجة"""
    try:
        args = context.args
        match_id = int(args[0])
        home_score = int(args[1])
        away_score = int(args[2])
        
        for match in matches_db:
            if match['id'] == match_id:
                match['home_score'] = home_score
                match['away_score'] = away_score
                update.message.reply_text(f"✅ تم تحديث النتيجة: {home_score} - {away_score}")
                text = f"⚽ **تحديث النتيجة:**\n\n{create_match_card(match)}"
                send_to_channel(context, text)
                return
        update.message.reply_text(f"❌ المباراة #{match_id} غير موجودة")
    except Exception as e:
        update.message.reply_text(f"❌ خطأ: {e}")

def delete_command(update, context):
    """حذف مباراة"""
    try:
        match_id = int(context.args[0])
        for i, match in enumerate(matches_db):
            if match['id'] == match_id:
                matches_db.pop(i)
                update.message.reply_text(f"✅ تم حذف المباراة #{match_id}")
                return
        update.message.reply_text(f"❌ المباراة #{match_id} غير موجودة")
    except Exception as e:
        update.message.reply_text(f"❌ خطأ: {e}")

# ========== معالجة الأزرار ==========
def button_callback(update, context):
    query = update.callback_query
    query.answer()
    
    data = query.data
    if data.startswith("vote_home_"):
        match_id = int(data.split("_")[2])
        for match in matches_db:
            if match['id'] == match_id:
                match['home_votes'] = match.get('home_votes', 0) + 1
                query.edit_message_text(f"🗳️ صوتك لـ {match['home']} تم تسجيله!")
                return
    elif data.startswith("vote_away_"):
        match_id = int(data.split("_")[2])
        for match in matches_db:
            if match['id'] == match_id:
                match['away_votes'] = match.get('away_votes', 0) + 1
                query.edit_message_text(f"🗳️ صوتك لـ {match['away']} تم تسجيله!")
                return
    elif data.startswith("vote_draw_"):
        match_id = int(data.split("_")[2])
        for match in matches_db:
            if match['id'] == match_id:
                match['draw_votes'] = match.get('draw_votes', 0) + 1
                query.edit_message_text("🗳️ صوتك للتعادل تم تسجيله!")
                return

# ========== صفحة الموقع ==========
HTML = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
        .status-upcoming{background:#3498db;color:#fff;padding:3px 12px;border-radius:20px;font-size:0.7em;display:inline-block;}
        .status-live{background:#e74c3c;color:#fff;padding:3px 12px;border-radius:20px;font-size:0.7em;display:inline-block;animation:blink 1s infinite;}
        @keyframes blink{50%{opacity:0.4;}}
        .footer{text-align:center;padding:30px;color:#555;border-top:1px solid #2a3f5f;margin-top:40px;}
        .footer a{color:#ffd700;text-decoration:none;}
        @media(max-width:600px){.header h1{font-size:2em;}}
    </style>
</head>
<body>
<div class="container">
<div class="header">
<h1>🏆 كأس العالم 2026</h1>
<p>جميع البطولات - جميع المباريات - جميع النتائج</p>
<div style="margin-top:15px;">
<a href="https://t.me/Ali_worldcup_bot" class="btn">🤖 البوت على تليجرام</a>
<a href="https://t.me/{{ channel_name }}" class="btn" style="background:transparent;border:2px solid #ffd700;color:#ffd700;">📢 القناة</a>
</div>
</div>
<div class="stats">
<div class="stat-box"><div class="number">{{ total }}</div><div class="label">كل المباريات</div></div>
<div class="stat-box"><div class="number">{{ today_count }}</div><div class="label">مباريات اليوم</div></div>
<div class="stat-box"><div class="number">{{ live_count }}</div><div class="label">مباشر</div></div>
</div>
<h2 class="section-title">⚽ المباريات</h2>
<div class="cards">
{% for match in matches %}
<div class="card">
<div class="tournament">🏆 {{ match.tournament }}</div>
<div class="stage">{{ match.stage }}</div>
{% if match.status == 'live' %}
<span class="status-live">🔴 مباشر</span>
{% else %}
<span class="status-upcoming">⏳ قادمة</span>
{% endif %}
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
<div class="footer">
<p>🏆 كأس العالم 2026 - جميع الحقوق محفوظة</p>
<p style="font-size:0.85em;color:#444;">🤖 <a href="https://t.me/Ali_worldcup_bot">@Ali_worldcup_bot</a></p>
</div>
</div>
</body>
</html>
"""

@app.route('/')
def home():
    matches = get_all_matches()
    total = len(matches)
    today_count = len(get_today_matches())
    live_count = len(get_live_matches())
    channel_name = CHANNEL_ID.replace('@', '')
    return render_template_string(
        HTML, 
        matches=matches, 
        total=total, 
        today_count=today_count,
        live_count=live_count,
        channel_name=channel_name
    )

# ========== تشغيل البوت ==========
def run_bot():
    if not BOT_TOKEN or BOT_TOKEN == "PUT_YOUR_BOT_TOKEN_HERE":
        logging.warning("⚠️ BOT_TOKEN غير مضبوط")
        return
    
    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("today", today_command))
    dp.add_handler(CommandHandler("live", live_command))
    dp.add_handler(CommandHandler("matches", matches_command))
    dp.add_handler(CommandHandler("send", send_command))
    dp.add_handler(CommandHandler("add", add_command))
    dp.add_handler(CommandHandler("set_live", set_live_command))
    dp.add_handler(CommandHandler("set_score", set_score_command))
    dp.add_handler(CommandHandler("delete", delete_command))
    dp.add_handler(CallbackQueryHandler(button_callback))
    
    # جدولة النشر التلقائي
    def schedule_check():
        while True:
            try:
                check_live_matches(updater)
                time.sleep(300)
            except Exception as e:
                logging.error(f"❌ خطأ: {e}")
                time.sleep(60)
    
    threading.Thread(target=schedule_check, daemon=True).start()
    
    logging.info("🤖 البوت يعمل...")
    updater.start_polling()
    updater.idle()

# ========== التشغيل ==========
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
