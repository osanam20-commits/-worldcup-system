import os
import logging
from threading import Thread
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from telegram import Update
from telegram.ext import Updater, CommandHandler

# ========== الإعدادات ==========
# ضع التوكن هنا - سيأخذه من متغيرات البيئة في Render
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8689943788:AAFfmE62a4h-eLXYAcOXvSUgmkLs5KZZwts")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@lvFaax5HzsxOTU0")
ADMIN_ID = int(os.environ.get("ADMIN_ID", 5528971195))

# ========== قاعدة البيانات ==========
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    home = db.Column(db.String(100))
    away = db.Column(db.String(100))
    home_flag = db.Column(db.String(10), default="🏴")
    away_flag = db.Column(db.String(10), default="🏴")
    stadium = db.Column(db.String(120))
    date = db.Column(db.String(20))
    time = db.Column(db.String(10))
    stage = db.Column(db.String(50), default="دور المجموعات")

# ========== إنشاء الجداول وإضافة مباريات تجريبية ==========
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
        print("✅ تم إضافة مباريات تجريبية!")

# ========== صفحات الويب ==========
@app.route('/')
def home():
    matches = Match.query.limit(5).all()
    total = Match.query.count()
    return render_template('index.html', matches=matches, total=total)

@app.route('/matches')
def matches_page():
    matches = Match.query.all()
    return render_template('matches.html', matches=matches)

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
            time=request.form['time'],
            stage=request.form.get('stage', 'دور المجموعات')
        )
        db.session.add(match)
        db.session.commit()
        return redirect(url_for('matches_page'))
    return render_template('add_match.html')

@app.route('/delete_match/<int:match_id>')
def delete_match(match_id):
    match = Match.query.get(match_id)
    if match:
        db.session.delete(match)
        db.session.commit()
    return redirect(url_for('matches_page'))

# ========== بوت التليجرام ==========
class TelegramBot:
    def __init__(self):
        self.token = BOT_TOKEN
        self.updater = Updater(self.token)
        self.dispatcher = self.updater.dispatcher
        self.dispatcher.add_handler(CommandHandler("start", self.start))
        self.dispatcher.add_handler(CommandHandler("help", self.help))
        self.dispatcher.add_handler(CommandHandler("matches", self.matches))

    def start(self, update: Update, context):
        update.message.reply_text(
            "🎉 مرحباً بك في بوت كأس العالم 2026!\n\n"
            "📌 الأوامر المتاحة:\n"
            "/start - بدء البوت\n"
            "/help - المساعدة\n"
            "/matches - عرض المباريات"
        )

    def help(self, update: Update, context):
        update.message.reply_text(
            "❓ المساعدة:\n"
            "/start - بدء البوت\n"
            "/help - هذه الرسالة\n"
            "/matches - عرض المباريات\n\n"
            "📱 يمكنك أيضاً زيارة موقعنا:\n"
            "https://wor-ldcup-system.onrender.com"
        )

    def matches(self, update: Update, context):
        matches = Match.query.all()
        if not matches:
            update.message.reply_text("📭 لا توجد مباريات حالياً")
            return
        result = "📋 قائمة المباريات:\n\n"
        for m in matches:
            result += f"{m.home_flag} {m.home} 🆚 {m.away_flag} {m.away}\n"
            result += f"📍 {m.stadium or 'غير محدد'}\n"
            result += f"📅 {m.date or 'غير محدد'} | 🕒 {m.time or 'غير محدد'}\n\n"
        update.message.reply_text(result)

    def run(self):
        logging.info("🤖 البوت يعمل...")
        self.updater.start_polling()
        self.updater.idle()

# ========== التشغيل ==========
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    # تشغيل البوت في خلفية
    bot = TelegramBot()
    bot_thread = Thread(target=bot.run, daemon=True)
    bot_thread.start()
    
    # تشغيل موقع الويب
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
