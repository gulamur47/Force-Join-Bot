import logging, os, threading, sqlite3
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, ConversationHandler, MessageHandler, filters
)

# ================= HEALTH CHECK =================
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

threading.Thread(target=lambda: HTTPServer(("0.0.0.0", int(os.environ.get("PORT",8000))), HealthCheckHandler).serve_forever(), daemon=True).start()

# ================= CONFIG =================
TOKEN = "8510787985:AAHjszZmTMwqvqTfbFMJdqC548zBw4Qh0S0"
ADMIN_IDS = {6406804999}
WATCH_NOW_URL = "https://mmshotbd.blogspot.com/?m=1"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ================= DATABASE =================
DB = sqlite3.connect("bot.db", check_same_thread=False)
CURSOR = DB.cursor()
CURSOR.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)")
CURSOR.execute("CREATE TABLE IF NOT EXISTS channels (username TEXT PRIMARY KEY, button TEXT, link TEXT)")
CURSOR.execute("""CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    photo_file_id TEXT,
    force_join_channels TEXT,
    target_channels TEXT,
    url TEXT
)""")
DB.commit()

# ================= CHANNELS =================
CHANNELS_DATA = [
    {"id": "@virallink259", "name": "ভাইরাল ভিদিও লিংক এক্সপ্রেস ২০২৬🔥❤️", "link": "https://t.me/virallink259"},
    {"id": -1002279183424, "name": "Primium App Zone", "link": "https://t.me/+5PNLgcRBC0IxYjll"},
    {"id": "@virallink246", "name": "Bd beauty viral", "link": "https://t.me/virallink246"},
    {"id": "@viralexpress1", "name": "Facebook🔥 Instagram Link🔥", "link": "https://t.me/viralexpress1"},
    {"id": "@movietime467", "name": "🎬MOVIE🔥 TIME💥", "link": "https://t.me/movietime467"},
    {"id": "@viralfacebook9", "name": "BD MMS VIDEO🔥🔥", "link": "https://t.me/viralfacebook9"},
    {"id": "@viralfb24", "name": "দেশি ভাবি ভাইরাল🔥🥵", "link": "https://t.me/viralfb24"},
    {"id": "@fbviral24", "name": "কচি মেয়েদের ভাইরাল ভিদিও🔥", "link": "https://t.me/fbviral24"},
    {"id": -1001550993047, "name": "ভাইরাল ভিদিও রিকুয়েষ্ট🥵", "link": "https://t.me/+WAOUc1rX6Qk3Zjhl"},
    {"id": -1002011739504, "name": "Viral Video BD 🌍🔥", "link": "https://t.me/+la630-IFwHAwYWVl"},
    {"id": -1002444538806, "name": "Ai Prompt Studio 🎨📸", "link": "https://t.me/+AHsGXIDzWmJlZjVl"}
]

# ================= UTILS =================
def is_admin(user_id): return user_id in ADMIN_IDS
async def save_user(user_id): CURSOR.execute("INSERT OR IGNORE INTO users VALUES (?)",(user_id,));DB.commit()
async def check_all_joined(user_id, context):
    not_joined = []
    for channel in CHANNELS_DATA:
        try:
            member = await context.bot.get_chat_member(chat_id=channel["id"],user_id=user_id)
            if member.status not in ['member','administrator','creator']: not_joined.append(channel)
        except: not_joined.append(channel)
    return not_joined

# ================= START / CHECK =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user; await save_user(user.id)
    stylish_name = f"👤 <b>{user.first_name}</b>"
    not_joined_list = await check_all_joined(user.id, context)
    if not not_joined_list:
        watch_kb = InlineKeyboardButton("Watch Now 🎬",url=WATCH_NOW_URL)
        await update.message.reply_text(f"🎉 স্বাগতম {stylish_name}\n✅ সব চ্যানেল join করা আছে ❤️\n▶️ ভিডিও দেখতে এখনই Watch Now", reply_markup=InlineKeyboardMarkup([[watch_kb]]), parse_mode=ParseMode.HTML)
    else:
        buttons = [[InlineKeyboardButton(f"Join {c['name']}",url=c['link'])] for c in not_joined_list]
        buttons.append([InlineKeyboardButton("Check Joined ✅",callback_data="check_status")])
        await update.message.reply_text("🚨 ভিডিও দেখার আগে সব Channel join করতে হবে❌\nJoin শেষ হলে Check Joined ক্লিক করুন✅", reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.HTML)

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    not_joined_list = await check_all_joined(update.effective_user.id,context)
    if not not_joined_list:
        watch_kb = InlineKeyboardButton("Watch Now 🎬",url=WATCH_NOW_URL)
        await update.message.reply_text("✅ সব চ্যানেল join করা আছে!",reply_markup=InlineKeyboardMarkup([[watch_kb]]))
    else: await update.message.reply_text("❌ এখনো সব চ্যানেলে join করা হয়নি!")

# ================= POST / BROADCAST / WIZARD =================
POST_TITLE, POST_PHOTO, POST_FORCE_JOIN, POST_TARGET, POST_URL, CONFIRM_SEND, BROADCAST_MODE = range(7)
post_data = {}
broadcast_mode = {}

async def newpost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    await update.message.reply_text("📌 Post Title লিখুন:")
    return POST_TITLE

async def post_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    post_data['title'] = update.message.text
    await update.message.reply_text("📸 Post Photo পাঠান / skip করতে /skip টাইপ করুন")
    return POST_PHOTO

async def post_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    post_data['photo_file_id'] = update.message.photo[-1].file_id
    await send_force_join_selection(update, context)
    return POST_FORCE_JOIN

async def skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    post_data['photo_file_id'] = None
    await send_force_join_selection(update, context)
    return POST_FORCE_JOIN

# ================= FORCE JOIN INLINE SELECTION =================
async def send_force_join_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    force_selection[user_id] = set()
    buttons = []
    for c in CHANNELS_DATA:
        buttons.append([InlineKeyboardButton(c['name'], callback_data=f"fj|{c['id']}")])
    buttons.append([InlineKeyboardButton("Next ✅", callback_data="force_next")])
    await update.message.reply_text("📌 Force Join Channels select করুন:", reply_markup=InlineKeyboardMarkup(buttons))

async def force_join_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    if data.startswith("fj|"):
        channel_id = data.split("|")[1]
        if channel_id in force_selection[user_id]: force_selection[user_id].remove(channel_id)
        else: force_selection[user_id].add(channel_id)
        await query.answer(f"Selected: {len(force_selection[user_id])} channels")
    elif data=="force_next":
        post_data['force_join_channels'] = ",".join(force_selection[user_id])
        await send_target_selection(query, context)
    await query.edit_message_reply_markup(reply_markup=query.message.reply_markup)

# ================= TARGET CHANNEL INLINE SELECTION =================
async def send_target_selection(query, context):
    user_id = query.from_user.id
    target_selection[user_id] = set()
    buttons = []
    for c in CHANNELS_DATA:
        buttons.append([InlineKeyboardButton(c['name'], callback_data=f"tc|{c['id']}")])
    buttons.append([InlineKeyboardButton("Next ✅", callback_data="target_next")])
    await query.message.reply_text("📌 Target Channels select করুন:", reply_markup=InlineKeyboardMarkup(buttons))
    return POST_TARGET

async def target_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    if data.startswith("tc|"):
        channel_id = data.split("|")[1]
        if channel_id in target_selection[user_id]: target_selection[user_id].remove(channel_id)
        else: target_selection[user_id].add(channel_id)
        await query.answer(f"Selected: {len(target_selection[user_id])} channels")
    elif data=="target_next":
        post_data['target_channels'] = ",".join(target_selection[user_id])
        await query.message.reply_text("🔗 URL দিন / skip করতে /skip টাইপ করুন")
        return POST_URL
    await query.edit_message_reply_markup(reply_markup=query.message.reply_markup)

async def post_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    post_data['url'] = update.message.text
    await confirm_post(update, context)
    return CONFIRM_SEND

async def skip_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    post_data['url'] = None
    await confirm_post(update, context)
    return CONFIRM_SEND

async def confirm_post(update, context):
    text = f"✅ Confirm Post\nTitle: {post_data['title']}\nForce Join: {post_data['force_join_channels']}\nTarget: {post_data['target_channels']}\nURL: {post_data['url']}"
    await update.message.reply_text(text+"\nType /postsend to send or /postcancel to cancel")

# ================= BROADCAST & POSTSEND =================
async def postsend(update, context):
    if not is_admin(update.effective_user.id): return
    for uid_row in CURSOR.execute("SELECT user_id FROM users"):
        uid = uid_row[0]
        try:
            text = post_data['title']
            if post_data['photo_file_id']:
                await context.bot.send_photo(uid, photo=post_data['photo_file_id'], caption=text)
            else:
                await context.bot.send_message(uid,text)
        except: continue
    await update.message.reply_text("✅ Post sent to all users!")

async def postcancel(update, context):
    post_data.clear()
    await update.message.reply_text("❌ Post cancelled")

# ================= ADD/REMOVE/LIST CHANNEL =================
async def addchannel(update, context):
    if not is_admin(update.effective_user.id): return
    try: username, link, *button_name = context.args; CURSOR.execute("INSERT OR REPLACE INTO channels VALUES (?,?,?)",(username," ".join(button_name),link)); DB.commit()
    except: await update.message.reply_text("❌ /addchannel @username link Button Name")

async def removechannel(update, context):
    if not is_admin(update.effective_user.id): return
    try: username = context.args[0]; CURSOR.execute("DELETE FROM channels WHERE username=?",(username,)); DB.commit()
    except: await update.message.reply_text("❌ /removechannel @username")

async def listchannels(update, context):
    if not is_admin(update.effective_user.id): return
    rows = CURSOR.execute("SELECT * FROM channels").fetchall()
    text = "\n".join([f"{r[0]} | {r[1]}" for r in rows]) or "No channels"
    await update.message.reply_text(text)

# ================= MAIN =================
if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check))
    app.add_handler(CommandHandler("newpost", newpost))
    app.add_handler(CommandHandler("postcancel", postcancel))
    app.add_handler(CommandHandler("postsend", postsend))
    app.add_handler(CommandHandler("addchannel", addchannel))
    app.add_handler(CommandHandler("removechannel", removechannel))
    app.add_handler(CommandHandler("listchannels", listchannels))

    # Callbacks
    app.add_handler(CallbackQueryHandler(force_join_callback, pattern="^fj\|"))
    app.add_handler(CallbackQueryHandler(force_join_callback, pattern="^force_next$"))
    app.add_handler(CallbackQueryHandler(target_callback, pattern="^tc\|"))
    app.add_handler(CallbackQueryHandler(target_callback, pattern="^target_next$"))
    app.add_handler(CallbackQueryHandler(button_callback, pattern="^check_status$"))

    print("🚀 Bot is running with ALL features!")
    app.run_polling()
