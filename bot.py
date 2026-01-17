import logging
import os
import threading
import sqlite3
import time
import asyncio
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, ConversationHandler, MessageHandler, filters
)

# ================= 🌐 হেলথ চেক ও সার্ভার স্ট্যাটাস =================
START_TIME = time.time()

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"<h1>Master Bot is Live with Auto-Delete Feature! 🚀🔥👑</h1>")

def run_health_check_server():
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_health_check_server, daemon=True).start()

# ================= ⚙️ কনফিগারেশন =================
TOKEN = "8510787985:AAHjszZmTMwqvqTfbFMJdqC548zBw4Qh0S0"
ADMIN_IDS = {6406804999}

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ================= 🗄️ ডাটাবেস সিস্টেম =================
DB = sqlite3.connect("final_master.db", check_same_thread=False)
CURSOR = DB.cursor()
CURSOR.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, join_date TEXT)")
CURSOR.execute("CREATE TABLE IF NOT EXISTS channels (username TEXT PRIMARY KEY, button TEXT, link TEXT)")
CURSOR.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")

# Default Settings
CURSOR.execute("INSERT OR IGNORE INTO settings VALUES (?, ?)", ("watch_url", "https://mmshotbd.blogspot.com/?m=1"))
CURSOR.execute("INSERT OR IGNORE INTO settings VALUES (?, ?)", ("welcome_photo", "https://i.ibb.co/LzVz4z0/welcome.jpg"))
DB.commit()

# ================= 🔗 ১১টি অরিজিনাল মাস্টার চ্যানেল =================
CHANNELS_DATA = [
    {"id": "@virallink259", "name": "ভাইরাল ভিদিও লিংক এক্সপ্রেস ২০২৬ 🔥❤️🔞🍿🎬🎥💎👑🚀🔥🔞🍿🎬🎥💎👑", "link": "https://t.me/virallink259"},
    {"id": -1002279183424, "name": "Primium App Zone 💎✨👑🚀🔥🔞🍿🎬🎥💎👑🚀🔥🔞🍿🎬🎥💎👑", "link": "https://t.me/+5PNLgcRBC0IxYjll"},
    {"id": "@virallink246", "name": "Bd beauty viral 🍑🥵🔞🍿🎬🎥💎👑🚀🔥🔞🍿🎬🎥💎👑🚀🔥🔞🍿", "link": "https://t.me/virallink246"},
    {"id": "@viralexpress1", "name": "Facebook🔥 Instagram Link🔥 🔥🔞🥵🍿🎬🎥💎👑🚀🔥🔞🍿🎬🎥💎👑", "link": "https://t.me/viralexpress1"},
    {"id": "@movietime467", "name": "🎬MOVIE🔥 TIME💥 🎬🎥💎👑🚀🔥🔞🍿🎬🎥💎👑🚀🔥🔞🍿🎬🎥💎", "link": "https://t.me/movietime467"},
    {"id": "@viralfacebook9", "name": "BD MMS VIDEO🔥🔥 🍑🥵🔞🍿🎬🎥💎👑🚀🔥🔞🍿🎬🎥💎👑🚀🔥🔞", "link": "https://t.me/viralfacebook9"},
    {"id": "@viralfb24", "name": "দেশি ভাবি ভাইরাল🔥🥵 🔥🔞🥵🍿🎬🎥💎👑🚀🔥🔞🍿🎬🎥💎👑🚀🔥🔞", "link": "https://t.me/viralfb24"},
    {"id": "@fbviral24", "name": "কচি মেয়েদের ভাইরাল ভিদিও🔥 🔥🔞🥵🍿🎬🎥💎👑🚀🔥🔞🍿🎬🎥💎👑🚀🔥", "link": "https://t.me/fbviral24"},
    {"id": -1001550993047, "name": "ভাইরাল ভিদিও রিকুয়েষ্ট🥵 🔥🔞🥵🍿🎬🎥💎👑🚀🔥🔞🍿🎬🎥💎👑🚀🔥🔞", "link": "https://t.me/+WAOUc1rX6Qk3Zjhl"},
    {"id": -1002011739504, "name": "Viral Video BD 🌍🔥 🌍🔥🍿🔞🎬🎥💎👑🚀🔥🔞🍿🎬🎥💎👑🚀🔥🔞", "link": "https://t.me/+la630-IFwHAwYWVl"},
    {"id": -1002444538806, "name": "Ai Prompt Studio 🎨📸 ✨🎨📸💎👑🚀🔥🔞🍿🎬🎥💎👑🚀🔥🔞🍿🎬🎥", "link": "https://t.me/+AHsGXIDzWmJlZjVl"}
]

# ================= 🛠️ হেল্পার ফাংশন =================
def is_admin(user_id):
    return user_id in ADMIN_IDS

def get_setting(key):
    CURSOR.execute("SELECT value FROM settings WHERE key=?", (key,))
    return CURSOR.fetchone()[0]

async def get_all_channels():
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

# ================= 👤 ইউজার ফাংশন (Welcome & Check) =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    CURSOR.execute("INSERT OR IGNORE INTO users VALUES (?, ?)", (user.id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    DB.commit()
    
    all_ch = await get_all_channels()
    not_joined = await check_all_joined(user.id, context, all_ch)
    
    url = get_setting("watch_url")
    photo = get_setting("welcome_photo")

    if not not_joined:
        text = (f"🌈✨🍭🎈🎊 <b>স্বাগতম প্রিয়, {user.first_name}!</b> 💖✨👑🌟🔥🔞🍿🎬🎥💎👑🚀🔥🔞🍿🎬🎥💎👑🚀🔥🔞🍿🎬🎥💎👑\n\n"
                f"🌟 <b>CONGRATULATION!</b> 🎉 ভেরিফিকেশন সফল হয়েছে। ✅💎✨👑🚀🔥🔞🍿🎬🎥💎👑🚀🔥🔞🍿🎬🎥💎👑\n\n"
                f"এখন আপনি সব <b>প্রিমিয়াম কন্টেন্ট</b> ফ্রিতে উপভোগ করতে পারবেন। 🔞🔥🎬🎥💎👑🚀🔥🔞🍿🎬🎥💎👑🚀🔥🔞🍿🎬🎥💎👑\n\n"
                f"🚀 <b>ভিডিও দেখতে নিচের বাটনে ক্লিক করুন:</b> 👇🎥🍿🔥🔞🎬💎👑🚀🔥🔞🍿🎬🎥💎👑")
        kb = [[InlineKeyboardButton("🎬 এখনই দেখুন (Watch Now) ✨🍿🔥🔞🎬💎👑", url=url)]]
        try: await update.message.reply_photo(photo=photo, caption=text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)
        except: await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)
    else:
        btns = [[InlineKeyboardButton(f"➕ জয়েন: {c['name']} 🚀", url=c['link'])] for c in not_joined]
        btns.append([InlineKeyboardButton("✅ ভেরিফাই করুন 🔄✨💎👑🚀🔥", callback_data="check_status")])
        text = (f"👋 <b>হ্যালো {user.first_name}!</b> ❤️🔥🔞🥵🍑😈👧💖💥🌍🎨📸✨🔥🔞🎬🍿🎥💎👑🚀🔥🔞🍿🎬🎥💎👑\n\n"
                f"🚨 <b>অ্যাক্সেস পেতে</b> অবশ্যই নিচের সব চ্যানেলে জয়েন করতে হবে। 💎✨🎬🍿🎥💎👑🚀🔥🔞🍿🎬🎥💎👑🚀🔥🔞🍿🎬🎥💎👑\n\n"
                f"⚠️ <b>সবগুলো জয়েন না করলে ভিডিও লিঙ্ক আসবে না!</b> ❌🔥🔞🍿🎬🎥💎👑🚀🔥🔞🍿🎬🎥💎👑\n\n"
                f"নিচের বাটনে জয়েন করে ভেরিফাই করুন। 👇💫👑🚀🔥🔞🍿🎬🎥💎👑🚀🔥🔞🍿🎬🎥💎👑")
        try: await update.message.reply_photo(photo=photo, caption=text, reply_markup=InlineKeyboardMarkup(btns), parse_mode=ParseMode.HTML)
        except: await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(btns), parse_mode=ParseMode.HTML)

# ================= 🛡️ অটো-ডিলিট সিস্টেম (The Magic Function) =================
async def auto_delete_msg(context, chat_id, message_id, delay=45):
    await asyncio.sleep(delay)
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except:
        pass

# ================= ✍️ প্রিমিয়াম পোস্ট ও এডমিন প্যানেল =================
P_TITLE, P_PHOTO, P_FJ, P_TARGET, P_CONFIRM = range(5)
SET_VAL = 50

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    btns = [
        [InlineKeyboardButton("📊 বটের পরিসংখ্যান", callback_data="adm_stats"), InlineKeyboardButton("📝 নতুন পোস্ট", callback_data="adm_newpost")],
        [InlineKeyboardButton("➕ চ্যানেল যোগ", callback_data="adm_addch"), InlineKeyboardButton("⚙️ সেটিংস এডিট", callback_data="adm_settings")],
        [InlineKeyboardButton("🖼️ ফটো পরিবর্তন", callback_data="set_photo"), InlineKeyboardButton("🔗 লিঙ্ক পরিবর্তন", callback_data="set_link")]
    ]
    await update.message.reply_text("👑 <b>মাস্টার অ্যাডমিন কন্ট্রোল প্যানেল</b> 👑\n\nসবকিছু এখান থেকে নিয়ন্ত্রণ করুন: 👇", reply_markup=InlineKeyboardMarkup(btns), parse_mode=ParseMode.HTML)

# (Newpost logic logic is kept simple for maximum reliability)
async def newpost_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query: await query.message.delete()
    msg = await (query.message if query else update.message).reply_text("📝 <b>ধাপ ১:</b> পোস্টের ক্যাপশন দিন: 👇", parse_mode=ParseMode.HTML)
    context.user_data['post'] = {'title': '', 'photo': None, 'fj': [], 'target': []}
    context.user_data['last_msg'] = msg.message_id
    return P_TITLE

async def p_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['post']['title'] = update.message.text
    await update.message.delete()
    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=context.user_data['last_msg'])
    msg = await update.message.reply_text("📸 <b>ধাপ ২:</b> ফটো পাঠান (নাহলে /skip দিন): 👇", parse_mode=ParseMode.HTML)
    context.user_data['last_msg'] = msg.message_id
    return P_PHOTO

async def p_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo: context.user_data['post']['photo'] = update.message.photo[-1].file_id
    await update.message.delete()
    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=context.user_data['last_msg'])
    
    all_ch = await get_all_channels()
    btns = [[InlineKeyboardButton(f"❌ {c['name']}", callback_data=f"tfj_{c['id']}")] for c in all_ch]
    btns.append([InlineKeyboardButton("➡️ পরবর্তী (Target) 🚀", callback_data="fj_done")])
    msg = await update.message.reply_text("🔒 <b>ধাপ ৩:</b> ফোর্স জয়েন চ্যানেল সিলেক্ট করুন: 👇", reply_markup=InlineKeyboardMarkup(btns), parse_mode=ParseMode.HTML)
    context.user_data['last_msg'] = msg.message_id
    return P_FJ

async def fj_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cid = query.data.replace("tfj_", "")
    if cid in context.user_data['post']['fj']: context.user_data['post']['fj'].remove(cid)
    else: context.user_data['post']['fj'].append(cid)
    all_ch = await get_all_channels()
    sel = context.user_data['post']['fj']
    btns = [[InlineKeyboardButton(f"{'✅' if str(c['id']) in sel else '❌'} {c['name']}", callback_data=f"tfj_{c['id']}")] for c in all_ch]
    btns.append([InlineKeyboardButton("➡️ পরবর্তী (Target) 🚀", callback_data="fj_done")])
    await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btns))

async def fj_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    all_ch = await get_all_channels()
    btns = [[InlineKeyboardButton(f"❌ {c['name']}", callback_data=f"ttg_{c['id']}")] for c in all_ch]
    btns.append([InlineKeyboardButton("🏁 প্রিভিউ দেখুন 📊", callback_data="tg_done")])
    await update.callback_query.edit_message_text("🎯 <b>ধাপ ৪:</b> টার্গেট চ্যানেল সিলেক্ট করুন: 👇", reply_markup=InlineKeyboardMarkup(btns), parse_mode=ParseMode.HTML)
    return P_TARGET

async def tg_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cid = query.data.replace("ttg_", "")
    if cid in context.user_data['post']['target']: context.user_data['post']['target'].remove(cid)
    else: context.user_data['post']['target'].append(cid)
    all_ch = await get_all_channels()
    sel = context.user_data['post']['target']
    btns = [[InlineKeyboardButton(f"{'✅' if str(c['id']) in sel else '❌'} {c['name']}", callback_data=f"ttg_{c['id']}")] for c in all_ch]
    btns.append([InlineKeyboardButton("🏁 প্রিভিউ দেখুন 📊", callback_data="tg_done")])
    await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btns))

async def tg_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    p = context.user_data['post']
    prev = f"🏁 <b>ফাইনাল প্রিভিউ:</b>\n\n{p['title']}\n\nFJ: {len(p['fj'])}টি | Target: {len(p['target'])}টি"
    btns = [[InlineKeyboardButton("🚀 এখনই পাঠান", callback_data="send_now")], [InlineKeyboardButton("❌ বাতিল", callback_data="cancel")]]
    if p['photo']: await query.message.reply_photo(photo=p['photo'], caption=prev, reply_markup=InlineKeyboardMarkup(btns), parse_mode=ParseMode.HTML)
    else: await query.message.reply_text(prev, reply_markup=InlineKeyboardMarkup(btns), parse_mode=ParseMode.HTML)
    return P_CONFIRM

async def send_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    p = context.user_data['post']
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🎬 এখনই দেখুন (Watch Now) ✨🍿🔥", callback_data=f"cp_{','.join(p['fj'])}")]])
    for tid in p['target']:
        try:
            if p['photo']: await context.bot.send_photo(chat_id=tid, photo=p['photo'], caption=p['title'], reply_markup=kb, parse_mode=ParseMode.HTML)
            else: await context.bot.send_message(chat_id=tid, text=p['title'], reply_markup=kb, parse_mode=ParseMode.HTML)
        except: pass
    await update.callback_query.message.reply_text("✅ পোস্ট সম্পন্ন হয়েছে! 🚀")
    return ConversationHandler.END

# ================= 🏁 কলব্যাক হ্যান্ডলার (With Auto-Delete) =================
async def global_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    all_ch = await get_all_channels()
    
    if query.data == "check_status":
        not_joined = await check_all_joined(query.from_user.id, context, all_ch)
        if not not_joined:
            url = get_setting("watch_url")
            await query.edit_message_text("✅ <b>ভেরিফিকেশন সফল!</b> 💖\n\nউপভোগ করুন! 👇🎬🍿", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎬 এখনই দেখুন (Watch Now) ✨🍿", url=url)]]), parse_mode=ParseMode.HTML)
        else:
            await query.answer("❌ আপনি সব চ্যানেলে জয়েন করেননি!", show_alert=True)
            
    elif query.data.startswith("cp_"):
        fjs = query.data.replace("cp_", "").split(",")
        fj_ch = [c for c in all_ch if str(c['id']) in fjs]
        missing = await check_all_joined(query.from_user.id, context, fj_ch)
        
        if not missing:
            url = get_setting("watch_url")
            text = (f"🚀✨ <b>আপনার প্রিমিয়াম ভিডিও লিঙ্ক এখানে:</b> 👇🔥🍿🔞🎬🎥💎👑\n\n"
                    f"🔗 <b>লিঙ্ক:</b> {url}\n\n"
                    f"⚠️ <b>সতর্কতা:</b> এই মেসেজটি নিরাপত্তা খাতিরে ঠিক <b>৪৫ সেকেন্ড</b> পর নিজে থেকেই ডিলেট হয়ে যাবে! ⏳✨🔥🔞🍿")
            
            sent_msg = await query.message.reply_text(text, parse_mode=ParseMode.HTML)
            # Schedule deletion
            asyncio.create_task(auto_delete_msg(context, query.message.chat_id, sent_msg.message_id, 45))
        else:
            btns = [[InlineKeyboardButton(f"➕ জয়েন: {c['name']}", url=c['link'])] for c in missing]
            btns.append([InlineKeyboardButton("ভেরিফাই করুন 🔄✨", callback_data=query.data)])
            await query.message.reply_text("⛔ <b>অ্যাক্সেস ডিনাইড!</b>\n\nভিডিও দেখতে আগে নিচের চ্যানেলগুলোতে জয়েন করুন: 👇", reply_markup=InlineKeyboardMarkup(btns), parse_mode=ParseMode.HTML)

# ================= 🚀 সেটিংস সেভ =================
async def set_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    context.user_data['set_key'] = "watch_url" if query.data == "set_link" else "welcome_photo"
    await query.message.reply_text("🔄 নতুন লিঙ্কটি লিখে পাঠান: 👇")
    return SET_VAL

async def set_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    CURSOR.execute("UPDATE settings SET value=? WHERE key=?", (update.message.text, context.user_data['set_key']))
    DB.commit()
    await update.message.reply_text("✅ সেটিংস আপডেট হয়েছে! 🎉")
    return ConversationHandler.END

async def cancel(update, context):
    return ConversationHandler.END

# ================= 🚀 মেইন রান =================
if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(newpost_start, pattern="^adm_newpost$")],
        states={
            P_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, p_title)],
            P_PHOTO: [MessageHandler(filters.PHOTO, p_photo), CommandHandler("skip", p_photo)],
            P_FJ: [CallbackQueryHandler(fj_toggle, pattern="^tfj_"), CallbackQueryHandler(fj_done, pattern="^fj_done$")],
            P_TARGET: [CallbackQueryHandler(tg_toggle, pattern="^ttg_"), CallbackQueryHandler(tg_done, pattern="^tg_done$")],
            P_CONFIRM: [CallbackQueryHandler(send_now, pattern="^send_now$")]
        }, fallbacks=[CommandHandler("cancel", cancel)]
    ))
    
    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(set_start, pattern="^set_link$|^set_photo$")],
        states={SET_VAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_save)]},
        fallbacks=[CommandHandler("cancel", cancel)]
    ))

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CallbackQueryHandler(global_callback))
    
    print("FINAL MASTER BOT IS ACTIVE! 🚀🔥🔞💎👑")
    app.run_polling()
