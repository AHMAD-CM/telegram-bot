import yt_dlp
import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("TOKEN")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    ydl_opts = {
        'outtmpl': 'video.%(ext)s',
        'format': 'mp4',
        'noplaylist': True,
        'quiet': True
    }

    try:
        await update.message.reply_text("⏳ جاري التحميل...")

        loop = asyncio.get_event_loop()

        def download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

        await loop.run_in_executor(None, download)

        # البحث عن اسم الملف الناتج
        file_name = None
        for file in os.listdir():
            if file.startswith("video.") and file.endswith(".mp4"):
                file_name = file
                break

        if file_name:
            with open(file_name, "rb") as video_file:
                await update.message.reply_video(video=video_file)
            os.remove(file_name)
        else:
            await update.message.reply_text("❌ ما تم العثور على الفيديو بعد التحميل.")

    except Exception as e:
        await update.message.reply_text("❌ صار خطأ أثناء التحميل.")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

print("Bot is running...")
app.run_polling()
