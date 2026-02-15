import os
import asyncio
import uuid
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters, CallbackQueryHandler
import yt_dlp

# سيرفر وهمي لتشغيل البوت مجانا على Render
app_flask = Flask('')
@app_flask.route('/')
def home(): return "Bot is Running!"

def run_flask():
    app_flask.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# إعدادات البوت
TOKEN = os.getenv("TOKEN")
CHANNEL_ID = "@ArabtikChannel" 
AD_LINK = "https://shrinkme.click/0TmnW"

# مخزن مؤقت للروابط
links_db = {}

# دالة الترحيب عند كتابة /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    welcome_text = (
        f"أهلاً بك يا {user_name} في بوت @ArabtikBot 🤖\n\n"
        "أنا أساعدك في تحميل المقاطع من تيك توك، إنستقرام، ويوتيوب بدون علامة مائية وبأعلى جودة! ✨\n\n"
        "**كيفية الاستخدام:**\n"
        "1️⃣ اشترك في قناتنا الرسمية.\n"
        "2️⃣ أرسل رابط الفيديو الذي تريد تحميله.\n"
        "3️⃣ اضغط على زر فتح القفل وشاهد الإعلان.\n\n"
        "ابدأ الآن بإرسال أول رابط! 🚀"
    )
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

def download_video(url):
    ydl_opts = {'format': 'best', 'outtmpl': 'video.mp4', 'quiet': True, 'no_warnings': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return 'video.mp4'

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url.startswith("http"): return
    user_id = update.message.from_user.id

    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if member.status in ['left', 'kicked']:
            keyboard = [[InlineKeyboardButton("اشترك في القناة لتفعيل البوت ✅", url=f"https://t.me/{CHANNEL_ID.replace('@', '')}")]]
            await update.message.reply_text("❌ يجب عليك الاشتراك أولاً لاستخدام البوت:", reply_markup=InlineKeyboardMarkup(keyboard))
            return
    except: pass

    link_id = str(uuid.uuid4())[:8]
    links_db[link_id] = url
    keyboard = [[InlineKeyboardButton("🔓 فتح قفل التحميل (اضغط هنا)", callback_data=f"down_{link_id}")]]
    await update.message.reply_text("✅ الرابط جاهز! اضغط للتحميل:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data.startswith("down_"):
        link_id = query.data.replace("down_", "")
        url = links_db.get(link_id)
        if not url:
            await query.edit_message_text("❌ انتهت صلاحية هذا الرابط.")
            return

        await query.edit_message_text(f"⚠️ **خطوة أخيرة:**\n🔗 {AD_LINK}\n\nتخطى الرابط وسيبدأ التحميل تلقائياً... ⏳")
        try:
            video_file = await asyncio.to_thread(download_video, url)
            await query.message.reply_video(video=open(video_file, 'rb'), caption="✨ تم بواسطة @ArabtikBot")
            os.remove(video_file)
            del links_db[link_id]
        except: await query.message.reply_text("❌ حدث خطأ في التحميل.")

if __name__ == '__main__':
    Thread(target=run_flask).start()
    application = ApplicationBuilder().token(TOKEN).build()
    
    # إضافة معالج أمر /start
    application.add_handler(CommandHandler("start", start))
    
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.run_polling()
