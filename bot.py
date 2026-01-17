import logging
import os
import threading
import sqlite3
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, ConversationHandler, MessageHandler, filters
)

# ================= HEALTH CHECK (RENDER FIX) =================
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_health_check_server():
    # Render-er dewa PORT use kora badhotamulok deploy success hoyar jonno
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_health_check_server, daemon=True).start()

# ================= CONFIG =================
TOKEN = "8510787985:AAHjszZmTMwqvqTfbFMJdqC548zBw4Qh0S0"
ADMIN_IDS = {6406804999}
WATCH_NOW_URL = "https://mmshotbd.blogspot.com/?m=1"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ================= DATABASE =================
DB = sqlite3.connect("bot.db", check_same_thread=False)
CURSOR = DB.cursor()
CURSOR.execute("""CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)""")
CURSOR.execute("""CREATE TABLE IF NOT EXISTS channels (username TEXT PRIMARY KEY, button TEXT, link TEXT)""")
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
def is_admin(user_id):
    return user_id in ADMIN_IDS

async def save_user(user_id):
    CURSOR.execute("INSERT OR IGNORE INTO users VALUES (?)", (user_id,))
    DB.commit()

async def check_all_joined(user_id, context, fj_list=CHANNELS_DATA):
    not_joined = []
    for channel in fj_list:
        try:
            member = await context.bot.get_chat_member(chat_id=channel["id"], user_id=user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                not_joined.append(channel)
        except:
            not_joined.append(channel)
    return not_joined

# ================= START / CHECK =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await save_user(user.id)
    not_joined_list = await check_all_joined(user.id, context)

    if not not_joined_list:
        watch_kb = [[InlineKeyboardButton("Watch Now 🎬", url=WATCH_NOW_URL)]]
        await update.message.reply_text(f"🎉 Welcome <b>{user.first_name}</b>!", reply_markup=InlineKeyboardMarkup(watch_kb), parse_mode=ParseMode.HTML)
    else:
        buttons = [[InlineKeyboardButton(f"Join {c['name']}", url=c['link'])] for c in not_joined_list]
        buttons.append([InlineKeyboardButton("Check Joined ✅", callback_data="check_status")])
        await update.message.reply_text("🚨 Prothome join korun!", reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.HTML)

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    not_joined_list = await check_all_joined(update.effective_user.id, context)
    if not not_joined_list:
        await update.message.reply_text("✅ All Joined!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Watch Now 🎬", url=WATCH_NOW_URL)]]))
    else:
        await update.message.reply_text("❌ Still missing some channels!")

# ================= CALLBACK HANDLER =================
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == "check_status":
        not_joined_list = await check_all_joined(query.from_user.id, context)
        if not not_joined_list:
            await query.edit_message_text("✅ Success!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Watch Now 🎬", url=WATCH_NOW_URL)]]))
        else:
            await query.answer("❌ Join baki ache!", show_alert=True)
            
    elif query.data.startswith("cp_"):
        fj_ids = query.data.replace("cp_", "").split(",")
        fj_to_check = [c for c in CHANNELS_DATA if str(c['id']) in fj_ids]
        not_joined = await check_all_joined(query.from_user.id, context, fj_to_check)
        if not not_joined:
            await query.answer("✅ Success!", show_alert=True)
            await query.message.reply_text(f"🎬 Video Link: {WATCH_NOW_URL}")
        else:
            btns = [[InlineKeyboardButton(f"Join {c['name']}", url=c['link'])] for c in not_joined]
            btns.append([InlineKeyboardButton("Check Again 🔄", callback_data=query.data)])
            await query.message.reply_text("❌ Prothome nicher channel gulote join korun!", reply_markup=InlineKeyboardMarkup(btns))

# ================= ADMIN CMDS =================
async def addchannel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    try:
        username, link = context.args[0], context.args[1]
        btn_name = " ".join(context.args[2:])
        CURSOR.execute("INSERT OR REPLACE INTO channels VALUES (?,?,?)", (username, btn_name, link))
        DB.commit()
        await update.message.reply_text(f"✅ Added {username}")
    except: await update.message.reply_text("Format error!")

async def removechannel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    try:
        CURSOR.execute("DELETE FROM channels WHERE username=?", (context.args[0],))
        DB.commit()
        await update.message.reply_text("✅ Removed")
    except: pass

async def listchannels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    CURSOR.execute("SELECT * FROM channels")
    rows = CURSOR.fetchall()
    text = "\n".join([f"{r[0]}" for r in rows])
    await update.message.reply_text(text or "Empty")

# ================= NEWPOST WIZARD =================
POST_TITLE, POST_PHOTO, POST_FJ, POST_TARGET, POST_URL, CONFIRM_SEND, BROADCAST_MODE = range(7)

async def newpost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return ConversationHandler.END
    context.user_data['post_data'] = {'fj': [], 'target': [], 'photo': None, 'url': None}
    await update.message.reply_text("✨ Step 1: Title likhun:")
    return POST_TITLE

async def post_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['post_data']['title'] = update.message.text
    await update.message.reply_text("📸 Step 2: Photo (ba /skip):")
    return POST_PHOTO

async def post_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['post_data']['photo'] = update.message.photo[-1].file_id
    return await show_fj_menu(update, context)

async def skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await show_fj_menu(update, context)

async def show_fj_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    selected = context.user_data['post_data']['fj']
    buttons = [[InlineKeyboardButton(f"{'✅' if str(c['id']) in selected else '❌'} {c['name']}", callback_data=f"sfj_{c['id']}")] for c in CHANNELS_DATA]
    buttons.append([InlineKeyboardButton("Done ➡️", callback_data="fj_done")])
    if update.callback_query: await update.callback_query.edit_message_text("🔒 Select FJ Channels:", reply_markup=InlineKeyboardMarkup(buttons))
    else: await update.message.reply_text("🔒 Select FJ Channels:", reply_markup=InlineKeyboardMarkup(buttons))
    return POST_FJ

async def fj_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == "fj_done": return await show_tg_menu(update, context)
    cid = str(query.data.replace("sfj_", ""))
    if cid in context.user_data['post_data']['fj']: context.user_data['post_data']['fj'].remove(cid)
    else: context.user_data['post_data']['fj'].append(cid)
    return await show_fj_menu(update, context)

async def show_tg_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    selected = context.user_data['post_data']['target']
    buttons = [[InlineKeyboardButton(f"{'✅' if str(c['id']) in selected else '❌'} {c['name']}", callback_data=f"stg_{c['id']}")] for c in CHANNELS_DATA]
    buttons.append([InlineKeyboardButton("Done ➡️", callback_data="tg_done")])
    await update.callback_query.edit_message_text("🎯 Select Targets:", reply_markup=InlineKeyboardMarkup(buttons))
    return POST_TARGET

async def tg_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == "tg_done":
        await query.message.reply_text("🔗 URL (ba /skip):")
        return POST_URL
    cid = str(query.data.replace("stg_", ""))
    if cid in context.user_data['post_data']['target']: context.user_data['post_data']['target'].remove(cid)
    else: context.user_data['post_data']['target'].append(cid)
    return await show_tg_menu(update, context)

async def post_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['post_data']['url'] = update.message.text
    return await show_sum(update, context)

async def skip_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await show_sum(update, context)

async def show_sum(update: Update, context: ContextTypes.DEFAULT_TYPE):
    d = context.user_data['post_data']
    summary = f"📊 Post Summary:\nTitle: {d['title']}\nFJ: {len(d['fj'])}\nTarget: {len(d['target'])}"
    await update.message.reply_text(summary, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Confirm Send", callback_data="csend")]]))
    return CONFIRM_SEND

async def confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    d = context.user_data['post_data']
    fj_ids = ",".join([str(x) for x in d['fj']])
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("Watch Now 🎬", callback_data=f"cp_{fj_ids}")]])
    for tid in d['target']:
        try:
            if d['photo']: await context.bot.send_photo(chat_id=tid, photo=d['photo'], caption=d['title'], reply_markup=kb)
            else: await context.bot.send_message(chat_id=tid, text=d['title'], reply_markup=kb)
        except: pass
    await query.edit_message_text("✅ Post Sent!")
    return ConversationHandler.END

# ================= BROADCAST =================
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    await update.message.reply_text("📢 Send broadcast:")
    return BROADCAST_MODE

async def broadcast_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    CURSOR.execute("SELECT user_id FROM users")
    for u in CURSOR.fetchall():
        try: await update.message.copy(chat_id=u[0])
        except: pass
    await update.message.reply_text("✅ Done")
    return ConversationHandler.END

async def postcancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("🚫 Cancelled")
    return ConversationHandler.END

# ================= MAIN =================
if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check))
    app.add_handler(CommandHandler("addchannel", addchannel))
    app.add_handler(CommandHandler("removechannel", removechannel))
    app.add_handler(CommandHandler("listchannels", listchannels))
    app.add_handler(CallbackQueryHandler(callback_handler))

    conv = ConversationHandler(
        entry_points=[CommandHandler("newpost", newpost), CommandHandler("broadcast", broadcast)],
        states={
            POST_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, post_title)],
            POST_PHOTO: [MessageHandler(filters.PHOTO, post_photo), CommandHandler("skip", skip_photo)],
            POST_FJ: [CallbackQueryHandler(fj_callback, pattern="^sfj_|^fj_done$")],
            POST_TARGET: [CallbackQueryHandler(tg_callback, pattern="^stg_|^tg_done$")],
            POST_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, post_url), CommandHandler("skip", skip_url)],
            CONFIRM_SEND: [CallbackQueryHandler(confirm_handler, pattern="^csend$")],
            BROADCAST_MODE: [MessageHandler(filters.ALL & ~filters.COMMAND, broadcast_send)],
        },
        fallbacks=[CommandHandler("postcancel", postcancel)],
    )
    app.add_handler(conv)
    app.run_polling()
