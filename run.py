import telebot

# ضع التوكن الخاص بك هنا بدلاً من النص الموجود
TOKEN = "8689943788:AAFfmE62a4h-eLXYAcOXvSUgmkLs5KZZwts" 
CHANNEL_ID = "-1004372754611"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "✅ البوت يعمل الآن!")

print("🤖 البوت متصل...")
bot.infinity_polling()
