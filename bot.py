import logging, os, threading, sqlite3, asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)

# ================== HEALTH CHECK ==================
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_health_check_server():
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_health_check_server, daemon=True).start()

# ================== CONFIG ==================
TOKEN = "YOUR_BOT_TOKEN"
ADMIN_IDS = [6406804999]
WATCH_NOW_URL = "https://mmshotbd.blogspot.com/?m=1"

logging.basicConfig(level=logging.INFO)

# ================== DATABASE ==================
db = sqlite3.connect("forcejoin.db", check_same_thread=False)
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS channels(
    id TEXT PRIMARY KEY,
    name TEXT,
    link TEXT
)
""")
cur.execute("""
CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY,
    unlocked INTEGER DEFAULT 0
)
""")
db.commit()

# ================== INITIAL CHANNELS ==================
INITIAL_CHANNELS = [
    ("@virallink259","ভাইরাল ভিদিও লিংক এক্সপ্রেস ২০২৬🔥❤️","https://t.me/virallink259"),
    ("-1002279183424","Primium App Zone","https://t.me/+5PNLgcRBC0IxYjll"),
    ("@virallink246","Bd beauty viral","https://t.me/virallink246"),
    ("@viralexpress1","Facebook🔥 Instagram Link🔥","https://t.me/viralexpress1"),
    ("@movietime467","🎬MOVIE🔥 TIME💥","https://t.me/movietime467"),
    ("@viralfacebook9","BD MMS VIDEO🔥🔥","https://t.me/viralfacebook9"),
    ("@viralfb24","দেশি ভাবি ভাইরাল🔥🥵","https://t.me/viralfb24"),
    ("@fbviral24","কচি মেয়েদের ভাইরাল ভিদিও🔥","https://t.me/fbviral24"),
    ("-1001550993047","ভাইরাল ভিদিও রিকুয়েষ্ট🥵","https://t.me/+WAOUc1rX6Qk3Zjhl"),
    ("-1002011739504","Viral Video BD 🌍🔥","https://t.me/+la630-IFwHAwYWVl"),
    ("-1002444538806","Ai Prompt Studio 🎨📸","https://t.me/+AHsGXIDzWmJlZjVl")
]

for c in INITIAL_CHANNELS:
    cur.execute("INSERT OR IGNORE INTO channels VALUES(?,?,?)", c)
db.commit()

# ================== UTIL ==================
def is_admin(uid):
    return uid in ADMIN_IDS

async def check_all_joined(user_id, bot):
    not_joined = []
    for cid, name, link in cur.execute("SELECT * FROM channels"):
        try:
            member = await bot.get_chat_member(cid, user_id)
            if member.status not in ["member","administrator","creator"]:
                not_joined.append((cid,name,link))
        except:
            not_joined.append((cid,name,link))
    return not_joined

# ================== STATES ==================
BROADCAST_MODE = {}
POST_TITLE, POST_PHOTO, POST_FORCE, POST_TARGET, POST_WEBSITE, POST_CONFIRM = range(6)
POST_CREATION = {}

# ================== START / CHECK ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if update.message is None: return
    uid = user.id
    stylish_name = f"<b>{user.first_name or 'User'} {user.last_name or ''}</b>"

    cur.execute("INSERT OR IGNORE INTO users(user_id) VALUES(?)",(uid,))
    db.commit()
    not_joined = await check_all_joined(uid, context.bot)

    if not not_joined:
        cur.execute("UPDATE users SET unlocked=1 WHERE user_id=?",(uid,))
        db.commit()
        await update.message.reply_text(
            f"🎉 স্বাগতম 👤 {stylish_name}\n✅ আপনি সফলভাবে সব চ্যানেলে Join করেছেন ❤️",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Watch Now 🎬", url=WATCH_NOW_URL)]]),
            parse_mode=ParseMode.HTML
        )
    else:
        buttons = [[InlineKeyboardButton(f"Join {name}", url=link)] for _,name,link in not_joined]
        buttons.append([InlineKeyboardButton("Check Joined ✅", callback_data="check")])
        caption = (f"Hello 👤 {stylish_name},\n\n🚨 <b>Attention Please!</b>\n\n"
                   f"Viral ভিডিও দেখার আগে আমাদের নিচের Channel গুলোতে Join করা বাধ্যতামূলক।\n"
                   f"সবগুলো চ্যানেল Join না করলে ভিডিও লিঙ্ক কাজ করবে না ❌\n\n"
                   f"Join শেষ হলে <b>Check Joined</b> ক্লিক করুন ✅")
        await update.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.HTML)

async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    not_joined = await check_all_joined(uid, context.bot)
    if not not_joined:
        cur.execute("UPDATE users SET unlocked=1 WHERE user_id=?",(uid,))
        db.commit()
        await update.message.reply_text("✅ সব চ্যানেল Join হয়েছে!", 
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Watch Now 🎬", url=WATCH_NOW_URL)]]))
    else:
        await update.message.reply_text("❌ এখনও সব Channel Join হয়নি!")

async def check_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    not_joined = await check_all_joined(uid, context.bot)
    if not not_joined:
        cur.execute("UPDATE users SET unlocked=1 WHERE user_id=?",(uid,))
        db.commit()
        await query.edit_message_text("✅ সব চ্যানেল Join সফল হয়েছে! ❤️", 
                                      reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Watch Now 🎬", url=WATCH_NOW_URL)]]))
    else:
        await query.answer("❌ এখনো সব চ্যানেল Join করেননি!", show_alert=True)

# ================== POST CREATION ==================
def get_channel_markup(selected_list, prefix):
    keyboard = []
    for cid, name, link in cur.execute("SELECT * FROM channels"):
        status = "✅" if cid in selected_list else "❌"
        keyboard.append([InlineKeyboardButton(f"{status} {name}", callback_data=f"{prefix}|{cid}")])
    keyboard.append([InlineKeyboardButton("➡️ Done", callback_data=f"{prefix}_done")])
    return InlineKeyboardMarkup(keyboard)

async def newpost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    POST_CREATION[update.effective_user.id] = {'force': set(), 'target': set()}
    await update.message.reply_text("📝 Send the Post Title:")
    return POST_TITLE

async def post_title_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    POST_CREATION[update.effective_user.id]['title'] = update.message.text
    await update.message.reply_text("📸 Now send the Post Photo:")
    return POST_PHOTO

async def post_photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("❌ Photo পাঠান!")
        return POST_PHOTO
    POST_CREATION[update.effective_user.id]['photo'] = update.message.photo[-1].file_id
    await update.message.reply_text("🛡️ Select Force Join Channels:", reply_markup=get_channel_markup(set(), "fchan"))
    return POST_FORCE

async def post_force_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    if query.data == "fchan_done":
        await query.edit_message_text("📌 Select Target Channels:", reply_markup=get_channel_markup(set(), "tchan"))
        return POST_TARGET
    cid = query.data.split("|")[1]
    POST_CREATION[uid]['force'].add(cid) if cid not in POST_CREATION[uid]['force'] else POST_CREATION[uid]['force'].remove(cid)
    await query.edit_message_reply_markup(get_channel_markup(POST_CREATION[uid]['force'], "fchan"))
    return POST_FORCE

async def post_target_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    if query.data == "tchan_done":
        await query.edit_message_text("🔗 Send URL or type 'skip':")
        return POST_WEBSITE
    cid = query.data.split("|")[1]
    POST_CREATION[uid]['target'].add(cid) if cid not in POST_CREATION[uid]['target'] else POST_CREATION[uid]['target'].remove(cid)
    await query.edit_message_reply_markup(get_channel_markup(POST_CREATION[uid]['target'], "tchan"))
    return POST_TARGET

async def post_website_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    data = POST_CREATION[uid]
    url = update.message.text if update.message.text.lower() != 'skip' else None

    # Sending post to target channels
    for cid in data['target']:
        btn = InlineKeyboardMarkup([[InlineKeyboardButton("🎬 Watch Video 🔞", callback_data=f"v|{','.join(data['force']) if data['force'] else 'none'}|{url or WATCH_NOW_URL}")]]) if url else None
        try:
            await context.bot.send_photo(chat_id=cid, photo=data['photo'], caption=data['title'], reply_markup=btn, parse_mode=ParseMode.HTML)
        except: pass

    await update.message.reply_text("✅ Post Sent!")
    POST_CREATION.pop(uid, None)
    return ConversationHandler.END

# ================== WATCH CALLBACK ==================
async def watch_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    _, force_str, url = query.data.split("|",2)
    required_ids = [] if force_str == "none" else force_str.split(",")
    not_joined = await check_all_joined(uid, context.bot)
    missing = [c for c in required_ids if c in [x[0] for x in not_joined]]
    if missing:
        buttons = [[InlineKeyboardButton(f"Join {x[1]}", url=x[2])] for x in not_joined if x[0] in missing]
        buttons.append([InlineKeyboardButton("♻️ Try Again", callback_data=query.data)])
        await query.answer("❌ Access Denied!", show_alert=True)
        await context.bot.send_message(uid, "🚫 You must join the channels below:", reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await query.answer("✅ Access Granted!")
        try: await context.bot.send_message(uid, f"🚀 Here is your Video/Link:\n{url}", parse_mode=ParseMode.HTML)
        except: await query.answer("❌ Please start bot in private first!", show_alert=True)

# ================== BOT RUN ==================
app = Application.builder().token(TOKEN).build()

post_handler = ConversationHandler(
    entry_points=[CommandHandler("newpost", newpost)],
    states={
        POST_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, post_title_handler)],
        POST_PHOTO: [MessageHandler(filters.PHOTO, post_photo_handler)],
        POST_FORCE: [CallbackQueryHandler(post_force_callback, pattern="^fchan")],
        POST_TARGET: [CallbackQueryHandler(post_target_callback, pattern="^tchan")],
        POST_WEBSITE: [MessageHandler(filters.TEXT & ~filters.COMMAND, post_website_handler)]
    },
    fallbacks=[CommandHandler("postcancel", post_cancel)]
)

# Admin commands
app.add_handler(post_handler)
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("check", check_command))
app.add_handler(CallbackQueryHandler(check_callback, pattern="check"))
app.add_handler(CallbackQueryHandler(watch_callback, pattern="^v\|"))
app.add_handler(CommandHandler("addchannel", addchannel))
app.add_handler(CommandHandler("removechannel", removechannel))
app.add_handler(CommandHandler("listchannels", listchannels))
app.add_handler(CommandHandler("broadcast", broadcast))
app.add_handler(MessageHandler(filters.ALL & (~filters.COMMAND), handle_broadcast))
app.add_handler(CommandHandler("postcancel", post_cancel))

print("🔥 FULL FORCE JOIN BOT WITH MULTI FORCE CHANNELS RUNNING...")
app.run_polling()
