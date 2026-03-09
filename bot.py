import logging
import base64
import os
import json
import time
import marshal
import zlib
import lzma
import re
import random
import threading
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)
from flask import Flask

# ====================== Security Scanner ======================
class SecurityScanner:
    @staticmethod
    def scan(content: str) -> tuple:
        if not content: return True, ""
        patterns = [r"os\.system", r"subprocess\.", r"exec\(", r"eval\("]
        for p in patterns:
            if re.search(p, content, re.IGNORECASE):
                return False, f"تم اكتشاف نمط خطر: {p}"
        return True, ""

# ====================== Web Server ======================
app = Flask(__name__)
@app.route("/")
def home(): return "Bot is running!"
@app.route("/health")
def health(): return {"status": "ok"}

# ====================== Bot Logic ======================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8541268288:AAEPRpX9FRzQkRb5odU3UJYfW1AgcxfltYg")
user_state = {}

def apply_encryption(text, method):
    if method == "base64": return base64.b64encode(text.encode()).decode()
    if method == "hex": return text.encode().hex()
    return base64.b64encode(text.encode()).decode()

async def start(update, context):
    kb = ReplyKeyboardMarkup([["🔐 تشفير"], ["🔓 فك التشفير"]], resize_keyboard=True)
    await update.message.reply_text("🔐 أهلاً! اختر العملية:", reply_markup=kb)

async def handle_message(update, context):
    text = update.message.text
    uid = update.effective_user.id
    state = user_state.get(uid, {})
    if text == "🔐 تشفير":
        user_state[uid] = {"step": "wait_content", "method": "base64"}
        await update.message.reply_text("أرسل النص المراد تشفيره:")
    elif state.get("step") == "wait_content":
        res = apply_encryption(text, state["method"])
        await update.message.reply_text(f"✅ النتيجة:\n`{res}`", parse_mode="Markdown")
        user_state[uid] = {}

def run_bot():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
