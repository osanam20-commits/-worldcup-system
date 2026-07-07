import os
import logging
import threading
import time
from flask import Flask, render_template_string, request, jsonify
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

# ========== إعدادات ==========
app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8689943788:AAFfmE62a4h-eLXYAcOXvSUgmkLs5KZZwts")
CHANNEL_ID = "@lvFaax5HzsxOTU0"  # ← تم إدخال معرف القناة مباشرة

# ========== قاعدة بيانات المباريات ==========
matches_db = []
match_id = 1

def add_match(home, away, home_flag="🏴", away_flag="🏴", stadium="", 
              date="", time="", stage="", tournament="", 
              channel="", commentator="", channel2="", commentator2="",
              status="upcoming", home_score=0, away_score=0):
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
        'channel': channel,
        'commentator': commentator,
        'channel2': channel2,
        'commentator2': commentator2,
        'status': status,
        'home_score': home_score,
        'away_score': away_score
    }
    matches_db.append(match)
    match_id += 1
    return match

# ========== إضافة مباريات ==========
add_match("الأهلي", "الزمالك", "🇪🇬", "🇪🇬", "استاد القاهرة", 
          "2026-07-07", "20:00", "نهائي", "الدوري المصري",
          "ON Time", "ميدو", "ON Sport", "أبو تريكة")

add_match("الهلال", "النصر", "🇸🇦", "🇸🇦", "ملعب الملك فهد", 
          "2026-07-07", "21:00", "نهائي", "الدوري السعودي",
          "SSC", "فهد العتيبي", "MBC", "عيسى الحربين")

add_match("الوداد", "الرجاء", "🇲🇦", "🇲🇦", "ملعب محمد الخامس", 
          "2026-07-07", "19:00", "نهائي", "الدوري المغربي",
          "Arryadia", "جواد", "2M", "نور الدين")

add_match("أمريكا", "بلجيكا", "🇺🇸", "🇧🇪", "ملعب أمريكا", 
          "2026-07-07", "15:00", "دور الـ16", "كأس العالم 2026",
          "beIN Max 2", "حفيظ دراجي", "beIN 4K", "حفيظ دراجي")

add_match("الأرجنتين", "مصر", "🇦🇷", "🇪🇬", "ملعب أمريكا", 
          "2026-07-07", "19:00", "دور الـ16", "كأس العالم 2026",
          "beIN Max 1", "علي محمد علي", "beIN 4K", "علي محمد علي")

add_match("سويسرا", "كولومبيا", "🇨🇭", "🇨🇴", "ملعب أمريكا", 
          "2026-07-07", "23:00", "دور الـ16", "كأس العالم 2026",
          "beIN Max 2", "علي سعيد الكعبي", "beIN 4K", "محمد بركات")

# ========== دوال مساعدة ==========
def get_today_matches():
    today = datetime.now().strftime("%Y-%m-%d")
    return [m for m in matches_db if m['date'] == today]

def get_all_matches():
    return matches_db

def get_tournaments():
    return list(set(m['tournament'] for m in matches_db))

def get_live_matches():
    return [m for m in matches_db if m['status'] == 'live']

def create_match_card(match):
    status_emoji = "🔴" if match['status'] == 'live' else "⏳" if match['status'] == 'upcoming' else "✅"
    status_text = "مباشر" if match['status'] == 'live' else "قادمة" if match['status'] == 'upcoming' else "انتهت"
    
    card = f"""
────────────────
🏆 *{match['tournament']}*
📌 {match['stage']}
────────────────

*🔹️ {match['home_flag']} {match['home']} × {match['away_flag']} {match['away']} 🔸️*
⌚️ {match['time']}
📍 {match['stadium']}
📊 الحالة: {status_text} {status_emoji}
"""
    
    if match['status'] == 'live':
        card += f"\n⚽ **{match['home_score']} - {match['away_score']}**"
    
    if match['channel']:
        card += f"\n\n📺 {match['channel']}"
        if match['commentator']:
            card += f"\n🎙 {match['commentator']}"
    
    if match['channel2']:
        card += f"\n📺 {match['channel2']}"
        if match['commentator2']:
            card += f"\n🎙️ {match['commentator2']}"
    
    card += "\n────────────────"
    return card

def create_full_schedule():
    matches = get_today_matches()
    if not matches:
        return "📭 لا توجد مباريات اليوم"
    
    today = datetime.now().strftime("%d/%m/%Y")
    schedule = f"""
────────────────
♦ *جدول مباريات اليوم* |
📆 {today}
────────────────
"""
    
    for match in matches:
        schedule += f"""
🏆 *{match['tournament']}* 
━━━━━━━━━━━━━━━━━━

*🔹️ {match['home_flag']} {match['home']} × {match['away_flag']} {match['away']} 🔸️*
⌚️ {match['time']}
📍 {match['stadium']}
"""
        if match['channel']:
            schedule += f"\n📺 {match['channel']} | 🎙 {match['commentator']}"
        if match['channel2']:
            schedule += f"\n📺 {match['channel2']} | 🎙️ {match['commentator2']}"
        
        schedule += "\n────────────────"
    
    return schedule

# ========== دوال النشر ==========
def send_to_channel(context, text):
    try:
        context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=text,
            parse_mode='Markdown'
        )
        return True
    except Exception as e:
        logging.error(f"❌ خطأ في الإرسال: {e}")
        return False

def send_daily_matches(context):
    today_matches = get_today_matches()
    if not today_matches:
        send_to_channel(context, "📭 لا توجد مباريات اليوم")
        return
    
    schedule = create_full_schedule()
    send_to_channel(context, schedule)
    logging.info(f"✅ تم نشر جدول مباريات اليوم")

def send_match_to_channel(context, match):
    card = create_match_card(match)
    send_to_channel(context, card)

# ========== أوامر البوت ==========
def start(update, context):
    update.message.reply_text(
        "🎉 **مرحباً بك في بوت جو كوره!**\n\n"
        "📌 **الأوامر المتاحة:**\n"
        "/start - بدء البوت\n"
        "/help - المساعدة\n"
        "/today - مباريات اليوم\n"
        "/matches - جميع المباريات\n"
        "/tournaments - البطولات\n"
        "/live - المباريات المباشرة\n"
        "/send - نشر جدول اليوم في القناة\n\n"
        "⚽ **جو كوره - بوابتك الرياضية الشاملة**",
        parse_mode='Markdown'
    )

def help_command(update, context):
    update.message.reply_text(
        "❓ **المساعدة:**\n\n"
        "/today - مباريات اليوم\n"
        "/matches - جميع المباريات\n"
        "/tournaments - قائمة البطولات\n"
        "/live - المباريات المباشرة\n"
        "/send - نشر جدول اليوم في القناة\n\n"
        "📌 **للمشرفين:**\n"
        "/add - إضافة مباراة\n"
        "/set_live - تفعيل مباشر\n"
        "/set_score - تحديث النتيجة\n"
        "/delete - حذف مباراة",
        parse_mode='Markdown'
    )

def today_command(update, context):
    matches = get_today_matches()
    if not matches:
        update.message.reply_text("📭 لا توجد مباريات اليوم")
        return
    
    schedule = create_full_schedule()
    update.message.reply_text(schedule, parse_mode='Markdown')

def matches_command(update, context):
    if not matches_db:
        update.message.reply_text("📭 لا توجد مباريات")
        return
    
    text = "📋 **جميع المباريات:**\n\n"
    for m in matches_db:
        text += f"#{m['id']} {m['home_flag']} {m['home']} 🆚 {m['away_flag']} {m['away']}\n"
        text += f"🏆 {m['tournament']} | 📅 {m['date']} | 🕒 {m['time']}\n\n"
    update.message.reply_text(text, parse_mode='Markdown')

def tournaments_command(update, context):
    tournaments = get_tournaments()
    if not tournaments:
        update.message.reply_text("📭 لا توجد بطولات")
        return
    
    text = "🏆 **البطولات:**\n\n"
    for t in tournaments:
        count = len([m for m in matches_db if m['tournament'] == t])
        text += f"🏆 {t} - {count} مباراة\n"
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

def send_command(update, context):
    try:
        send_daily_matches(context)
        update.message.reply_text("✅ تم نشر جدول مباريات اليوم في القناة!")
    except Exception as e:
        update.message.reply_text(f"❌ خطأ: {e}")

def add_command(update, context):
    try:
        args = context.args
        if len(args) < 7:
            update.message.reply_text(
                "⚠️ الصيغة: /add الفريق1 الفريق2 الملعب التاريخ الوقت البطولة المرحلة\n"
                "مثال: /add الأهلي الزمالك استاد_القاهرة 2026-07-07 20:00 الدوري_المصري نهائي"
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
        
        send_match_to_channel(context, match)
        
    except Exception as e:
        update.message.reply_text(f"❌ خطأ: {e}")

def set_live_command(update, context):
    try:
        match_id = int(context.args[0])
        for match in matches_db:
            if match['id'] == match_id:
                match['status'] = 'live'
                update.message.reply_text(f"✅ تم تفعيل المباراة #{match_id} كمباشرة")
                send_match_to_channel(context, match)
                return
        update.message.reply_text(f"❌ المباراة #{match_id} غير موجودة")
    except Exception as e:
        update.message.reply_text(f"❌ خطأ: {e}")

def set_score_command(update, context):
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
                send_match_to_channel(context, match)
                return
        update.message.reply_text(f"❌ المباراة #{match_id} غير موجودة")
    except Exception as e:
        update.message.reply_text(f"❌ خطأ: {e}")

def delete_command(update, context):
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
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>جو كوره - GoalKora</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet" />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" />
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        :root {
            --gz-bg: #0a0a0f;
            --gz-card: #12121a;
            --gz-card-hover: #1a1a24;
            --gz-surface: #1c1c28;
            --gz-border: #2a2a3a;
            --gz-text: #f0f0f5;
            --gz-text-secondary: #9a9ab0;
            --gz-text-muted: #6a6a80;
            --gz-accent: #e63946;
            --gz-accent-light: #ff4d5a;
            --gz-green: #2ecc71;
            --gz-gold: #d4a017;
            --gz-font: 'Cairo', 'Segoe UI', sans-serif;
            --gz-radius: 14px;
            --gz-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        }
        body {
            font-family: var(--gz-font);
            background: var(--gz-bg);
            color: var(--gz-text);
            min-height: 100vh;
            overflow-x: hidden;
            line-height: 1.6;
        }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: var(--gz-bg); }
        ::-webkit-scrollbar-thumb { background: var(--gz-border); border-radius: 10px; }
        ::-webkit-scrollbar-thumb:hover { background: var(--gz-accent); }
        
        .gz-header {
            background: rgba(10, 10, 15, 0.92);
            backdrop-filter: blur(20px);
            border-bottom: 1px solid var(--gz-border);
            padding: 0 24px;
            position: sticky;
            top: 0;
            z-index: 1000;
        }
        .gz-header-inner {
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: space-between;
            height: 72px;
            gap: 20px;
        }
        .gz-logo {
            display: flex;
            align-items: center;
            gap: 12px;
            text-decoration: none;
        }
        .gz-logo-icon {
            width: 48px;
            height: 48px;
            background: linear-gradient(135deg, var(--gz-accent) 0%, #ff6b6b 100%);
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            font-weight: 900;
            color: #fff;
            box-shadow: 0 4px 20px rgba(230, 57, 70, 0.3);
        }
        .gz-logo-text {
            font-size: 28px;
            font-weight: 900;
            color: var(--gz-text);
            letter-spacing: -1px;
        }
        .gz-logo-text span { color: var(--gz-accent); }
        
        .gz-main {
            max-width: 1400px;
            margin: 0 auto;
            padding: 24px;
        }
        
        .gz-hero-match {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            border: 1px solid var(--gz-border);
            border-radius: var(--gz-radius);
            padding: 32px 28px;
            margin-bottom: 24px;
            position: relative;
            overflow: hidden;
        }
        .gz-hero-match::before {
            content: '';
            position: absolute;
            top: -50%;
            right: -20%;
            width: 400px;
            height: 400px;
            background: radial-gradient(circle, rgba(230, 57, 70, 0.08) 0%, transparent 70%);
            pointer-events: none;
        }
        .gz-hero-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 24px;
            position: relative;
            z-index: 1;
        }
        .gz-hero-competition {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 13px;
            color: var(--gz-text-secondary);
        }
        .gz-hero-teams {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 40px;
            position: relative;
            z-index: 1;
        }
        .gz-team {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 10px;
            flex: 1;
        }
        .gz-team-logo {
            width: 80px;
            height: 80px;
            background: var(--gz-surface);
            border: 2px solid var(--gz-border-light);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 32px;
            font-weight: 900;
            color: var(--gz-text);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        }
        .gz-team-name {
            font-size: 18px;
            font-weight: 700;
            color: var(--gz-text);
            text-align: center;
        }
        .gz-score-box {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 8px;
        }
        .gz-score {
            font-size: 60px;
            font-weight: 900;
            color: var(--gz-text);
            line-height: 1;
        }
        .gz-score-divider {
            width: 40px;
            height: 3px;
            background: linear-gradient(90deg, transparent, var(--gz-accent), transparent);
            border-radius: 4px;
        }
        .gz-match-time {
            font-size: 14px;
            color: var(--gz-accent-light);
            font-weight: 700;
        }
        .gz-match-venue {
            text-align: center;
            margin-top: 20px;
            font-size: 13px;
            color: var(--gz-text-muted);
        }
        
        .gz-section-title {
            font-size: 20px;
            font-weight: 700;
            color: var(--gz-text);
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .gz-match-list {
            display: flex;
            flex-direction: column;
            gap: 10px;
            margin-bottom: 30px;
        }
        .gz-match-row {
            display: grid;
            grid-template-columns: 80px 1fr 60px 1fr 80px;
            align-items: center;
            gap: 12px;
            padding: 14px 18px;
            background: var(--gz-card);
            border: 1px solid var(--gz-border);
            border-radius: var(--gz-radius-sm);
            transition: all 0.3s;
            cursor: pointer;
        }
        .gz-match-row:hover {
            background: var(--gz-card-hover);
            border-color: var(--gz-border-light);
            transform: translateX(-4px);
        }
        .gz-match-row.live {
            border-color: rgba(230, 57, 70, 0.3);
            background: linear-gradient(90deg, rgba(230, 57, 70, 0.05) 0%, var(--gz-card) 100%);
        }
        .gz-match-time-cell {
            font-size: 13px;
            font-weight: 600;
            color: var(--gz-text-secondary);
            text-align: center;
        }
        .gz-match-time-cell.live-time { color: var(--gz-accent); }
        .gz-match-team {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .gz-match-team.away { justify-content: flex-end; flex-direction: row-reverse; }
        .gz-match-team-logo {
            width: 34
