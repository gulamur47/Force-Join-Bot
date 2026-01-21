import os
import logging
import json
import sqlite3
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, InputFile
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ConversationHandler, CallbackContext
)
from telegram.helpers import mention_html

# ------------------ কনফিগ ------------------
TOKEN = os.environ.get("8007194607:AAHhuMvS3z814Fr2eF_17K1wv8UPXmvA1kY", "YOU")
ADMIN_IDS = {int(x) for x in os.environ.get("8013042180", "YOUR_ADMIN_ID").split(",")}
DB_PATH = "bot.db"

# ------------------ লোগিং ------------------
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ------------------ ডাটাবেস ------------------
class DB:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.setup()

    def setup(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            join_date DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS channels (
            channel_id TEXT PRIMARY KEY,
            name TEXT,
            link TEXT,
            force_join BOOLEAN DEFAULT 1
        )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,
            value TEXT
        )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS welcome_photo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            photo_id TEXT
        )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS posts (
            post_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            photo_id TEXT,
            post_text TEXT,
            buttons TEXT,
            force_channels TEXT,
            target_channel_id TEXT,
            watch_url TEXT
        )''')
        self.conn.commit()
        self._set_defaults()

    def _set_defaults(self):
        # ডিফল্ট কনফিগ
        defaults = {
            'welcome_message': '💖✨ <b>স্বাগতম! তোমাকে দেখে খুব খুশি! 💖✨</b>',
            'lock_message': '🔥💋 <b>অ্যাক্সেস লক করা আছে! আগে সব চ্যানেল Join করুন।</b>',
            'success_message': '💖🔥 আপনি সফলভাবে জয়েন করেছেন! এখন ভিডিও দেখুন।',
            'failed_message': '🔥💔 আপনি জয়েন করেননি। আগে জয়েন করুন।',
            'watch_url': 'https://example.com',
            'button_text': '🎬 ভিডিও দেখুন এখনই! 🔥',
            'auto_delete': '60',
            'verify_popup_not_joined': '🔥💋 প্রিয়, আগে সব চ্যানেল Join করুন 🔔💖\nতারপর 👉 ✅ Verified চাপুন 😘💎\nতারপর ভিডিও আনলক হবে 😍🔥',
            'verify_popup_joined': '💖🔥 হেই প্রিয়! 🔥💖\n✅ আপনি সফলভাবে Join করেছেন 🎉✨\nএবার 👉 ▶️ WATCH NOW ▶️ বাটনে ক্লিক করুন😘💎\n😈 তারপরই খুলে যাবে ভাইরাল ভিডিও 💋🔥'
        }
        for k, v in defaults.items():
            self.cursor.execute('INSERT OR IGNORE INTO config (key, value) VALUES (?, ?)', (k, v))
        # ডিফল্ট চ্যানেল
        self.cursor.execute("SELECT COUNT(*) FROM channels")
        if self.cursor.fetchone()[0] == 0:
            default_channels = [
                {'channel_id': '@channel1', 'name': 'Channel 1', 'link': 'https://t.me/channel1'},
                {'channel_id': '@channel2', 'name': 'Channel 2', 'link': 'https://t.me/channel2'}
            ]
            for ch in default_channels:
                self.cursor.execute('INSERT OR IGNORE INTO channels (channel_id, name, link) VALUES (?, ?, ?)',
                                    (ch['channel_id'], ch['name'], ch['link']))
        self.conn.commit()

    def add_user(self, user):
        self.cursor.execute('INSERT OR IGNORE INTO users (user_id, username, first_name, last_name) VALUES (?, ?, ?, ?)', 
                            (user.id, user.username, user.first_name, user.last_name))
        self.conn.commit()

    def get_config(self, key):
        self.cursor.execute('SELECT value FROM config WHERE key=?', (key,))
        row = self.cursor.fetchone()
        return row[0] if row else None

    def set_config(self, key, value):
        self.cursor.execute('REPLACE INTO config (key, value) VALUES (?, ?)', (key, value))
        self.conn.commit()

    def get_welcome_photo(self):
        self.cursor.execute('SELECT photo_id FROM welcome_photo ORDER BY id DESC LIMIT 1')
        row = self.cursor.fetchone()
        return row[0] if row else None

    def set_welcome_photo(self, photo_id):
        self.cursor.execute('DELETE FROM welcome_photo')
        self.cursor.execute('INSERT INTO welcome_photo (photo_id) VALUES (?)', (photo_id,))
        self.conn.commit()

    def add_post(self, title, photo_id, post_text, buttons, force_channels, target_channel_id, watch_url):
        self.cursor.execute('''INSERT INTO posts (title, photo_id, post_text, buttons, force_channels, target_channel_id, watch_url)
                               VALUES (?, ?, ?, ?, ?, ?, ?)''',
                            (title, photo_id, post_text, json.dumps(buttons), json.dumps(force_channels), target_channel_id, watch_url))
        self.conn.commit()

    def get_channels(self):
        self.cursor.execute('SELECT * FROM channels')
        return self.cursor.fetchall()

    def get_channel(self, channel_id):
        self.cursor.execute('SELECT * FROM channels WHERE channel_id=?', (channel_id,))
        return self.cursor.fetchone()

    def get_force_channels(self):
        self.cursor.execute('SELECT * FROM channels WHERE force_join=1')
        return self.cursor.fetchall()

db = DB()

# ------------------ ইউজার জয়েন চেক ------------------
import asyncio
async def check_membership(user_id, bot):
    channels = db.get_force_channels()
    joined = 0
    total = len(channels)
    for ch in channels:
        try:
            member = await bot.get_chat_member(chat_id=ch[0], user_id=user_id)
            if member.status in ['member', 'administrator', 'creator']:
                joined += 1
        except:
            pass
    all_joined = (joined == total)
    return all_joined, channels

# ------------------ UI ------------------
def format_text(text, user):
    text = text.replace("@UserName", f"<b>{user.first_name}</b>")
    return text

# ------------------ /start ------------------
async def start(update: Update, context: CallbackContext):
    user = update.effective_user
    db.add_user(user)
    # চ্যানেল জয়েন চেক
    all_joined, channels = await check_membership(user.id, context.bot)
    if not all_joined:
        msg = db.get_config('lock_message')
        buttons = []
        for ch in channels:
            buttons.append([{"text": f"🛑 Join {ch[1]}", "url": ch[2]}])
        buttons.append([{"text": "✅ Verify Membership", "callback": "verify"}])
        photo_id = db.get_welcome_photo()
        if photo_id:
            await update.message.reply_photo(photo=photo_id, caption=msg, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.HTML)
        return
    # জয়েন হলে
    await send_welcome(update, user)

async def send_welcome(update, user):
    msg = db.get_config('welcome_message')
    btn_text = db.get_config('button_text')
    watch_url = db.get_config('watch_url')
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(btn_text, url=watch_url)]])
    photo_id = db.get_welcome_photo()
    if photo_id:
        await update.message.reply_photo(photo=photo_id, caption=msg, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text(msg, reply_markup=keyboard, parse_mode=ParseMode.HTML)

# ------------------ verify ------------------
async def verify(update: Update, context: CallbackContext):
    user = update.effective_user
    all_joined, channels = await check_membership(user.id, context.bot)
    if all_joined:
        # জয়েন হলে
        msg = db.get_config('verify_popup_joined')
        await update.callback_query.message.edit_caption(caption=msg, parse_mode=ParseMode.HTML)
        await send_welcome(update, user)
    else:
        # না হলে
        msg = db.get_config('verify_popup_not_joined')
        await update.callback_query.message.edit_caption(caption=msg, parse_mode=ParseMode.HTML)

# ------------------ /setwelcomephoto ------------------
async def set_welcome_photo(update: Update, context: CallbackContext):
    if update.message.photo:
        photo_id = update.message.photo[-1].file_id
        db.set_welcome_photo(photo_id)
        await update.message.reply_text("Welcome photo set!")
    else:
        await update.message.reply_text("Please send a photo.")

# ------------------ /createpost ------------------
from telegram.ext import ConversationHandler
POST_STEPS = ['title', 'photo', 'text', 'watch_url', 'buttons', 'force_channels', 'target_channel', 'confirm']
async def create_post_start(update: Update, context: CallbackContext):
    context.user_data['post'] = {}
    await update.message.reply_text("Send post title:")
    return 'title'

async def create_post_title(update: Update, context: CallbackContext):
    context.user_data['post']['title'] = update.message.text
    await update.message.reply_text("Send post photo or /skip:")
    return 'photo'

async def create_post_photo(update: Update, context: CallbackContext):
    if update.message.photo:
        photo_id = update.message.photo[-1].file_id
        context.user_data['post']['photo_id'] = photo_id
        await update.message.reply_text("Send post text or /skip:")
        return 'text'
    elif update.message.text and update.message.text.lower() == '/skip':
        context.user_data['post']['photo_id'] = ''
        await update.message.reply_text("Send post text or /skip:")
        return 'text'
    else:
        await update.message.reply_text("Please send a photo or /skip.")
        return 'photo'

async def create_post_text(update: Update, context: CallbackContext):
    if update.message.text and update.message.text.lower() != '/skip':
        context.user_data['post']['post_text'] = update.message.text
    else:
        context.user_data['post']['post_text'] = ''
    await update.message.reply_text("Send watch URL:")
    return 'watch_url'

async def create_post_watch_url(update: Update, context: CallbackContext):
    context.user_data['post']['watch_url'] = update.message.text
    # এখানে পোস্টের বাটন ও ফোর্স চ্যানেল সেটাপের জন্য স্টেপ চালিয়ে যাবো।
    # এখন সরাসরি পোস্টের প্রিভিউ দেখাব।
    post = context.user_data['post']
    await update.message.reply_text(f"Post Title: {post['title']}\nPost Text: {post['post_text']}\nWatch URL: {post['watch_url']}\n\nSend /done to publish or /cancel to cancel.")
    # পরে এই স্টেপের জন্য আলাদা হ্যান্ডলার থাকবে।
    return 'confirm'

async def create_post_done(update: Update, context: CallbackContext):
    post = context.user_data['post']
    # ডেটাবেসে সংরক্ষণ
    db.add_post(
        title=post['title'],
        photo_id=post.get('photo_id', ''),
        post_text=post.get('post_text', ''),
        buttons=[],  # এখনি যোগ হবে
        force_channels=[],  # এখনি যোগ হবে
        target_channel_id='',  # এখনি যোগ হবে
        watch_url=post['watch_url']
    )
    await update.message.reply_text("Post published successfully!")
    return ConversationHandler.END

# ------------------ ক্যাশ ও চ্যানেল জয়েন চেক ------------------
async def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    user = query.from_user
    if data == 'verify':
        await verify(update, context)
    elif data == 'set_welcome_photo':
        await set_welcome_photo(update, context)
    elif data == 'create_post_start':
        await create_post_start(update, context)
    # আরও অন্যান্য callback গুলো এখানে যোগ হবে

# ------------------ মূল ------------------
def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(CommandHandler("setwelcomephoto", set_welcome_photo))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('createpost', create_post_start)],
        states={
            'title': [MessageHandler(filters.TEXT & ~filters.COMMAND, create_post_title)],
            'photo': [MessageHandler(filters.PHOTO | filters.TEXT & ~filters.COMMAND, create_post_photo)],
            'text': [MessageHandler(filters.TEXT & ~filters.COMMAND, create_post_text)],
            'watch_url': [MessageHandler(filters.TEXT & ~filters.COMMAND, create_post_watch_url)],
            'confirm': [MessageHandler(filters.TEXT & ~filters.COMMAND, create_post_done)],
        },
        fallbacks=[CommandHandler('cancel', lambda u, c: u.message.reply_text("Cancelled"))]
    )

    application.add_handler(conv_handler)

    application.run_polling()

if __name__ == '__main__':
    main()
