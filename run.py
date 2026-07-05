import os
import logging
from threading import Thread
from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from telegram import Update
from telegram.ext import Updater, CommandHandler

# ========== الإعدادات ==========
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8689943788:AAFfmE62a4h-eLXYAcOXvSUgmkLs5KZZwts")

# ========== تهيئة Flask وقاعدة البيانات ==========
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ========== نموذج المباريات ==========
class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    home = db.Column(db.String(100))
    away = db.Column(db.String(100))
    home_flag = db.Column(db.String(10), default="🏴")
    away_flag = db.Column(db.String(10), default="🏴")
    stadium = db.Column(db.String(120))
    date = db.Column(db.String(20))
    time = db.Column(db.String(10))

# ========== إنشاء الجداول وإضافة بيانات ==========
with app.app_context():
    db.create_all()
    if Match.query.count() == 0:
        matches = [
            Match(home="الهلال", away="العين", home_flag="🇸🇦", away_flag="🇦🇪", 
                  stadium="ملعب الملك فهد", date="2026-07-10", time="20:00"),
            Match(home="الأهلي", away="الترجي", home_flag="🇪🇬", away_flag="🇹🇳", 
                  stadium="استاد القاهرة", date="2026-07-11", time="21:00"),
            Match(home="شباب بلوزداد", away="الوداد", home_flag="🇩🇿", away_flag="🇲🇦", 
                  stadium="ملعب 5 جويلية", date="2026-07-12", time="19:00"),
        ]
        db.session.add_all(matches)
        db.session.commit()

# ========== قالب HTML الجميل ==========
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
            font-family: 'Segoe UI', Arial, sans-serif;
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header {
            text-align: center;
            padding: 40px 20px;
            background: linear-gradient(145deg, #1a1f35, #2a3f5f);
            border-radius: 20px;
            margin-bottom: 30px;
            border: 1px solid rgba(255, 215, 0, 0.2);
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }
        .header h1 {
            font-size: 3.2em;
            color: #ffd700;
            text-shadow: 0 0 30px rgba(255, 215, 0, 0.2);
            letter-spacing: 2px;
        }
        .header p {
            color: #aaa;
            font-size: 1.3em;
            margin-top: 10px;
        }
        .header .sub {
            color: #ffd700;
            font-size: 1.1em;
            margin-top: 5px;
        }
        .btn-group {
            margin-top: 25px;
            display: flex;
            justify-content: center;
            gap: 15px;
            flex-wrap: wrap;
        }
        .btn {
            padding: 14px 35px;
            background: linear-gradient(135deg, #ffd700, #f5a623);
            color: #1a1f35;
            text-decoration: none;
            border-radius: 50px;
            font-weight: bold;
            font-size: 1.1em;
            transition: all 0.3s;
            border: none;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
        }
        .btn:hover { transform: translateY(-3px) scale(1.02); box-shadow: 0 8px 25px rgba(255, 215, 0, 0.4); }
        .btn-secondary {
            background: transparent;
            color: #ffd700;
            border: 2px solid #ffd700;
            box-shadow: none;
        }
        .btn-secondary:hover { background: rgba(255, 215, 0, 0.1); }
        .btn-danger {
            background: #e74c3c;
            color: #fff;
            padding: 8px 20px;
            font-size: 0.85em;
        }
        .btn-danger:hover { background: #c0392b; }

        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        .stat-box {
            background: rgba(26, 31, 53, 0.8);
            padding: 25px 20px;
            border-radius: 15px;
            text-align: center;
            border: 1px solid #2a3f5f;
            backdrop-filter: blur(5px);
            transition: 0.3s;
        }
        .stat-box:hover { border-color: #ffd700; transform: translateY(-5px); }
        .stat-box .number {
            font-size: 2.8em;
            color: #ffd700;
            font-weight: bold;
        }
        .stat-box .label { color: #aaa; font-size: 1em; margin-top: 5px; }

        .section-title {
            font-size: 2em;
            color: #ffd700;
            margin: 40px 0 20px;
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
            transition: all 0.4s;
            position: relative;
            overflow: hidden;
        }
        .card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #ffd700, #f5a623);
            opacity: 0;
            transition: 0.4s;
        }
        .card:hover::before { opacity: 1; }
        .card:hover {
            border-color: #ffd700;
            transform: translateY(-8px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.3);
        }
        .card .stage {
            background: rgba(255, 215, 0, 0.15);
            color: #ffd700;
            padding: 5px 18px;
            border-radius: 30px;
            font-size: 0.8em;
            display: inline-block;
            margin-bottom: 10px;
        }
        .card .teams {
            font-size: 1.6em;
            font-weight: bold;
            margin: 15px 0;
        }
        .card .teams .home { color: #2ecc71; }
        .card .teams .away { color: #e74c3c; }
        .card .teams .vs { color: #ffd700; margin: 0 10px; }
        .card .info {
            color: #aaa;
            font-size: 0.95em;
            line-height: 1.8;
        }
        .card .info span { color: #fff; }

        .form-container {
            max-width: 600px;
            margin: 0 auto;
            background: #1a1f35;
            padding: 35px;
            border-radius: 20px;
            border: 1px solid #2a3f5f;
        }
        .form-group { margin-bottom: 20px; }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #aaa;
            font-weight: bold;
        }
        .form-group input, .form-group select {
            width: 100%;
            padding: 14px 18px;
            background: #0d1120;
            border: 1px solid #2a3f5f;
            border-radius: 12px;
            color: #fff;
            font-size: 1em;
            transition: 0.3s;
        }
        .form-group input:focus, .form-group select:focus {
            outline: none;
            border-color: #ffd700;
            box-shadow: 0 0 20px rgba(255, 215, 0, 0.1);
        }

        .footer {
            text-align: center;
            padding: 30px;
            color: #555;
            border-top: 1px solid #2a3f5f;
            margin-top: 50px;
        }
        .footer a { color: #ffd700; text-decoration: none; }
        .footer a:hover { text-decoration: underline; }

        .empty-state {
            grid-column: 1/-1;
            text-align: center;
            padding: 60px 20px;
            background: #1a1f35;
            border-radius: 18px;
            border: 2px dashed #2a3f5f;
        }
        .empty-state p { font-size: 1.5em; color: #666; }

        @media (max-width: 600px) {
            .header h1 { font-size: 2.2em; }
            .card .teams { font-size: 1.2em; }
            .btn { padding: 12px 25px; font-size: 0.95em; }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- الهيدر -->
        <div class="header">
            <h1>🏆 كأس العالم 2026</h1>
            <p>تابع جميع المباريات والنتائج لحظة بلحظة</p>
            <div class="sub">📱 تواصل معنا عبر <a href="https://t.me/Ali_worldcup_bot" style="color:#ffd700;">البوت على تليجرام</a></div>
            <div class="btn-group">
                <a href="/matches" class="btn">📋 جميع المباريات</a>
                <a href="/add_match" class="btn btn-secondary">➕ إضافة مباراة</a>
            </div>
        </div>

        <!-- الإحصائيات -->
        <div class="stats">
            <div class="stat-box">
                <div class="number">{{ total }}</div>
                <div class="label">عدد المباريات</div>
            </div>
            <div class="stat-box">
                <div class="number">🏆</div>
                <div class="label">كأس العالم</div>
            </div>
            <div class="stat-box">
                <div class="number">2026</div>
                <div class="label">العام</div>
            </div>
        </div>

        <!-- المباريات -->
        <h2 class="section-title">🔥 أحدث المباريات</h2>
        <div class="cards">
            {% for match in matches %}
            <div class="card">
                <div class="stage">{{ match.stage or 'دور المجموعات' }}</div>
                <div class="teams">
                    <span class="home">{{ match.home_flag }} {{ match.home }}</span>
                    <span class="vs">⚔️</span>
                    <span class="away">{{ match.away_flag }} {{ match.away }}</span>
                </div>
                <div class="info">
                    📍 <span>{{ match.stadium or 'غير محدد' }}</span><br>
                    📅 <span>{{ match.date or 'غير محدد' }}</span> | 🕒 <span>{{ match.time or 'غير محدد' }}</span>
                </div>
            </div>
            {% else %}
            <div class="empty-state">
                <p>📭 لا توجد مباريات حالياً</p>
                <a href="/add_match" class="btn" style="margin-top:20px; display:inline-block;">➕ أضف أول مباراة</a>
            </div>
            {% endfor %}
        </div>

        <!-- الفوتر -->
        <div class="footer">
            <p>🏆 كأس العالم 2026 - جميع الحقوق محفوظة</p>
            <p style="font-size: 0.85em; color: #444;">🤖 <a href="https://t.me/Ali_worldcup_bot">البوت على تليجرام</a></p>
        </div>
    </div>
</body>
</html>
"""

# ========== صفحات الويب ==========
@app.route('/')
def home():
    matches = Match.query.limit(6).all()
    total = Match.query.count()
    return render_template_string(HTML_TEMPLATE, matches=matches, total=total)

@app.route('/matches')
def matches_page():
    matches = Match.query.all()
    return render_template_string(HTML_TEMPLATE, matches=matches, total=len(matches))

@app.route('/add_match', methods=['GET', 'POST'])
def add_match():
    if request.method == 'POST':
        match = Match(
            home=request.form['home'],
            away=request.form['away'],
            home_flag=request.form.get('home_flag', '🏴'),
            away_flag=request.form.get('away_flag', '🏴'),
            stadium=request.form['stadium'],
            date=request.form['date'],
            time=request.form['time']
        )
        db.session.add(match)
        db.session.commit()
        return redirect(url_for('home'))
    return '''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>➕ إضافة مباراة</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box;}
        body{background:linear-gradient(135deg,#0a0e1a,#1a1f35);color:#fff;font-family:'Segoe UI',Arial;min-height:100vh;padding:20px;}
        .container{max-width:600px;margin:0 auto;}
        .header{text-align:center;padding:30px 0;border-bottom:1px solid #2a3f5f;margin-bottom:30px;}
        .header h1{color:#ffd700;font-size:2.2em;}
        .header a{color:#ffd700;text-decoration:none;}
        .form-group{margin-bottom:20px;}
        .form-group label{display:block;margin-bottom:8px;color:#aaa;font-weight:bold;}
        .form-group input,.form-group select{width:100%;padding:14px 18px;background:#0d1120;border:1px solid #2a3f5f;border-radius:12px;color:#fff;font-size:1em;}
        .form-group input:focus{outline:none;border-color:#ffd700;}
        .btn{width:100%;padding:16px;background:linear-gradient(135deg,#ffd700,#f5a623);color:#1a1f35;border:none;border-radius:12px;font-size:1.2em;font-weight:bold;cursor:pointer;transition:0.3s;}
        .btn:hover{transform:scale(1.02);}
        .footer{text-align:center;padding:30px;color:#555;border-top:1px solid #2a3f5f;margin-top:40px;}
        .footer a{color:#ffd700;text-decoration:none;}
    </style>
    </head>
    <body>
    <div class="container">
        <div class="header"><h1>➕ إضافة مباراة جديدة</h1><a href="/">🏠 العودة للرئيسية</a></div>
        <form method="POST">
            <div class="form-group"><label>🏠 الفريق الأول</label><input type="text" name="home" placeholder="مثال: الهلال" required></div>
            <div class="form-group"><label>✈️ الفريق الثاني</label><input type="text" name="away" placeholder="مثال: النصر" required></div>
            <div class="form-group"><label>🏴 علم الأول</label><input type="text" name="home_flag" placeholder="🇸🇦" value="🏴"></div>
            <div class="form-group"><label>🏴 علم الثاني</label><input type="text" name="away_flag" placeholder="🇦🇪" value="🏴"></div>
            <div class="form-group"><label>📍 الملعب</label><input type="text" name="stadium" placeholder="مثال: ملعب الملك فهد"></div>
            <div class="form-group"><label>📅 التاريخ</label><input type="date" name="date" required></div>
            <div class="form-group"><label>🕒 الوقت</label><input type="time" name="time" required></div>
            <button type="submit" class="btn">✅ إضافة المباراة</button>
        </form>
        <div class="footer"><p>🏆 كأس العالم 2026 - <a href="https://t.me/Ali_worldcup_bot">البوت على تليجرام</a></p></div>
    </div>
    </body>
    </html>
    '''

@app.route('/delete_match/<int:match_id>')
def delete_match(match_id):
    match = Match.query.get(match_id)
    if match:
        db.session.delete(match)
        db.session.commit()
    return redirect(url_for('home'))

# ========== بوت التليجرام ==========
class TelegramBot:
    def __init__(self):
        self.token = BOT_TOKEN
        self.updater = Updater(self.token)
        self.dispatcher = self.updater.dispatcher
        self.dispatcher.add_handler(CommandHandler("start", self.start))
        self.dispatcher.add_handler(CommandHandler("matches", self.matches))

    def start(self, update: Update, context):
        update.message.reply_text(
            "🎉 مرحباً بك في بوت كأس العالم 2026!\n\n"
            "📌 الأوامر:\n"
            "/start - بدء البوت\n"
            "/matches - عرض المباريات\n\n"
            "🌐 زور موقعنا:\n"
            "https://wor-ldcup-system.onrender.com"
        )

    def matches(self, update: Update, context):
        matches = Match.query.all()
        if not matches:
            update.message.reply_text("📭 لا توجد مباريات")
            return
        result = "📋 المباريات:\n\n"
        for m in matches:
            result += f"{m.home_flag} {m.home} 🆚 {m.away_flag} {m.away}\n"
            result += f"📍 {m.stadium or 'غير محدد'} | 📅 {m.date or 'غير محدد'}\n\n"
        update.message.reply_text(result)

    def run(self):
        logging.info("🤖 البوت يعمل...")
        self.updater.start_polling()
        self.updater.idle()

# ========== التشغيل ==========
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    bot = TelegramBot()
    Thread(target=bot.run, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
