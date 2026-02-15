import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import yt_dlp

# جلب التوكن من إعدادات Render
TOKEN = os.getenv("TOKEN")

async def download_video(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video.mp4',
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return 'video.mp4'

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "http" in url:
        msg = await update.message.reply_text("جاري التحميل... انتظر قليلاً ⏳")
        try:
            video_file = await asyncio.to_thread(download_video, url)
            await update.message.reply_video(video=open(video_file, 'rb'), caption="تم التحميل بواسطة بوتك الخاص! ✨")
            os.remove(video_file) # حذف الملف بعد الإرسال لتوفير المساحة
            await msg.delete()
        except Exception as e:
            await update.message.reply_text(f"حدث خطأ: {str(e)}")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    application.run_polling()
