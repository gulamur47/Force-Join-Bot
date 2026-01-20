"""
================================================================================
SUPREME GOD MODE BOT - ULTIMATE EDITION (FULL & FIXED)
VERSION: v10.5 (Final Fixed & Enhanced)
AUTHOR: AI ASSISTANT
DATE: January 20, 2026
================================================================================
"""

import os
import sys
import time
import json
import sqlite3
import logging
import threading
import psutil
import asyncio
import datetime
import hashlib
import secrets
import string
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import List, Dict, Union, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import traceback
import pickle
import base64
from contextlib import contextmanager
from collections import defaultdict, deque

# Telegram imports
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    InputMediaPhoto, InputMediaVideo, BotCommand
)
from telegram.constants import ParseMode
from telegram.helpers import mention_html
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, ConversationHandler, MessageHandler,
    filters, ApplicationBuilder, CallbackContext
)

# ==============================================================================
# ⚙️ CONFIGURATION CONSTANTS
# ==============================================================================

class Config:
    # Bot Configuration
    TOKEN = "8456027249:AAEqg2j7jhJDSl4R0dnVCqaCvYBJQeG8NM4"
    ADMIN_IDS = {6406804999}
    DB_NAME = "supreme_bot_v10.db"
    BACKUP_DIR = "backups"
    LOG_FILE = "bot_activity.log"
    
    # System Constants
    DEFAULT_AUTO_DELETE = 60  # Fixed to 60 Seconds
    MAX_MESSAGE_LENGTH = 4000
    FLOOD_LIMIT = 3
    SESSION_TIMEOUT = 300
    
    # Channel Settings
    DEFAULT_CHANNELS = [
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
    
    # Emoji Pack
    EMOJIS = {
        "heart": "❤️", "star": "⭐", "fire": "🔥", "lock": "🔒", "unlock": "🔓",
        "gear": "⚙️", "bell": "🔔", "chart": "📊", "users": "👥", "admin": "👑",
        "camera": "📸", "video": "🎬", "link": "🔗", "time": "⏰", "check": "✅",
        "cross": "❌", "warn": "⚠️", "info": "ℹ️", "tada": "🎉"
    }
    
    # Conversation States (ALL STATES INCLUDED)
    STATE_EDIT_CONFIG = 1
    STATE_POST_CAPTION = 2
    STATE_POST_MEDIA = 3
    STATE_POST_BUTTON = 4
    STATE_POST_CONFIRM = 5
    STATE_BROADCAST = 6
    STATE_CHANNEL_ADD_ID = 7
    STATE_CHANNEL_ADD_NAME = 8
    STATE_CHANNEL_ADD_LINK = 9
    STATE_USER_BLOCK = 10
    STATE_VIP_ADD = 11
    STATE_BACKUP_RESTORE = 12

    # 🔥 NEW Enhanced Post Wizard States
    STATE_EP_TITLE = 20
    STATE_EP_MEDIA = 21
    STATE_EP_BTN_NAME = 22
    STATE_EP_BTN_LINK = 23
    STATE_EP_ADD_MORE = 24
    STATE_EP_FORCE_CHANNELS = 25
    STATE_EP_TARGET = 26

    # 🔥 Bangla Hot Messages
    MSG_SUCCESS = """<b>💖🔥 Heyyy {mention} 😘💋</b>

🌹✨ অবশেষে তুমি এসে গেছো, আমার মিষ্টি Love 😍
💯💎 সব Force Channel Join সম্পন্ন! এখন তোমার জন্য সব দরজা খুলে গেছে 😈🔥

💋 নিচে Button গুলোতে ক্লিক করো আর মজা নাও 💕💎

🌹🔥 <b>Stay Hot • Stay Wild • Stay With Us 💋💋</b>"""

    MSG_FAIL = """<b>😘🔥 Ohhh {mention} 💔💋</b>

💞✨ তুমি এখনো সব Channel Join করোনি 😢🔥

💋 আগে সব Channel Join করো, তারপর <b>Verify Button</b> চাপো 💎💋
🔥 তখনই Full Premium • Hot • Exclusive Content দেখতে পারবে 😈🔥"""

# ==============================================================================
# 📝 LOGGING SYSTEM
# ==============================================================================

class SupremeLogger:
    def __init__(self):
        self.logger = logging.getLogger("SupremeBot")
        self.setup_logging()
        
    def setup_logging(self):
        console_handler = logging.StreamHandler(sys.stdout)
        file_handler = logging.FileHandler(Config.LOG_FILE, encoding='utf-8')
        
        console_handler.setLevel(logging.INFO)
        file_handler.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.DEBUG)
        self.logger.info("SUPREME GOD BOT STARTING...")
    
    def get_logger(self):
        return self.logger

logger_instance = SupremeLogger()
logger = logger_instance.get_logger()

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
        self.backup_dir = Config.BACKUP_DIR
        os.makedirs(self.backup_dir, exist_ok=True)
        self.connection_pool = {}
        self.init_database()
        self._initialized = True
        
    def get_connection(self, thread_id=None):
        if thread_id is None: thread_id = threading.get_ident()
        with self._lock:
            if thread_id not in self.connection_pool:
                conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=30)
                conn.row_factory = sqlite3.Row
                self.connection_pool[thread_id] = conn
            return self.connection_pool[thread_id]
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Original Tables
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT, 
            last_name TEXT, join_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_active DATETIME DEFAULT CURRENT_TIMESTAMP,
            message_count INTEGER DEFAULT 0, is_vip BOOLEAN DEFAULT 0,
            is_blocked BOOLEAN DEFAULT 0, metadata TEXT DEFAULT '{}'
        )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY, value TEXT NOT NULL, encrypted BOOLEAN DEFAULT 0,
            category TEXT DEFAULT 'general', description TEXT, updated_at DATETIME
        )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS channels (
            channel_id TEXT PRIMARY KEY, name TEXT NOT NULL, link TEXT NOT NULL,
            is_private BOOLEAN DEFAULT 0, force_join BOOLEAN DEFAULT 1,
            added_date DATETIME DEFAULT CURRENT_TIMESTAMP, status TEXT DEFAULT 'active'
        )''')
        
        # New: Enhanced Posts Table
        cursor.execute('''CREATE TABLE IF NOT EXISTS enhanced_posts (
            post_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            media_id TEXT,
            media_type TEXT,
            buttons TEXT,          -- JSON list of buttons
            force_channels TEXT,   -- JSON list of required channel IDs
            created_by INTEGER,
            created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            view_count INTEGER DEFAULT 0
        )''')
        
        # Helper Tables
        cursor.execute('''CREATE TABLE IF NOT EXISTS vip_users (
            vip_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER UNIQUE,
            level INTEGER DEFAULT 1, perks TEXT, expires_at DATETIME
        )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS activity_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
            action TEXT, details TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS flood_control (
            user_id INTEGER PRIMARY KEY, message_count INTEGER DEFAULT 0,
            last_message DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Session table
        cursor.execute('''CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY, user_id INTEGER, data TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP, expires_at DATETIME
        )''')
        
        conn.commit()
        self.initialize_defaults()
    
    def initialize_defaults(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        defaults = [
            ('welcome_msg', '''{heart} {star} <b>💖✨ওগো শুনছো! স্বাগতম জানাই তোমাকে!💖✨</b> {star} {heart}

{fire} <b>❤️তুমি অবশেষে আমাদের মাঝে এসেছো, আমার হৃদয়টা আনন্দে নেচে উঠলো! 😍💃
তোমাকে ছাড়া আমাদের এই আয়োজন অসম্পূর্ণ ছিল।</b>

{tada} <b>💖✨তোমার জন্য যা যা থাকছে::</b>
🎀 এক্সক্লুসিভ ভাইরাল ভিডিও 🔞
🎀 নতুন সব কালেকশন 🔥
🎀 এবং আমার হৃদয়ের ভালোবাসা... ❤️

{link} <b>নিচের বাটনে ক্লিক করে শুরু করুন:</b>'''),
            
            ('lock_msg', '''{lock} <b>অ্যাক্সেস লক করা আছে!</b>

{cross} 😢💔ওহ নো বেবি! তুমি এখনো জয়েন করোনি? আমার লক্ষ্মীটা, তুমি যদি নিচের চ্যানেলগুলোতে জয়েন না করো, তাহলে আমি তোমাকে ভিডিওটা দেখাতে পারবো না! 🥺🥀
প্লিজ সোনা, রাগ করো না!

{info} নিচের সবগুলোতে জয়েন করে💖✨ {check} ভেরিফাই বাটনে ক্লিক করুন। আমি অপেক্ষা করছি... 😘❤️'''),
            
            ('welcome_photo', 'https://images.unsplash.com/photo-1618005198919-d3d4b5a92ead'),
            ('watch_url', 'https://mmshotbd.blogspot.com/?m=1'),
            ('btn_text', '{video} 🎬🎉ভিডিও দেখুন এখনই! {fire}'),
            ('auto_delete', '60'),
            ('maint_mode', 'OFF'),
            ('force_join', 'ON')
        ]
        
        for k, v in defaults:
            cursor.execute('INSERT OR IGNORE INTO config (key, value) VALUES (?, ?)', (k, v))
            
        cursor.execute("SELECT COUNT(*) FROM channels")
        if cursor.fetchone()[0] == 0:
            for channel in Config.DEFAULT_CHANNELS:
                cursor.execute('INSERT OR IGNORE INTO channels (channel_id, name, link) VALUES (?, ?, ?)',
                             (str(channel["id"]), channel["name"], channel["link"]))
        conn.commit()

    # === Enhanced Post Methods ===
    def save_enhanced_post(self, title, media_id, media_type, buttons, force_channels, created_by):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO enhanced_posts (title, media_id, media_type, buttons, force_channels, created_by)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (title, media_id, media_type, json.dumps(buttons), json.dumps(force_channels), created_by))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error saving post: {e}")
            return None

    def get_enhanced_post(self, post_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM enhanced_posts WHERE post_id = ?', (post_id,))
        row = cursor.fetchone()
        if row:
            d = dict(row)
            d['buttons'] = json.loads(d['buttons']) if d['buttons'] else []
            d['force_channels'] = json.loads(d['force_channels']) if d['force_channels'] else []
            return d
        return None

    def increment_post_views(self, post_id):
        conn = self.get_connection()
        conn.execute("UPDATE enhanced_posts SET view_count = view_count + 1 WHERE post_id = ?", (post_id,))
        conn.commit()

    # === User & Channel Management ===
    def add_user(self, user_id, username, first_name, last_name=""):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (user_id, username, first_name, last_name, last_active)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET last_active=CURRENT_TIMESTAMP, username=excluded.username
        ''', (user_id, username, first_name, last_name))
        conn.commit()
    
    def get_all_users(self, active_only=True):
        conn = self.get_connection()
        cursor = conn.cursor()
        sql = "SELECT user_id FROM users WHERE is_blocked=0" if active_only else "SELECT user_id FROM users"
        cursor.execute(sql)
        return [row[0] for row in cursor.fetchall()]

    def get_channels(self, active_only=True, force_join_only=False):
        conn = self.get_connection()
        cursor = conn.cursor()
        if force_join_only and active_only:
            sql = "SELECT * FROM channels WHERE status='active' AND force_join=1"
        elif active_only:
            sql = "SELECT * FROM channels WHERE status='active'"
        else:
            sql = "SELECT * FROM channels"
        cursor.execute(sql)
        return [dict(row) for row in cursor.fetchall()]

    def add_channel(self, channel_id, name, link, is_private=False, force_join=True):
        conn = self.get_connection()
        try:
            conn.execute('''INSERT OR REPLACE INTO channels (channel_id, name, link, is_private, force_join) 
                         VALUES (?, ?, ?, ?, ?)''', (channel_id, name, link, is_private, force_join))
            conn.commit()
            return True
        except: return False

    def remove_channel(self, channel_id):
        conn = self.get_connection()
        conn.execute("UPDATE channels SET status='inactive' WHERE channel_id=?", (channel_id,))
        conn.commit()
        return True

    def get_config(self, key, default=""):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM config WHERE key=?", (key,))
        res = cursor.fetchone()
        
        if res:
            value = res[0]
            for emoji_key, emoji in Config.EMOJIS.items():
                value = value.replace(f"{{{emoji_key}}}", emoji)
            return value
        return default

    def set_config(self, key, value):
        conn = self.get_connection()
        conn.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", (key, value))
        conn.commit()
        return True
    
    # === VIP & Block ===
    def block_user(self, user_id, admin_id, reason=""):
        conn = self.get_connection()
        conn.execute("UPDATE users SET is_blocked = 1 WHERE user_id = ?", (user_id,))
        conn.commit()
        return True

    def add_vip(self, user_id):
        conn = self.get_connection()
        conn.execute("UPDATE users SET is_vip = 1 WHERE user_id = ?", (user_id,))
        conn.commit()
        return True
        
    def is_vip(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT is_vip FROM users WHERE user_id=?", (user_id,))
        res = cursor.fetchone()
        return res and res[0]

    def get_stats(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        stats = {}
        cursor.execute("SELECT COUNT(*) FROM users")
        stats['total_users'] = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM channels WHERE status='active'")
        stats['active_channels'] = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM enhanced_posts")
        stats['enhanced_posts'] = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_vip=1")
        stats['vip_users'] = cursor.fetchone()[0]
        return stats

    def create_backup(self):
        backup_file = os.path.join(self.backup_dir, f"backup_{int(time.time())}.db")
        try:
            with self.get_connection() as source:
                backup = sqlite3.connect(backup_file)
                source.backup(backup)
                backup.close()
            return backup_file
        except: return None
        
    def check_flood(self, user_id): return False 
    
    def cleanup_sessions(self):
        conn = self.get_connection()
        conn.execute("DELETE FROM sessions WHERE expires_at <= CURRENT_TIMESTAMP")
        conn.commit()
    
    def get_user(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        columns = [desc[0] for desc in cursor.description]
        row = cursor.fetchone()
        if row: return dict(zip(columns, row))
        return None

db = DatabaseManager()

# ==============================================================================
# 🔧 SYSTEM MONITOR
# ==============================================================================

class SystemMonitor:
    def __init__(self):
        self.start_time = time.time()
        self.message_count = 0
        
    def get_system_stats(self):
        return {
            'uptime': str(datetime.timedelta(seconds=int(time.time() - self.start_time))),
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'message_count': self.message_count
        }
    
    def increment_message(self): self.message_count += 1
    def update_user_activity(self, uid): pass
    def increment_error(self): pass

system_monitor = SystemMonitor()

# ==============================================================================
# 🌐 HEALTH SERVER
# ==============================================================================

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Supreme Bot Online")

def run_health_server():
    try:
        port = int(os.environ.get('PORT', 8080))
        server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
        server.serve_forever()
    except: pass

threading.Thread(target=run_health_server, daemon=True).start()

# ==============================================================================
# 🎨 UI MANAGER
# ==============================================================================

class UIManager:
    @staticmethod
    def format_text(text: str, user=None, emojis=True):
        if emojis:
            for k, v in Config.EMOJIS.items():
                text = text.replace(f"{{{k}}}", v)
        if user:
            text = text.replace("{mention}", mention_html(user.id, user.first_name))
        return text
    
    @staticmethod
    def create_keyboard(buttons, add_back=False, add_close=False):
        kb = []
        for row in buttons:
            r = []
            for btn in row:
                r.append(InlineKeyboardButton(text=btn['text'], callback_data=btn.get('callback'), url=btn.get('url')))
            kb.append(r)
        if add_back: kb.append([InlineKeyboardButton("🔙 Back", callback_data="main_menu")])
        if add_close: kb.append([InlineKeyboardButton("❌ Close", callback_data="close_panel")])
        return InlineKeyboardMarkup(kb)
    
    @staticmethod
    def get_admin_menu():
        buttons = [
            [{"text": "🚀 Create Post", "callback": "enhanced_post_start"}],
            [{"text": "📢 Channels", "callback": "menu_channels"}, {"text": "📊 Stats", "callback": "menu_stats"}],
            [{"text": "📣 Broadcast", "callback": "broadcast_start"}, {"text": "👑 VIP", "callback": "menu_vip"}],
            [{"text": "💾 Backup", "callback": "backup_now"}, {"text": "🛡️ Security", "callback": "menu_security"}]
        ]
        return UIManager.create_keyboard(buttons, add_close=True)
        
    @staticmethod
    def get_stats_display(stats):
        return f"""
📊 <b>Stats</b>
Users: {stats['total_users']}
Channels: {stats['active_channels']}
Posts: {stats['enhanced_posts']}
"""

ui = UIManager()

# ==============================================================================
# 🔐 SECURITY MANAGER
# ==============================================================================

class SecurityManager:
    async def check_membership(self, user_id, bot, force_channels=None):
        missing_channels = []
        
        if force_channels:
            all_channels = db.get_channels()
            channels_to_check = [c for c in all_channels if c['id'] in force_channels]
        else:
            channels_to_check = db.get_channels(active_only=True, force_join_only=True)
        
        for channel in channels_to_check:
            try:
                member = await bot.get_chat_member(chat_id=channel['id'], user_id=user_id)
                if member.status in ['left', 'kicked']:
                    missing_channels.append(channel)
            except Exception:
                missing_channels.append(channel)
        
        return missing_channels

    def check_flood(self, user_id): return False
    def check_maintenance(self, user_id): return False

security = SecurityManager()

# ==============================================================================
# 🎯 ENHANCED POST WIZARD (STEP-BY-STEP & FIXED)
# ==============================================================================

class EnhancedPostWizard:
    def __init__(self):
        self.active_wizards = {}
    
    async def start_wizard(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Step 1: Title"""
        user = update.effective_user
        self.active_wizards[user.id] = {'data': {'buttons': []}}
        
        await update.callback_query.answer()
        await update.callback_query.message.reply_text(
            "📝 <b>Create Post - Step 1/6</b>\n\n✏️ Send the <b>Post Title</b>:",
            parse_mode=ParseMode.HTML
        )
        return Config.STATE_EP_TITLE
    
    async def handle_title(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Step 2: Media"""
        user = update.effective_user
        if user.id not in self.active_wizards: return ConversationHandler.END
        
        self.active_wizards[user.id]['data']['title'] = update.message.text
        
        await update.message.reply_text(
            "📸 <b>Create Post - Step 2/6</b>\n\n🖼️ Send a <b>Photo</b> (or type /skip for text only):",
            parse_mode=ParseMode.HTML
        )
        return Config.STATE_EP_MEDIA
    
    async def handle_media(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Step 3: Button Name"""
        user = update.effective_user
        if user.id not in self.active_wizards: return ConversationHandler.END
        
        if update.message.photo:
            self.active_wizards[user.id]['data']['media_id'] = update.message.photo[-1].file_id
            self.active_wizards[user.id]['data']['media_type'] = 'photo'
        else:
            self.active_wizards[user.id]['data']['media_id'] = None
            self.active_wizards[user.id]['data']['media_type'] = 'text'
            
        await update.message.reply_text(
            "🔘 <b>Create Post - Step 3/6</b>\n\n"
            "Send the <b>Button Name</b> (e.g. Watch Video):",
            parse_mode=ParseMode.HTML
        )
        return Config.STATE_EP_BTN_NAME
    
    async def handle_btn_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Step 4: Button Link"""
        user = update.effective_user
        if user.id not in self.active_wizards: return ConversationHandler.END
        
        self.active_wizards[user.id]['temp_btn_name'] = update.message.text
        
        await update.message.reply_text(
            "🔗 <b>Create Post - Step 4/6</b>\n\n"
            "Send the <b>Button URL</b> (https://...):",
            parse_mode=ParseMode.HTML
        )
        return Config.STATE_EP_BTN_LINK

    async def handle_btn_link(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Step 5: Add More or Done"""
        user = update.effective_user
        if user.id not in self.active_wizards: return ConversationHandler.END
        
        link = update.message.text
        if not link.startswith("http"):
            await update.message.reply_text("❌ Invalid URL! Send again (start with http/https):")
            return Config.STATE_EP_BTN_LINK
        
        name = self.active_wizards[user.id]['temp_btn_name']
        self.active_wizards[user.id]['data']['buttons'].append({'text': name, 'url': link})
        
        keyboard = [
            [{"text": "➕ Add Another Button", "callback": "add_more_btn"}],
            [{"text": "✅ Done / Next Step", "callback": "done_btns"}]
        ]
        
        await update.message.reply_text(
            f"✅ Button Added: <b>{name}</b>\n\nTotal Buttons: {len(self.active_wizards[user.id]['data']['buttons'])}",
            reply_markup=ui.create_keyboard(keyboard),
            parse_mode=ParseMode.HTML
        )
        return Config.STATE_EP_ADD_MORE

    async def handle_add_more(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Loop or Proceed (FIXED)"""
        query = update.callback_query
        user = query.from_user
        await query.answer() # Vital fix!
        
        if query.data == "add_more_btn":
            await query.message.reply_text("🔘 Send <b>Button Name</b>:", parse_mode=ParseMode.HTML)
            return Config.STATE_EP_BTN_NAME
            
        elif query.data == "done_btns":
            # Initialize temp channels
            self.active_wizards[user.id]['data']['temp_channels'] = []
            
            # Show Force Selection UI
            await self.show_force_selection(update, user.id)
            return Config.STATE_EP_FORCE_CHANNELS
            
    async def show_force_selection(self, update, user_id):
        channels = db.get_channels(active_only=True)
        # If no channels, skip to target
        if not channels:
            return await self.show_target_selection(update, user_id)
            
        selected = self.active_wizards[user_id]['data']['temp_channels']
        
        # 2 Column Layout
        buttons = []
        row = []
        for ch in channels:
            status = "✅" if ch['id'] in selected else "⭕"
            row.append({
                "text": f"{status} {ch['name'][:10]}",
                "callback": f"toggle_force_{ch['id']}"
            })
            if len(row) == 2:
                buttons.append(row)
                row = []
        if row: buttons.append(row)
        
        buttons.append([{"text": "➡️ Continue to Publish", "callback": "confirm_force"}])
        
        text = "🔒 <b>Step 5/6: Force Join Channels</b>\nSelect channels users MUST join:"
        
        # Send new message instead of edit to ensure it works
        if update.callback_query:
            try:
                await update.callback_query.message.reply_text(text, reply_markup=ui.create_keyboard(buttons), parse_mode=ParseMode.HTML)
            except:
                 await update.effective_message.reply_text(text, reply_markup=ui.create_keyboard(buttons), parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(text, reply_markup=ui.create_keyboard(buttons), parse_mode=ParseMode.HTML)

    async def handle_force_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        user = query.from_user
        await query.answer("Processing...")
        data = query.data
        
        if data.startswith("toggle_force_"):
            cid = data.replace("toggle_force_", "")
            selected = self.active_wizards[user.id]['data']['temp_channels']
            
            if cid in selected: selected.remove(cid)
            else: selected.append(cid)
            
            # Refresh List (Edit Message)
            channels = db.get_channels(active_only=True)
            buttons = []
            row = []
            for ch in channels:
                status = "✅" if ch['id'] in selected else "⭕"
                row.append({
                    "text": f"{status} {ch['name'][:10]}",
                    "callback": f"toggle_force_{ch['id']}"
                })
                if len(row) == 2:
                    buttons.append(row)
                    row = []
            if row: buttons.append(row)
            
            buttons.append([{"text": "➡️ Continue to Publish", "callback": "confirm_force"}])
            
            await query.edit_message_reply_markup(ui.create_keyboard(buttons))
            return Config.STATE_EP_FORCE_CHANNELS
            
        elif data == "confirm_force":
            await self.show_target_selection(update, user.id)
            return Config.STATE_EP_TARGET
            
    async def show_target_selection(self, update, user_id):
        channels = db.get_channels(active_only=True)
        if not channels:
             if update.callback_query: await update.callback_query.message.reply_text("❌ No channels active.")
             return ConversationHandler.END

        buttons = []
        row = []
        for ch in channels:
            row.append({"text": f"📢 {ch['name'][:15]}", "callback": f"target_{ch['id']}"})
            if len(row) == 2:
                buttons.append(row)
                row = []
        if row: buttons.append(row)
        
        text = "🚀 <b>Step 6/6: Select Publish Channel</b>\nWhere to post?"
        
        if update.callback_query:
             await update.callback_query.message.reply_text(text, reply_markup=ui.create_keyboard(buttons), parse_mode=ParseMode.HTML)
        else:
             await update.message.reply_text(text, reply_markup=ui.create_keyboard(buttons), parse_mode=ParseMode.HTML)
        return Config.STATE_EP_TARGET

    async def handle_target_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        user = query.from_user
        await query.answer("Publishing...")
        target_id = query.data.replace("target_", "")
        
        data = self.active_wizards[user.id]['data']
        
        # Save Post
        post_id = db.save_enhanced_post(
            title=data['title'],
            media_id=data['media_id'],
            media_type=data['media_type'],
            buttons=data['buttons'],
            force_channels=data['temp_channels'],
            created_by=user.id
        )
        
        if not post_id:
            await query.edit_message_text("❌ DB Error")
            return ConversationHandler.END
            
        # Deep Link
        bot_username = context.bot.username
        deep_link = f"https://t.me/{bot_username}?start=post_{post_id}"
        
        # Publish
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔥 CLICK TO WATCH 🔥", url=deep_link)]])
        caption = f"<b>{data['title']}</b>\n\n🔥 <i>Click below to verify and watch!</i> 🔥"
        
        try:
            if data['media_type'] == 'photo' and data['media_id']:
                await context.bot.send_photo(target_id, data['media_id'], caption=caption, reply_markup=kb, parse_mode=ParseMode.HTML)
            else:
                await context.bot.send_message(target_id, caption, reply_markup=kb, parse_mode=ParseMode.HTML)
            
            await query.message.reply_text(f"✅ Published! Post ID: {post_id}")
        except Exception as e:
            await query.message.reply_text(f"❌ Error: {e}")
            
        del self.active_wizards[user.id]
        return ConversationHandler.END

enhanced_wizard = EnhancedPostWizard()

# ==============================================================================
# 🚀 COMMAND HANDLERS
# ==============================================================================

async def auto_delete_task(context: ContextTypes.DEFAULT_TYPE):
    """Deletes message after 60 seconds"""
    job = context.job
    try:
        await context.bot.delete_message(chat_id=job.chat_id, message_id=job.data)
    except Exception:
        pass

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.add_user(user.id, user.username, user.first_name, user.last_name)
    system_monitor.increment_message()
    
    args = context.args
    
    # === DEEP LINK FLOW ===
    if args and args[0].startswith("post_"):
        post_id = args[0].replace("post_", "")
        post = db.get_enhanced_post(post_id)
        
        if not post:
            m = await update.message.reply_text("❌ Post not found.")
            context.job_queue.run_once(auto_delete_task, 5, chat_id=user.id, data=m.message_id)
            return
            
        # Check Membership
        missing = await security.check_membership(user.id, context.bot, post.get('force_channels', []))
        
        if not missing:
            # ✅ SUCCESS
            rows = []
            for b in post['buttons']:
                rows.append([InlineKeyboardButton(b['text'], url=b['url'])])
            
            text = Config.MSG_SUCCESS.format(mention=mention_html(user.id, user.first_name))
            
            if post['media_type'] == 'photo' and post['media_id']:
                msg = await update.message.reply_photo(
                    post['media_id'],
                    caption=f"{text}\n\n🎬 <b>{post['title']}</b>",
                    reply_markup=InlineKeyboardMarkup(rows),
                    parse_mode=ParseMode.HTML
                )
            else:
                msg = await update.message.reply_text(
                    f"{text}\n\n🎬 <b>{post['title']}</b>",
                    reply_markup=InlineKeyboardMarkup(rows),
                    parse_mode=ParseMode.HTML
                )
        else:
            # ❌ FAIL
            text = Config.MSG_FAIL.format(mention=mention_html(user.id, user.first_name))
            
            rows = []
            for ch in missing:
                rows.append([InlineKeyboardButton(f"📢 Join {ch['name']}", url=ch['link'])])
            
            # Verify Button
            deep_link = f"https://t.me/{context.bot.username}?start=post_{post_id}"
            rows.append([InlineKeyboardButton("✅ Verify Now", url=deep_link)])
            
            msg = await update.message.reply_text(
                text,
                reply_markup=InlineKeyboardMarkup(rows),
                parse_mode=ParseMode.HTML
            )
            
        # AUTO DELETE
        db.increment_post_views(post_id)
        context.job_queue.run_once(auto_delete_task, Config.DEFAULT_AUTO_DELETE, chat_id=user.id, data=msg.message_id)
        return

    # === NORMAL START ===
    welcome_text = db.get_config('welcome_msg')
    welcome_text = ui.format_text(welcome_text, user)
    
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(db.get_config('btn_text'), url=db.get_config('watch_url'))
    ]])
    
    try:
        await update.message.reply_photo(
            photo=db.get_config('welcome_photo'),
            caption=welcome_text,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
    except:
         await update.message.reply_text(welcome_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in Config.ADMIN_IDS: return
    await update.message.reply_text(
        "👑 <b>Admin Panel</b>", 
        reply_markup=ui.get_admin_menu(), 
        parse_mode=ParseMode.HTML
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Available Commands:\n/start - Start Bot\n/admin - Panel")

async def backup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in Config.ADMIN_IDS: return
    f = db.create_backup()
    await update.message.reply_text(f"Backup created: {os.path.basename(f)}")

# ==============================================================================
# 🔄 CALLBACK HANDLER (ALL MENUS)
# ==============================================================================

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user = query.from_user
    
    # Wizard Hooks
    if data == "enhanced_post_start":
        return await enhanced_wizard.start_wizard(update, context)
    elif "toggle_force_" in data or data == "confirm_force":
        return await enhanced_wizard.handle_force_selection(update, context)
    elif data == "add_more_btn" or data == "done_btns":
        return await enhanced_wizard.handle_add_more(update, context)
    elif data.startswith("target_"):
        return await enhanced_wizard.handle_target_selection(update, context)
        
    # Admin Menus
    elif data == "menu_channels":
        channels = db.get_channels()
        text = "📢 <b>Channels</b>\n\n"
        buttons = []
        for ch in channels:
            text += f"• {ch['name']}\n"
            buttons.append([{"text": f"❌ {ch['name']}", "callback": f"rm_{ch['id']}"}])
        buttons.append([{"text": "➕ Add", "callback": "add_channel_start"}])
        buttons.append([{"text": "🔙 Back", "callback": "main_menu"}])
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.HTML)
        
    elif data == "add_channel_start":
        await query.message.reply_text("Send Channel ID:")
        return Config.STATE_CHANNEL_ADD_ID
        
    elif data.startswith("rm_"):
        db.remove_channel(data.replace("rm_", ""))
        await query.answer("Removed")
        await callback_handler(update, context) # refresh
    
    elif data == "broadcast_start":
        await query.message.reply_text("📢 Send Message to Broadcast:")
        return Config.STATE_BROADCAST
        
    elif data == "menu_vip":
        await query.message.reply_text("👑 Send User ID to add VIP:")
        return Config.STATE_VIP_ADD
        
    elif data == "menu_security":
         await query.message.reply_text("🛡️ Send User ID to Block:")
         return Config.STATE_USER_BLOCK
        
    elif data == "menu_stats":
        stats = db.get_stats()
        t = ui.get_stats_display(stats)
        await query.edit_message_text(t, reply_markup=ui.create_keyboard([], add_back=True), parse_mode=ParseMode.HTML)

    elif data == "main_menu":
        await query.message.delete()
        await admin_command(query, context)
        
    elif data == "close_panel":
        await query.message.delete()

    elif data == "backup_now":
        f = db.create_backup()
        await query.answer(f"Saved: {os.path.basename(f)}", show_alert=True)

# ==============================================================================
# ✏️ CONVERSATION HANDLERS
# ==============================================================================

# Add Channel
async def add_ch_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['chid'] = update.message.text
    await update.message.reply_text("Name:")
    return Config.STATE_CHANNEL_ADD_NAME
async def add_ch_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['chname'] = update.message.text
    await update.message.reply_text("Link:")
    return Config.STATE_CHANNEL_ADD_LINK
async def add_ch_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db.add_channel(context.user_data['chid'], context.user_data['chname'], update.message.text)
    await update.message.reply_text("✅ Added")
    return ConversationHandler.END

# Broadcast
async def broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = db.get_all_users()
    msg = update.message
    await msg.reply_text(f"🚀 Broadcasting to {len(users)} users...")
    success = 0
    for uid in users:
        try:
            await msg.copy(uid)
            success += 1
        except: pass
    await msg.reply_text(f"✅ Sent to {success} users.")
    return ConversationHandler.END

# Block
async def block_user_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        uid = int(update.message.text)
        db.block_user(uid, update.effective_user.id)
        await update.message.reply_text(f"🚫 Blocked {uid}")
    except: await update.message.reply_text("Error")
    return ConversationHandler.END

# VIP
async def add_vip_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        uid = int(update.message.text)
        db.add_vip(uid)
        await update.message.reply_text(f"👑 Added VIP {uid}")
    except: await update.message.reply_text("Error")
    return ConversationHandler.END

# Old Post Wizard (Kept for compatibility)
async def post_caption_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['post_wizard']['caption'] = update.message.text_html
    await update.message.reply_text("Photo?")
    return Config.STATE_POST_MEDIA
async def post_media_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Stub for old flow compatibility
    await update.message.reply_text("Use New Wizard.")
    return ConversationHandler.END
async def post_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return ConversationHandler.END
async def post_confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelled")
    return ConversationHandler.END

# ==============================================================================
# 🚀 MAIN SETUP
# ==============================================================================

def main():
    application = ApplicationBuilder().token(Config.TOKEN).build()
    
    # 1. New Enhanced Post Wizard
    post_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(enhanced_wizard.start_wizard, pattern='^enhanced_post_start$')],
        states={
            Config.STATE_EP_TITLE: [MessageHandler(filters.TEXT, enhanced_wizard.handle_title)],
            Config.STATE_EP_MEDIA: [MessageHandler(filters.ALL, enhanced_wizard.handle_media)],
            Config.STATE_EP_BTN_NAME: [MessageHandler(filters.TEXT, enhanced_wizard.handle_btn_name)],
            Config.STATE_EP_BTN_LINK: [MessageHandler(filters.TEXT, enhanced_wizard.handle_btn_link)],
            Config.STATE_EP_ADD_MORE: [CallbackQueryHandler(enhanced_wizard.handle_add_more)],
            Config.STATE_EP_FORCE_CHANNELS: [CallbackQueryHandler(enhanced_wizard.handle_force_selection)],
            Config.STATE_EP_TARGET: [CallbackQueryHandler(enhanced_wizard.handle_target_selection)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    # 2. Add Channel
    ch_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(callback_handler, pattern='^add_channel_start$')],
        states={
            Config.STATE_CHANNEL_ADD_ID: [MessageHandler(filters.TEXT, add_ch_id)],
            Config.STATE_CHANNEL_ADD_NAME: [MessageHandler(filters.TEXT, add_ch_name)],
            Config.STATE_CHANNEL_ADD_LINK: [MessageHandler(filters.TEXT, add_ch_link)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    # 3. Broadcast
    bc_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(callback_handler, pattern='^broadcast_start$')],
        states={Config.STATE_BROADCAST: [MessageHandler(filters.ALL & ~filters.COMMAND, broadcast_handler)]},
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    # 4. Old Wizard (Kept for compatibility with old imports)
    old_post_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(callback_handler, pattern='^create_post_start$')],
        states={
            Config.STATE_POST_CAPTION: [MessageHandler(filters.TEXT, post_caption_handler)],
            Config.STATE_POST_MEDIA: [MessageHandler(filters.ALL, post_media_handler)],
            Config.STATE_POST_BUTTON: [MessageHandler(filters.TEXT, post_button_handler)],
            Config.STATE_POST_CONFIRM: [CallbackQueryHandler(post_confirm_handler)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # 5. Security Menus
    blk_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(callback_handler, pattern='^block_user_start$')],
        states={Config.STATE_USER_BLOCK: [MessageHandler(filters.TEXT, block_user_handler)]},
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    vip_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(callback_handler, pattern='^add_vip_start$')],
        states={Config.STATE_VIP_ADD: [MessageHandler(filters.TEXT, add_vip_handler)]},
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("backup", backup_command))
    
    application.add_handler(post_conv)
    application.add_handler(ch_conv)
    application.add_handler(bc_conv)
    application.add_handler(old_post_conv)
    application.add_handler(blk_conv)
    application.add_handler(vip_conv)
    
    application.add_handler(CallbackQueryHandler(callback_handler))
    
    async def error_handler(update, context):
        logger.error(f"Error: {context.error}")
        traceback.print_exc()
        
    application.add_error_handler(error_handler)
    
    print("🚀 SUPREME BOT v10.5 IS RUNNING...")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
