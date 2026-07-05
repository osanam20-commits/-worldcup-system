# إدارة المباريات
from datetime import datetime
from app.utils import get_flag

matches_db = []
match_id_counter = 1

def add_match(home, away, home_flag=None, away_flag=None, stadium="", 
              date="", time="", stage="دور المجموعات", status="upcoming"):
    """إضافة مباراة جديدة"""
    global match_id_counter
    
    if home_flag is None:
        home_flag = get_flag(home)
    if away_flag is None:
        away_flag = get_flag(away)
    
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    if not time:
        time = datetime.now().strftime("%H:%M")
    
    match = {
        'id': match_id_counter,
        'home': home,
        'away': away,
        'home_flag': home_flag,
        'away_flag': away_flag,
        'stadium': stadium,
        'date': date,
        'time': time,
        'stage': stage,
        'status': status,
        'home_score': 0,
        'away_score': 0,
        'home_votes': 0,
        'away_votes': 0,
        'draw_votes': 0
    }
    
    matches_db.append(match)
    match_id_counter += 1
    return match

def get_match(match_id):
    for match in matches_db:
        if match['id'] == match_id:
            return match
    return None

def delete_match(match_id):
    global matches_db
    match = get_match(match_id)
    if match:
        matches_db = [m for m in matches_db if m['id'] != match_id]
        return True
    return False

def update_score(match_id, home_score, away_score):
    match = get_match(match_id)
    if match:
        match['home_score'] = home_score
        match['away_score'] = away_score
        return True
    return False

def set_match_status(match_id, status):
    match = get_match(match_id)
    if match:
        match['status'] = status
        return True
    return False

def get_all_matches():
    return matches_db.copy()

def get_matches_by_date(date):
    return [m for m in matches_db if m['date'] == date]

def add_sample_matches():
    """إضافة مباريات تجريبية"""
    matches = [
        {"home": "الهلال", "away": "العين", "stadium": "ملعب الملك فهد", "date": "2026-07-10", "time": "20:00"},
        {"home": "الأهلي", "away": "الترجي", "stadium": "استاد القاهرة", "date": "2026-07-11", "time": "21:00"},
        {"home": "الوداد", "away": "الرجاء", "stadium": "ملعب محمد الخامس", "date": "2026-07-12", "time": "19:00"},
        {"home": "ريال مدريد", "away": "برشلونة", "stadium": "سانتياغو برنابيو", "date": "2026-07-13", "time": "22:00"},
    ]
    
    for m in matches:
        add_match(**m)

# إضافة العينات عند التحميل
if len(matches_db) == 0:
    add_sample_matches()
