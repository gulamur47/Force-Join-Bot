import os
import sys
import time
import sqlite3
import logging
import threading
import psutil
import datetime
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.helpers import mention_html
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, ConversationHandler, MessageHandler, 
    filters, ApplicationBuilder
)

# ================= 🔧 কনফিগারেশন (এখানে হাত দেবেন না) =================
# আপনার টোকেন এবং অ্যাডমিন আইডি
TOKEN = "8510787985:AAEw4UNXdCZLK_r25EKJnuIwrlkE8cyk7VE"
ADMIN_IDS = {6406804999} 

# লগিং সিস্টেম (এরর দেখার জন্য)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
START_TIME = time.time()

# কনভারসেশন স্টেটস (স্টেপ বাই স্টেপ কাজ করার জন্য)
EDIT_VALUE = 1
POST_CAPTION, POST_MEDIA, POST_CONFIRM = 2, 3, 4
BROADCAST_MSG = 5

# ================= 🗄️ ডাটাবেস সিস্টেম (অটোমেটিক) =================
class SupremeDB:
    def __init__(self):
        # মাল্টি-থ্রেড সাপোর্টেড কানেকশন
        self.conn = sqlite3.connect("supreme_final_v200.db", check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.init_tables()

    def init_tables(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, join_date TEXT, status TEXT)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, value TEXT)")
        
        # 💖 রোমান্টিক ডিফল্ট সেটিংস (৫০+ ফিচার)
        defaults = {
            "watch_url": "https://mmshotbd.blogspot.com/?m=1",
            "welcome_photo": "https://cdn.pixabay.com/photo/2018/01/14/23/12/nature-3082832_1280.jpg",
            "auto_delete": "45",
            "maint_mode": "OFF",
            "force_join": "ON",
            
            # বিশাল লাভ মেসেজ
            "welcome_msg": """💖✨ <b>ওগো শুনছো! স্বাগতম জানাই তোমাকে!</b> ✨💖

🌹 <b>প্রিয়তম/প্রিয়তমা,</b>
তুমি অবশেষে আমাদের মাঝে এসেছো, আমার হৃদয়টা খুশিতে নেচে উঠলো! 😍💃
তোমাকে ছাড়া আমাদের এই আয়োজন একদমই অসম্পূর্ণ ছিল।

✨ <b>তোমার জন্য স্পেশাল গিফট:</b>
🎀 এক্সক্লুসিভ ভাইরাল ভিডিও 🔞
🎀 নতুন সব হট কালেকশন 🔥
🎀 এবং আমার হৃদয়ের গভীর ভালোবাসা... ❤️

👇 <b>দেরি না করে নিচের বাটনে আলতো করে ক্লিক করো সোনা:</b> 👇""",
            
            # ইমোশনাল লক মেসেজ
            "lock_msg": """💔 <b>ওহ নো বেবি! তুমি এখনো জয়েন করোনি?</b> 😢💔

আমার লক্ষ্মীটা, তুমি যদি নিচের চ্যানেলগুলোতে জয়েন না করো, তাহলে আমি তোমাকে ভিডিওটা দেখাতে পারবো না! 🥺🥀
আমার খুব কষ্ট লাগবে যদি তুমি চলে যাও... 😭

🌹 <b>প্লিজ সোনা, রাগ করো না!</b>
নিচের সবগুলোতে জয়েন করে <b>"Verify Me Love"</b> বাটনে ক্লিক করো। আমি তোমার অপেক্ষায় আছি... 😘💕""",
            
            "btn_text": "🎬 ভিডিও দেখুন (Watch Now) ✨😍"
        }
        
        for k, v in defaults.items():
            self.cursor.execute("INSERT OR IGNORE INTO config VALUES (?, ?)", (k, v))
        self.conn.commit()

    def get(self, key):
        self.cursor.execute("SELECT value FROM config WHERE key=?", (key,))
        res = self.cursor.fetchone()
        return res[0] if res else "Not Set"

    def set(self, key, val):
        self.cursor.execute("INSERT OR REPLACE INTO config VALUES (?, ?)", (key, str(val)))
        self.conn.commit()

    def add_user(self, user):
        self.cursor.execute("INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?)", 
                            (user.id, user.first_name, datetime.datetime.now().strftime("%Y-%m-%d"), "active"))
        self.conn.commit()

    def get_stats(self):
        try:
            total = self.cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            today = self.cursor.execute("SELECT COUNT(*) FROM users WHERE join_date=?", (datetime.datetime.now().strftime("%Y-%m-%d"),)).fetchone()[0]
            return total, today
        except: return 0, 0

    def get_all_users(self):
        return [r[0] for r in self.cursor.execute("SELECT id FROM users").fetchall()]

db = SupremeDB()

# ================= 🔗 ফোর্স জয়েন চ্যানেল লিস্ট =================
# ⚠️ এই চ্যানেলগুলোতে বটকে অবশ্যই অ্যাডমিন বানাতে হবে!
MASTER_CHANNELS = [
    {"id": "@virallink259", "name": "Viral Link 2026 🔥", "link": "https://t.me/virallink259"},
    {"id": -1002279183424, "name": "Premium Apps 💎", "link": "https://t.me/+5PNLgcRBC0IxYjll"},
    {"id": "@virallink246", "name": "BD Beauty 🍑", "link": "https://t.me/virallink246"},
    {"id": "@viralexpress1", "name": "FB Insta Links 🔗", "link": "https://t.me/viralexpress1"},
    {"id": "@movietime467", "name": "Movie Time 🎬", "link": "https://t.me/movietime467"},
    {"id": "@viralfacebook9", "name": "BD MMS Video 🔞", "link": "https://t.me/viralfacebook9"},
    {"id": "@viralfb24", "name": "Deshi Bhabi 🔥", "link": "https://t.me/viralfb24"},
    {"id": "@fbviral24", "name": "Kochi Meye 🎀", "link": "https://t.me/fbviral24"},
    {"id": -1001550993047, "name": "Request Zone 📥", "link": "https://t.me/+WAOUc1rX6Qk3Zjhl"},
    {"id": -1002011739504, "name": "Viral BD 🌍", "link": "https://t.me/+la630-IFwHAwYWVl"},
    {"id": -1002444538806, "name": "AI Studio 🎨", "link": "https://t.me/+AHsGXIDzWmJlZjVl"}
]

# ================= 🌐 রেন্ডার হেলথ সার্ভার (Port Binding) =================
class HealthServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.wfile.write(b"Supreme Bot is Running Smoothly!")

def run_server():
    try:
        # Render Environment থেকে Port নেয়
        port = int(os.environ.get("PORT", 8080))
        HTTPServer(("0.0.0.0", port), HealthServer).serve_forever()
    except Exception as e:
        logger.error(f"Server Error: {e}")

threading.Thread(target=run_server, daemon=True).start()

# ================= 🎨 ডিজাইন ফাংশন =================
def decor(text, user):
    name = mention_html(user.id, user.first_name)
    header = "🌺🍃 <b>SUPREME LOVE ZONE</b> 🍃🌺\n━━━━━━━━━━━━━━━━━━━━━━\n"
    footer = f"\n━━━━━━━━━━━━━━━━━━━━━━\n💖 <b>User:</b> {name}\n⏰ <b>Time:</b> {datetime.datetime.now().strftime('%I:%M %p')}"
    return header + text + footer

# ================= 🛡️ লজিক: চেক জয়েন স্ট্যাটাস =================
async def check_join_status(user_id, context):
    if db.get("force_join") == "OFF": return []
    missing = []
    
    for ch in MASTER_CHANNELS:
        try:
            # বট অ্যাডমিন কিনা চেক না করেই মেম্বার চেক করার চেষ্টা করবে
            member = await context.bot.get_chat_member(chat_id=ch["id"], user_id=user_id)
            if member.status in ['left', 'kicked', 'restricted']:
                missing.append(ch)
        except Exception as e:
            # যদি বট চ্যানেলে ব্যান থাকে বা এক্সেস না পায়, তবুও ইউজারকে জয়েন করতে বলবে (সেফটি)
            missing.append(ch)
            
    return missing

# ================= 👤 ইউজার হ্যান্ডলার (START) =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.add_user(user)
    
    # 1. মেইনটেনেন্স মোড চেক
    if db.get("maint_mode") == "ON" and user.id not in ADMIN_IDS:
        await update.message.reply_html(decor("🚧 <b>সিস্টেম মেইনটেনেন্স চলছে!</b>\nএকটু পরে চেষ্টা করুন জানু! 🥺", user))
        return

    # 2. জয়েন স্ট্যাটাস চেক
    missing = await check_join_status(user.id, context)
    photo_url = db.get("welcome_photo")
    
    if not missing:
        # সব জয়েন করা আছে
        txt = db.get("welcome_msg")
        kb = [[InlineKeyboardButton(db.get("btn_text"), url=db.get("watch_url"))]]
    else:
        # জয়েন করা বাকি আছে
        txt = db.get("lock_msg")
        # ডায়নামিক বাটন জেনারেশন
        kb = []
        for c in missing:
            kb.append([InlineKeyboardButton(f"💞 জয়েন: {c['name']}", url=c['link'])])
        kb.append([InlineKeyboardButton("✨ Verify Me Love ✨", callback_data="verify_join")])

    # 3. মেসেজ পাঠানো (এরর হ্যান্ডলিং সহ)
    try:
        await update.message.reply_photo(photo=photo_url, caption=decor(txt, user), reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)
    except Exception as e:
        # ছবি নষ্ট থাকলে টেক্সট যাবে
        await update.message.reply_html(decor(txt, user), reply_markup=InlineKeyboardMarkup(kb))

# ================= 👑 অ্যাডমিন প্যানেল (মেইন মেনু) =================
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS: return
    
    total, today = db.get_stats()
    uptime = str(datetime.timedelta(seconds=int(time.time() - START_TIME)))
    
    txt = (f"👑 <b>SUPREME GOD ADMIN PANEL</b>\n\n"
           f"👥 <b>Total Users:</b> {total}\n"
           f"📅 <b>Today Joined:</b> {today}\n"
           f"⚡ <b>Uptime:</b> {uptime}\n"
           f"💾 <b>RAM:</b> {psutil.virtual_memory().percent}%\n"
           f"👇 <b>Control Everything Below:</b>")
    
    btns = [
        [InlineKeyboardButton("📝 মেসেজ এডিটর", callback_data="menu_msg"), InlineKeyboardButton("🔗 লিঙ্ক সেটিংস", callback_data="menu_links")],
        [InlineKeyboardButton("🛡️ সিকিউরিটি গার্ড", callback_data="menu_security"), InlineKeyboardButton("📢 মার্কেটিং টুলস", callback_data="menu_marketing")],
        [InlineKeyboardButton("❌ প্যানেল বন্ধ করুন", callback_data="close_panel")]
    ]
    
    # মেসেজ এডিট নাকি নতুন মেসেজ - সেটা চেক করে রিপ্লাই দিবে
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_caption(caption=decor(txt, update.effective_user), reply_markup=InlineKeyboardMarkup(btns), parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_html(decor(txt, update.effective_user), reply_markup=InlineKeyboardMarkup(btns))

# ================= 🎮 গ্লোবাল বাটন হ্যান্ডলার (সব লজিক এখানে) =================
async def global_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer() # লোডিং বন্ধ করার জন্য
    
    data = query.data
    user = query.from_user

    # --- ১. মেনু নেভিগেশন ---
    if data == "main_menu":
        await admin_panel(update, context)

    elif data == "menu_msg":
        btns = [
            [InlineKeyboardButton("✍️ ওয়েলকাম মেসেজ", callback_data="edit_welcome_msg")],
            [InlineKeyboardButton("✍️ লক মেসেজ", callback_data="edit_lock_msg")],
            [InlineKeyboardButton("🖼️ ওয়েলকাম ফটো", callback_data="edit_welcome_photo")],
            [InlineKeyboardButton("🔙 ব্যাক", callback_data="main_menu")]
        ]
        await query.edit_message_caption(decor("📝 <b>মেসেজ এডিটর</b>\nকি এডিট করতে চান?", user), reply_markup=InlineKeyboardMarkup(btns), parse_mode=ParseMode.HTML)

    elif data == "menu_links":
        btns = [
            [InlineKeyboardButton("🔗 ওয়াচ লিঙ্ক", callback_data="edit_watch_url")],
            [InlineKeyboardButton("🔘 বাটন টেক্সট", callback_data="edit_btn_text")],
            [InlineKeyboardButton("⏱️ টাইমার", callback_data="edit_auto_delete")],
            [InlineKeyboardButton("🔙 ব্যাক", callback_data="main_menu")]
        ]
        await query.edit_message_caption(decor("🔗 <b>লিঙ্ক সেটিংস</b>", user), reply_markup=InlineKeyboardMarkup(btns), parse_mode=ParseMode.HTML)

    elif data == "menu_security":
        maint = "✅ ON" if db.get("maint_mode") == "ON" else "❌ OFF"
        force = "✅ ON" if db.get("force_join") == "ON" else "❌ OFF"
        btns = [
            [InlineKeyboardButton(f"Maintenance: {maint}", callback_data="tog_maint_mode")],
            [InlineKeyboardButton(f"Force Join: {force}", callback_data="tog_force_join")],
            [InlineKeyboardButton("🔙 ব্যাক", callback_data="main_menu")]
        ]
        await query.edit_message_caption(decor("🛡️ <b>সিকিউরিটি গার্ড</b>", user), reply_markup=InlineKeyboardMarkup(btns), parse_mode=ParseMode.HTML)

    elif data == "menu_marketing":
        btns = [
            [InlineKeyboardButton("✨ নতুন পোস্ট (Wizard)", callback_data="wiz_start")],
            [InlineKeyboardButton("📡 ব্রডকাস্ট", callback_data="broadcast_init")],
            [InlineKeyboardButton("🔙 ব্যাক", callback_data="main_menu")]
        ]
        await query.edit_message_caption(decor("📢 <b>মার্কেটিং জোন</b>", user), reply_markup=InlineKeyboardMarkup(btns), parse_mode=ParseMode.HTML)

    # --- ২. টগল লজিক (অন/অফ) ---
    elif data.startswith("tog_"):
        key = data.replace("tog_", "")
        current = db.get(key)
        new_val = "OFF" if current == "ON" else "ON"
        db.set(key, new_val)
        # রিফ্রেশ করার জন্য আবার সিকিউরিটি মেনুতে পাঠাবে
        query.data = "menu_security"
        await global_callback_handler(update, context)

    # --- ৩. ইউজার ভেরিফিকেশন ---
    elif data == "verify_join":
        missing = await check_join_status(user.id, context)
        if not missing:
            await query.answer("💖 ভেরিফিকেশন সফল জানু!", show_alert=True)
            try: await query.message.delete()
            except: pass
            
            kb = [[InlineKeyboardButton(db.get("btn_text"), url=db.get("watch_url"))]]
            await query.message.reply_photo(
                photo=db.get("welcome_photo"),
                caption=decor(db.get("welcome_msg"), user),
                reply_markup=InlineKeyboardMarkup(kb),
                parse_mode=ParseMode.HTML
            )
        else:
            await query.answer("💔 এখনো সবগুলোতে জয়েন করোনি!", show_alert=True)

    elif data == "close_panel":
        await query.message.delete()

# ================= 📝 কনভারসেশন ১: সেটিংস এডিটর =================
async def edit_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    key = query.data.replace("edit_", "")
    context.user_data['edit_key'] = key
    
    await query.message.reply_html(decor(f"✍️ <b>এডিট মোড চালু হয়েছে!</b>\n\nKey: <code>{key}</code>\n\nনতুন ভ্যালু লিখে মেসেজ দিন (টেক্সট/লিঙ্ক):", query.from_user))
    return EDIT_VALUE

async def edit_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = context.user_data.get('edit_key')
    val = update.message.text
    db.set(key, val)
    await update.message.reply_html(decor(f"✅ <b>সফলভাবে সেভ হয়েছে!</b>\n\nনতুন ভ্যালু সেট করা হয়েছে।", update.effective_user))
    return ConversationHandler.END

# ================= 📢 কনভারসেশন ২: পোস্ট উইজার্ড =================
async def wiz_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.reply_html(decor("📝 <b>পোস্ট উইজার্ড: ধাপ ১</b>\n\nপোস্টের ক্যাপশন লিখে পাঠান:", update.effective_user))
    context.user_data['post'] = {}
    return POST_CAPTION

async def wiz_caption(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['post']['cap'] = update.message.text
    await update.message.reply_html(decor("📸 <b>পোস্ট উইজার্ড: ধাপ ২</b>\n\nফটো/ভিডিও পাঠান (অথবা /skip লিখুন):", update.effective_user))
    return POST_MEDIA

async def wiz_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo: context.user_data['post']['med'] = update.message.photo[-1].file_id
    elif update.message.video: context.user_data['post']['med'] = update.message.video.file_id
    else: context.user_data['post']['med'] = None
    
    btns = [[InlineKeyboardButton(f"Send to {c['name']}", callback_data=f"send_{c['id']}")] for c in MASTER_CHANNELS]
    await update.message.reply_html(decor("🚀 <b>পোস্ট উইজার্ড: শেষ ধাপ</b>\n\nকোথায় সেন্ড করবেন সিলেক্ট করুন:", update.effective_user), reply_markup=InlineKeyboardMarkup(btns))
    return POST_CONFIRM

async def wiz_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.callback_query.data.replace("send_", "")
    p = context.user_data['post']
    kb = InlineKeyboardMarkup([[InlineKeyboardButton(db.get("btn_text"), url=db.get("watch_url"))]])
    
    try:
        if p['med']: await context.bot.send_photo(cid, p['med'], caption=p['cap'], reply_markup=kb, parse_mode=ParseMode.HTML)
        else: await context.bot.send_message(cid, p['cap'], reply_markup=kb, parse_mode=ParseMode.HTML)
        await update.callback_query.message.reply_text("✅ পোস্ট সফল হয়েছে!")
    except Exception as e:
        await update.callback_query.message.reply_text(f"❌ এরর: {e} (বট কি ওই চ্যানেলে অ্যাডমিন?)")
    return ConversationHandler.END

# ================= 📡 কনভারসেশন ৩: ব্রডকাস্ট =================
async def broad_init(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.reply_html(decor("📢 <b>ব্রডকাস্ট মোড</b>\n\nমেসেজ ফরোয়ার্ড করুন বা টাইপ করুন:", update.effective_user))
    return BROADCAST_MSG

async def broad_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = db.get_all_users()
    msg = update.message
    status = await update.message.reply_text("⏳ ব্রডকাস্ট শুরু হচ্ছে...")
    s, f = 0, 0
    
    for uid in users:
        try:
            await msg.copy(uid)
            s += 1
        except: f += 1
        if s % 50 == 0: await status.edit_text(f"📤 পাঠাচ্ছে... {s}/{len(users)}")
        
    await status.edit_text(decor(f"✅ <b>ব্রডকাস্ট রিপোর্ট</b>\n\nসফল: {s}\nব্যর্থ: {f}", update.effective_user))
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ অপারেশন বাতিল করা হয়েছে।")
    return ConversationHandler.END

# ================= 🚀 মেইন অ্যাপ্লিকেশন রানার =================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # ১. সেটিংস এডিটর হ্যান্ডলার (High Priority)
    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(edit_start, pattern="^edit_")],
        states={EDIT_VALUE: [MessageHandler(filters.TEXT, edit_save)]},
        fallbacks=[CommandHandler("cancel", cancel)]
    ))

    # ২. পোস্ট উইজার্ড হ্যান্ডলার (High Priority)
    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(wiz_start, pattern="^wiz_start$")],
        states={
            POST_CAPTION: [MessageHandler(filters.TEXT, wiz_caption)],
            POST_MEDIA: [MessageHandler(filters.ALL, wiz_media)],
            POST_CONFIRM: [CallbackQueryHandler(wiz_send, pattern="^send_")]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    ))

    # ৩. ব্রডকাস্ট হ্যান্ডলার (High Priority)
    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(broad_init, pattern="^broadcast_init$")],
        states={BROADCAST_MSG: [MessageHandler(filters.ALL, broad_send)]},
        fallbacks=[CommandHandler("cancel", cancel)]
    ))

    # ৪. বেসিক কমান্ডস
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))

    # ৫. গ্লোবাল বাটন হ্যান্ডলার (সবশেষে থাকবে)
    # এটি মেনু নেভিগেশন এবং ভেরিফিকেশন হ্যান্ডেল করবে
    app.add_handler(CallbackQueryHandler(global_callback_handler))

    print("✅ SUPREME GOD BOT v200.0 IS ONLINE AND STABLE!")
    app.run_polling()

if __name__ == "__main__":
    main()
