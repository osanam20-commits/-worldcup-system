#!/usr/bin/env python3
import logging
from threading import Thread
from app.dashboard import app
from app.bot import TelegramBot
from app.scheduler import MatchScheduler
from app.models import db
logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
def run_bot(): TelegramBot().run()
def run_scheduler(): MatchScheduler().run()
def run_dashboard():
    with app.app_context(): db.create_all()
    app.run(host='0.0.0.0',port=5000,debug=False)
if __name__=='__main__':
    bot_thread=Thread(target=run_bot,daemon=True);bot_thread.start()
    scheduler_thread=Thread(target=run_scheduler,daemon=True);scheduler_thread.start()
    run_dashboard()
