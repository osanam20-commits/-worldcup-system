import os
import logging
import threading
import time
from flask import Flask, render_template_string
from datetime import datetime, timedelta

# ========== إعدادات Flask ==========
app = Flask(__name__)

# ========== قاعدة بيانات المباريات ==========
all_matches = []
match_id = 1

# ========== إضافة مباراة ==========
def add_match(home, away, home_flag="🏴", away_flag="🏴", stadium="", 
              date="", time="", stage="دور المجموعات", tournament="كأس العالم"):
    global match_id
    if not date:
        date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
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
        'status': 'upcoming',  # upcoming, live, finished
        'home_score': 0,
        'away_score': 0,
        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    all_matches.append(match)
    match_id += 1
    return match

# ========== مباريات تجريبية ==========
add_match("الهلال", "النصر", "🇸🇦", "🇸🇦", "ملعب الملك فهد", "2026-07-15", "20:00", "نهائي", "دوري روشن")
add_match("الأهلي", "الترجي", "🇪🇬", "🇹🇳", "استاد القاهرة", "2026-07-16", "21:00", "نصف نهائي", "دوري أبطال أفريقيا")
add_match("الوداد", "الرجاء", "🇲🇦", "🇲🇦", "ملعب محمد الخامس", "2026-07-17", "19:00", "ربع نهائي", "البطولة العربية")
add_match("ريال مدريد", "برشلونة", "🇪🇸", "🇪🇸", "سانتياغو برنابيو", "2026-07-18", "22:00", "نهائي", "الدوري الإسباني")
add_match("بايرن", "بوروسيا", "🇩🇪", "🇩🇪", "أليانز أرينا", "2026-07-19", "21:30", "نهائي", "الدوري الألماني")
add_match("مانشستر سيتي", "ليفربول", "🏴", "🏴", "الاتحاد", "2026-07-20", "20:00", "نهائي", "الدوري الإنجليزي")

# ========== دوال مساعدة ==========
def get_tournaments():
    """جلب جميع البطولات"""
    return list(set(m['tournament'] for m in all_matches))

def get_matches_by_tournament(tournament):
    """جلب مباريات بطولة معينة"""
    return [m for m in all_matches if m['tournament'] == tournament]

def get_today_matches():
    """جلب مباريات اليوم"""
    today = datetime.now().strftime("%Y-%m-%d")
    return [m for m in all_matches if m['date'] == today]

def get_live_matches():
    """جلب المباريات المباشرة"""
    return [m for m in all_matches if m['status'] == 'live']

def get_upcoming_matches():
    """جلب المباريات القادمة"""
    today = datetime.now().strftime("%Y-%m-%d")
    return [m for m in all_matches if m['status'] == 'upcoming' and m['date'] >= today]

def create_match_card(match):
    """إنشاء بطاقة مباراة نصية"""
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
        f"🆔 #{match['id']}"
    )
    
    return card

# ========== قالب الموقع ==========
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
        
        .filter-buttons {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 20px;
        }
        .filter-btn {
            padding: 8px 20px;
            background: #1a1f35;
            color: #aaa;
            border: 1px solid #2a3f5f;
            border-radius: 25px;
            cursor: pointer;
            text-decoration: none;
            transition: 0.3s;
        }
        .filter-btn:hover, .filter-btn.active {
            background: #ffd700;
            color: #1a1f35;
            border-color: #ffd700;
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
        .card:hover {
            border-color: #ffd700;
            transform: translateY(-5px);
        }
        .card .tournament {
            color: #ffd700;
            font-size: 0.9em;
            margin-bottom: 5px;
        }
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
        .btn:hover { transform: scale(1.05); }
        
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
                <a href="/tournaments" class="btn" style="background:transparent;border:2px solid #ffd700;color:#ffd700;">🏆 البطولات</a>
            </div>
        </div>

        <div class="stats">
            <div class="stat-box"><div class="number">{{ total }}</div><div class="label">كل المباريات</div></div>
            <div class="stat-box"><div class="number">{{ live_count }}</div><div class="label">مباشر</div></div>
            <div class="stat-box"><div class="number">{{ tournaments_count }}</div><div class="label">بطولات</div></div>
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
            <p style="font-size:0.85em;color:#444;">
                🤖 <a href="https://t.me/Ali_worldcup_bot">@Ali_worldcup_bot</a>
            </p>
        </div>
    </div>
</body>
</html>
"""

# ========== صفحات الموقع ==========
@app.route('/')
def home():
    total = len(all_matches)
    live_count = len(get_live_matches())
    tournaments_count = len(get_tournaments())
    today_matches = get_today_matches()
    live_matches = get_live_matches()
    
    return render_template_string(
        HTML_TEMPLATE,
        total=total,
        live_count=live_count,
        tournaments_count=tournaments_count,
        today_matches=today_matches,
        live_matches=live_matches
    )

@app.route('/tournaments')
def tournaments_page():
    tournaments = get_tournaments()
    html = """
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🏆 البطولات - كأس العالم 2026</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                background: linear-gradient(135deg, #0a0e1a, #1a1f35);
                color: #fff;
                font-family: Arial, sans-serif;
                min-height: 100vh;
                padding: 20px;
            }
            .container { max-width: 800px; margin: 0 auto; }
            .header {
                text-align: center;
                padding: 30px;
                background: linear-gradient(145deg, #1a1f35, #2a3f5f);
                border-radius: 20px;
                margin-bottom: 30px;
                border: 1px solid rgba(255, 215, 0, 0.2);
            }
            .header h1 { color: #ffd700; font-size: 2.5em; }
            .header a { color: #ffd700; text-decoration: none; }
            .card {
                background: #1a1f35;
                padding: 20px 30px;
                border-radius: 15px;
                margin-bottom: 15px;
                border: 1px solid #2a3f5f;
                display: flex;
                justify-content: space-between;
                align-items: center;
                transition: 0.3s;
            }
            .card:hover { border-color: #ffd700; }
            .card .name { font-size: 1.3em; color: #ffd700; }
            .card .count { color: #aaa; }
            .btn {
                display: inline-block;
                padding: 12px 30px;
                background: linear-gradient(135deg, #ffd700, #f5a623);
                color: #1a1f35;
                text-decoration: none;
                border-radius: 30px;
                font-weight: bold;
            }
            .btn-secondary {
                background: transparent;
                color: #ffd700;
                border: 2px solid #ffd700;
            }
            .footer {
                text-align: center;
                padding: 30px;
                color: #555;
                border-top: 1px solid #2a3f5f;
                margin-top: 40px;
            }
            .footer a { color: #ffd700; text-decoration: none; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏆 البطولات</h1>
                <a href="/">🏠 العودة للرئيسية</a>
            </div>
    """
    
    for t in tournaments:
        count = len(get_matches_by_tournament(t))
        html += f"""
            <div class="card">
                <span class="name">🏆 {t}</span>
                <span class="count">{count} مباراة</span>
            </div>
        """
    
    html += """
            <div style="text-align:center;margin-top:20px;">
                <a href="/" class="btn">🏠 الرئيسية</a>
            </div>
            <div class="footer">
                <p>🏆 كأس العالم 2026 - جميع الحقوق محفوظة</p>
                <p style="font-size:0.85em;color:#444;">🤖 <a href="https://t.me/Ali_worldcup_bot">@Ali_worldcup_bot</a></p>
            </div>
        </div>
    </body>
    </html>
    """
    return html

# ========== بوت التليجرام ==========
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

BOT_TOKEN = os.environ.get("BOT_TOKEN", "PUT_YOUR_BOT_TOKEN_HERE")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@your_channel")

def start(update: Update, context):
    update.message.reply_text(
        "🎉 **مرحباً بك في بوت كأس العالم 2026!**\n\n"
        "📌 **الأوامر المتاحة:**\n"
        "/start - بدء البوت\n"
        "/help - المساعدة\n"
        "/today - مباريات اليوم\n"
        "/live - المباريات المباشرة\n"
        "/matches - جميع المباريات\n"
        "/tournaments - البطولات\n"
        "/send - نشر بطاقات اليوم للقناة\n\n"
        "🏆 جميع البطولات - جميع المباريات",
        parse_mode='Markdown'
    )

def help_command(update: Update, context):
    update.message.reply_text(
        "❓ **المساعدة:**\n\n"
        "/start - بدء البوت\n"
        "/help - هذه الرسالة\n"
        "/today - مباريات اليوم\n"
        "/live - المباريات المباشرة\n"
        "/matches - جميع المباريات\n"
        "/tournaments - قائمة البطولات\n"
        "/send - نشر بطاقات اليوم للقناة\n\n"
        "📌 **للمشرفين:**\n"
        "/add_match الفريق1 الفريق2 الملعب التاريخ الوقت البطولة المرحلة\n"
        "/set_live معرف_المباراة\n"
        "/set_score معرف_المباراة هدف1 هدف2",
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
        text += f"🏆 {m['tournament']} | 📍 {m['stadium']} | 🕒 {m['time']}\n\n"
    
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
    if not all_matches:
        update.message.reply_text("📭 لا توجد مباريات")
        return
    
    text = "📋 **جميع المباريات:**\n\n"
    for m in all_matches:
        status_emoji = "🔴" if m['status'] == 'live' else "⏳" if m['status'] == 'upcoming' else "✅"
        text += f"{status_emoji} #{m['id']} {m['home_flag']} {m['home']} 🆚 {m['away_flag']} {m['away']}\n"
        text += f"🏆 {m['tournament']} | 📅 {m['date']} | 🕒 {m['time']}\n\n"
    
    update.message.reply_text(text, parse_mode='Markdown')

def tournaments_command(update: Update, context):
    tournaments = get_tournaments()
    if not tournaments:
        update.message.reply_text("📭 لا توجد بطولات")
        return
    
    text = "🏆 **البطولات:**\n\n"
    for t in tournaments:
        count = len(get_matches_by_tournament(t))
        text += f"🏆 {t} - {count} مباراة\n"
    
    update.message.reply_text(text, parse_mode='Markdown')

def send_command(update: Update, context):
    """إرسال بطاقات اليوم إلى القناة"""
    try:
        today_matches = get_today_matches()
        if not today_matches:
            update.message.reply_text("📭 لا توجد مباريات اليوم")
            return
        
        for match in today_matches:
            card = create_match_card(match)
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButt
