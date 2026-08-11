import os
import yt_dlp
import instaloader
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📹 دانلود از یوتیوب", callback_data="menu_youtube")],
        [InlineKeyboardButton("📸 دانلود از اینستاگرام", callback_data="menu_instagram")],
        [InlineKeyboardButton("🎵 آهنگ‌یاب", callback_data="menu_song")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🎬 به ربات دانلود و آهنگ‌یاب خوش آمدید!\n"
        "یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=reply_markup
    )

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data

    if choice == "menu_youtube":
        await query.edit_message_text("🌐 لینک ویدیو یوتیوب را بفرست:")
    elif choice == "menu_instagram":
        await query.edit_message_text("🌐 لینک پست اینستاگرام را بفرست:")
    elif choice == "menu_song":
        await query.edit_message_text("🎵 لینک ویدیو اینستاگرام را بفرست تا آهنگش را پیدا کنم:")

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    link = update.message.text
    if "youtube.com" in link or "youtu.be" in link:
        await update.message.reply_text("🎬 در حال دانلود از یوتیوب...")
        await download_youtube(update, link)
    elif "instagram.com" in link:
        await update.message.reply_text("📸 در حال دانلود از اینستاگرام...")
        await download_instagram(update, link)
    else:
        await update.message.reply_text("❌ لینک معتبر نیست. لینک یوتیوب یا اینستاگرام بفرست.")

async def download_youtube(update: Update, link: str):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'outtmpl': '%(title)s.%(ext)s'
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=True)
            filename = ydl.prepare_filename(info)
        await update.message.reply_text("✅ ویدیو دانلود شد!")
        await update.message.reply_document(document=open(filename, 'rb'))
        os.remove(filename)
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {e}")

async def download_instagram(update: Update, link: str):
    try:
        L = instaloader.Instaloader()
        shortcode = link.split('/')[-2]
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        filename = f"instagram_{shortcode}.mp4"
        L.download_post(post, target=".")
        await update.message.reply_text("✅ ویدیو دانلود شد!")
        await update.message.reply_document(document=open(filename, 'rb'))
        os.remove(filename)
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {e}")

async def find_instagram_song(update: Update, link: str):
    await update.message.reply_text("🎵 در حال جستجوی آهنگ...")
    try:
        response = requests.get(f"https://api.spotify.com/v1/search?q=instagram&type=track&limit=1")
        data = response.json()
        if data['tracks']['items']:
            song = data['tracks']['items'][0]
            song_name = song['name']
            artist = song['artists'][0]['name']
            await update.message.reply_text(f"🎵 آهنگ پیدا شد:\n{artist} - {song_name}")
        else:
            await update.message.reply_text("آهنگی پیدا نشد.")
    except Exception as e:
        await update.message.reply_text(f"❌ خطا در جستجوی آهنگ: {e}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(menu_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    print("🤖 ربات روشن شد...")
    app.run_polling()