import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CallbackQueryHandler
import yt_dlp

# --- الإعدادات (تأكد من تعديل معرف قناتك) ---
TOKEN = os.getenv("TOKEN")
CHANNEL_ID = "@ArabtikChannel"  # <--- استبدل هذا بمعرف قناتك (مثل @MyChannel)
CHANNEL_LINK = f"https://t.me/ArabtikChannel"
# رابطك الربحي الجديد
AD_LINK = "https://shrinkme.click/0TmnW"

def download_video(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video.mp4',
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return 'video.mp4'

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    url = update.message.text

    if not url.startswith("http"):
        return

    # 1. التحقق من الاشتراك الإجباري
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if member.status in ['left', 'kicked']:
            keyboard = [[InlineKeyboardButton("اشترك في القناة لتفعيل البوت ✅", url=CHANNEL_LINK)]]
            await update.message.reply_text(
                "❌ **عذراً!** يجب عليك الاشتراك في القناة أولاً لاستخدام ميزة التحميل المجانية.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return
    except Exception:
        await update.message.reply_text("⚠️ **خطأ:** تأكد من إضافة البوت (@ArabtikBot) كمسؤول (Admin) في قناتك.")
        return

    # 2. عرض زر الإعلان قبل التحميل
    keyboard = [[InlineKeyboardButton("🔓 فتح قفل التحميل (اضغط هنا)", callback_data=f"down_{url}")]]
    await update.message.reply_text(
        "✅ **الرابط جاهز!**\nللحصول على الفيديو بدون علامة مائية وبأعلى جودة، يرجى الضغط على الزر أدناه وتخطي الإعلان لمرة واحدة فقط 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("down_"):
        url = query.data.replace("down_", "")
        
        # رسالة الإعلان مع رابط ShrinkMe الخاص بك
        ad_msg = (
            "⚠️ **خطوة أخيرة:**\n\n"
            f"يرجى الضغط على الرابط التالي وتخطي الإعلان:\n🔗 {AD_LINK}\n\n"
            "بمجرد الانتهاء من التخطي، سيبدأ التحميل تلقائياً هنا في المحادثة ⏳"
        )
        await query.edit_message_text(ad_msg)

        try:
            # 3. عملية التحميل في الخلفية
            video_file = await asyncio.to_thread(download_video, url)
            
            # إرسال الفيديو النهائي للمستخدم
            await query.message.reply_video(
                video=open(video_file, 'rb'),
                caption=f"✨ تم التحميل بنجاح بواسطة @ArabtikBot\n📢 للمزيد من المحتوى تابعنا هنا: {CHANNEL_LINK}"
            )
            os.remove(video_file) # حذف الملف لتوفير مساحة السيرفر
        except Exception:
            await query.message.reply_text("❌ حدث خطأ أثناء معالجة الرابط. تأكد أن الفيديو عام وغير محمي.")

if __name__ == '__main__':
    # بناء وتشغيل البوت
    app = ApplicationBuilder().token(TOKEN).build()
    
    # إضافة معالجات الرسائل والأزرار
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    print("البوت يعمل الآن بنجاح...")
    app.run_polling()
