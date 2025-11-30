import os
import sqlite3
from telegram import Update
from telegram.ext import Application, ContextTypes, CommandHandler, MessageHandler, filters
from groq import Groq
from flask import Flask, request

# Kalitlar
TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_KEY = os.getenv("GROQ_KEY")

client = Groq(api_key=GROQ_KEY)
app = Flask(__name__)
bot_app = Application.builder().token(TOKEN).build()

# Ma'lumotlar bazasi
conn = sqlite3.connect('data.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS history (user_id INTEGER, date TEXT, text TEXT)')

# Start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Xo'jayin, men abadiy tayyorman 🔥\nBuyruq bering!")

# Barcha xabarlarni qayta ishlash
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text or ""

    # Ovozli xabarni matnga aylantirish
    if update.message.voice or update.message.video or update.message.video_note:
        file = await (update.message.voice or update.message.video or update.message.video_note).get_file()
        path = "temp.ogg"
        await file.download_to_drive(path)
        with open(path, "rb") as f:
            transcript = client.audio.transcriptions.create(model="whisper-large-v3", file=f)
        text = transcript.text
        os.remove(path)

    # Oldingi suhbatlarni olish
    c.execute("SELECT date, text FROM history WHERE
