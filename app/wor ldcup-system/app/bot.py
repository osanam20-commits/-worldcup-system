# بوت التليجرام
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

from app.matches import matches_db, add_match, get_match, delete_match, update_score
from app.utils import format_match_card, get_today_matches, get_live_matches

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
        "/matches - عرض جميع المباريات\n"
        "/send - إرسال بطاقات اليوم للقناة\n\n"
        "📌 **للمشرفين:**\n"
        "/add_match الفريق1 الفريق2 الملعب التاريخ الوقت\n"
        "/delete_match معرف_المباراة\n"
        "/set_score معرف_المباراة هدف1 هدف2\n"
        "/set_status معرف_المباراة live|finished",
        parse_mode='Markdown'
    )

def today_command(update: Update, context):
    matches = get_today_matches(matches_db)
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
    matches = get_live_matches(matches_db)
    if not matches:
        update.message.reply_text("🔴 لا توجد مباريات مباشرة حالياً")
        return
    
    text = "🔴 **المباريات المباشرة:**\n\n"
    for m in matches:
        text += f"{m['home_flag']} {m['home']} {m['home_score']} - {m['away_score']} {m['away_flag']} {m['away']}\n"
        text += f"📍 {m['stadium']} | 🕒 {m['time']}\n\n"
    
    update.message.reply_text(text, parse_mode='Markdown')

def matches_command(update: Update, context):
    if not matches_db:
        update.message.reply_text("📭 لا توجد مباريات مسجلة")
        return
    
    text = "📋 **جميع المباريات:**\n\n"
    for m in matches_db:
        status_emoji = "🔴" if m['status'] == 'live' else "⏳" if m['status'] == 'upcoming' else "✅"
        text += f"{status_emoji} #{m['id']} {m['home_flag']} {m['home']} 🆚 {m['away_flag']} {m['away']}\n"
        text += f"📍 {m['stadium']} | 📅 {m['date']} | 🕒 {m['time']}\n\n"
    
    update.message.reply_text(text, parse_mode='Markdown')

def send_command(update: Update, context):
    """إرسال بطاقات اليوم إلى القناة"""
    try:
        channel_id = context.bot_data.get('channel_id')
        if not channel_id:
            update.message.reply_text("❌ CHANNEL_ID غير مضبوط")
            return
        
        today_matches = get_today_matches(matches_db)
        if not today_matches:
            update.message.reply_text("📭 لا توجد مباريات اليوم")
            return
        
        for match in today_matches:
            card = format_match_card(match)
            keyboard = create_match_keyboard(match)
            context.bot.send_message(
                chat_id=channel_id,
                text=card,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        
        update.message.reply_text(f"✅ تم إرسال {len(today_matches)} بطاقة إلى القناة!")
    except Exception as e:
        update.message.reply_text(f"❌ خطأ: {e}")

def add_match_command(update: Update, context):
    """إضافة مباراة جديدة"""
    try:
        args = context.args
        if len(args) < 5:
            update.message.reply_text(
                "⚠️ الصيغة: /add_match الفريق1 الفريق2 الملعب التاريخ الوقت\n"
                "مثال: /add_match الهلال النصر ملعب_الملك_فهد 2026-07-15 21:00"
            )
            return
        
        match = add_match(
            home=args[0],
            away=args[1],
            stadium=args[2],
            date=args[3],
            time=args[4]
        )
        update.message.reply_text(
            f"✅ تم إضافة المباراة #{match['id']}:\n"
            f"🏆 {match['home']} 🆚 {match['away']}\n"
            f"📍 {match['stadium']}\n"
            f"📅 {match['date']} | 🕒 {match['time']}"
        )
    except Exception as e:
        update.message.reply_text(f"❌ خطأ: {e}")

def delete_match_command(update: Update, context):
    """حذف مباراة"""
    try:
        match_id = int(context.args[0])
        if delete_match(match_id):
            update.message.reply_text(f"✅ تم حذف المباراة #{match_id}")
        else:
            update.message.reply_text(f"❌ المباراة #{match_id} غير موجودة")
    except Exception as e:
        update.message.reply_text(f"❌ خطأ: {e}")

def set_score_command(update: Update, context):
    """تحديث نتيجة مباراة"""
    try:
        args = context.args
        match_id = int(args[0])
        home_score = int(args[1])
        away_score = int(args[2])
        
        if update_score(match_id, home_score, away_score):
            match = get_match(match_id)
            update.message.reply_text(
                f"✅ تم تحديث النتيجة:\n"
                f"{match['home']} {home_score} - {away_score} {match['away']}"
            )
        else:
            update.message.reply_text(f"❌ المباراة #{match_id} غير موجودة")
    except Exception as e:
        update.message.reply_text(f"❌ خطأ: {e}")

def set_status_command(update: Update, context):
    """تغيير حالة مباراة"""
    try:
        args = context.args
        match_id = int(args[0])
        status = args[1]
        
        if status not in ['upcoming', 'live', 'finished']:
            update.message.reply_text("❌ الحالات المتاحة: upcoming, live, finished")
            return
        
        from app.matches import set_match_status
        if set_match_status(match_id, status):
            update.message.reply_text(f"✅ تم تغيير حالة المباراة #{match_id} إلى {status}")
        else:
            update.message.reply_text(f"❌ المباراة #{match_id} غير موجودة")
    except Exception as e:
        update.message.reply_text(f"❌ خطأ: {e}")

# ========== أزرار التصويت ==========

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

def button_callback(update: Update, context):
    query = update.callback_query
    query.answer()
    
    data = query.data
    
    if data.startswith("vote_home_"):
        match_id = int(data.split("_")[2])
        match = get_match(match_id)
        if match:
            match['home_votes'] += 1
            query.edit_message_text(f"🗳️ صوتك لـ **{match['home']}** تم تسجيله!", parse_mode='Markdown')
    
    elif data.startswith("vote_away_"):
        match_id = int(data.split("_")[2])
        match = get_match(match_id)
        if match:
            match['away_votes'] += 1
            query.edit_message_text(f"🗳️ صوتك لـ **{match['away']}** تم تسجيله!", parse_mode='Markdown')
    
    elif data.startswith("vote_draw_"):
        match_id = int(data.split("_")[2])
        match = get_match(match_id)
        if match:
            match['draw_votes'] += 1
            query.edit_message_text("🗳️ صوتك للتعادل تم تسجيله!", parse_mode='Markdown')
    
    elif data.startswith("update_"):
        match_id = int(data.split("_")[1])
        match = get_match(match_id)
        if match and match['status'] == 'live':
            keyboard = create_match_keyboard(match)
            query.edit_message_text(
                text=format_match_card(match),
                reply_markup=keyboard,
                parse_mode='Markdown'
            )

# ========== تشغيل البوت ==========

def run_bot(token, channel_id):
    """تشغيل البوت"""
    logging.info("🤖 بدء تشغيل البوت...")
    
    updater = Updater(token)
    dp = updater.dispatcher
    
    dp.bot_data['channel_id'] = channel_id
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("today", today_command))
    dp.add_handler(CommandHandler("live", live_command))
    dp.add_handler(CommandHandler("matches", matches_command))
    dp.add_handler(CommandHandler("send", send_command))
    dp.add_handler(CommandHandler("add_match", add_match_command))
    dp.add_handler(CommandHandler("delete_match", delete_match_command))
    dp.add_handler(CommandHandler("set_score", set_score_command))
    dp.add_handler(CommandHandler("set_status", set_status_command))
    dp.add_handler(CallbackQueryHandler(button_callback))
    
    updater.start_polling()
    logging.info("🤖 البوت يعمل...")
    updater.idle()
