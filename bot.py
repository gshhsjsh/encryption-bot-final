import logging
import base64
import os
import threading
import re
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask

# ====================== Web Server ======================
app = Flask(__name__)
@app.route("/")
def home(): return "Bot is running!"
@app.route("/health")
def health(): return "OK", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# ====================== Bot Logic ======================
BOT_TOKEN = "8541268288:AAEPRpX9FRzQkRb5odU3UJYfW1AgcxfltYg"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = ReplyKeyboardMarkup([["🔐 تشفير"], ["🔓 فك التشفير"]], resize_keyboard=True)
    await update.message.reply_text("🔐 أهلاً! البوت يعمل الآن بنجاح.", reply_markup=kb)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🔐 تشفير":
        await update.message.reply_text("أرسل النص المراد تشفيره:")
    else:
        res = base64.b64encode(text.encode()).decode()
        await update.message.reply_text(f"✅ النتيجة:\n`{res}`", parse_mode="Markdown")

def main():
    # Start Flask in a separate thread
    threading.Thread(target=run_flask, daemon=True).start()
    
    # Start Telegram Bot
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == "__main__":
    main()
