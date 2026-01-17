import logging, os, threading, sqlite3
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
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
    {"id": "@virallink259", "name": "ভাইরাল ভিডিও এক্সপ্রেস ২০২৬🔥❤️", "link": "https://t.me/virallink259"},
    {"id": -1002279183424, "name": "Primium App Zone", "link": "https://t.me/+5PNLgcRBC0IxYjll"},
    {"id": "@virallink246", "name": "Bd beauty viral", "link": "https://t.me/virallink246"},
    {"id": "@viralexpress1", "name": "Facebook🔥 Instagram Link🔥", "link": "https://t.me/viralexpress1"},
    {"id": "@movietime467", "name": "🎬MOVIE🔥 TIME💥", "link": "https://t.me/movietime467"},
    {"id": "@viralfacebook9", "name": "BD MMS VIDEO🔥🔥", "link": "https://t.me/viralfacebook9"},
    {"id": "@viralfb24", "name": "দেশি ভাবি ভাইরাল🔥🥵", "link": "https://t.me/viralfb24"},
    {"id": "@fbviral24", "name": "কচি মেয়েদের ভাইরাল ভিডিও🔥", "link": "https://t.me/fbviral24"},
    {"id": -1001550993047, "name": "ভাইরাল ভিডিও রিকুয়েস্ট🥵", "link": "https://t.me/+WAOUc1rX6Qk3Zjhl"},
    {"id": -1002011739504, "name": "Viral Video BD 🌍🔥", "link": "https://t.me/+la630-IFwHAwYWVl"},
    {"id": -1002444538806, "name": "Ai Prompt Studio 🎨📸", "link": "https://t.me/+AHsGXIDzWmJlZjVl"}
]

# ================= UTILS =================
def is_admin(user_id): return user_id in ADMIN_IDS
async def save_user(user_id): CURSOR.execute("INSERT OR IGNORE INTO users VALUES (?)",(user_id,)); DB.commit()
async def check_all_joined(user_id, context):
    not_joined = []
    for channel in CHANNELS_DATA:
        try:
            member = await context.bot.get_chat_member(chat_id=channel["id"], user_id=user_id)
            if member.status not in ['member','administrator','creator']:
                not_joined.append(channel)
        except:
            not_joined.append(channel)
    return not_joined

# ================= START / CHECK =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await save_user(user.id)
    stylish_name = f"👤 <b>{user.first_name}</b>"
    not_joined_list = await check_all_joined(user.id, context)
    if not not_joined_list:
        watch_kb = InlineKeyboardButton("Watch Now 🎬", url=WATCH_NOW_URL)
        await update.message.reply_text(f"🎉 স্বাগতম {stylish_name}\n✅ সব চ্যানেল join করা আছে ❤️\n▶️ ভিডিও দেখতে এখনই Watch Now", reply_markup=InlineKeyboardMarkup([[watch_kb]]), parse_mode=ParseMode.HTML)
    else:
        buttons = [[InlineKeyboardButton(f"Join {c['name']}", url=c['link'])] for c in not_joined_list]
        buttons.append([InlineKeyboardButton("Check Joined ✅", callback_data="check_status")])
        await update.message.reply_text("🚨 ভিডিও দেখার আগে সব Channel join করতে হবে❌\nJoin শেষ হলে Check Joined ক্লিক করুন✅", reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.HTML)

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    not_joined_list = await check_all_joined(update.effective_user.id, context)
    if not not_joined_list:
        watch_kb = InlineKeyboardButton("Watch Now 🎬", url=WATCH_NOW_URL)
        await update.message.reply_text("✅ সব চ্যানেল join করা আছে!", reply_markup=InlineKeyboardMarkup([[watch_kb]]))
    else: await update.message.reply_text("❌ এখনো সব চ্যানেলে join করা হয়নি!")

# ================= GLOBALS FOR NEWPOST =================
POST_WIZARD, POST_TITLE, POST_PHOTO, FORCE_SELECT, TARGET_SELECT, POST_URL, CONFIRM_SEND = range(7)
force_selection = {}
target_selection = {}
post_data = {}
broadcast_mode = False

# ================= NEWPOST WIZARD =================
async def newpost_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("❌ আপনি admin নন!")
        return ConversationHandler.END
    await update.message.reply_text("📝 Post Title লিখুন:")
    return POST_TITLE

async def newpost_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    post_data['title'] = update.message.text
    await update.message.reply_text("📸 Post Photo পাঠান (Photo ছাড়া skip করতে পারেন /skip):")
    return POST_PHOTO

async def newpost_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        post_data['photo_file_id'] = file_id
    else:
        post_data['photo_file_id'] = None
    # Force Join selection
    keyboard = [[InlineKeyboardButton(c['name'], callback_data=f"force_{c['id']}")] for c in CHANNELS_DATA]
    keyboard.append([InlineKeyboardButton("Next ➡️", callback_data="force_next")])
    await update.message.reply_text("📌 Force Join Channels select করুন:", reply_markup=InlineKeyboardMarkup(keyboard))
    force_selection.clear()
    return FORCE_SELECT

# ================= BUTTON CALLBACK FOR NEWPOST =================
async def newpost_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id

    # Force Join selection
    if data.startswith("force_"):
        cid = data[6:]
        if cid in force_selection: del force_selection[cid]
        else: force_selection[cid] = True
        await query.answer("Selected updated ✅")
        return
    elif data == "force_next":
        post_data['force_join_channels'] = ",".join(force_selection.keys())
        # Target Channels
        keyboard = [[InlineKeyboardButton(c['name'], callback_data=f"target_{c['id']}")] for c in CHANNELS_DATA]
        keyboard.append([InlineKeyboardButton("Next ➡️", callback_data="target_next")])
        target_selection.clear()
        await query.edit_message_text("🎯 Target Channels select করুন:", reply_markup=InlineKeyboardMarkup(keyboard))
        return TARGET_SELECT
    elif data.startswith("target_"):
        cid = data[7:]
        if cid in target_selection: del target_selection[cid]
        else: target_selection[cid] = True
        await query.answer("Selected updated ✅")
        return
    elif data == "target_next":
        post_data['target_channels'] = ",".join(target_selection.keys())
        await query.edit_message_text("🔗 URL দিন অথবা skip করতে /skip")
        return POST_URL
    elif data == "confirm_send":
        # Save to DB and send to target channels
        CURSOR.execute("INSERT INTO posts (title,photo_file_id,force_join_channels,target_channels,url) VALUES (?,?,?,?,?)",
                       (post_data.get('title'), post_data.get('photo_file_id'), post_data.get('force_join_channels'), post_data.get('target_channels'), post_data.get('url')))
        DB.commit()
        # Send to target channels
        for cid in post_data.get('target_channels','').split(','):
            try:
                if post_data.get('photo_file_id'):
                    await context.bot.send_photo(chat_id=cid, photo=post_data['photo_file_id'], caption=post_data['title'])
                else:
                    await context.bot.send_message(chat_id=cid, text=post_data['title'])
            except: pass
        await query.edit_message_text("✅ Post sent successfully!")
        post_data.clear()
        return ConversationHandler.END

# ================= URL HANDLER =================
async def post_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    post_data['url'] = update.message.text if update.message.text!='/skip' else None
    keyboard = [[InlineKeyboardButton("Confirm & Send ✅", callback_data="confirm_send")]]
    await update.message.reply_text(f"🔎 Confirm Post:\nTitle: {post_data.get('title')}\nURL: {post_data.get('url')}", reply_markup=InlineKeyboardMarkup(keyboard))
    return CONFIRM_SEND

# ================= POST CANCEL =================
async def post_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    post_data.clear()
    force_selection.clear()
    target_selection.clear()
    await update.message.reply_text("❌ Post/Broadcast cancelled!")
    return ConversationHandler.END

# ================= BROADCAST =================
async def broadcast_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("❌ আপনি admin নন!")
        return
    global broadcast_mode
    broadcast_mode = True
    await update.message.reply_text("📢 Broadcast mode on. এখন পাঠানো message/photo সব ইউজারের কাছে যাবে।\n❌ বাতিল করতে /postcancel")
    return

async def broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global broadcast_mode
    if not broadcast_mode: return
    CURSOR.execute("SELECT user_id FROM users")
    users = [r[0] for r in CURSOR.fetchall()]
    for uid in users:
        try:
            if update.message.photo:
                file_id = update.message.photo[-1].file_id
                await context.bot.send_photo(chat_id=uid, photo=file_id, caption=update.message.caption)
            else:
                await context.bot.send_message(chat_id=uid, text=update.message.text)
        except: pass
    await update.message.reply_text("✅ Broadcast sent to all users!")
    broadcast_mode = False

# ================= ADD/REMOVE/LIST CHANNELS =================
async def add_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ আপনি admin নন!")
        return
    args = context.args
    if len(args)<3:
        await update.message.reply_text("Usage: /addchannel @username link 'Button Name'")
        return
    username, link, button = args[0], args[1], " ".join(args[2:])
    CURSOR.execute("INSERT OR REPLACE INTO channels VALUES (?,?,?)",(username,button,link))
    DB.commit()
    await update.message.reply_text(f"✅ Channel {username} added!")

async def remove_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ আপনি admin নন!")
        return
    if len(context.args)<1:
        await update.message.reply_text("Usage: /removechannel @username")
        return
    username = context.args[0]
    CURSOR.execute("DELETE FROM channels WHERE username=?",(username,))
    DB.commit()
    await update.message.reply_text(f"✅ Channel {username} removed!")

async def list_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ আপনি admin নন!")
        return
    CURSOR.execute("SELECT username,button,link FROM channels")
    rows = CURSOR.fetchall()
    text = "📃 Channel List:\n"
    for r in rows: text += f"{r[0]} | {r[1]} | {r[2]}\n"
    await update.message.reply_text(text)

# ================= MAIN =================
if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()

    # START / CHECK
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check))

    # NEWPOST conversation
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("newpost", newpost_start)],
        states={
            POST_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, newpost_title)],
            POST_PHOTO: [MessageHandler(filters.PHOTO | filters.Regex("^/skip$"), newpost_photo)],
            FORCE_SELECT: [CallbackQueryHandler(newpost_button, pattern="^force_.*|^force_next$")],
            TARGET_SELECT: [CallbackQueryHandler(newpost_button, pattern="^target_.*|^target_next$")],
            POST_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, post_url)],
            CONFIRM_SEND: [CallbackQueryHandler(newpost_button, pattern="^confirm_send$")]
        },
        fallbacks=[CommandHandler("postcancel", post_cancel)]
    )
    app.add_handler(conv_handler)

    # BROADCAST
    app.add_handler(CommandHandler("broadcast", broadcast_start))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, broadcast_handler))

    # CHANNEL MANAGEMENT
    app.add_handler(CommandHandler("addchannel", add_channel))
    app.add_handler(CommandHandler("removechannel", remove_channel))
    app.add_handler(CommandHandler("listchannels", list_channels))

    # Check Joined button
    app.add_handler(CallbackQueryHandler(button_callback, pattern="^check_status$"))

    print("🚀 Full bot running with /start, /check, /newpost wizard, broadcast, channel management!")
    app.run_polling()
