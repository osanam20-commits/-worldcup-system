import os
import logging
import threading
import time
import requests
from datetime import datetime, timedelta
from flask import Flask, render_template_string, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

# ========== إعدادات ==========
app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8689943788:AAFfmE62a4h-eLXYAcOXvSUgmkLs5KZZwts")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@lvFaax5HzsxOTU0")

# ========== قاعدة البيانات ==========
matches_db = []
match_id = 1

# ========== دوال المباريات ==========
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
        'away_score': 0,
        'home_votes': 0,
        'away_votes': 0,
        'draw_votes': 0
    }
    matches_db.append(match)
    match_id += 1
    return match

def get_today_matches():
    today = datetime.now().strftime("%Y-%m-%d")
    return [m for m in matches_db if m['date'] == today]

def get_live_matches():
    return [m for m in matches_db if m['status'] == 'live']

def get_upcoming_matches():
    today = datetime.now().strftime("%Y-%m-%d")
    return [m for m in matches_db if m['date'] >= today and m['status'] == 'upcoming']

def get_all_matches():
    return matches_db

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
    keyboard = [
        [
            InlineKeyboardButton(f"🏠 {match['home']}", callback_data=f"vote_home_{match['id']}"),
            InlineKeyboardButton(f"⚽ تعادل", callback_data=f"vote_draw_{match['id']}")
        ],
        [
            InlineKeyboardButton(f"✈️ {match['away']}", callback_data=f"vote_away_{match['id']}")
        ]
    ]
    
    if match['status'] == 'live':
        keyboard.append([
            InlineKeyboardButton("🔄 تحديث", callback_data=f"update_{match['id']}")
        ])
    
    return InlineKeyboardMarkup(keyboard)

# ========== دوال النشر التلقائي ==========
def send_match_to_channel(context, match):
    """إرسال مباراة إلى القناة"""
    try:
        card = create_match_card(match)
        keyboard = create_match_keyboard(match)
        context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=card,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        logging.info(f"✅ تم نشر المباراة: {match['home']} 🆚 {match['away']}")
        return True
    except Exception as e:
        logging.error(f"❌ خطأ في النشر: {e}")
        return False

def send_daily_matches(context):
    """نشر مباريات اليوم تلقائياً"""
    today_matches = get_today_matches()
    if not today_matches:
        context.bot.send_message(
            chat_id=CHANNEL_ID,
            text="📭 لا توجد مباريات اليوم"
        )
        return
    
    for match in today_matches:
        send_match_to_channel(context, match)
        time.sleep(1)

def check_live_matches(context):
    """التحقق من المباريات التي أصبحت مباشرة"""
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    today = now.strftime("%Y-%m-%d")
    
    for match in matches_db:
        if match['status'] == 'upcoming' and match['date'] == today:
            # إذا كان الوقت الحالي قريباً من وقت المباراة
            if match['time'] <= current_time <= (datetime.strptime(match['time'], "%H:%M") + timedelta(minutes=30)).strftime("%H:%M"):
                match['status'] = 'live'
                # إرسال إشعار
                context.bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=f"🔴 **المباراة أصبحت مباشرة!**\n\n{create_match_card(match)}",
                    parse_mode='Markdown'
                )
                logging.info(f"✅ تم تفعيل المباراة المباشرة: {match['home']} 🆚 {match['away']}")

# ========== صفحة الموقع ==========
HTML_TEMPLATE = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏆 كأس العالم 2026</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: linear-gradient(135deg, #0a0e1a, #1a1f35);
            color: #fff;
            font-family: 'Tajawal', Arial, sans-serif;
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header {
            text-align: center;
            padding: 40px;
            background: linear-gradient(145deg, #1a1f35, #2a3f5f);
            border-radius: 20px;
            margin-bottom: 30px;
            border: 1px solid rgba(255, 215, 0, 0.2);
        }
        .header h1 { font-size: 3.5em; color: #ffd700; }
        .header p { color: #aaa; font-size: 1.2em; margin-top: 10px; }
        .btn {
            display: inline-block;
            padding: 12px 30px;
            background: linear-gradient(135deg, #ffd700, #f5a623);
            color: #1a1f35;
            text-decoration: none;
            border-radius: 30px;
            font-weight: bold;
            margin: 5px;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        .stat-box {
            background: #1a1f35;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            border: 1px solid #2a3f5f;
        }
        .stat-box .number { font-size: 2.5em; color: #ffd700; font-weight: bold; }
        .stat-box .label { color: #aaa; }
        .section-title {
            font-size: 2em;
            color: #ffd700;
            margin: 30px 0 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid rgba(255, 215, 0, 0.2);
        }
        .cards {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 25px;
            margin-bottom: 40px;
        }
        .card {
            background: linear-gradient(145deg, #1a1f35, #252a45);
            padding: 25px;
            border-radius: 18px;
            border: 1px solid #2a3f5f;
            text-align: center;
            transition: 0.3s;
        }
        .card:hover { border-color: #ffd700; transform: translateY(-5px); }
        .card .tournament { color: #ffd700; font-size: 0.9em; margin-bottom: 5px; }
        .card .stage {
            background: rgba(255, 215, 0, 0.15);
            color: #ffd700;
            padding: 3px 15px;
            border-radius: 20px;
            font-size: 0.8em;
            display: inline-block;
        }
        .card .status-badge {
            padding: 3px 12px;
            border-radius: 20px;
            font-size: 0.7em;
            display: inline-block;
            margin: 5px 0;
        }
        .status-upcoming { background: #3498db; color: #fff; }
        .status-live { background: #e74c3c; color: #fff; animation: blink 1s infinite; }
        .status-finished { background: #2ecc71; color: #fff; }
        @keyframes blink { 50% { opacity: 0.4; } }
        .card .teams { font-size: 1.5em; font-weight: bold; margin: 15px 0; }
        .card .teams .home { color: #2ecc71; }
        .card .teams .away { color: #e74c3c; }
        .card .teams .vs { color: #ffd700; margin: 0 10px; }
        .card .info { color: #aaa; line-height: 1.8; }
        .card .info span { color: #fff; }
        .card .score { font-size: 2em; color: #ffd700; margin: 10px 0; }
        .card .match-id { color: #555; font-size: 0.7em; margin-top: 10px; }
        .footer {
            text-align: center;
            padding: 30px;
            color: #555;
            border-top: 1px solid #2a3f5f;
            margin-top: 40px;
        }
        .footer a { color: #ffd700; text-decoration: none; }
        @media (max-width: 600px) {
            .header h1 { font-size: 2em; }
            .card .teams { font-size: 1.2em; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏆 كأس العالم 2026</h1>
            <p>جميع البطولات - جميع المباريات - جميع النتائج</p>
            <div style="margin-top: 15px;">
                <a href="https://t.me/Ali_worldcup_bot" class="btn">🤖 البوت على تليجرام</a>
            </div>
        </div>

        <div class="stats">
            <div class="stat-box"><div class="number">{{ total }}</div><div class="label">كل المباريات</div></div>
            <div class="stat-box"><div class="number">{{ live_count }}</div><div class="label">مباشر</div></div>
            <div class="stat-box"><div class="number">{{ upcoming_count }}</div><div class="label">قادمة</div></div>
        </div>

        <h2 class="section-title">⚽ مباريات اليوم</h2>
        <div class="cards">
            {% for match in today_matches %}
            <div class="card">
                <div class="tournament">🏆 {{ match.tournament }}</div>
                <div class="stage">{{ match.stage }}</div>
                <div class="status-badge status-{{ match.status }}">
                    {% if match.status == 'live' %}🔴 مباشر{% elif match.status == 'finished' %}✅ انتهت{% else %}⏳ قادمة{% endif %}
                </div>
                <div class="teams">
                    <span class="home">{{ match.home_flag }} {{ match.home }}</span>
                    <span class="vs">⚔️</span>
                    <span class="away">{{ match.away_flag }} {{ match.away }}</span>
                </div>
                {% if match.status == 'live' %}
                <div class="score">{{ match.home_score }} - {{ match.away_score }}</div>
                {% endif %}
                <div class="info">
                    📍 <span>{{ match.stadium }}</span><br>
                    📅 <span>{{ match.date }}</span> | 🕒 <span>{{ match.time }}</span>
                </div>
                <div class="match-id">#{{ match.id }}</div>
            </div>
            {% else %}
            <div class="card" style="grid-column:1/-1;padding:40px;">
                <p>📭 لا توجد مباريات اليوم</p>
                <p style="color:#aaa;margin-top:10px;">يمكنك إضافة مباريات عبر البوت</p>
            </div>
            {% endfor %}
        </div>

        <h2 class="section-title">🔴 مباريات مباشرة</h2>
        <div class="cards">
            {% for match in live_matches %}
            <div class="card" style="border-color:#e74c3c;">
                <div class="tournament">🏆 {{ match.tournament }}</div>
                <div class="stage">{{ match.stage }}</div>
                <div class="status-badge status-live">🔴 مباشر</div>
                <div class="teams">
                    <span class="home">{{ match.home_flag }} {{ match.home }}</span>
                    <span class="vs">⚔️</span>
                    <span class="away">{{ match.away_flag }} {{ match.away }}</span>
                </div>
                <div class="score">{{ match.home_score }} - {{ match.away_score }}</div>
                <div class="info">
                    📍 <span>{{ match.stadium }}</span><br>
                    📅 <span>{{ match.date }}</span> | 🕒 <span>{{ match.time }}</span>
                </div>
            </div>
            {% else %}
            <div class="card" style="grid-column:1/-1;padding:40px;">
                <p>🔴 لا توجد مباريات مباشرة</p>
            </div>
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
    total = len(get_all_matches())
    live_count = len(get_live_matches())
    upcoming_count = len(get_upcoming_matches())
    today_matches = get_today_matches()
    live_matches = get_live_matches()
    
    return render_template_string(
        HTML_TEMPLATE,
        total=total,
        live_count=live_count,
        upcoming_count=upcoming_count,
        today_matches=today_matches,
        live_matches=live_matches
    )

@app.route('/api/matches')
def api_matches():
    """API للمباريات"""
    return jsonify(get_all_matches())

# ========== أوامر البوت ==========
def start(update: Update, context):
    update.message.reply_text(
        "🎉 **مرحباً بك في بوت كأس العالم 2026!**\n\n"
        "📌 **الأوامر المتاحة:**\n"
        "/start - بدء البوت\n"
        "/help - المساعدة\n"
        "/today - مباريات اليوم\n"
        "/live - المباريات المباشرة\n"
        "/matches - جميع المباريات\n"
        "/send - نشر مباريات اليوم في القناة\n\n"
        "🏆 **للمشرفين:**\n"
        "/add_match الفريق1 الفريق2 الملعب التاريخ الوقت البطولة المرحلة\n"
        "/set_live معرف_المباراة\n"
        "/set_score معرف_المباراة هدف1 هدف2\n"
        "/delete_match معرف_المباراة",
        parse_mode='Markdown'
    )

def help_command(update: Update, context):
    update.message.reply_text(
        "❓ **المساعدة:**\n\n"
        "📌 **للمشاهدة:**\n"
        "/today - مباريات اليوم\n"
        "/live - المباريات المباشرة\n"
        "/matches - جميع المباريات\n\n"
        "📌 **للنشر:**\n"
        "/send - نشر مباريات اليوم في القناة\n\n"
        "📌 **للمشرفين:**\n"
        "/add_match الفريق1 الفريق2 الملعب التاريخ الوقت البطولة المرحلة\n"
        "/set_live معرف_المباراة\n"
        "/set_score معرف_المباراة هدف1 هدف2\n"
        "/delete_match معرف_المباراة\n\n"
        "مثال: /add_match الهلال النصر ملعب_الملك_فهد 2026-07-06 20:00 دوري_روشن نهائي",
        parse_mode='Markdown'
    )

def today_command(update: Update, context):
    matches = get_today_matches()
    if not matches:
        update.message.reply_text("📭 لا توجد مباريات اليوم")
        return
    
    text = "📅 **مباريات اليوم:**\n\n"
    for m in matches:
        status_emoji = "🔴" if m['status'] == 'live' else "⏳"
        text += f"{status_emoji} {m['home_flag']} {m['home']} 🆚 {m['away_flag']} {m['away']}\n"
        text += f"🏆 {m['tournament']} | 📍 {m['stadium']} | 🕒 {m['time']}\n"
        if m['status'] == 'live':
            text += f"⚽ {m['home_score']} - {m['away_score']}\n"
        text += "\n"
    
    update.message.reply_text(text, parse_mode='Markdown')

def live_command(update: Update, context):
    matches = get_live_matches()
    if not matches:
        update.message.reply_text("🔴 لا توجد مباريات مباشرة")
        return
    
    text = "🔴 **المباريات المباشرة:**\n\n"
    for m in matches:
        text += f"{m['home_flag']} {m['home']} {m['home_score']} - {m['away_score']} {m['away_flag']} {m['away']}\n"
        text += f"🏆 {m['tournament']} | 📍 {m['stadium']}\n\n"
    
    update.message.reply_text(text, parse_mode='Markdown')

def matches_command(update: Update, context):
    matches = get_all_matches()
    if not matches:
        update.message.reply_text("📭 لا توجد مباريات")
        return
    
    text = "📋 **جميع المباريات:**\n\n"
    for m in matches:
        status_emoji = "🔴" if m['status'] == 'live' else "⏳" if m['status'] == 'upcoming' else "✅"
        text += f"{status_emoji} #{m['id']} {m['home_flag']} {m['home']} 🆚 {m['away_flag']} {m['away']}\n"
        text += f"🏆 {m['tournament']} | 📅 {m['date']} | 🕒 {m['time']}\n\n"
    
    update.message.reply_text(text, parse_mode='Markdown')

def send_command(update: Update, context):
    """نشر مباريات اليوم في القناة"""
    try:
        today_matches = get_today_matches()
        if not today_matches:
            update.message.reply_text("📭 لا توجد مباريات اليوم للنشر")
            return
        
        for match in today_matches:
            send_match_to_channel(context, match)
            time.sleep(1)
        
        update.message.reply_text(f"✅ تم نشر {len(today_matches)} مباراة في القناة!")
    except Exception as e:
        update.message.reply_text(f"❌ خطأ: {e}")

def add_match_command(update: Update, context):
    """إضافة مباراة جديدة"""
    try:
        args = context.args
        if len(args) < 7:
            update.message.reply_text(
                "⚠️ الصيغة: /add_match الفريق1 الفريق2 الملعب التاريخ الوقت البطولة المرحلة\n"
                "مثال: /add_match الهلال النصر ملعب_الملك_فهد 2026-07-06 20:00 دوري_روشن نهائي"
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
            f"🏆 {match['tournament']}\n"
            f"{match['home']} 🆚 {match['away']}\n"
            f"📍 {match['stadium']} | 📅 {match['date']} | 🕒 {match['time']}"
        )
        
        # نشر المباراة في القناة تلقائياً
        send_match_to_channel(context, match)
        
    except Exception as e:
        update.message.reply_text(f"❌ خطأ: {e}")

def set_live_command(update: Update, context):
    """تفعيل مباراة كمباشرة"""
    try:
        match_id = int(context.args[0])
        for match in matches_db:
            if match['id'] == match_id:
                match['status'] = 'live'
                update.message.reply_text(f"✅ تم تفعيل المباراة #{match_id} كمباشرة")
                context.bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=f"🔴 **المباراة أصبحت مباشرة!**\n\n{create_match_card(match)}",
                    parse_mode='Markdown'
                )
                return
        update.message.reply_text(f"❌ المباراة #{match_id} غير موجودة")
    except Exception as e:
        update.message.reply_text(f"❌ خطأ: {e}")

def set_score_command(update: Update, context):
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
                context.bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=f"⚽ **تحديث النتيجة:**\n\n{create_match_card(match)}",
                    parse_mode='Markdown'
                )
                return
        update.message.reply_text(f"❌ المباراة #{match_id} غير موجودة")
    except Exception as e:
        update.message.reply_text(f"❌ خطأ: {e}")

def delete
