"""
================================================================================
SUPREME GOD BOT - PREMIUM EDITION v10.1 (POPUP FIXED)
FULLY WORKING WITH ALL FEATURES - ENHANCED VERIFICATION
BOT.BUILDER.CO OPTIMIZED - STABLE VERSION
================================================================================
"""

import os
import sys
import time
import json
import sqlite3
import logging
import threading
import asyncio
from typing import List, Dict, Optional
from datetime import datetime

# Telegram imports
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    BotCommand
)
from telegram.constants import ParseMode
from telegram.helpers import mention_html
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, ConversationHandler, MessageHandler,
    filters, ApplicationBuilder
)

# ==============================================================================
# ⚙️ CONFIGURATION
# ==============================================================================

class Config:
    # Bot Token
    TOKEN = os.environ.get("BOT_TOKEN", "8007194607:AAHhuMvS3z814Fr2eF_17K1wv8UPXmvA1kY")
    ADMIN_IDS = {int(x) for x in os.environ.get("ADMIN_IDS", "8013042180").split(",")}
    
    # Video Downloader Bot
    VIDEO_BOT_USERNAME = "@videodownloader247_bot"
    VIDEO_BOT_LINK = f"https://t.me/{VIDEO_BOT_USERNAME.replace('@', '')}"
    
    # Database
    DB_NAME = os.environ.get("DB_NAME", "supreme_bot.db")
    
    # System
    DEFAULT_AUTO_DELETE = 60
    
    # Default Channels
    DEFAULT_CHANNELS = [
        {"id": "@virallink259", "name": "Viral Link 2026 🔥", "link": "https://t.me/virallink259"},
        {"id": -1002279183424, "name": "Premium Apps 💎", "link": "https://t.me/+5PNLgcRBC0IxYjll"},
        {"id": "@virallink246", "name": "BD Beauty 🍑", "link": "https://t.me/virallink246"},
        {"id": "@viralexpress1", "name": "FB Insta Links 🔗", "link": "https://t.me/viralexpress1"},
        {"id": "@movietime467", "name": "Movie Time 🎬", "link": "https://t.me/movietime467"},
    ]
    
    # Conversation States
    STATE_POST_TITLE = 1
    STATE_POST_PHOTO = 2
    STATE_POST_TEXT = 3
    STATE_POST_WATCH_URL = 4
    STATE_POST_BUTTONS = 5
    STATE_POST_BUTTON_NAME = 6
    STATE_POST_BUTTON_LINK = 7
    STATE_POST_FORCE_CHANNELS = 8
    STATE_POST_TARGET_CHANNEL = 9
    STATE_POST_CONFIRM = 10
    
    STATE_CHANNEL_ADD_ID = 11
    STATE_CHANNEL_ADD_NAME = 12
    STATE_CHANNEL_ADD_LINK = 13
    STATE_EDIT_MESSAGE = 14
    STATE_WELCOME_PHOTO = 15
    STATE_EDIT_CHANNEL_NAME = 16
    STATE_EDIT_CHANNEL_LINK = 17
    
    # Emojis
    EMOJIS = {
        "heart": "❤️", "fire": "🔥", "star": "⭐", "lock": "🔒", "unlock": "🔓",
        "check": "✅", "cross": "❌", "users": "👥", "admin": "👑", "camera": "📸",
        "video": "🎬", "link": "🔗", "time": "⏰", "warn": "⚠️", "info": "ℹ️",
        "gear": "⚙️", "chart": "📊", "megaphone": "📢", "crown": "👑", "rocket": "🚀",
        "target": "🎯", "photo": "🖼️", "edit": "✏️", "delete": "🗑️", "telegram": "📱"
    }
    
    # Enhanced Verification Messages
    VERIFICATION_MESSAGES = {
        'not_joined_popup': "🔥💋 প্রিয়, আগে সব চ্যানেল Join করুন 🔔💖\nতারপর 👉 ✅ Verified চাপুন 😘💎\nএরপরই দেখবেন HOT & LOVE ভিডিও 😍🔥",
        'joined_popup': "💖🔥 হেই প্রিয়! 🔥💖\n✅ আপনি সফলভাবে Join করেছেন 🎉✨\nএবার 👉 ▶️ WATCH NOW ▶️ বাটনে ক্লিক করুন 😘💎\n😈 তারপরই খুলে যাবে আপনার জন্য 🔞 ভাইরাল ভিডিও এর দুনিয়া 💋🔥",
        'access_granted': "🎉 ✅ অ্যাক্সেস গ্রান্টেড! এখন ভিডিও লিংক দেখতে পারবেন।",
        'watch_button_text': "▶️ WATCH NOW ▶️",
        'verify_button_text': "✅ Verify & View"
    }

# ==============================================================================
# 📝 LOGGING
# ==============================================================================

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler('bot_debug.log')]
)
logger = logging.getLogger(__name__)

# ==============================================================================
# 🗄️ DATABASE MANAGER
# ==============================================================================

class DatabaseManager:
    _instance = None
    _lock = threading.RLock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self):
        if self._initialized: return
        self.db_path = Config.DB_NAME
        self.connection_pool = {}
        self.init_database()
        self._initialized = True
    
    def get_connection(self):
        thread_id = threading.get_ident()
        with self._lock:
            if thread_id not in self.connection_pool:
                conn = sqlite3.connect(self.db_path, check_same_thread=False)
                conn.row_factory = sqlite3.Row
                self.connection_pool[thread_id] = conn
            return self.connection_pool[thread_id]
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT, last_name TEXT,
            join_date DATETIME DEFAULT CURRENT_TIMESTAMP, last_active DATETIME DEFAULT CURRENT_TIMESTAMP, is_blocked BOOLEAN DEFAULT 0)''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS channels (
            channel_id TEXT PRIMARY KEY, name TEXT NOT NULL, link TEXT NOT NULL,
            force_join BOOLEAN DEFAULT 1, is_active BOOLEAN DEFAULT 1, added_date DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, value TEXT NOT NULL)''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS posts (
            post_id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, photo_id TEXT, post_text TEXT,
            buttons TEXT, force_channels TEXT, target_channel_id TEXT, created_by INTEGER,
            created_date DATETIME DEFAULT CURRENT_TIMESTAMP, video_bot_link TEXT, is_active BOOLEAN DEFAULT 1)''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS user_access (
            user_id INTEGER, post_id INTEGER, access_granted BOOLEAN DEFAULT 0,
            access_date DATETIME DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (user_id, post_id))''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS welcome_photo (
            id INTEGER PRIMARY KEY AUTOINCREMENT, photo_id TEXT, added_date DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        
        self.initialize_defaults()
        conn.commit()
    
    def initialize_defaults(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        defaults = [
            ('welcome_message', Config.EMOJIS['heart'] + " <b>স্বাগতম!</b> " + Config.EMOJIS['fire'] + "\n\nনিচের বাটনে ক্লিক করুন:"),
            ('lock_message', Config.EMOJIS['lock'] + " <b>লক করা!</b>\n\nসব চ্যানেল জয়েন করে ভেরিফাই করুন।"),
            ('auto_delete', '60'),
            ('video_bot_link', Config.VIDEO_BOT_LINK)
        ]
        
        for key, value in defaults:
            cursor.execute('INSERT OR IGNORE INTO config (key, value) VALUES (?, ?)', (key, value))
        
        cursor.execute("SELECT COUNT(*) FROM channels")
        if cursor.fetchone()[0] == 0:
            for channel in Config.DEFAULT_CHANNELS:
                cursor.execute('INSERT OR IGNORE INTO channels (channel_id, name, link) VALUES (?, ?, ?)',
                             (str(channel["id"]), channel["name"], channel["link"]))
        conn.commit()

    # === User & Channel Methods ===
    def add_user(self, user_id, username, first_name, last_name=""):
        try:
            conn = self.get_connection()
            conn.execute('INSERT OR REPLACE INTO users (user_id, username, first_name, last_name, last_active) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)',
                        (user_id, username, first_name, last_name))
            conn.commit()
            return True
        except: return False
    
    def update_user_activity(self, user_id):
        try:
            conn = self.get_connection()
            conn.execute('UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE user_id = ?', (user_id,))
            conn.commit()
        except: pass
    
    def get_user(self, user_id):
        try:
            conn = self.get_connection()
            cursor = conn.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except: return None
        
    def get_all_users(self):
        try:
            conn = self.get_connection()
            cursor = conn.execute('SELECT * FROM users ORDER BY last_active DESC')
            return [dict(row) for row in cursor.fetchall()]
        except: return []

    def get_channels(self, force_only=False, active_only=True):
        try:
            conn = self.get_connection()
            query = "SELECT * FROM channels WHERE 1=1"
            if active_only: query += " AND is_active = 1"
            if force_only: query += " AND force_join = 1"
            query += " ORDER BY name"
            cursor = conn.execute(query)
            return [dict(row) for row in cursor.fetchall()]
        except: return []
    
    def get_channel(self, channel_id):
        try:
            conn = self.get_connection()
            cursor = conn.execute('SELECT * FROM channels WHERE channel_id = ?', (str(channel_id),))
            row = cursor.fetchone()
            return dict(row) if row else None
        except: return None
    
    def add_channel(self, channel_id, name, link, force_join=True):
        try:
            conn = self.get_connection()
            conn.execute('INSERT OR REPLACE INTO channels (channel_id, name, link, force_join) VALUES (?, ?, ?, ?)',
                        (str(channel_id), name, link, force_join))
            conn.commit()
            return True
        except: return False
        
    def update_channel(self, channel_id, name=None, link=None, force_join=None):
        try:
            conn = self.get_connection()
            updates, params = [], []
            if name: updates.append("name = ?"); params.append(name)
            if link: updates.append("link = ?"); params.append(link)
            if force_join is not None: updates.append("force_join = ?"); params.append(force_join)
            if not updates: return False
            params.append(str(channel_id))
            conn.execute(f"UPDATE channels SET {', '.join(updates)} WHERE channel_id = ?", params)
            conn.commit()
            return True
        except: return False

    def delete_channel(self, channel_id):
        try:
            conn = self.get_connection()
            conn.execute("DELETE FROM channels WHERE channel_id = ?", (str(channel_id),))
            conn.commit()
            return True
        except: return False

    def toggle_force_join(self, channel_id):
        try:
            conn = self.get_connection()
            conn.execute('UPDATE channels SET force_join = NOT force_join WHERE channel_id = ?', (str(channel_id),))
            conn.commit()
            cursor = conn.execute("SELECT force_join FROM channels WHERE channel_id = ?", (str(channel_id),))
            return cursor.fetchone()[0]
        except: return False

    # === Config, Photo & Stats ===
    def get_config(self, key, default=""):
        try:
            conn = self.get_connection()
            cursor = conn.execute("SELECT value FROM config WHERE key = ?", (key,))
            res = cursor.fetchone()
            if res:
                val = res[0]
                for k, e in Config.EMOJIS.items(): val = val.replace(f"{{{k}}}", e)
                return val
            return default
        except: return default

    def set_config(self, key, value):
        try:
            conn = self.get_connection()
            conn.execute('INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)', (key, value))
            conn.commit()
            return True
        except: return False

    def set_welcome_photo(self, photo_id):
        try:
            conn = self.get_connection()
            conn.execute('DELETE FROM welcome_photo')
            conn.execute('INSERT INTO welcome_photo (photo_id) VALUES (?)', (photo_id,))
            conn.commit()
            return True
        except: return False

    def get_welcome_photo(self):
        try:
            conn = self.get_connection()
            res = conn.execute('SELECT photo_id FROM welcome_photo ORDER BY id DESC LIMIT 1').fetchone()
            return res[0] if res else None
        except: return None
        
    def remove_welcome_photo(self):
        try:
            conn = self.get_connection()
            conn.execute('DELETE FROM welcome_photo')
            conn.commit()
            return True
        except: return False

    def get_stats(self):
        try:
            conn = self.get_connection()
            stats = {}
            stats['total_users'] = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            stats['today_users'] = conn.execute("SELECT COUNT(*) FROM users WHERE DATE(join_date) = DATE('now')").fetchone()[0]
            stats['blocked_users'] = conn.execute("SELECT COUNT(*) FROM users WHERE is_blocked = 1").fetchone()[0]
            stats['active_channels'] = conn.execute("SELECT COUNT(*) FROM channels WHERE is_active = 1").fetchone()[0]
            stats['force_channels'] = conn.execute("SELECT COUNT(*) FROM channels WHERE force_join = 1 AND is_active = 1").fetchone()[0]
            stats['total_posts'] = conn.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
            return stats
        except: return {}

    # === Post Management ===
    def save_post(self, title, photo_id, post_text, buttons, force_channels, target_channel_id, created_by, video_bot_link=""):
        try:
            conn = self.get_connection()
            video_bot_link = video_bot_link or Config.VIDEO_BOT_LINK
            cursor = conn.execute('''INSERT INTO posts (title, photo_id, post_text, buttons, force_channels, target_channel_id, created_by, video_bot_link)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (title, photo_id, post_text, json.dumps(buttons), 
                  json.dumps(force_channels), target_channel_id, created_by, video_bot_link))
            conn.commit()
            return cursor.lastrowid
        except: return None

    def get_post(self, post_id):
        try:
            conn = self.get_connection()
            cursor = conn.execute('SELECT * FROM posts WHERE post_id = ?', (post_id,))
            row = cursor.fetchone()
            if row:
                post = dict(row)
                if post.get('buttons'): post['buttons'] = json.loads(post['buttons'])
                if post.get('force_channels'): post['force_channels'] = json.loads(post['force_channels'])
                return post
            return None
        except: return None

    def grant_user_access(self, user_id, post_id):
        try:
            conn = self.get_connection()
            conn.execute('INSERT OR REPLACE INTO user_access (user_id, post_id, access_granted, access_date) VALUES (?, ?, 1, CURRENT_TIMESTAMP)', (user_id, post_id))
            conn.commit()
            return True
        except: return False

    def has_user_access(self, user_id, post_id):
        try:
            conn = self.get_connection()
            res = conn.execute('SELECT access_granted FROM user_access WHERE user_id = ? AND post_id = ?', (user_id, post_id)).fetchone()
            return res[0] == 1 if res else False
        except: return False

db = DatabaseManager()

# ==============================================================================
# 🎨 UI MANAGER
# ==============================================================================

class UIManager:
    @staticmethod
    def format_text(text: str, user=None):
        for key, emoji in Config.EMOJIS.items(): text = text.replace(f"{{{key}}}", emoji)
        if user: text = text.replace("@UserName", mention_html(user.id, user.first_name or 'User'))
        return text
    
    @staticmethod
    def create_keyboard(buttons, add_back=True, add_close=False):
        keyboard = []
        for row in buttons:
            keyboard_row = []
            for btn in row:
                if 'url' in btn: keyboard_row.append(InlineKeyboardButton(btn['text'], url=btn['url']))
                else: keyboard_row.append(InlineKeyboardButton(btn['text'], callback_data=btn['callback']))
            keyboard.append(keyboard_row)
        if add_back: keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="main_menu")])
        if add_close: keyboard.append([InlineKeyboardButton("❌ Close", callback_data="close_panel")])
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_admin_menu():
        buttons = [
            [{"text": "📝 Message Editor", "callback": "menu_messages"}, {"text": "📢 Channel Manager", "callback": "menu_channels"}],
            [{"text": "🎯 Create Post", "callback": "create_post_start"}, {"text": "🛡️ User Management", "callback": "menu_users"}],
            [{"text": "📊 Statistics", "callback": "menu_stats"}, {"text": "🖼️ Welcome Photo", "callback": "menu_welcome_photo"}]
        ]
        return UIManager.create_keyboard(buttons, add_back=False, add_close=True)
    
    @staticmethod
    def create_channel_buttons(channels, prefix="select_channel", include_edit=True):
        buttons, row = [], []
        for i, channel in enumerate(channels):
            cb = f"view_channel_{channel['channel_id']}" if include_edit else f"{prefix}_{channel['channel_id']}"
            row.append({"text": f"📢 {channel['name'][:15]}", "callback": cb})
            if len(row) == 2 or i == len(channels) - 1: buttons.append(row); row = []
        return buttons
    
    @staticmethod
    def create_channel_management_buttons(channel_id):
        buttons = [
            [{"text": "✏️ Edit Name", "callback": f"edit_channel_name_{channel_id}"}, {"text": "✏️ Edit Link", "callback": f"edit_channel_link_{channel_id}"}],
            [{"text": "✅ Toggle Force", "callback": f"toggle_channel_force_{channel_id}"}, {"text": "🗑️ Delete", "callback": f"delete_channel_{channel_id}"}],
            [{"text": "🔙 Back to Channels", "callback": "menu_channels"}]
        ]
        return UIManager.create_keyboard(buttons, add_back=False, add_close=True)

ui = UIManager()

# ==============================================================================
# 🔐 SECURITY MANAGER
# ==============================================================================

class SecurityManager:
    def __init__(self):
        self.verification_cache = {}
    
    async def check_membership(self, user_id, bot, channel_ids=None):
        cache_key = f"membership_{user_id}_{hash(str(channel_ids))}"
        if cache_key in self.verification_cache:
            cached_time, result = self.verification_cache[cache_key]
            if time.time() - cached_time < 30: return result
        
        channels = db.get_channels(active_only=True)
        if channel_ids: channels = [ch for ch in channels if str(ch['channel_id']) in map(str, channel_ids)]
        else: channels = [ch for ch in channels if ch['force_join']]
        
        joined, missing = [], []
        for channel in channels:
            try:
                member = await bot.get_chat_member(chat_id=channel['channel_id'], user_id=user_id)
                if member.status in ['left', 'kicked']: missing.append(channel)
                else: joined.append(channel)
            except: missing.append(channel)
        
        result = {'joined': joined, 'missing': missing, 'all_joined': len(missing) == 0}
        self.verification_cache[cache_key] = (time.time(), result)
        return result
    
    def clear_user_cache(self, user_id):
        for k in list(self.verification_cache.keys()):
            if k.startswith(f"membership_{user_id}_"): del self.verification_cache[k]
    
    def clear_post_cache(self, post_id):
        for k in list(self.verification_cache.keys()):
            if f"post_{post_id}" in k: del self.verification_cache[k]

security = SecurityManager()

# ==============================================================================
# 🎯 POST WIZARD
# ==============================================================================

class EnhancedPostWizard:
    def __init__(self):
        self.active_wizards = {}
    
    async def start_wizard(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        self.active_wizards[query.from_user.id] = {
            'step': 'title', 'data': {'buttons': [], 'force_channels': [], 'video_bot_link': Config.VIDEO_BOT_LINK}
        }
        await query.answer()
        await query.edit_message_text(ui.format_text("📝 <b>Step 1/7:</b> Send <b>POST TITLE</b>:", query.from_user), parse_mode=ParseMode.HTML)
        return Config.STATE_POST_TITLE
    
    async def handle_title(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.active_wizards[update.effective_user.id]['data']['title'] = update.message.text
        await update.message.reply_text("📸 <b>Step 2/7:</b> Send <b>PHOTO</b> (or /skip):", parse_mode=ParseMode.HTML)
        return Config.STATE_POST_PHOTO
    
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        uid = update.effective_user.id
        if update.message.text == '/skip': self.active_wizards[uid]['data']['photo_id'] = ""
        elif update.message.photo: self.active_wizards[uid]['data']['photo_id'] = update.message.photo[-1].file_id
        else: await update.message.reply_text("❌ Send photo or /skip!"); return Config.STATE_POST_PHOTO
        await update.message.reply_text("📝 <b>Step 3/7:</b> Send <b>POST TEXT</b> (or /skip):", parse_mode=ParseMode.HTML)
        return Config.STATE_POST_TEXT
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        txt = update.message.text
        self.active_wizards[update.effective_user.id]['data']['post_text'] = "" if txt == '/skip' else txt
        await update.message.reply_text(f"🤖 <b>Step 4/7:</b> Video Bot Link\nDefault: {Config.VIDEO_BOT_USERNAME}\nSend new link or /skip:", parse_mode=ParseMode.HTML)
        return Config.STATE_POST_WATCH_URL
    
    async def handle_video_bot_link(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        uid = update.effective_user.id
        if update.message.text != '/skip': self.active_wizards[uid]['data']['video_bot_link'] = update.message.text
        return await self.show_button_menu(update, context, update.effective_user)

    async def show_button_menu(self, update, context, user):
        btns = self.active_wizards[user.id]['data']['buttons']
        preview = "\n".join([f"{i+1}. {b['name']}" for i, b in enumerate(btns)]) if btns else "No buttons."
        kb = ui.create_keyboard({"text": "➕ Add Button", "callback": "add_button"}], [{"text": "➡️ Continue", "callback": "continue_buttons"}, True, True)
        msg = f"🔘 <b>Step 5/7: Buttons</b>\n\n{preview}\n\nAdd button or Continue:"
        if update.callback_query: await update.callback_query.edit_message_text(msg, reply_markup=kb, parse_mode=ParseMode.HTML)
        else: await update.message.reply_text(msg, reply_markup=kb, parse_mode=ParseMode.HTML)
        return Config.STATE_POST_BUTTONS
    
    async def handle_button_management(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        user = query.from_user
        if query.data == "add_button":
            await query.edit_message_text("✏️ Send <b>BUTTON NAME</b>:", parse_mode=ParseMode.HTML)
            return Config.STATE_POST_BUTTON_NAME
        elif query.data == "continue_buttons":
            await self.handle_force_channel_selection(update, context, True)
            return Config.STATE_POST_FORCE_CHANNELS
        return Config.STATE_POST_BUTTONS
    
    async def handle_button_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data['temp_btn'] = update.message.text
        await update.message.reply_text("🌐 Send <b>BUTTON LINK</b>:", parse_mode=ParseMode.HTML)
        return Config.STATE_POST_BUTTON_LINK

    async def handle_button_link(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.active_wizards[update.effective_user.id]['data']['buttons'].append({'name': context.user_data['temp_btn'], 'link': update.message.text})
        return await self.show_button_menu(update, context, update.effective_user)

    async def handle_force_channel_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, init=False):
        query = update.callback_query
        user = query.from_user
        if init:
            chans = db.get_channels(force_only=True)
            if not chans: return await self.handle_target_channel_selection(update, context, True)
            self.active_wizards[user.id]['data']['force_channels'] = []
        
        data = query.data
        if data == "select_all_force":
            self.active_wizards[user.id]['data']['force_channels'] = [c['channel_id'] for c in db.get_channels(force_only=True)]
            await query.answer("✅ All Selected")
        elif data.startswith("select_force_"):
            cid = data.replace("select_force_", "")
            lst = self.active_wizards[user.id]['data']['force_channels']
            if cid in lst: lst.remove(cid)
            else: lst.append(cid)
            await query.answer()
        elif data == "continue_force":
            return await self.handle_target_channel_selection(update, context, True)

        force_channels = db.get_channels(force_only=True)
        btns = []
        row = []
        for i, ch in enumerate(force_channels):
            mark = "✅" if ch['channel_id'] in self.active_wizards[user.id]['data']['force_channels'] else "📢"
            row.append({"text": f"{mark} {ch['name'][:10]}", "callback": f"select_force_{ch['channel_id']}"})
            if len(row) == 2 or i == len(force_channels) - 1: btns.append(row); row = []
        btns.append([{"text": "✅ Select All", "callback": "select_all_force"}, {"text": "➡️ Continue", "callback": "continue_force"}])
        
        msg = "🎯 <b>Step 6/7: Force Channels</b>\nSelect channels users MUST join:"
        if init: await query.edit_message_text(msg, reply_markup=ui.create_keyboard(btns, True), parse_mode=ParseMode.HTML)
        else: await query.edit_message_reply_markup(ui.create_keyboard(btns, True))
        return Config.STATE_POST_FORCE_CHANNELS

    async def handle_target_channel_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, init=False):
        query = update.callback_query
        if init:
            btns = ui.create_channel_buttons(db.get_channels(), "select_target", False)
            await query.edit_message_text("📤 <b>Step 7/7: Select TARGET CHANNEL</b>:", reply_markup=ui.create_keyboard(btns, True), parse_mode=ParseMode.HTML)
            return Config.STATE_POST_TARGET_CHANNEL
        
        if query.data.startswith("select_target_"):
            cid = query.data.replace("select_target_", "")
            self.active_wizards[query.from_user.id]['data']['target_channel_id'] = cid
            return await self.show_preview(update, context)
        return Config.STATE_POST_TARGET_CHANNEL
    
    async def show_preview(self, update, context):
        data = self.active_wizards[update.callback_query.from_user.id]['data']
        txt = f"🎯 <b>CONFIRM POST</b>\n\n<b>Title:</b> {data['title']}\n<b>Buttons:</b> {len(data['buttons'])}\n"
        kb = ui.create_keyboard({"text": "🚀 Post Now", "callback": "final_post"}], [{"text": "🔙 Edit", "callback": "edit_post"}, True)
        if data.get('photo_id'): await context.bot.send_photo(update.callback_query.from_user.id, data['photo_id'], caption=txt, reply_markup=kb, parse_mode=ParseMode.HTML)
        else: await update.callback_query.edit_message_text(txt, reply_markup=kb, parse_mode=ParseMode.HTML)
        return Config.STATE_POST_CONFIRM

    async def finalize_post(self, update, context):
        query = update.callback_query
        data = self.active_wizards[query.from_user.id]['data']
        pid = db.save_post(data['title'], data.get('photo_id'), data.get('post_text'), data['buttons'], data['force_channels'], data['target_channel_id'], query.from_user.id, data.get('video_bot_link'))
        
        kb = InlineKeyboardMarkup(InlineKeyboardButton(Config.VERIFICATION_MESSAGES['verify_button_text'], callback_data=f"verify_post_{pid}"))
        caption = f"<b>{data['title']}</b>\n\n{data.get('post_text','')}\n\n🔒 <i>Locked Content</i>"
        
        try:
            if data.get('photo_id'): await context.bot.send_photo(data['target_channel_id'], data['photo_id'], caption=caption, reply_markup=kb, parse_mode=ParseMode.HTML)
            else: await context.bot.send_message(data['target_channel_id'], caption, reply_markup=kb, parse_mode=ParseMode.HTML)
            await query.edit_message_text(f"✅ <b>Posted! ID: {pid}</b>", parse_mode=ParseMode.HTML)
        except Exception as e: await query.edit_message_text(f"❌ Error: {e}")
        return ConversationHandler.END

post_wizard = EnhancedPostWizard()

# ==============================================================================
# 🎮 COMMAND HANDLERS
# ==============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.add_user(user.id, user.username, user.first_name, user.last_name)
    
    welcome_photo = db.get_welcome_photo()
    result = await security.check_membership(user.id, context.bot)
    
    if not result['all_joined']:
        btns = {"text": f"📢 Join {c['name']}", "url": c['link']}] for c in result['missing'
        btns.append([{"text": "✅ Verify Membership", "callback": "verify_membership"}])
        msg_text = ui.format_text(db.get_config('lock_message'), user)
        if welcome_photo: await update.message.reply_photo(welcome_photo, caption=msg_text, reply_markup=ui.create_keyboard(btns, False), parse_mode=ParseMode.HTML)
        else: await update.message.reply_text(msg_text, reply_markup=ui.create_keyboard(btns, False), parse_mode=ParseMode.HTML)
    else:
        await send_welcome(update, user, welcome_photo)

async def send_welcome(update, user, welcome_photo=None):
    kb = InlineKeyboardMarkup(InlineKeyboardButton("🎬 Download Videos Now", url=db.get_config('video_bot_link', Config.VIDEO_BOT_LINK)))
    text = ui.format_text(db.get_config('welcome_message'), user)
    try:
        if welcome_photo: msg = await update.message.reply_photo(welcome_photo, caption=text, reply_markup=kb, parse_mode=ParseMode.HTML)
        else: msg = await update.message.reply_text(text, reply_markup=kb, parse_mode=ParseMode.HTML)
        asyncio.create_task(delete_later(msg, int(db.get_config('auto_delete', 60))))
    except: pass

async def delete_later(msg, delay):
    await asyncio.sleep(delay)
    try: await msg.delete()
    except: pass

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id in Config.ADMIN_IDS:
        await update.message.reply_text("👑 <b>Admin Panel</b>", reply_markup=ui.get_admin_menu(), parse_mode=ParseMode.HTML)

# ==============================================================================
# 🔄 FIXED CALLBACK HANDLER (POPUP ISSUE SOLVED)
# ==============================================================================

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    data = query.data
    
    # NOTE: Removed the global await query.answer() from here to fix popup issue
    
    db.update_user_activity(user.id)
    
    if data == "verify_membership":
        security.clear_user_cache(user.id)
        result = await security.check_membership(user.id, context.bot)
        
        if result['all_joined']:
            await query.answer(Config.VERIFICATION_MESSAGES['joined_popup'], show_alert=True)
            try: await query.message.delete()
            except: pass
            await send_welcome(query, user, db.get_welcome_photo())
        else:
            await query.answer(Config.VERIFICATION_MESSAGES['not_joined_popup'], show_alert=True)
            
    elif data.startswith("verify_post_"):
        await handle_post_verification(update, context, int(data.replace("verify_post_", "")))
        
    elif data.startswith("watch_now_"):
        await handle_watch_now(update, context, int(data.replace("watch_now_", "")))
        
    else:
        # Standard Menu Handlers (Non-Popup) - We answer here to stop loading animation
        try: await query.answer()
        except: pass
        
        if data == "main_menu":
            if user.id in Config.ADMIN_IDS: await query.edit_message_text("👑 <b>Admin Panel</b>", reply_markup=ui.get_admin_menu(), parse_mode=ParseMode.HTML)
            
        elif data == "close_panel":
            try: await query.message.delete()
            except: pass
            
        elif data == "menu_channels":
            chans = db.get_channels()
            btns = ui.create_channel_buttons(chans, include_edit=True)
            btns.append([{"text": "➕ Add Channel", "callback": "add_channel"}])
            btns.append([{"text": "🔙 Back", "callback": "main_menu"}])
            await query.edit_message_text(f"📢 <b>Channels: {len(chans)}</b>", reply_markup=ui.create_keyboard(btns, False, True), parse_mode=ParseMode.HTML)

        elif data.startswith("view_channel_"):
            ch = db.get_channel(data.replace("view_channel_", ""))
            if ch: await query.edit_message_text(f"📢 <b>{ch['name']}</b>\nForce: {ch['force_join']}", reply_markup=ui.create_channel_management_buttons(ch['channel_id']), parse_mode=ParseMode.HTML)

        elif data.startswith("toggle_channel_force_"):
            db.toggle_force_join(data.replace("toggle_channel_force_", ""))
            # Refresh view
            ch = db.get_channel(data.replace("toggle_channel_force_", ""))
            if ch: await query.edit_message_text(f"📢 <b>{ch['name']}</b>\nForce: {ch['force_join']}", reply_markup=ui.create_channel_management_buttons(ch['channel_id']), parse_mode=ParseMode.HTML)
            
        elif data.startswith("delete_channel_"):
            db.delete_channel(data.replace("delete_channel_", ""))
            await callback_handler(update, context) # Refresh list

        elif data == "add_channel":
            await query.message.reply_text("➕ Send Channel ID:")
            return Config.STATE_CHANNEL_ADD_ID
            
        elif data == "create_post_start":
            return await post_wizard.start_wizard(update, context)
            
        elif data == "menu_messages":
            btns = {"text": "✏️ Welcome Msg", "callback": "edit_welcome_message"}, {"text": "✏️ Lock Msg", "callback": "edit_lock_message"}
            await query.edit_message_text("📝 Select Message:", reply_markup=ui.create_keyboard(btns), parse_mode=ParseMode.HTML)
            
        elif data.startswith("edit_"):
            context.user_data['edit_key'] = data.replace("edit_", "")
            await query.message.reply_text(f"✏️ Send new text for {context.user_data['edit_key']}:")
            return Config.STATE_EDIT_MESSAGE
            
        # Post Wizard Callbacks
        elif data.startswith("select_force_") or data == "select_all_force" or data == "continue_force":
            return await post_wizard.handle_force_channel_selection(update, context)
        elif data.startswith("select_target_"):
            return await post_wizard.handle_target_channel_selection(update, context)
        elif data == "final_post":
            return await post_wizard.finalize_post(update, context)
        elif data == "edit_post":
            # Restart wizard from step 1
            post_wizard.active_wizards[user.id]['step'] = 'title'
            await query.edit_message_text("📝 <b>Step 1/7:</b> Send <b>POST TITLE</b>:", parse_mode=ParseMode.HTML)
            return Config.STATE_POST_TITLE

# ==============================================================================
# 🔐 VERIFICATION LOGIC
# ==============================================================================

async def handle_post_verification(update, context, post_id):
    query = update.callback_query
    if db.has_user_access(query.from_user.id, post_id):
        await show_watch_button(query, post_id)
        return

    post = db.get_post(post_id)
    if not post: return
    
    force_channels = post.get('force_channels', [])
    if force_channels:
        res = await security.check_membership(query.from_user.id, context.bot, force_channels)
        if not res['all_joined']:
            await query.answer(Config.VERIFICATION_MESSAGES['not_joined_popup'], show_alert=True)
            btns = InlineKeyboardButton(f"📢 Join {c['name']}", url=c['link'])] for c in res['missing'
            btns.append([InlineKeyboardButton("✅ Verify Again", callback_data=f"verify_post_{post_id}")])
            try: await query.edit_message_reply_markup(InlineKeyboardMarkup(btns))
            except: pass
            return
        else:
            await query.answer(Config.VERIFICATION_MESSAGES['joined_popup'], show_alert=True)

    db.grant_user_access(query.from_user.id, post_id)
    await show_watch_button(query, post_id)

async def show_watch_button(query, post_id):
    try: await query.edit_message_reply_markup(InlineKeyboardMarkup(InlineKeyboardButton(Config.VERIFICATION_MESSAGES['watch_button_text'], callback_data=f"watch_now_{post_id}")))
    except: pass

async def handle_watch_now(update, context, post_id):
    query = update.callback_query
    if not db.has_user_access(query.from_user.id, post_id):
        await query.answer("❌ Verify first!", show_alert=True)
        return

    post = db.get_post(post_id)
    vid_link = post.get('video_bot_link', Config.VIDEO_BOT_LINK)
    
    btns = [[InlineKeyboardButton(b['name'], url=b['link'])] for b in post.get('buttons', [])]
    btns.append([InlineKeyboardButton("🎬 Download Video", url=vid_link)])
    
    await query.answer(Config.VERIFICATION_MESSAGES['access_granted'], show_alert=True)
    
    txt = f"<b>{post['title']}</b>\n\n{post.get('post_text', '')}\n\n✅ <i>Access Granted!</i>"
    try:
        if post.get('photo_id'): await context.bot.send_photo(query.from_user.id, post['photo_id'], caption=txt, reply_markup=InlineKeyboardMarkup(btns), parse_mode=ParseMode.HTML)
        else: await context.bot.send_message(query.from_user.id, txt, reply_markup=InlineKeyboardMarkup(btns), parse_mode=ParseMode.HTML)
    except: await query.answer("❌ Error sending content (Bot blocked?)", show_alert=True)

# ==============================================================================
# ✏️ SIMPLE HANDLERS
# ==============================================================================

async def edit_config_handler(update, context):
    if db.set_config(context.user_data['edit_key'], update.message.text): await update.message.reply_text("✅ Updated!")
    return ConversationHandler.END

async def add_channel_steps(update, context):
    state = context.user_data.get('add_ch_state', 0)
    if not state: 
        context.user_data['cid'] = update.message.text
        context.user_data['add_ch_state'] = 1
        await update.message.reply_text("📝 Send Name:")
        return Config.STATE_CHANNEL_ADD_NAME
    elif state == 1:
        context.user_data['cname'] = update.message.text
        context.user_data['add_ch_state'] = 2
        await update.message.reply_text("🔗 Send Link:")
        return Config.STATE_CHANNEL_ADD_LINK
    elif state == 2:
        db.add_channel(context.user_data['cid'], context.user_data['cname'], update.message.text)
        await update.message.reply_text("✅ Channel Added!")
        context.user_data.pop('add_ch_state', None)
        return ConversationHandler.END

async def cancel_op(update, context):
    await update.message.reply_text("❌ Cancelled.")
    return ConversationHandler.END

# ==============================================================================
# 🚀 MAIN
# ==============================================================================

def main():
    print("🤖 Bot Starting...")
    app = ApplicationBuilder().token(Config.TOKEN).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("admin", admin_command))
    
    # Conversations
    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(callback_handler, pattern='^create_post_start$')],
        states={
            Config.STATE_POST_TITLE: [MessageHandler(filters.TEXT, post_wizard.handle_title)],
            Config.STATE_POST_PHOTO: [MessageHandler(filters.PHOTO | filters.TEXT, post_wizard.handle_photo)],
            Config.STATE_POST_TEXT: [MessageHandler(filters.TEXT, post_wizard.handle_text)],
            Config.STATE_POST_WATCH_URL: [MessageHandler(filters.TEXT, post_wizard.handle_video_bot_link)],
            Config.STATE_POST_BUTTONS: [CallbackQueryHandler(post_wizard.handle_button_management)],
            Config.STATE_POST_BUTTON_NAME: [MessageHandler(filters.TEXT, post_wizard.handle_button_name)],
            Config.STATE_POST_BUTTON_LINK: [MessageHandler(filters.TEXT, post_wizard.handle_button_link)],
            Config.STATE_POST_FORCE_CHANNELS: [CallbackQueryHandler(callback_handler, pattern='^(select_force_|select_all_force|continue_force)')],
            Config.STATE_POST_TARGET_CHANNEL: [CallbackQueryHandler(callback_handler, pattern='^select_target_')],
            Config.STATE_POST_CONFIRM: [CallbackQueryHandler(callback_handler, pattern='^(final_post|edit_post)')]
        },
        fallbacks=[CommandHandler('cancel', cancel_op)]
    ))

    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(callback_handler, pattern='^add_channel$')],
        states={
            Config.STATE_CHANNEL_ADD_ID: [MessageHandler(filters.TEXT, add_channel_steps)],
            Config.STATE_CHANNEL_ADD_NAME: [MessageHandler(filters.TEXT, add_channel_steps)],
            Config.STATE_CHANNEL_ADD_LINK: [MessageHandler(filters.TEXT, add_channel_steps)]
        }, fallbacks=[CommandHandler('cancel', cancel_op)]
    ))
    
    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(callback_handler, pattern='^edit_')],
        states={Config.STATE_EDIT_MESSAGE: [MessageHandler(filters.TEXT, edit_config_handler)]},
        fallbacks=[CommandHandler('cancel', cancel_op)]
    ))

    app.add_handler(CallbackQueryHandler(callback_handler))
    
    print("✅ Polling...")
    app.run_polling()

if __name__ == "__main__":
    main()
