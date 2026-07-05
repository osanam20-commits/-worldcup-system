#!/usr/bin/env python3
import os
import logging
import threading
import time
from app import app
from app.bot import run_bot
from app.matches import matches_db
from app.utils import check_live_matches

# ========== الإعدادات ==========
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8689943788:AAFfmE62a4h-eLXYAcOXvSUgmkLs5KZZwts")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@your_channel")
PORT = int(os.environ.get("PORT", 5000))

# ========== الجدولة ==========
def schedule_check():
    """التحقق الدوري من المباريات"""
    while True:
        try:
            check_live_matches(matches_db, CHANNEL_ID, None)
            time.sleep(60)
        except Exception as e:
            logging.error(f"❌ خطأ في الجدولة: {e}")
            time.sleep(60)

# ========== التشغيل ==========
if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logging.info("🚀 بدء تشغيل النظام...")
    
    # تشغيل البوت في خلفية
    bot_thread = threading.Thread(
        target=run_bot,
        args=(BOT_TOKEN, CHANNEL_ID),
        daemon=True
    )
    bot_thread.start()
    
    # تشغيل الجدولة
    scheduler_thread = threading.Thread(
        target=schedule_check,
        daemon=True
    )
    scheduler_thread.start()
    
    # تشغيل موقع الويب
    logging.info(f"🌐 تشغيل الموقع على المنفذ {PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=False)
