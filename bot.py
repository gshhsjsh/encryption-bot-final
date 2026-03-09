#!/usr/bin/env python3
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
    """فحص الملفات والنصوص للبحث عن محتوى مشبوه"""
    
    MALICIOUS_PATTERNS = [
        r"os\.system", r"os\.popen", r"subprocess\.",
        r"exec\(", r"eval\(", r"__import__",
        r"open\(", r"os\.remove", r"shutil\.",
        r"socket\.", r"requests\.", r"urllib\.",
        r"getattr", r"setattr", r"globals\(\)", r"locals\(\)",
        r"__dict__", r"__code__", r"__builtins__",
    ]
    
    DANGEROUS_KEYWORDS = [
        "DROP TABLE", "DELETE FROM", "INSERT INTO", "cmd.exe", 
        "powershell", "bash", "sh", "nc", "ncat", "wget", "curl"
    ]
    
    @staticmethod
    def scan(content: str) -> tuple:
        """فحص المحتوى عن الأنماط الخطرة"""
        if not content or len(content) < 5:
            return True, ""
        
        for pattern in SecurityScanner.MALICIOUS_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                return False, f"تم اكتشاف نمط خطر: {pattern}"
        
        for keyword in SecurityScanner.DANGEROUS_KEYWORDS:
            if keyword.lower() in content.lower():
                return False, f"تم اكتشاف كلمة مفتاحية خطرة: {keyword}"
        
        if len(content) > 1000000:
            return False, "حجم الملف كبير جداً"
        
        return True, ""

# ====================== Web Server for Render ======================
app = Flask(__name__)

@app.route("/")
def home():
    return "🔐 Encryption Bot is running!"

@app.route("/health")
def health():
    return {"status": "ok"}

# ====================== Configuration ======================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8541268288:AAEPRpX9FRzQkRb5odU3UJYfW1AgcxfltYg")
ADMIN_ID = 8532063752

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

user_state = {}

# ====================== Encryption Functions ======================
def encrypt_base64(data: str) -> str:
    return base64.b64encode(data.encode()).decode()

def encrypt_base32(data: str) -> str:
    return base64.b32encode(data.encode()).decode()

def encrypt_base16(data: str) -> str:
    return base64.b16encode(data.encode()).decode()

def encrypt_base85(data: str) -> str:
    return base64.b85encode(data.encode()).decode()

def encrypt_hex(data: str) -> str:
    return data.encode().hex()

def encrypt_zlib(data: str) -> str:
    return zlib.compress(data.encode()).hex()

def encrypt_lzma(data: str) -> str:
    return lzma.compress(data.encode()).hex()

def encrypt_marshal(data: str) -> str:
    try:
        code = compile(data, "<string>", "exec")
        return f"import marshal\nexec(marshal.loads({repr(marshal.dumps(code))}))"
    except:
        return data

def encrypt_emoji(data: str) -> str:
    emojis = ["😂", "🔥", "👍", "❤️", "💯", "✨", "🚀", "💎"]
    return "".join([random.choice(emojis) + c for c in data])

def apply_encryption(text: str, method: str) -> str:
    try:
        if method == "base64":
            return encrypt_base64(text)
        elif method == "base32":
            return encrypt_base32(text)
        elif method == "base16":
            return encrypt_base16(text)
        elif method == "base85":
            return encrypt_base85(text)
        elif method == "hex":
            return encrypt_hex(text)
        elif method == "zlib":
            return encrypt_zlib(text)
        elif method == "lzma":
            return encrypt_lzma(text)
        elif method == "marshal":
            return encrypt_marshal(text)
        elif method == "emoji":
            return encrypt_emoji(text)
        else:
            return encrypt_base64(text)
    except Exception as e:
        logger.error(f"Encryption error: {e}")
        return text

def apply_multi_layer(text: str, method: str, layers: int) -> str:
    current = text
    for _ in range(layers):
        current = apply_encryption(current, method)
    return current

def auto_decrypt(text: str) -> str:
    try:
        # Try base64
        if re.match(r"^[A-Za-z0-9+/=]+$", text) and len(text) % 4 == 0:
            try:
                return base64.b64decode(text).decode()
            except:
                pass
        
        # Try base32
        try:
            return base32.b32decode(text).decode()
        except:
            pass
        
        # Try hex
        if re.match(r"^[0-9a-fA-F]+$", text):
            try:
                return bytes.fromhex(text).decode()
            except:
                pass
        
        # Try zlib
        try:
            return zlib.decompress(bytes.fromhex(text)).decode()
        except:
            pass
        
        # Try lzma
        try:
            return lzma.decompress(bytes.fromhex(text)).decode()
        except:
            pass
    except Exception as e:
        logger.error(f"Decryption error: {e}")
    
    return "❌ تعذر فك التشفير"

# ====================== Bot Handlers ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = ReplyKeyboardMarkup([["🔐 تشفير"], ["🔓 فك التشفير"]], resize_keyboard=True)
    await update.message.reply_text("🔐 أهلاً! اختر العملية:", reply_markup=kb)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    uid = update.effective_user.id
    state = user_state.get(uid, {})

    if text == "🔐 تشفير":
        user_state[uid] = {"step": "choose_method"}
        ikb = InlineKeyboardMarkup([
            [InlineKeyboardButton("base64", callback_data="m_base64"), InlineKeyboardButton("base32", callback_data="m_base32")],
            [InlineKeyboardButton("base16", callback_data="m_base16"), InlineKeyboardButton("base85", callback_data="m_base85")],
            [InlineKeyboardButton("hex", callback_data="m_hex"), InlineKeyboardButton("zlib", callback_data="m_zlib")],
            [InlineKeyboardButton("lzma", callback_data="m_lzma"), InlineKeyboardButton("marshal", callback_data="m_marshal")],
            [InlineKeyboardButton("emoji", callback_data="m_emoji")]
        ])
        await update.message.reply_text("اختر طريقة التشفير:", reply_markup=ikb)
    
    elif text == "🔓 فك التشفير":
        user_state[uid] = {"step": "wait_decrypt"}
        await update.message.reply_text("أرسل النص أو الملف المشفر:")
    
    elif state.get("step") == "wait_decrypt":
        is_safe, reason = SecurityScanner.scan(text)
        if not is_safe:
            await update.message.reply_text(f"⚠️ تنبيه أمني: {reason}")
            return
        
        result = auto_decrypt(text)
        await update.message.reply_text(f"✅ النتيجة:\n\n`{result}`", parse_mode="Markdown")
        user_state[uid] = {}
    
    elif state.get("step") == "wait_content":
        is_safe, reason = SecurityScanner.scan(text)
        if not is_safe:
            await update.message.reply_text(f"⚠️ تنبيه أمني: {reason}")
            return
        
        user_state[uid].update({"content": text, "step": "wait_layers"})
        await update.message.reply_text("كم عدد الطبقات؟ (1-100):")
    
    elif state.get("step") == "wait_layers":
        try:
            layers = int(text)
            if 1 <= layers <= 100:
                s = user_state[uid]
                result = apply_multi_layer(s["content"], s["method"], layers)
                await update.message.reply_text(f"✅ تم التشفير بـ {layers} طبقة")
                await update.message.reply_text(f"`{result}`", parse_mode="Markdown")
                user_state[uid] = {}
            else:
                await update.message.reply_text("أدخل رقم بين 1 و 100")
        except:
            await update.message.reply_text("أدخل رقم صحيح")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    await query.answer()
    data = query.data

    if data.startswith("m_"):
        method = data[2:]
        user_state[uid] = {"method": method, "step": "wait_content"}
        await query.edit_message_text("أرسل النص المراد تشفيره:")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    state = user_state.get(uid, {})
    
    if state.get("step") == "wait_decrypt":
        try:
            doc = update.message.document
            file = await doc.get_file()
            content = await file.download_as_bytearray()
            text_content = content.decode('utf-8', errors='ignore')
            
            is_safe, reason = SecurityScanner.scan(text_content)
            if not is_safe:
                await update.message.reply_text(f"⚠️ ملف ملغم: {reason}")
                return
            
            result = auto_decrypt(text_content)
            await update.message.reply_text(f"✅ النتيجة:\n\n`{result}`", parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"❌ خطأ: {str(e)}")
        
        user_state[uid] = {}

def run_bot():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.run_polling()

if __name__ == "__main__":
    import threading
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
