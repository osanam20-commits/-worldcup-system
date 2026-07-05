import os
import logging
from threading import Thread
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from telegram import Update
from telegram.ext import Updater, CommandHandler

# ========== الإعدادات ==========
# ضع التوكن هنا مباشرة
BOT_TOKEN = "8689943788:AAFfmE62a4h-eLXYAcOXvSUgmkLs5KZZwts"  # <- استبدل هذا بالتوكن
CHANNEL_ID = "@lvFaax5HzsxOTU0"
ADMIN_ID = 5528971195

# ========== قاعدة البيانات ==========
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    home = db.Column(db.String(100))
    away = db.Column(db.String(100))
    stadium = db.Column(db.String(120))
    date = db.Column(db.String(20))
    time = db.Column(db.String(10))

# ========== إنشاء الجداول ==========
with app.app_context():
    db.create_all()

# ========== صفحات الويب ==========
@app.route('/')
def home():
    return "✅ البوت شغال! 🎉"

@app.route('/matches')
def matches():
    matches = Match.query.all()
    return f"عدد المباريات: {len(matches)}"

# ========== بوت التليجرام ==========
class TelegramBot:
    def __init__(self):
        self.token = BOT_TOKEN
        self.updater = Updater(self.token)
        self.dispatcher = self.updater.dispatcher
        self.dispatcher.add_handler(CommandHandler("start", self.start))
        self.dispatcher.add_handler(CommandHandler("help", self.help))

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
            "/matches - عرض المباريات"
        )

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
