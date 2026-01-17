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

# ================= HEALTH CHECK =================
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_health_check_server():
    port = int(os.environ.get("PORT", 8000))
    HTTPServer(("0.0.0.0", port), HealthCheckHandler).serve_forever()

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
DB.commit()

# ================= 11 ORIGINAL CHANNELS =================
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

async def get_all_channels():
    # Code-er 11 ti + DB-er channel eksathe kora
    CURSOR.execute("SELECT username, button, link FROM channels")
    rows = CURSOR.fetchall()
    db_channels = [{"id": r[0], "name": r[1], "link": r[2]} for r in rows]
    return CHANNELS_DATA + db_channels

async def check_all_joined(user_id, context, fj_list):
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
    all_ch = await get_all_channels()
    not_joined_list = await check_all_joined(user.id, context, all_ch)

    if not not_joined_list:
        success_text = (
            f"🎉 স্বাগতম 👤 <b>{user.first_name}</b>\n"
            f"✅ আপনি সফলভাবে সব চ্যানেলে Join করেছেন ❤️\n"
            f"▶️ ভিডিও দেখতে এখনই <b>[Watch Now]</b> বাটনে ক্লিক করুন 🎬✨"
        )
        watch_kb = [[InlineKeyboardButton("Watch Now 🎬", url=WATCH_NOW_URL)]]
        await update.message.reply_text(success_text, reply_markup=InlineKeyboardMarkup(watch_kb), parse_mode=ParseMode.HTML)
    else:
        buttons = [[InlineKeyboardButton(f"Join {c['name']}", url=c['link'])] for c in not_joined_list]
        buttons.append([InlineKeyboardButton("Check Joined ✅", callback_data="check_status")])
        caption = (
            f"Hello 👤 <b>{user.first_name}</b>,\n\n"
            "🚨 <b>Attention Please!</b>\n\n"
            "Viral ভিডিও দেখার আগে আমাদের নিচের Channel গুলোতে Join করা বাধ্যতামূলক।\n"
            "সবগুলো চ্যানেল Join না করলে ভিডিও লিঙ্ক কাজ করবে না ❌\n\n"
            "Join শেষ হলে <b>Check Joined</b> ক্লিক করুন ✅"
        )
        await update.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.HTML)

# ================= ADD CHANNEL WIZARD =================
ADD_CH_ID, ADD_CH_LINK, ADD_CH_NAME = range(10, 13)

async def addchannel_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return ConversationHandler.END
    await update.message.reply_text("✨ **ধাপ ১:** চ্যানেলের ইউজারনেম বা আইডি দিন (যেমন: @channel বা -100xxx):")
    return ADD_CH_ID

async def addchannel_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['new_ch_id'] = update.message.text
    await update.message.reply_text("🔗 **ধাপ ২:** চ্যানেলের ইনভাইট লিঙ্ক (Link) দিন:")
    return ADD_CH_LINK

async def addchannel_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['new_ch_link'] = update.message.text
    await update.message.reply_text("🔘 **ধাপ ৩:** বাটনের জন্য একটি নাম দিন (যেমন: Join Now):")
    return ADD_CH_NAME

async def addchannel_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    btn_name = update.message.text
    ch_id = context.user_data['new_ch_id']
    ch_link = context.user_data['new_ch_link']
    CURSOR.execute("INSERT OR REPLACE INTO channels VALUES (?,?,?)", (ch_id, btn_name, ch_link))
    DB.commit()
    await update.message.reply_text(f"✅ **চ্যানেল সফলভাবে যুক্ত হয়েছে!**\n🆔 ID: `{ch_id}`\n📛 নাম: {btn_name}")
    return ConversationHandler.END

# ================= CHANNEL MGMT =================
async def listchannels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    all_ch = await get_all_channels()
    text = "📋 **চ্যানেল লিস্ট:**\n\n" + "\n".join([f"🔹 `{c['id']}` | {c['name']}" for c in all_ch])
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

async def removechannel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    try:
        CURSOR.execute("DELETE FROM channels WHERE username=?", (context.args[0],))
        DB.commit()
        await update.message.reply_text("✅ রিমুভ হয়েছে। (বি:দ্র: কোডের ভেতরের ১১টি চ্যানেল রিমুভ হবে না)")
    except: pass

# ================= CALLBACK HANDLER =================
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    all_ch = await get_all_channels()
    
    if query.data == "check_status":
        not_joined_list = await check_all_joined(user.id, context, all_ch)
        if not not_joined_list:
            watch_kb = [[InlineKeyboardButton("Watch Now 🎬", url=WATCH_NOW_URL)]]
            await query.edit_message_text(f"🎉 ধন্যবাদ <b>{user.first_name}</b>! সব চ্যানেল join করা আছে।", reply_markup=InlineKeyboardMarkup(watch_kb), parse_mode=ParseMode.HTML)
        else:
            await query.answer("❌ এখনো সব চ্যানেলে join করা হয়নি!", show_alert=True)
            
    elif query.data.startswith("cp_"):
        fj_ids = query.data.replace("cp_", "").split(",")
        fj_to_check = [c for c in all_ch if str(c['id']) in fj_ids]
        not_joined = await check_all_joined(user.id, context, fj_to_check)
        if not not_joined:
            await query.answer("✅ ভেরিফিকেশন সফল!", show_alert=True)
            await query.message.reply_text(f"🎬 Video Link: {WATCH_NOW_URL}")
        else:
            btns = [[InlineKeyboardButton(f"Join {c['name']}", url=c['link'])] for c in not_joined]
            btns.append([InlineKeyboardButton("Check Again 🔄", callback_data=query.data)])
            await query.message.reply_text("❌ আগে এই চ্যানেলগুলোতে জয়েন করুন!", reply_markup=InlineKeyboardMarkup(btns))

# ================= NEWPOST / BROADCAST =================
POST_TITLE, POST_PHOTO, POST_FJ, POST_TARGET, POST_URL, CONFIRM_SEND, BROADCAST_MODE = range(7)

async def newpost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return ConversationHandler.END
    context.user_data['post_data'] = {'fj': [], 'target': [], 'photo': None, 'url': None}
    await update.message.reply_text("✨ ধাপ ১: টাইটেল লিখুন:")
    return POST_TITLE

async def post_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['post_data']['title'] = update.message.text
    await update.message.reply_text("📸 ধাপ ২: ফটো দিন বা /skip দিন:")
    return POST_PHOTO

async def post_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['post_data']['photo'] = update.message.photo[-1].file_id
    return await show_fj_menu(update, context)

async def skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await show_fj_menu(update, context)

async def show_fj_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    selected = context.user_data['post_data']['fj']
    all_ch = await get_all_channels()
    buttons = [[InlineKeyboardButton(f"{'✅' if str(c['id']) in selected else '❌'} {c['name']}", callback_data=f"sfj_{c['id']}")] for c in all_ch]
    buttons.append([InlineKeyboardButton("Done ➡️", callback_data="fj_done")])
    if update.callback_query: await update.callback_query.edit_message_text("🔒 Force Join সিলেক্ট করুন:", reply_markup=InlineKeyboardMarkup(buttons))
    else: await update.message.reply_text("🔒 Force Join সিলেক্ট করুন:", reply_markup=InlineKeyboardMarkup(buttons))
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
    all_ch = await get_all_channels()
    buttons = [[InlineKeyboardButton(f"{'✅' if str(c['id']) in selected else '❌'} {c['name']}", callback_data=f"stg_{c['id']}")] for c in all_ch]
    buttons.append([InlineKeyboardButton("Done ➡️", callback_data="tg_done")])
    await update.callback_query.edit_message_text("🎯 Target চ্যানেল সিলেক্ট করুন:", reply_markup=InlineKeyboardMarkup(buttons))
    return POST_TARGET

async def tg_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == "tg_done":
        await query.message.reply_text("🔗 লিঙ্ক দিন বা /skip দিন:")
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
    await update.message.reply_text(f"📊 সামারি:\nটাইটেল: {d['title']}\nFJ: {len(d['fj'])}\nTargets: {len(d['target'])}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ পাঠান", callback_data="csend")]]))
    return CONFIRM_SEND

async def confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    d = context.user_data['post_data']
    fj_ids = ",".join([str(x) for x in d['fj']])
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("Watch Now 🎬", callback_data=f"cp_{fj_ids}")]])
    for tid in d['target']:
        try:
            if d['photo']: await context.bot.send_photo(chat_id=tid, photo=d['photo'], caption=d['title'], reply_markup=kb, parse_mode=ParseMode.HTML)
            else: await context.bot.send_message(chat_id=tid, text=d['title'], reply_markup=kb, parse_mode=ParseMode.HTML)
        except: pass
    await query.edit_message_text("✅ পোস্ট সফলভাবে পাঠানো হয়েছে।")
    return ConversationHandler.END

# ================= BROADCAST =================
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    await update.message.reply_text("📢 ব্রডকাস্ট মেসেজ পাঠান:")
    return BROADCAST_MODE

async def broadcast_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    CURSOR.execute("SELECT user_id FROM users")
    for u in CURSOR.fetchall():
        try: await update.message.copy(chat_id=u[0])
        except: pass
    await update.message.reply_text("✅ ব্রডকাস্ট সফল।")
    return ConversationHandler.END

async def postcancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("🚫 ক্যানসেল হয়েছে।")
    return ConversationHandler.END

# ================= MAIN =================
if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    
    # Combined Wizard Handler
    all_conv = ConversationHandler(
        entry_points=[
            CommandHandler("newpost", newpost), 
            CommandHandler("broadcast", broadcast),
            CommandHandler("addchannel", addchannel_start)
        ],
        states={
            POST_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, post_title)],
            POST_PHOTO: [MessageHandler(filters.PHOTO, post_photo), CommandHandler("skip", skip_photo)],
            POST_FJ: [CallbackQueryHandler(fj_callback, pattern="^sfj_|^fj_done$")],
            POST_TARGET: [CallbackQueryHandler(tg_callback, pattern="^stg_|^tg_done$")],
            POST_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, post_url), CommandHandler("skip", skip_url)],
            CONFIRM_SEND: [CallbackQueryHandler(confirm_handler, pattern="^csend$")],
            BROADCAST_MODE: [MessageHandler(filters.ALL & ~filters.COMMAND, broadcast_send)],
            ADD_CH_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, addchannel_id)],
            ADD_CH_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, addchannel_link)],
            ADD_CH_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, addchannel_save)],
        },
        fallbacks=[CommandHandler("postcancel", postcancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("listchannels", listchannels))
    app.add_handler(CommandHandler("removechannel", removechannel))
    app.add_handler(all_conv)
    app.add_handler(CallbackQueryHandler(callback_handler))

    app.run_polling()
