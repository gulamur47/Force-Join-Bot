import logging
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

# --- Render Port Fix ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_health_check_server():
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_health_check_server, daemon=True).start()

# --- কনফিগারেশন ---
TOKEN = '8510787985:AAHjszZmTMwqvqTfbFMJdqC548zBw4Qh0S0' 
WATCH_NOW_URL = "https://mmshotbd.blogspot.com/?m=1"

# নতুন ১১টি চ্যানেল ডাটাবেস (ID/Username এবং Invite Link)
CHANNELS_DATA = [
    {"id": "@virallink259", "name": "ভাইরাল ভিদিও লিংক এক্সপ্রেস ২০২৬🔥❤️", "link": "https://t.me/virallink259"},
    {"id": -1002279183424, "name": "Primium App Zone", "link": "https://t.me/+5PNLgcRBC0IxYjll"}, # Private
    {"id": "@virallink246", "name": "Bd beauty viral", "link": "https://t.me/virallink246"},
    {"id": "@viralexpress1", "name": "Facebook🔥 Instagram Link🔥", "link": "https://t.me/viralexpress1"},
    {"id": "@movietime467", "name": "🎬MOVIE🔥 TIME💥", "link": "https://t.me/movietime467"},
    {"id": "@viralfacebook9", "name": "BD MMS VIDEO🔥🔥", "link": "https://t.me/viralfacebook9"},
    {"id": "@viralfb24", "name": "দেশি ভাবি ভাইরাল🔥🥵", "link": "https://t.me/viralfb24"},
    {"id": "@fbviral24", "name": "কচি মেয়েদের ভাইরাল ভিদিও🔥", "link": "https://t.me/fbviral24"},
    {"id": -1001550993047, "name": "ভাইরাল ভিদিও রিকুয়েষ্ট🥵", "link": "https://t.me/+WAOUc1rX6Qk3Zjhl"}, # Private
    {"id": -1002011739504, "name": "Viral Video BD 🌍🔥", "link": "https://t.me/+la630-IFwHAwYWVl"}, # Private
    {"id": -1002444538806, "name": "Ai Prompt Studio 🎨📸", "link": "https://t.me/+AHsGXIDzWmJlZjVl"} # Private
]

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def check_all_joined(user_id, context):
    not_joined = []
    for channel in CHANNELS_DATA:
        try:
            member = await context.bot.get_chat_member(chat_id=channel["id"], user_id=user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                not_joined.append(channel)
        except Exception as e:
            # যদি বট চ্যানেলে অ্যাডমিন না থাকে তবে এরর দিবে, তখন আমরা ধরে নেব জয়েন করেনি
            not_joined.append(channel)
    return not_joined

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    stylish_name = f"👤 <b>{user.first_name}</b>"
    
    not_joined_list = await check_all_joined(user_id, context)

    if not not_joined_list:
        success_text = (
            f"🎉 স্বাগতম {stylish_name}\n"
            f"✅ আপনি সফলভাবে সব চ্যানেলে Join করেছেন ❤️\n"
            f"▶️ ভিডিও দেখতে এখনই <b>[Watch Now]</b> বাটনে ক্লিক করুন 🎬✨"
        )
        watch_kb = [[InlineKeyboardButton("Watch Now 🎬", url=WATCH_NOW_URL)]]
        await update.message.reply_text(success_text, reply_markup=InlineKeyboardMarkup(watch_kb), parse_mode=ParseMode.HTML)
    else:
        buttons = []
        for channel in not_joined_list:
            buttons.append([InlineKeyboardButton(f"Join {channel['name']}", url=channel['link'])])
        
        buttons.append([InlineKeyboardButton("Check Joined ✅", callback_data="check_status")])
        
        caption = (
            f"Hello {stylish_name},\n\n"
            "🚨 <b>Attention Please!</b>\n\n"
            "Viral ভিডিও দেখার আগে আমাদের নিচের Channel গুলোতে Join করা বাধ্যতামূলক।\n"
            "সবগুলো চ্যানেল Join না করলে ভিডিও লিঙ্ক কাজ করবে না ❌\n\n"
            "Join শেষ হলে <b>Check Joined</b> ক্লিক করুন ✅"
        )
        await update.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.HTML)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    stylish_name = f"<b>{user.first_name}</b>"
    not_joined_list = await check_all_joined(user.id, context)
    
    if not not_joined_list:
        await query.answer(f"ধন্যবাদ {user.first_name}! সব চেক করা হয়েছে।", show_alert=True)
        success_text = (
            f"🎉 স্বাগতম {stylish_name}\n"
            f"✅ আপনি সফলভাবে সব চ্যানেলে Join করেছেন ❤️\n"
            f"▶️ ভিডিও দেখতে এখনই <b>[Watch Now]</b> বাটনে ক্লিক করুন 🎬✨"
        )
        watch_kb = [[InlineKeyboardButton("Watch Now 🎬", url=WATCH_NOW_URL)]]
        await query.edit_message_text(success_text, reply_markup=InlineKeyboardMarkup(watch_kb), parse_mode=ParseMode.HTML)
    else:
        await query.answer("❌ আপনি এখনও সব চ্যানেলে জয়েন করেননি! সব লিঙ্কে ক্লিক করে জয়েন করুন।", show_alert=True)

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    print("Bot is running with 11 channels on Render...")
    app.run_polling()
