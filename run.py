import os
import logging
import threading
import time
from datetime import datetime, timedelta
from flask import Flask, render_template_string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

# ========== الإعدادات ==========
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8689943788:AAFfmE62a4h-eLXYAcOXvSUgmkLs5KZZwts")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@your_channel")

# ========== قاعدة بيانات مؤقتة (في الذاكرة) ==========
matches_db = []
match_id_counter = 1

# ========== فلاسك ==========
app = Flask(__name__)

# ========== دوال المباريات ==========
def add_match(home, away, home_flag="🏴", away_flag="🏴", stadium="", date="", time="", stage="دور المجموعات", status="upcoming"):
    """إضافة مباراة جديدة"""
    global match_id_counter
    match = {
        'id': match_id_counter,
        'home': home,
        'away': away,
        'home_flag': home_flag,
        'away_flag': away_flag,
        'stadium': stadium,
        'date': date or datetime.now().strftime("%Y-%m-%d"),
        'time': time or datetime.now().strftime("%H:%M"),
        'stage': stage,
        'status': status,  # upcoming, live, finished
        'home_score': 0,
        'away_score': 0,
        'home_votes': 0,
        'away_votes': 0,
        'draw_votes': 0
    }
    matches_db.append(match)
    match_id_counter += 1
    return match

# إضافة مباريات تجريبية
add_match("الهلال", "العين", "🇸🇦", "🇦🇪", "ملعب الملك فهد", "2026-07-10", "20:00")
add_match("الأهلي", "الترجي", "🇪🇬", "🇹🇳", "استاد القاهرة", "2026-07-11", "21:00")
add_match("شباب بلوزداد", "الوداد", "🇩🇿", "🇲🇦", "ملعب 5 جويلية", "2026-07-12", "19:00")

# مباراة مباشرة تجريبية (اليوم)
today = datetime.now().strftime("%Y-%m-%d")
now = datetime.now().strftime("%H:%M")
add_match("الريال", "برشلونة", "🇪🇸", "🇪🇸", "سانتياغو برنابيو", today, now, "نهائي", "live")

def get_today_matches():
    """جلب مباريات اليوم"""
    today = datetime.now().strftime("%Y-%m-%d")
    return [m for m in matches_db if m['date'] == today]

def get_live_matches():
    """جلب المباريات المباشرة"""
    return [m for m in matches_db if m['status'] == 'live']

def get_upcoming_matches():
    """جلب المباريات القادمة"""
    today = datetime.now().strftime("%Y-%m-%d")
    return [m for m in matches_db if m['status'] == 'upcoming' and m['date'] >= today]

# ========== إنشاء بطاقة مباراة ==========
def create_match_card(match):
    """إنشاء بطاقة مباراة نصية"""
    status_emoji = "🔴" if match['status'] == 'live' else "⏳" if match['status'] == 'upcoming' else "✅"
    status_text = "مباشر" if match['status'] == 'live' else "قادمة" if match['status'] == 'upcoming' else "انتهت"
    
    card = (
        f"{status_emoji} **{match['stage']}**\n\n"
        f"{match['home_flag']} **{match['home']}**\n"
        f"⚔️ VS\n"
        f"{match['away_flag']} **{match['away']}**\n\n"
    )
    
    if match['status'] == 'live':
        card += f"⚽ **{match['home_score']} - {match['away_score']}**\n\n"
    
    card += (
        f"📍 {match['stadium']}\n"
        f"📅 {match['date']} | 🕒 {match['time']}\n\n"
        f"📊 الحالة: {status_text} {status_emoji}\n\n"
        "🗳️ **من تتوقع الفائز؟**"
    )
    
    return card

def create_match_keyboard(match):
    """إنشاء أزرار للمباراة"""
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
            InlineKeyboardButton("🔄 تحديث النتيجة", callback_data=f"update_{match['id']}")
        ])
    
    return InlineKeyboardMarkup(keyboard)

# ========== إرسال البطاقات ==========
def send_match_card(context, match_id=None):
    """إرسال بطاقة مباراة إلى القناة"""
    try:
        if match_id is None:
            # إرسال جميع مباريات اليوم
            today_matches = get_today_matches()
            if not today_matches:
                context.bot.send_message(
                    chat_id=CHANNEL_ID,
                    text="📭 لا توجد مباريات اليوم"
                )
                return
            
            for match in today_matches:
                card = create_match_card(match)
                keyboard = create_match_keyboard(match)
                context.bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=card,
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
                time.sleep(1)  # تجنب السبام
            return
        
        # إرسال مباراة محددة
        match = next((m for m in matches_db if m['id'] == match_id), None)
        if not match:
            return
        
        card = create_match_card(match)
        keyboard = create_match_keyboard(match)
        context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=card,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    except Exception as e:
        logging.error(f"❌ خطأ في إرسال البطاقة: {e}")

def send_live_matches(context):
    """إرسال المباريات المباشرة"""
    live_matches = get_live_matches()
    if not live_matches:
        context.bot.send_message(
            chat_id=CHANNEL_ID,
            text="🔴 لا توجد مباريات مباشرة حالياً"
        )
        return
    
    for match in live_matches:
        card = create_match_card(match)
        keyboard = create_match_keyboard(match)
        context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=card,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        time.sleep(1)

# ========== صفحة الويب ==========
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
            font-family: Arial, sans-serif;
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
        .header h1 { font-size: 3em; color: #ffd700; }
        .header p { color: #aaa; font-size: 1.2em; }
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
        .card .live-badge {
            background: #e74c3c;
            color: #fff;
            padding: 3px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            display: inline-block;
            animation: blink 1s infinite;
        }
        @keyframes blink {
            50% { opacity: 0.3; }
        }
        .card .teams { font-size: 1.5em; font-weight: bold; margin: 15px 0; }
        .card .teams .home { color: #2ecc71; }
        .card .teams .away { color: #e74c3c; }
        .card .teams .vs { color: #ffd700; margin: 0 10px; }
        .card .score { font-size: 2em; color: #ffd700; margin: 10px 0; }
        .card .info { color: #aaa; line-height: 1.8; }
        .card .info span { color: #fff; }
        .status-upcoming { color: #3498db; }
        .status-live { color: #e74c3c; }
        .status-finished { color: #2ecc71; }
        .footer {
            text-align: center;
            padding: 30px;
            color: #555;
            border-top: 1px solid #2a3f5f;
            margin-top: 40px;
        }
        .footer a { color: #ffd700; text-decoration: none; }
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
        @media (max-width: 600px) {
            .header h1 { font-size: 2em; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏆 كأس العالم 2026</h1>
            <p>تابع المباريات المباشرة والقادمة</p>
            <div style="margin-top: 15px;">
                <a href="https://t.me/Ali_worldcup_bot" class="btn">🤖 البوت على تليجرام</a>
            </div>
        </div>

        <h2 class="section-title">🔴 مباريات مباشرة</h2>
        <div class="cards">
            {% for match in live_matches %}
            <div class="card">
                <span class="live-badge">🔴 مباشر</span>
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
                <p>🔴 لا توجد مباريات مباشرة حالياً</p>
            </div>
            {% endfor %}
        </div>

        <h2 class="section-title">📅 مباريات اليوم</h2>
        <div class="cards">
            {% for match in today_matches %}
            <div class="card">
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
                <p>📭 لا توجد مباريات اليوم</p>
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
    today_matches = get_today_matches()
    live_matches = get_live_matches()
    return render_template_string(HTML_TEMPLATE, today_matches=today_matches, live_matches=live_matches)

# ========== أوامر البوت ==========
def start(update: Update, context):
    update.message.reply_text(
        "🎉 **مرحباً بك في بوت كأس العالم 2026!**\n\n"
        "📌 **الأوامر المتاحة:**\n"
        "/start - بدء البوت\n"
        "/help - المساعدة\n"
        "/today - مباريات اليوم\n"
        "/live - المباريات المباشرة\n"
        "/send - إرسال بطاقات اليوم للقناة\n\n"
        "🔗 **رابط البوت:**\n"
        "https://t.me/Ali_worldcup_bot",
        parse_mode='Markdown'
    )

def help_command(update: Update, context):
    update.message.reply_text(
        "❓ **المساعدة:**\n\n"
        "/start - بدء البوت\n"
        "/help - هذه الرسالة\n"
        "/today - عرض مباريات اليوم\n"
        "/live - عرض المباريات المباشرة\n"
        "/send - إرسال بطاقات اليوم للقناة\n\n"
        "📌 للمشرفين:\n"
        "/add_match الفريق1 الفريق2 الملعب التاريخ الوقت\n"
        "/set_live معرف_المباراة - تفعيل المباشر\n"
        "/update_score معرف_المباراة هدف1 هدف2",
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
        text += f"📍 {m['stadium']} | 🕒 {m['time']}\n\n"
    
    update.message.reply_text(text, parse_mode='Markdown')

def live_command(update: Update, context):
    matches = get_live_matches()
    if not matches:
        update.message.reply_text("🔴 لا توجد مباريات مباشرة حالياً")
        return
    
    text = "🔴 **المباريات المباشرة:**\n\n"
    for m in matches:
        text += f"{m['home_flag']} {m['home']} {m['home_score']} - {m['away_score']} {m['away_flag']} {m['away']}\n"
        text += f"📍 {m['stadium']}\n\n"
    
    update.message.reply_text(text, parse_mode='Markdown')

def send_command(update: Update, context):
    """إرسال بطاقات اليوم إلى القناة"""
    try:
        send_match_card(context)
        update.message.reply_text("✅ تم إرسال بطاقات مباريات اليوم إلى القناة!")
    except Exception as e:
        update.message.reply_text(f"❌ خطأ: {e}")

def add_match_command(update: Update, context):
    """إضافة مباراة جديدة"""
    try:
        args = context.args
        if len(args) < 6:
            update.message.reply_text(
                "⚠️ الصيغة: /add_match الفريق1 الفريق2 العلم1 العلم2 الملعب التاريخ الوقت\n"
                "مثال: /add_match الهلال النصر 🇸🇦 🇦🇪 ملعب_الملك_فهد 2026-07-15 21:00"
            )
            return
        
        match = add_match(
            home=args[0],
            away=args[1],
            home_flag=args[2],
            away_flag=args[3],
            stadium=args[4],
            date=args[5],
            time=args[6]
        )
        update.message.reply_text(f"✅ تم إضافة المباراة:\n{match['home']} 🆚 {match['away']}")
    except Exception as e:
        update.message.reply_text(f"❌ خطأ: {e}")

def set_live_command(update: Update, context):
    """تفعيل المباراة كمباشرة"""
    try:
        match_id = int(context.args[0])
        match = next((m for m in matches_db if m['id'] == match_id), None)
        if not match:
            update.message.reply_text("❌ المباراة غير موجودة")
            return
        
        match['status'] = 'live'
        update.message.reply_text(f"✅ تم تفعيل المباراة كمباشرة:\n{match['home']} 🆚 {match['away']}")
    except Exception as e:
        update.message.reply_text(f"❌ خطأ: {e}")

def update_score_command(update: Update, context):
    """تحديث نتيجة مباراة"""
    try:
        args = context.args
        match_id = int(args[0])
        home_score = int(args[1])
        away_score = int(args[2])
        
        match = next((m for m in matches_db if m['id'] == match_id), None)
        if not match:
            update.message.reply_text("❌ المباراة غير موجودة")
            return
        
        match['home_score'] = home_score
        match['away_score'] = away_score
        
        # إرسال تحديث للقناة
        context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=f"⚽ **تحديث النتيجة:**\n\n{match['home_flag']} {match['home']} {home_score} - {away_score} {match['away_flag']} {match['away']}",
            parse_mode='Markdown'
        )
        update.message.reply_text("✅ تم تحديث النتيجة وإرسالها للقناة")
    except Exception as e:
        update.message.reply_text(f"❌ خطأ: {e}")

# ========== معالجة الأزرار ==========
def button_callback(update: Update, context):
    query = update.callback_query
    query.answer()
    
    data = query.data
    
    if data.startswith("vote_home_"):
        match_id = int(data.split("_")[2])
        match = next((m for m in matches_db if m['id'] == match_id), None)
        if match:
            match['home_votes'] += 1
            query.edit_message_text(f"🗳️ صوتك لـ **{match['home']}** تم تسجيله!", parse_mode='Markdown')
    
    elif data.startswith("vote_away_"):
        match_id = int(data.split("_")[2])
        match = next((m for m in matches_db if m['id'] == match_id), None)
        if match:
            match['away_votes'] += 1
            query.edit_message_text(f"🗳️ صوتك لـ **{match['away']}** تم تسجيله!", parse_mode='Markdown')
    
    elif data.startswith("vote_draw_"):
        match_id = int(data.split("_")[2])
        match = next((m for m in matches_db if m['id'] == match_id), None)
        if match:
            match['draw_votes'] += 1
            query.edit_message_text("🗳️ صوتك للتعادل تم تسجيله!", parse_mode='Markdown')
    
    elif data.startswith("update_"):
        match_id = int(data.split("_")[1])
        match = next((m for m in matches_db if m['id'] == match_id), None)
        if match and match['status'] == 'live':
            keyboard = create_match_keyboard(match)
            query.edit_message_text(
                text=create_match_card(match),
                reply_markup=keyboard,
                parse_mode='Markdown'
            )

# ========== جدولة النشر ==========
def schedule_posts(context):
    """نشر تلقائي للمباريات"""
    while True:
        try:
            # كل ساعة يتحقق من المباريات المباشرة
            time.sleep(3600)
            send_live_matches(context)
        except Exception as e:
            logging.error(f"❌ خطأ في الجدولة: {e}")

# ========== تشغيل البوت ==========
def run_bot():
    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("today", today_command))
    dp.add_handler(CommandHandler("live", live_command))
    dp.add_handler(CommandHandler("send", send_command))
    dp.add_handler(CommandHandler("add_match", add_match_command))
    dp.add_handler(CommandHandler("set_live", set_live_command))
    dp.add_handler(CommandHandler("update_score", update_score_command))
    dp.add_handler(CallbackQueryHandler(button_callback))
    
    logging.info("🤖 البوت يعمل...")
    updater.start_polling()
    updater.idle()

# ========== التشغيل ==========
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    # تشغيل البوت
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # تشغيل الجدولة
    scheduler_thread = threading.Thread(target=schedule_posts, args=(None,), daemon=True)
    scheduler_thread.start()
    
    # تشغيل فلاسك
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
