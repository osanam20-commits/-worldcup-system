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

# ========== كأس العالم 2026 ==========
def add_worldcup_matches():
    # دور الـ16
    add_match("فرنسا", "باراغواي", "🇫🇷", "🇵🇾", "ملعب أمريكا", "2026-07-04", "18:00", "دور الـ16", "كأس العالم 2026")
    add_match("المغرب", "كندا", "🇲🇦", "🇨🇦", "ملعب أمريكا", "2026-07-04", "21:00", "دور الـ16", "كأس العالم 2026")
    add_match("البرازيل", "النرويج", "🇧🇷", "🇳🇴", "ملعب أمريكا", "2026-07-05", "16:00", "دور الـ16", "كأس العالم 2026")
    add_match("المكسيك", "إنجلترا", "🇲🇽", "🏴", "ملعب أمريكا", "2026-07-05", "20:00", "دور الـ16", "كأس العالم 2026")
    add_match("البرتغال", "إسبانيا", "🇵🇹", "🇪🇸", "ملعب أمريكا", "2026-07-06", "15:00", "دور الـ16", "كأس العالم 2026")
    add_match("أمريكا", "بلجيكا", "🇺🇸", "🇧🇪", "ملعب أمريكا", "2026-07-06", "20:00", "دور الـ16", "كأس العالم 2026")
    add_match("الأرجنتين", "مصر", "🇦🇷", "🇪🇬", "ملعب أمريكا", "2026-07-07", "12:00", "دور الـ16", "كأس العالم 2026")
    add_match("سويسرا", "كولومبيا", "🇨🇭", "🇨🇴", "ملعب أمريكا", "2026-07-07", "16:00", "دور الـ16", "كأس العالم 2026")
    
    # ربع النهائي
    add_match("فرنسا", "المغرب", "🇫🇷", "🇲🇦", "ملعب أمريكا", "2026-07-09", "18:00", "ربع النهائي", "كأس العالم 2026")
    add_match("البرتغال/إسبانيا", "أمريكا/بلجيكا", "🇵🇹", "🇺🇸", "ملعب أمريكا", "2026-07-10", "18:00", "ربع النهائي", "كأس العالم 2026")
    add_match("البرازيل/النرويج", "المكسيك/إنجلترا", "🇧🇷", "🇲🇽", "ملعب أمريكا", "2026-07-11", "16:00", "ربع النهائي", "كأس العالم 2026")
    add_match("الأرجنتين/مصر", "سويسرا/كولومبيا", "🇦🇷", "🇨🇭", "ملعب أمريكا", "2026-07-11", "20:00", "ربع النهائي", "كأس العالم 2026")
    
    # نصف النهائي
    add_match("الفائز ربع الأول", "الفائز ربع الثاني", "🏆", "🏆", "أرلينغتون", "2026-07-14", "18:00", "نصف النهائي", "كأس العالم 2026")
    add_match("الفائز ربع الثالث", "الفائز ربع الرابع", "🏆", "🏆", "أتلانتا", "2026-07-15", "18:00", "نصف النهائي", "كأس العالم 2026")
    
    # المركز الثالث والنهائي
    add_match("المركز الثالث", "المركز الثالث", "🥉", "🥉", "ميامي", "2026-07-18", "17:00", "المركز الثالث", "كأس العالم 2026")
    add_match("النهائي", "النهائي", "🏆", "🏆", "ملعب ميتلايف، نيوجيرسي", "2026-07-19", "15:00", "النهائي", "كأس العالم 2026")

# ========== الدوريات الخمسة الكبار ==========
def add_top_leagues():
    # الدوري الإنجليزي
    add_match("مانشستر سيتي", "آرسنال", "🏴", "🏴", "الاتحاد", "2026-08-10", "18:30", "الجولة 1", "الدوري الإنجليزي")
    add_match("ليفربول", "تشيلسي", "🏴", "🏴", "أنفيلد", "2026-08-10", "21:00", "الجولة 1", "الدوري الإنجليزي")
    
    # الدوري الإسباني
    add_match("ريال مدريد", "برشلونة", "🇪🇸", "🇪🇸", "سانتياغو برنابيو", "2026-08-11", "22:00", "الجولة 1", "الدوري الإسباني")
    add_match("أتلتيكو", "فالنسيا", "🇪🇸", "🇪🇸", "ميتروبوليتانو", "2026-08-11", "20:00", "الجولة 1", "الدوري الإسباني")
    
    # الدوري الإيطالي
    add_match("يوفنتوس", "ميلان", "🇮🇹", "🇮🇹", "أليانز", "2026-08-12", "20:45", "الجولة 1", "الدوري الإيطالي")
    add_match("إنتر ميلان", "روما", "🇮🇹", "🇮🇹", "جوزيبي مياتزا", "2026-08-12", "18:30", "الجولة 1", "الدوري الإيطالي")
    
    # الدوري الألماني
    add_match("بايرن ميونخ", "بوروسيا دورتموند", "🇩🇪", "🇩🇪", "أليانز أرينا", "2026-08-13", "20:30", "الجولة 1", "الدوري الألماني")
    
    # الدوري الفرنسي
    add_match("باريس سان جيرمان", "مارسيليا", "🇫🇷", "🇫🇷", "بارك دي برينس", "2026-08-14", "21:00", "الجولة 1", "الدوري الفرنسي")

# ========== الدوري اليمني ==========
def add_yemeni_league():
    add_match("أهلي صنعاء", "الوحدة", "🇾🇪", "🇾🇪", "ملعب صنعاء", "2026-08-15", "16:00", "الجولة 1", "الدوري اليمني")
    add_match("شعب إب", "التلال", "🇾🇪", "🇾🇪", "ملعب إب", "2026-08-15", "18:00", "الجولة 1", "الدوري اليمني")
    add_match("اليرموك", "حسان", "🇾🇪", "🇾🇪", "ملعب عدن", "2026-08-16", "16:00", "الجولة 1", "الدوري اليمني")

# ========== إضافة جميع المباريات ==========
add_worldcup_matches()
add_top_leagues()
add_yemeni_league()

# ========== دوال المساعدة ==========
def get_today_matches():
    today = datetime.now().strftime("%Y-%m-%d")
    return [m for m in matches_db if m['date'] == today]

def get_live_matches():
    return [m for m in matches_db if m['status'] == 'live']

def get_matches_by_tournament(tournament):
    return [m for m in matches_db if m['tournament'] == tournament]

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
        f"📊 الحالة: {status_text} {status_emoji}"
    )
    
    return card

def send_match_to_channel(context, match):
    try:
        card = create_match_card(match)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"🏠 {match['home']}", callback_data=f"vote_home_{match['id']}"),
             InlineKeyboardButton(f"✈️ {match['away']}", callback_data=f"vote_away_{match['id']}")],
            [InlineKeyboardButton("⚽ تعادل", callback_data=f"vote_draw_{match['id']}")]
        ])
        context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=card,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        return True
    except Exception as e:
        logging.error(f"❌ خطأ في النشر: {e}")
        return False

def send_daily_matches(context):
    today_matches = get_today_matches()
    if not today_matches:
        context.bot.send_message(chat_id=CHANNEL_ID, text="📭 لا توجد مباريات اليوم")
        return
    for match in today_matches:
        send_match_to_channel(context, match)
        time.sleep(1)

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
        @keyframes blink { 50% { opacity: 0.4; } }
        .card .teams { font-size: 1.5em; font-weight: bold; margin: 15px 0; }
        .card .teams .home { color: #2ecc71; }
        .card .teams .away { color: #e74c3c; }
        .card .teams .vs { color: #ffd700; margin: 0 10px; }
        .card .info { color: #aaa; line-height: 1.8; }
        .card .info span { color: #fff; }
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
            text-decoration: none;
            transition: 0.3s;
        }
        .filter-btn:hover, .filter-btn.active {
            background: #ffd700;
            color: #1a1f35;
        }
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
            <div class="stat-box"><div class="number">{{ tournaments }}</div><div class="label">بطولات</div></div>
            <div class="stat-box"><div class="number">{{ today_count }}</div><div class="label">مباريات اليوم</div></div>
        </div>

        <div class="filter-buttons">
            <a href="/" class="filter-btn active">🏆 الكل</a>
            <a href="/?tournament=كأس%20العالم%202026" class="filter-btn">🌍 كأس العالم</a>
            <a href="/?tournament=الدوري%20الإنجليزي" class="filter-btn">🏴 الدوري الإنجليزي</a>
            <a href="/?tournament=الدوري%20الإسباني" class="filter-btn">🇪🇸 الدوري الإسباني</a>
            <a href="/?tournament=الدوري%20الإيطالي" class="filter-btn">🇮🇹 الدوري الإيطالي</a>
            <a href="/?tournament=الدوري%20الألماني" class="filter-btn">🇩🇪 الدوري الألماني</a>
            <a href="/?tournament=الدوري%20الفرنسي" class="filter-btn">🇫🇷 الدوري الفرنسي</a>
            <a href="/?tournament=الدوري%20اليمني" class="filter-btn">🇾🇪 الدوري اليمني</a>
        </div>

        <h2 class="section-title">⚽ المباريات</h2>
        <div class="cards">
            {% for match in matches %}
            <div class="card">
                <div class="tournament">🏆 {{ match.tournament }}</div>
                <div class="stage">{{ match.stage }}</div>
                <div class="status-badge status-{{ match.status }}">
                    {% if match.status == 'live' %}🔴 مباشر{% else %}⏳ قادمة{% endif %}
                </div>
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
            <div class="card" style="grid-column:1/-1;padding:40px;">
                <p>📭 لا توجد مباريات</p>
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
    tournament = request.args.get('tournament')
    if tournament:
        matches = get_matches_by_tournament(tournament)
    else:
        matches = get_all_matches()
    
    total = len(get_all_matches())
    tournaments = len(set(m['tournament'] for m in matches_db))
    today_count = len(get_today_matches())
    
    return render_template_string(
        HTML_TEMPLATE,
        matches=matches,
        total=total,
        tournaments=tournaments,
        today_count=today_count
    )

# ========== أوامر البوت ==========
def start(update, context):
    update.message.reply_text(
        "🎉 **مرحباً بك في بوت كأس العالم 2026!**\n\n"
        "📌 **الأوامر المتاحة:**\n"
        "/today - مباريات اليوم\n"
        "/matches - جميع المباريات\n"
        "/worldcup - مباريات كأس العالم\n"
        "/leagues - الدوريات الخمسة\n"
        "/yemen - الدوري اليمني\n"
        "/send - نشر مباريات اليوم في القناة",
        parse_mode='Markdown'
    )

def today_command(update, context):
    matches = get_today_matches()
    if not matches:
        update.message.reply_text("📭 لا توجد مباريات اليوم")
        return
    text = "📅 مباريات اليوم:\n\n"
    for m in matches:
        text += f"{m['home_flag']} {m['home']} 🆚 {m['away_flag']} {m['away']}\n"
        text += f"🏆 {m['tournament']} | 📍 {m['stadium']} | 🕒 {m['time']}\n\n"
    update.message.reply_text(text)

def matches_command(update, context):
    text = "📋 جميع المباريات:\n\n"
    for m in matches_db[:20]:
        text += f"#{m['id']} {m['home_flag']} {m['home']} 🆚 {m['away_flag']} {m['away']}\n"
        text += f"🏆 {m['tournament']} | 📅 {m['date']} | 🕒 {m['time']}\n\n"
    update.message.reply_text(text)

def worldcup_command(update, context):
    matches = get_matches_by_tournament("كأس العالم 2026")
    if not matches:
        update.message.reply_text("📭 لا توجد مباريات")
        return
    text = "🌍 مباريات كأس العالم 2026:\n\n"
    for m in matches:
        text += f"{m['home_flag']} {m['home']} 🆚 {m['away_flag']} {m['away']}\n"
        text += f"📌 {m['stage']} | 📅 {m['date']} | 🕒 {m['time']}\n\n"
    update.message.reply_text(text)

def leagues_command(update, context):
    leagues = ["الدوري الإنجليزي", "الدوري الإسباني", "الدوري الإيطالي", "الدوري الألماني", "الدوري الفرنسي"]
    text = "🏆 الدوريات الخمسة الكبار:\n\n"
    for league in leagues:
        count = len(get_matches_by_tournament(league))
        text += f"🏆 {league} - {count} مباراة\n"
    update.message.reply_text(text)

def yemen_command(update, context):
    matches = get_matches_by_tournament("الدوري اليمني")
    if not matches:
        update.message.reply_text("📭 لا توجد مباريات في الدوري اليمني")
        return
    text = "🇾🇪 مباريات الدوري اليمني:\n\n"
    for m in matches:
        text += f"{m['home_flag']} {m['home']} 🆚 {m['away_flag']} {m['away']}\n"
        text += f"📍 {m['stadium']} | 📅 {m['date']} | 🕒 {m['time']}\n\n"
    update.message.reply_text(text)

def send_command(update, context):
    try:
        today_matches = get_today_matches()
        if not today_matches:
            update.message.reply_text("📭 لا توجد مباريات اليوم")
            return
        for match in today_matches:
            send_match_to_channel(context, match)
            time.sleep(1)
        update.message.reply_text(f"✅ تم نشر {len(today_matches)} مباراة في القناة!")
    except Exception as e:
        update.message.reply_text(f"❌ خطأ: {e}")

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

def run_bot():
    if not BOT_TOKEN or BOT_TOKEN == "PUT_YOUR_BOT_TOKEN_HERE":
        logging.warning("⚠️ BOT_TOKEN غير مضبوط")
        return
    
    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("today", today_command))
    dp.add_handler(CommandHandler("matches", matches_command))
    dp.add_handler(CommandHandler("worldcup", worldcup_command))
    dp.add_handler(CommandHandler("leagues", leagues_command))
    dp.add_handler(CommandHandler("yemen", yemen_command))
    dp.add_handler(CommandH
