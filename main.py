import os
import asyncio
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CallbackQueryHandler
import yt_dlp

# --- سيرفر وهمي لتشغيل البوت مجانا على Render ---
app_flask = Flask('')
@app_flask.route('/')
def home(): return "Bot is Running!"

def run_flask():
    app_flask.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# --- إعدادات البوت ---
TOKEN = os.getenv("TOKEN")
CHANNEL_ID = "@ArabtikChannel"
AD_LINK = "https://shrinkme.click/0TmnW"

def download_video(url):
    ydl_opts = {'format': 'best', 'outtmpl': 'video.mp4', 'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return 'video.mp4'

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    url = update.message.text
    if not url.startswith("http"): return

    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if member.status in ['left', 'kicked']:
            keyboard = [[InlineKeyboardButton("اشترك في القناة لتفعيل البوت ✅", url=f"https://t.me/{CHANNEL_ID.replace('@', '')}")]]
            await update.message.reply_text("❌ اشترك أولاً:", reply_markup=InlineKeyboardMarkup(keyboard))
            return
    except: pass

    keyboard = [[InlineKeyboardButton("🔓 فتح قفل التحميل", callback_data=f"down_{url}")]]
    await update.message.reply_text("✅ جاهز! اضغط للمشاهدة والتحميل:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data.startswith("down_"):
        url = query.data.replace("down_", "")
        await query.edit_message_text(f"⚠️ **خطوة أخيرة:**\n🔗 {AD_LINK}\n\nتخطى الرابط وسيبدأ التحميل تلقائياً...")
        try:
            video_file = await asyncio.to_thread(download_video, url)
            await query.message.reply_video(video=open(video_file, 'rb'), caption="✨ تم بواسطة @ArabtikBot")
            os.remove(video_file)
        except: await query.message.reply_text("❌ خطأ في التحميل.")

if __name__ == '__main__':
    # تشغيل السيرفر الوهمي في خلفية الكود
    Thread(target=run_flask).start()
    
    # تشغيل البوت
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.run_polling()
