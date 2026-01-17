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
TOKEN = "8510787985:AAHjszZmTMwqvqTfbFMJdqC548zBw4Qh0S0"
ADMIN_IDS = [6406804999]
WATCH_NOW_URL = "https://mmshotbd.blogspot.com/?m=1"

logging.basicConfig(level=logging.INFO)

# ================== DATABASE ==================
db = sqlite3.connect("forcejoin.db", check_same_thread=False)
cur = db.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS channels(id TEXT PRIMARY KEY, name TEXT, link TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY, unlocked INTEGER DEFAULT 0)")
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

async def check_specific_channels(user_id, bot, channel_ids):
    not_joined = []
    for cid in channel_ids:
        cur.execute("SELECT name, link FROM channels WHERE id=?", (cid,))
        res = cur.fetchone()
        if res:
            name, link = res
            try:
                member = await bot.get_chat_member(cid, user_id)
                if member.status not in ["member", "administrator", "creator"]:
                    not_joined.append((cid, name, link))
            except:
                not_joined.append((cid, name, link))
    return not_joined

# ================== STATES ==================
BROADCAST_MODE = {}
POST_TITLE, POST_PHOTO, POST_FORCE_CHANS, POST_WEBSITE, POST_TARGET_CHANS = range(5)
POST_CREATION = {}

# ================== START ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if update.message is None: return
    uid = user.id
    stylish_name = f"<b>{user.first_name or 'User'}</b>"

    cur.execute("INSERT OR IGNORE INTO users(user_id) VALUES(?)",(uid,))
    db.commit()
    not_joined = await check_all_joined(uid, context.bot)

    if not not_joined:
        await update.message.reply_text(f"🎉 স্বাগতম 👤 {stylish_name}\n✅ আপনি সব চ্যানেলে জয়েন আছেন ❤️",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Watch Now 🎬", url=WATCH_NOW_URL)]]),
            parse_mode=ParseMode.HTML)
    else:
        buttons = [[InlineKeyboardButton(f"Join {name}", url=link)] for _,name,link in not_joined]
        buttons.append([InlineKeyboardButton("Check Joined ✅", callback_data="check")])
        await update.message.reply_text(f"Hello 👤 {stylish_name},\n🚨 ভিডিও দেখার আগে নিচের সব চ্যানেলে জয়েন করুন।",
            reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.HTML)

# ================== NEW POST SYSTEM ==================
async def newpost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    POST_CREATION[update.effective_user.id] = {'force_chans': set(), 'target_chans': set()}
    await update.message.reply_text("📝 Please send the <b>Post Title</b>:", parse_mode=ParseMode.HTML)
    return POST_TITLE

async def p_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    POST_CREATION[update.effective_user.id]['title'] = update.message.text
    await update.message.reply_text("📸 Now send the <b>Post Photo</b>:")
    return POST_PHOTO

async def p_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo: return POST_PHOTO
    POST_CREATION[update.effective_user.id]['photo'] = update.message.photo[-1].file_id
    btns = [[InlineKeyboardButton(f"➕ {n}", callback_data=f"fsel|{i}")] for i, n, l in cur.execute("SELECT * FROM channels")]
    btns.append([InlineKeyboardButton("✅ Done Force Join Selection", callback_data="fsel_done")])
    await update.message.reply_text("🛡 <b>Force Join:</b> সিলেক্ট করুন কোনগুলো চেক করবে:", reply_markup=InlineKeyboardMarkup(btns), parse_mode=ParseMode.HTML)
    return POST_FORCE_CHANS

async def p_force_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == "fsel_done":
        await query.edit_message_text("🔗 এখন <b>Website URL</b> দিন (না থাকলে skip লিখুন):")
        return POST_WEBSITE
    cid = query.data.split("|")[1]
    POST_CREATION[query.from_user.id]['force_chans'].add(cid)
    await query.answer("Added!")
    return POST_FORCE_CHANS

async def p_website(update: Update, context: ContextTypes.DEFAULT_TYPE):
    POST_CREATION[update.effective_user.id]['url'] = update.message.text
    btns = [[InlineKeyboardButton(f"📤 {n}", callback_data=f"tsel|{i}")] for i, n, l in cur.execute("SELECT * FROM channels")]
    btns.append([InlineKeyboardButton("🚀 Send Post Now", callback_data="tsel_done")])
    await update.message.reply_text("📢 <b>Target:</b> কোন কোন চ্যানেলে পোস্টটি যাবে?", reply_markup=InlineKeyboardMarkup(btns), parse_mode=ParseMode.HTML)
    return POST_TARGET_CHANS

async def p_target_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    data = POST_CREATION[uid]
    if query.data == "tsel_done":
        force_list = ",".join(data['force_chans']) if data['force_chans'] else "none"
        watch_btn = InlineKeyboardMarkup([[InlineKeyboardButton("🎬 Watch Video", callback_data=f"v|{force_list}|{data['url']}")]])
        sent = 0
        for target_cid in data['target_chans']:
            try:
                await context.bot.send_photo(target_cid, data['photo'], caption=data['title'], reply_markup=watch_btn, parse_mode=ParseMode.HTML)
                sent += 1
            except: pass
        await query.edit_message_text(f"✅ পোস্টটি {sent}টি চ্যানেলে পাঠানো হয়েছে।")
        POST_CREATION.pop(uid, None)
        return ConversationHandler.END
    cid = query.data.split("|")[1]
    POST_CREATION[uid]['target_chans'].add(cid)
    await query.answer("Added to target!")
    return POST_TARGET_CHANS

# ================== ADMIN COMMANDS (FIXED) ==================
async def addchannel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    if len(context.args) < 3:
        await update.message.reply_text("Usage: /addchannel @id https://link Name")
        return
    cur.execute("INSERT OR REPLACE INTO channels VALUES(?,?,?)", (context.args[0], " ".join(context.args[2:]), context.args[1]))
    db.commit()
    await update.message.reply_text("✅ Channel Added Successfully")

async def watch_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    parts = query.data.split("|")
    f_chans = parts[1].split(",") if parts[1] != "none" else []
    not_joined = await check_specific_channels(query.from_user.id, context.bot, f_chans)
    if not not_joined:
        url = WATCH_NOW_URL if parts[2].lower() == 'skip' else parts[2]
        await query.message.reply_text(f"🚀 ভিডিও লিঙ্ক: {url}")
    else:
        btns = [[InlineKeyboardButton(f"Join {n}", url=l)] for _,n,l in not_joined]
        btns.append([InlineKeyboardButton("Verify Again ✅", callback_data=query.data)])
        await query.message.reply_text("❌ আগে জয়েন করুন:", reply_markup=InlineKeyboardMarkup(btns))
    await query.answer()

async def post_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    POST_CREATION.pop(update.effective_user.id, None)
    BROADCAST_MODE.pop(update.effective_user.id, None)
    await update.message.reply_text("❌ বাতিল করা হয়েছে।")
    return ConversationHandler.END

async def broadcast_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    BROADCAST_MODE[update.effective_user.id] = True
    await update.message.reply_text("📢 ব্রডকাস্ট মেসেজ পাঠান:")

async def handle_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not BROADCAST_MODE.get(uid): return
    BROADCAST_MODE.pop(uid)
    users = cur.execute("SELECT user_id FROM users").fetchall()
    for (u_id,) in users:
        try: await update.message.copy(u_id)
        except: pass
    await update.message.reply_text("✅ Broadcast Done")

# ================== RUN BOT ==================
app = Application.builder().token(TOKEN).build()

post_handler = ConversationHandler(
    entry_points=[CommandHandler("newpost", newpost)],
    states={
        POST_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, p_title)],
        POST_PHOTO: [MessageHandler(filters.PHOTO, p_photo)],
        POST_FORCE_CHANS: [CallbackQueryHandler(p_force_cb, pattern="^fsel")],
        POST_WEBSITE: [MessageHandler(filters.TEXT & ~filters.COMMAND, p_website)],
        POST_TARGET_CHANS: [CallbackQueryHandler(p_target_cb, pattern="^tsel")],
    },
    fallbacks=[CommandHandler("postcancel", post_cancel)]
)

app.add_handler(post_handler)
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("addchannel", addchannel)) # ব্রডকাস্টের আগে রাখা হয়েছে
app.add_handler(CommandHandler("broadcast", broadcast_cmd))
app.add_handler(CommandHandler("postcancel", post_cancel))
app.add_handler(CallbackQueryHandler(watch_callback, pattern="^v\|"))
app.add_handler(CallbackQueryHandler(start, pattern="check"))
app.add_handler(MessageHandler(filters.ALL & (~filters.COMMAND), handle_broadcast))

print("🔥 BOT IS ONLINE...")
app.run_polling()
