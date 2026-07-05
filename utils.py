# دوال مساعدة
import os
from datetime import datetime, timedelta

def get_flag(team_name):
    """إرجاع علم الفريق بناءً على اسمه"""
    flags = {
        'الهلال': '🇸🇦', 'النصر': '🇸🇦', 'الاتحاد': '🇸🇦', 'الأهلي': '🇸🇦',
        'العين': '🇦🇪', 'الجزيرة': '🇦🇪', 'الوحدة': '🇦🇪',
        'الأهلي': '🇪🇬', 'الزمالك': '🇪🇬', 'بيراميدز': '🇪🇬',
        'الترجي': '🇹🇳', 'النجم': '🇹🇳', 'الصفاقسي': '🇹🇳',
        'الوداد': '🇲🇦', 'الرجاء': '🇲🇦', 'الجيش': '🇲🇦',
        'ريال مدريد': '🇪🇸', 'برشلونة': '🇪🇸', 'أتلتيكو': '🇪🇸',
        'بايرن ميونخ': '🇩🇪', 'بوروسيا': '🇩🇪', 'لايبزيغ': '🇩🇪',
        'مانشستر سيتي': '🏴', 'ليفربول': '🏴', 'تشيلسي': '🏴',
        'أرسنال': '🏴', 'توتنهام': '🏴', 'مانشستر يونايتد': '🏴',
        'باريس سان جيرمان': '🇫🇷', 'مارسيليا': '🇫🇷', 'ليون': '🇫🇷',
        'ميلان': '🇮🇹', 'إنتر ميلان': '🇮🇹', 'يوفنتوس': '🇮🇹',
        'روما': '🇮🇹', 'نابولي': '🇮🇹',
    }
    return flags.get(team_name, '🏴')

def get_status_emoji(status):
    emojis = {
        'upcoming': '⏳',
        'live': '🔴',
        'finished': '✅',
        'cancelled': '❌',
        'postponed': '📌'
    }
    return emojis.get(status, '⏳')

def get_status_text(status):
    texts = {
        'upcoming': 'قادمة',
        'live': 'مباشر',
        'finished': 'انتهت',
        'cancelled': 'ملغية',
        'postponed': 'مؤجلة'
    }
    return texts.get(status, 'قادمة')

def format_match_card(match):
    card = (
        f"{get_status_emoji(match['status'])} **{match['stage']}**\n\n"
        f"{match['home_flag']} **{match['home']}**\n"
        f"⚔️ VS\n"
        f"{match['away_flag']} **{match['away']}**\n\n"
    )
    
    if match['status'] == 'live':
        card += f"⚽ **{match['home_score']} - {match['away_score']}**\n\n"
    
    card += (
        f"📍 {match['stadium']}\n"
        f"📅 {match['date']} | 🕒 {match['time']}\n\n"
        f"📊 الحالة: {get_status_text(match['status'])} {get_status_emoji(match['status'])}"
    )
    
    return card

def get_today_matches(matches_db):
    today = datetime.now().strftime("%Y-%m-%d")
    return [m for m in matches_db if m['date'] == today]

def get_live_matches(matches_db):
    return [m for m in matches_db if m['status'] == 'live']

def get_upcoming_matches(matches_db):
    today = datetime.now().strftime("%Y-%m-%d")
    return [m for m in matches_db if m['status'] == 'upcoming' and m['date'] >= today]

def check_live_matches(matches_db, channel_id, bot):
    now = datetime.now()
    updated = False
    
    for match in matches_db:
        if match['status'] == 'upcoming':
            try:
                match_time = datetime.strptime(f"{match['date']} {match['time']}", "%Y-%m-%d %H:%M")
                if match_time <= now <= match_time + timedelta(hours=2):
                    match['status'] = 'live'
                    updated = True
                    if bot and channel_id:
                        text = f"🔴 **المباراة أصبحت مباشرة!**\n\n"
                        text += f"{match['home_flag']} {match['home']} 🆚 {match['away_flag']} {match['away']}\n"
                        text += f"📍 {match['stadium']}"
                        bot.send_message(chat_id=channel_id, text=text, parse_mode='Markdown')
            except:
                pass
    
    return updated
