"""
================================================================================
SUPREME GOD BOT - PREMIUM EDITION v10.0 (FIXED)
FULLY WORKING WITH ALL FEATURES - ENHANCED VERIFICATION
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

# Telegram imports
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    BotCommand, InputFile
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
    # Bot Token (Updated)
    TOKEN = "8007194607:AAHhuMvS3z814Fr2eF_17K1wv8UPXmvA1kY"
    ADMIN_IDS = {8013042180}  # Add your admin ID here
    
    # Database
    DB_NAME = "supreme_bot.db"
    
    # System
    DEFAULT_AUTO_DELETE = 60  # 60 seconds auto delete
    
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
    STATE_POST_BUTTONS = 4
    STATE_POST_BUTTON_NAME = 5
    STATE_POST_BUTTON_LINK = 6
    STATE_POST_FORCE_CHANNELS = 7
    STATE_POST_TARGET_CHANNEL = 8
    STATE_POST_CONFIRM = 9
    
    STATE_CHANNEL_ADD_ID = 10
    STATE_CHANNEL_ADD_NAME = 11
    STATE_CHANNEL_ADD_LINK = 12
    STATE_BLOCK_USER = 13
    STATE_ADD_VIP = 14
    STATE_EDIT_MESSAGE = 15
    STATE_BROADCAST = 16
    
    # Emojis
    EMOJIS = {
        "heart": "❤️",
        "fire": "🔥",
        "star": "⭐",
        "lock": "🔒",
        "unlock": "🔓",
        "check": "✅",
        "cross": "❌",
        "users": "👥",
        "admin": "👑",
        "camera": "📸",
        "video": "🎬",
        "link": "🔗",
        "time": "⏰",
        "warn": "⚠️",
        "info": "ℹ️",
        "gear": "⚙️",
        "chart": "📊",
        "megaphone": "📢",
        "crown": "👑",
        "rocket": "🚀",
        "target": "🎯"
    }
    
    # Enhanced Verification Messages
    VERIFICATION_MESSAGES = {
        'not_joined_popup': "🔥💋 প্রিয়, আগে সব চ্যানেল Join করুন 🔔💖\nতারপর 👉 ✅ Verified চাপুন 😘💎\nএরপরই দেখবেন HOT & LOVE ভিডিও 😍🔥",
        'joined_popup': "💖🔥 হেই প্রিয়! 🔥💖\n✅ আপনি সফলভাবে Join করেছেন 🎉✨\nএবার 👉 ▶️ WATCH NOW ▶️ বাটনে ক্লিক করুন 😘💎\n😈 তারপরই খুলে যাবে আপনার জন্য 🔞 ভাইরাল ভিডিও এর দুনিয়া 💋🔥",
        'access_granted': "🎉 ✅ অ্যাক্সেস গ্রান্টেড! এখন ভিডিও লিংক দেখতে পারবেন।",
        'watch_button_text': "▶️ WATCH NOW ▶️",
        'verify_button_text': "✅ Verified"
    }

# ==============================================================================
# 📝 LOGGING
# ==============================================================================

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
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
        if self._initialized:
            return
            
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
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                join_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_active DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_blocked BOOLEAN DEFAULT 0
            )
        ''')
        
        # Channels table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS channels (
                channel_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                link TEXT NOT NULL,
                force_join BOOLEAN DEFAULT 1,
                is_active BOOLEAN DEFAULT 1,
                added_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Config table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        ''')
        
        # Posts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                post_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                photo_id TEXT,
                post_text TEXT,
                buttons TEXT,
                force_channels TEXT,
                target_channel_id TEXT,
                created_by INTEGER,
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                watch_url TEXT,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # User post access tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_access (
                user_id INTEGER,
                post_id INTEGER,
                access_granted BOOLEAN DEFAULT 0,
                access_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, post_id)
            )
        ''')
        
        # Initialize defaults
        self.initialize_defaults()
        conn.commit()
        logger.info("Database initialized successfully")
    
    def initialize_defaults(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Default config
        defaults = [
            ('welcome_message', '''{heart} {fire} <b>💖✨ওগো শুনছো! স্বাগতম জানাই তোমাকে!💖✨</b> {fire} {heart}

{star} <b>❤️তুমি অবশ্যই আমাদের মাঝে এসেছো, আমার হৃদয়টা আনন্দে নেচে উঠলো! 😍💃
তোমাকে ছাড়া আমাদের এই আয়োজন অসম্পূর্ণ ছিল।</b>

{star} <b>💖✨তোমার জন্য যা যা থাকছে::</b>
🎀 এক্সক্লুসিভ ভাইরাল ভিডিও 🔞
🎀 নতুন সব কালেকশন 🔥
🎀 এবং আমার হৃদয়ের ভালোবাসা... ❤️

{link} <b>নিচের বাটনে ক্লিক করে শুরু করুন:</b>'''),
            
            ('lock_message', '''{lock} <b>অ্যাক্সেস লক করা আছে!</b>

{cross} 😢💔ওহ নো বেবি! তুমি এখনো জয়েন করোনি? আমার লক্ষ্মীটা, তুমি যদি নিচের চ্যানেলগুলোতে জয়েন না করো, তাহলে আমি তোমাকে ভিডিওটা দেখাতে পারবো না! 🥺🥀
প্লিজ সোনা, রাগ করো না!

{info} নিচের সবগুলোতে জয়েন করে💖✨ {check} ভেরিফাই বাটনে ক্লিক করুন। আমি অপেক্ষা করছি... 😘❤️'''),
            
            ('success_message', '''💖🔥 Heyyy @UserName 😘💋
🌹✨ অবশেষে তুমি এসে গেছো, আমার মিষ্টি Love 😍
💯💎 সব Force Channel Join সম্পন্ন! এখন তোমার জন্য সব দরজা খুলে গেছে 😈🔥
💋 নিচে Button গুলোতে ক্লিক করো আর মজা নাও 💕💎
🌹🔥 Stay Hot • Stay Wild • Stay With Us 💋💋.'''),
            
            ('failed_message', '''😘🔥 Ohhh @UserName 💔💋
💞✨ তুমি এখনো সব Channel Join করোনি 😢🔥
💋 আগে সব Channel Join করো, তারপর Verify Button চাপো 💎💋
🔥 তখনই Full Premium • Hot • Exclusive Content দেখতে পারবে 😈🔥.'''),
            
            ('watch_url', 'https://mmshotbd.blogspot.com/?m=1'),
            ('button_text', '🎬 ভিডিও দেখুন এখনই! 🔥'),
            ('auto_delete', '60'),
            ('verify_popup_not_joined', Config.VERIFICATION_MESSAGES['not_joined_popup']),
            ('verify_popup_joined', Config.VERIFICATION_MESSAGES['joined_popup'])
        ]
        
        for key, value in defaults:
            cursor.execute('INSERT OR IGNORE INTO config (key, value) VALUES (?, ?)', (key, value))
        
        # Add default channels
        cursor.execute("SELECT COUNT(*) FROM channels")
        if cursor.fetchone()[0] == 0:
            for channel in Config.DEFAULT_CHANNELS:
                cursor.execute('''
                    INSERT OR IGNORE INTO channels (channel_id, name, link)
                    VALUES (?, ?, ?)
                ''', (str(channel["id"]), channel["name"], channel["link"]))
        
        conn.commit()
    
    # === User Management ===
    def add_user(self, user_id, username, first_name, last_name=""):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO users 
            (user_id, username, first_name, last_name, last_active)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (user_id, username, first_name, last_name))
        conn.commit()
        return True
    
    def update_user_activity(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE user_id = ?', (user_id,))
        conn.commit()
    
    def get_user(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def block_user(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET is_blocked = 1 WHERE user_id = ?', (user_id,))
        conn.commit()
        return cursor.rowcount > 0
    
    def unblock_user(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET is_blocked = 0 WHERE user_id = ?', (user_id,))
        conn.commit()
        return cursor.rowcount > 0
    
    # === Channel Management ===
    def get_channels(self, force_only=False, active_only=True):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM channels WHERE 1=1"
        if active_only:
            query += " AND is_active = 1"
        if force_only:
            query += " AND force_join = 1"
        
        query += " ORDER BY name"
        cursor.execute(query)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def add_channel(self, channel_id, name, link, force_join=True):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO channels (channel_id, name, link, force_join)
                VALUES (?, ?, ?, ?)
            ''', (str(channel_id), name, link, force_join))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding channel: {e}")
            return False
    
    def remove_channel(self, channel_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE channels SET is_active = 0 WHERE channel_id = ?", (str(channel_id),))
        conn.commit()
        return cursor.rowcount > 0
    
    def toggle_force_join(self, channel_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE channels 
            SET force_join = NOT force_join 
            WHERE channel_id = ?
        ''', (str(channel_id),))
        conn.commit()
        cursor.execute("SELECT force_join FROM channels WHERE channel_id = ?", (str(channel_id),))
        result = cursor.fetchone()
        return result[0] if result else False
    
    # === Config Management ===
    def get_config(self, key, default=""):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM config WHERE key = ?", (key,))
        result = cursor.fetchone()
        
        if result:
            value = result[0]
            for emoji_key, emoji in Config.EMOJIS.items():
                value = value.replace(f"{{{emoji_key}}}", emoji)
            return value
        return default
    
    def set_config(self, key, value):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO config (key, value)
            VALUES (?, ?)
        ''', (key, value))
        conn.commit()
        return True
    
    # === Post Management ===
    def save_post(self, title, photo_id, post_text, buttons, force_channels, target_channel_id, created_by, watch_url=""):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO posts (title, photo_id, post_text, buttons, force_channels, target_channel_id, created_by, watch_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (title, photo_id, post_text, json.dumps(buttons), 
                  json.dumps(force_channels), target_channel_id, created_by, watch_url))
            
            post_id = cursor.lastrowid
            conn.commit()
            return post_id
        except Exception as e:
            logger.error(f"Error saving post: {e}")
            return None
    
    def get_post(self, post_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM posts WHERE post_id = ?', (post_id,))
        row = cursor.fetchone()
        if row:
            post = dict(row)
            if post.get('buttons'):
                post['buttons'] = json.loads(post['buttons'])
            if post.get('force_channels'):
                post['force_channels'] = json.loads(post['force_channels'])
            return post
        return None
    
    def get_watch_url(self, post_id):
        post = self.get_post(post_id)
        return post.get('watch_url', '') if post else ''
    
    def set_watch_url(self, post_id, watch_url):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE posts SET watch_url = ? WHERE post_id = ?', (watch_url, post_id))
        conn.commit()
        return cursor.rowcount > 0
    
    # === User Access Management ===
    def grant_user_access(self, user_id, post_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO user_access (user_id, post_id, access_granted, access_date)
            VALUES (?, ?, 1, CURRENT_TIMESTAMP)
        ''', (user_id, post_id))
        conn.commit()
        return True
    
    def revoke_user_access(self, user_id, post_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM user_access WHERE user_id = ? AND post_id = ?', (user_id, post_id))
        conn.commit()
        return cursor.rowcount > 0
    
    def has_user_access(self, user_id, post_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT access_granted FROM user_access WHERE user_id = ? AND post_id = ?', (user_id, post_id))
        result = cursor.fetchone()
        return result[0] == 1 if result else False
    
    # === Statistics ===
    def get_stats(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        stats = {}
        cursor.execute("SELECT COUNT(*) FROM users")
        stats['total_users'] = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM users WHERE DATE(join_date) = DATE('now')")
        stats['today_users'] = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_blocked = 1")
        stats['blocked_users'] = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM channels WHERE is_active = 1")
        stats['active_channels'] = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM channels WHERE force_join = 1 AND is_active = 1")
        stats['force_channels'] = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM posts")
        stats['total_posts'] = cursor.fetchone()[0]
        return stats

db = DatabaseManager()

# ==============================================================================
# 🎨 UI MANAGER
# ==============================================================================

class UIManager:
    @staticmethod
    def format_text(text: str, user=None):
        for key, emoji in Config.EMOJIS.items():
            text = text.replace(f"{{{key}}}", emoji)
        if user:
            user_mention = mention_html(user.id, user.first_name or 'User')
            text = text.replace("@UserName", user_mention)
        return text
    
    @staticmethod
    def create_keyboard(buttons, add_back=True, add_close=False):
        keyboard = []
        for row in buttons:
            keyboard_row = []
            for btn in row:
                if 'url' in btn:
                    keyboard_row.append(InlineKeyboardButton(btn['text'], url=btn['url']))
                else:
                    keyboard_row.append(InlineKeyboardButton(btn['text'], callback_data=btn['callback']))
            keyboard.append(keyboard_row)
        
        if add_back:
            keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="main_menu")])
        if add_close:
            keyboard.append([InlineKeyboardButton("❌ Close", callback_data="close_panel")])
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_admin_menu():
        buttons = [
            [
                {"text": "📝 Message Editor", "callback": "menu_messages"},
                {"text": "📢 Channel Manager", "callback": "menu_channels"}
            ],
            [
                {"text": "🎯 Create Post", "callback": "create_post_start"},
                {"text": "📢 Broadcast", "callback": "broadcast_start"}
            ],
            [
                {"text": "🛡️ User Management", "callback": "menu_users"},
                {"text": "📊 Statistics", "callback": "menu_stats"}
            ],
            [
                {"text": "⚙️ Settings", "callback": "menu_settings"}
            ]
        ]
        return UIManager.create_keyboard(buttons, add_back=False, add_close=True)
    
    @staticmethod
    def create_channel_buttons(channels, prefix="select_channel"):
        buttons = []
        row = []
        for i, channel in enumerate(channels):
            row.append({
                "text": f"📢 {channel['name'][:15]}",
                "callback": f"{prefix}_{channel['channel_id']}"
            })
            if len(row) == 2 or i == len(channels) - 1:
                buttons.append(row)
                row = []
        return buttons

ui = UIManager()

# ==============================================================================
# 🔐 ENHANCED SECURITY MANAGER
# ==============================================================================

class SecurityManager:
    def __init__(self):
        self.verification_cache = {}
        self.user_access_cache = {}
    
    async def check_membership(self, user_id, bot, channel_ids=None):
        """
        চ্যানেল জয়েন চেক করে এবং মিসিং চ্যানেলগুলোর তথ্য সহ রিটার্ন করে
        """
        cache_key = f"membership_{user_id}_{hash(str(channel_ids))}"
        
        if cache_key in self.verification_cache:
            cached_time, result = self.verification_cache[cache_key]
            if time.time() - cached_time < 60:  # 1 minute cache
                return result
        
        if not channel_ids:
            channels = db.get_channels(force_only=True, active_only=True)
        else:
            all_channels = db.get_channels(active_only=True)
            channels = [ch for ch in all_channels if str(ch['channel_id']) in map(str, channel_ids)]
        
        joined_channels = []
        missing_channels = []
        
        for channel in channels:
            try:
                member = await bot.get_chat_member(
                    chat_id=channel['channel_id'],
                    user_id=user_id
                )
                if member.status in ['left', 'kicked']:
                    missing_channels.append(channel)
                else:
                    joined_channels.append(channel)
            except Exception as e:
                logger.warning(f"Failed to check channel {channel['channel_id']}: {e}")
                missing_channels.append(channel)
        
        result = {
            'joined': joined_channels,
            'missing': missing_channels,
            'all_joined': len(missing_channels) == 0,
            'total_required': len(channels)
        }
        
        self.verification_cache[cache_key] = (time.time(), result)
        return result
    
    def clear_user_cache(self, user_id):
        """
        ইউজারের ক্যাশে ক্লিয়ার করে
        """
        keys_to_remove = [k for k in self.verification_cache.keys() if k.startswith(f"membership_{user_id}_")]
        for key in keys_to_remove:
            del self.verification_cache[key]
        
        keys_to_remove = [k for k in self.user_access_cache.keys() if k.startswith(f"access_{user_id}_")]
        for key in keys_to_remove:
            del self.user_access_cache[key]
    
    def clear_post_cache(self, post_id):
        """
        পোস্টের ক্যাশে ক্লিয়ার করে
        """
        keys_to_remove = [k for k in self.verification_cache.keys() if f"post_{post_id}" in k]
        for key in keys_to_remove:
            del self.verification_cache[key]

security = SecurityManager()

# ==============================================================================
# 🎯 ENHANCED POST WIZARD WITH WATCH URL
# ==============================================================================

class EnhancedPostWizard:
    def __init__(self):
        self.active_wizards = {}
    
    async def start_wizard(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        user = query.from_user
        
        self.active_wizards[user.id] = {
            'step': 'title',
            'data': {
                'buttons': [],
                'force_channels': [],
                'watch_url': db.get_config('watch_url', 'https://mmshotbd.blogspot.com/?m=1')
            }
        }
        
        await query.answer()
        await query.edit_message_text(
            ui.format_text("📝 <b>🎯 Create New Post - Step 1/7</b>\n\n"
                          "✏️ Please send the <b>POST TITLE</b>:", user),
            parse_mode=ParseMode.HTML
        )
        return Config.STATE_POST_TITLE
    
    async def handle_title(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if user.id not in self.active_wizards:
            await update.message.reply_text("❌ Session expired. Please start again.")
            return ConversationHandler.END
        
        title = update.message.text
        self.active_wizards[user.id]['data']['title'] = title
        self.active_wizards[user.id]['step'] = 'photo'
        
        await update.message.reply_text(
            ui.format_text("📸 <b>🎯 Create New Post - Step 2/7</b>\n\n"
                          "🖼️ Please send the <b>POST PHOTO</b>:", user),
            parse_mode=ParseMode.HTML
        )
        return Config.STATE_POST_PHOTO
    
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if user.id not in self.active_wizards:
            return ConversationHandler.END
        
        if update.message.photo:
            photo_id = update.message.photo[-1].file_id
            self.active_wizards[user.id]['data']['photo_id'] = photo_id
            self.active_wizards[user.id]['step'] = 'text'
            
            await update.message.reply_text(
                ui.format_text("📝 <b>🎯 Create New Post - Step 3/7</b>\n\n"
                              "💬 Please send the <b>POST TEXT</b> (or type /skip):", user),
                parse_mode=ParseMode.HTML
            )
            return Config.STATE_POST_TEXT
        else:
            await update.message.reply_text("❌ Please send a photo!")
            return Config.STATE_POST_PHOTO
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if user.id not in self.active_wizards:
            return ConversationHandler.END
        
        if update.message.text and update.message.text.lower() != '/skip':
            self.active_wizards[user.id]['data']['post_text'] = update.message.text
        else:
            self.active_wizards[user.id]['data']['post_text'] = ""
        
        self.active_wizards[user.id]['step'] = 'watch_url'
        await update.message.reply_text(
            ui.format_text("🔗 <b>🎯 Create New Post - Step 4/7</b>\n\n"
                          "🌐 Please send the <b>WATCH URL</b> for this post:\n"
                          "(This is the hidden video link that will be revealed after verification)", user),
            parse_mode=ParseMode.HTML
        )
        return Config.STATE_POST_BUTTONS
    
    async def handle_watch_url(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if user.id not in self.active_wizards:
            return ConversationHandler.END
        
        if update.message.text:
            url = update.message.text.strip()
            if not url.startswith(('http://', 'https://')):
                await update.message.reply_text("❌ Please provide a valid URL starting with http:// or https://")
                return Config.STATE_POST_BUTTONS
            
            self.active_wizards[user.id]['data']['watch_url'] = url
        
        self.active_wizards[user.id]['step'] = 'buttons'
        return await self.show_button_menu(update, context, user)

    async def show_button_menu(self, update, context, user):
        buttons = []
        
        if self.active_wizards[user.id]['data']['buttons']:
            current_buttons = self.active_wizards[user.id]['data']['buttons']
            preview_text = "📋 <b>Current buttons:</b>\n" + "\n".join([f"{i+1}. {btn['name']}" for i, btn in enumerate(current_buttons)])
        else:
            preview_text = "📭 No buttons added yet."
        
        keyboard_buttons = [
            [{"text": "➕ Add Button", "callback": "add_button"}],
            [{"text": "➡️ Continue", "callback": "continue_buttons"}]
        ]
        
        keyboard = ui.create_keyboard(keyboard_buttons, add_back=True, add_close=True)
        
        msg_text = ui.format_text("🔘 <b>🎯 Create New Post - Step 5/7</b>\n\n"
                                 "🔗 <b>Button Management</b>\n\n"
                                 f"{preview_text}\n\n"
                                 "Click 'Add Button' to add button or 'Continue' to proceed:", user)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(msg_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(msg_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
            
        return Config.STATE_POST_BUTTONS
    
    async def handle_button_management(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        user = query.from_user
        
        if user.id not in self.active_wizards:
            await query.answer("❌ Session expired!")
            return ConversationHandler.END
        
        data = query.data
        
        if data == "add_button":
            await query.edit_message_text(
                ui.format_text("🔘 <b>Add Button - Step 1/2</b>\n\n"
                              "✏️ Please send the <b>BUTTON NAME</b>:", user),
                parse_mode=ParseMode.HTML
            )
            return Config.STATE_POST_BUTTON_NAME
        
        elif data == "continue_buttons":
            if not self.active_wizards[user.id]['data']['buttons']:
                await query.answer("⚠️ No buttons added. Continue anyway?", show_alert=False)
            
            # Move to force channel selection
            self.active_wizards[user.id]['step'] = 'force_channels'
            force_channels = db.get_channels(force_only=True, active_only=True)
            
            if not force_channels:
                await query.answer("ℹ️ No force channels found. Skipping force channel selection.")
                # Skip to target channel if no force channels
                return await self.handle_force_channel_selection(update, context, skip=True)

            channel_buttons = ui.create_channel_buttons(force_channels, prefix="select_force")
            channel_buttons.append([
                {"text": "✅ Select All", "callback": "select_all_force"},
                {"text": "➡️ Continue", "callback": "continue_force"}
            ])
            keyboard = ui.create_keyboard(channel_buttons, add_back=True, add_close=True)
            
            await query.edit_message_text(
                ui.format_text(f"🎯 <b>Step 6/7: Force Channels</b>\n\n"
                              "Select channels that users MUST join to see the content:", user),
                reply_markup=keyboard, parse_mode=ParseMode.HTML
            )
            return Config.STATE_POST_FORCE_CHANNELS
        
        return Config.STATE_POST_BUTTONS
    
    async def handle_button_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if user.id not in self.active_wizards:
            return ConversationHandler.END
        
        context.user_data['temp_btn_name'] = update.message.text
        await update.message.reply_text(
            "🔗 <b>Add Button - Step 2/2</b>\n\n"
            "🌐 Send <b>BUTTON LINK</b>:", 
            parse_mode=ParseMode.HTML
        )
        return Config.STATE_POST_BUTTON_LINK

    async def handle_button_link(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if user.id not in self.active_wizards:
            return ConversationHandler.END
        
        link = update.message.text
        if not link.startswith(('http://', 'https://')):
            await update.message.reply_text("❌ Invalid URL! Start with http:// or https://")
            return Config.STATE_POST_BUTTON_LINK
            
        name = context.user_data.get('temp_btn_name', 'Button')
        self.active_wizards[user.id]['data']['buttons'].append({'name': name, 'link': link})
        
        await update.message.reply_text("✅ Button Added!")
        return await self.show_button_menu(update, context, user)

    async def handle_force_channel_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, skip=False):
        if skip:
            # Jump to target channel selection
            all_channels = db.get_channels(active_only=True)
            channel_buttons = ui.create_channel_buttons(all_channels, prefix="select_target")
            keyboard = ui.create_keyboard(channel_buttons, add_back=True, add_close=True)
            
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    "📤 <b>Step 7/7: Select TARGET CHANNEL</b> to post:",
                    reply_markup=keyboard, parse_mode=ParseMode.HTML
                )
            return Config.STATE_POST_TARGET_CHANNEL

        query = update.callback_query
        user = query.from_user
        if user.id not in self.active_wizards:
            return ConversationHandler.END
            
        data = query.data
        
        if data == "select_all_force":
            force_channels = db.get_channels(force_only=True, active_only=True)
            self.active_wizards[user.id]['data']['force_channels'] = [ch['channel_id'] for ch in force_channels]
            await query.answer("✅ Selected All")
            
        elif data.startswith("select_force_"):
            cid = data.replace("select_force_", "")
            current = self.active_wizards[user.id]['data']['force_channels']
            if cid in current:
                current.remove(cid)
                await query.answer("❌ Deselected")
            else:
                current.append(cid)
                await query.answer("✅ Selected")
                
        elif data == "continue_force":
            # Move to target
            all_channels = db.get_channels(active_only=True)
            if not all_channels:
                await query.answer("❌ No channels found!")
                return ConversationHandler.END
                
            channel_buttons = ui.create_channel_buttons(all_channels, prefix="select_target")
            keyboard = ui.create_keyboard(channel_buttons, add_back=True, add_close=True)
            
            await query.edit_message_text(
                "📤 <b>Step 7/7: Select TARGET CHANNEL</b> to post:",
                reply_markup=keyboard, parse_mode=ParseMode.HTML
            )
            return Config.STATE_POST_TARGET_CHANNEL
            
        # Refresh buttons
        force_channels = db.get_channels(force_only=True, active_only=True)
        channel_buttons = []
        row = []
        for i, ch in enumerate(force_channels):
            is_sel = ch['channel_id'] in self.active_wizards[user.id]['data']['force_channels']
            emoji = "✅" if is_sel else "📢"
            row.append({"text": f"{emoji} {ch['name'][:12]}", "callback": f"select_force_{ch['channel_id']}"})
            if len(row) == 2 or i == len(force_channels) - 1:
                channel_buttons.append(row)
                row = []
                
        selected_count = len(self.active_wizards[user.id]['data']['force_channels'])
        channel_buttons.append([
            {"text": "✅ Select All", "callback": "select_all_force"},
            {"text": f"➡️ Continue ({selected_count})", "callback": "continue_force"}
        ])
        await query.edit_message_reply_markup(ui.create_keyboard(channel_buttons, add_back=True, add_close=True))
        return Config.STATE_POST_FORCE_CHANNELS

    async def handle_target_channel_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        user = query.from_user
        
        if query.data.startswith("select_target_"):
            cid = query.data.replace("select_target_", "")
            channel = next((ch for ch in db.get_channels(active_only=True) if ch['channel_id'] == cid), None)
            
            if not channel:
                await query.answer("❌ Channel not found!")
                return Config.STATE_POST_TARGET_CHANNEL
                
            self.active_wizards[user.id]['data']['target_channel_id'] = cid
            self.active_wizards[user.id]['data']['target_channel_name'] = channel['name']
            
            # Preview
            data = self.active_wizards[user.id]['data']
            preview = f"📝 <b>Title:</b> {data['title']}\n"
            preview += f"📸 <b>Has Photo:</b> {'Yes' if 'photo_id' in data else 'No'}\n"
            preview += f"💬 <b>Text:</b> {'Yes' if data.get('post_text') else 'No'}\n"
            preview += f"🔗 <b>Watch URL:</b> {'Set' if data.get('watch_url') else 'Not Set'}\n"
            preview += f"🔘 <b>Buttons:</b> {len(data['buttons'])}\n"
            preview += f"🎯 <b>Force Channels:</b> {len(data['force_channels'])}\n"
            preview += f"📤 <b>Target:</b> {data['target_channel_name']}\n"
            
            keyboard_buttons = [[{"text": "🚀 Post Now", "callback": "final_post"}]]
            keyboard = ui.create_keyboard(keyboard_buttons, add_back=True, add_close=True)
            
            await query.edit_message_text(
                ui.format_text(f"🎯 <b>FINAL CONFIRMATION</b>\n\n{preview}\n\n⚠️ <b>Click 'Post Now' to confirm:</b>", user),
                reply_markup=keyboard, parse_mode=ParseMode.HTML
            )
            return Config.STATE_POST_CONFIRM
        return Config.STATE_POST_TARGET_CHANNEL

    async def finalize_post(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        user = query.from_user
        
        if user.id not in self.active_wizards:
            await query.answer("❌ Session expired!")
            return ConversationHandler.END
            
        data = self.active_wizards[user.id]['data']
        
        post_id = db.save_post(
            data['title'], 
            data.get('photo_id', ''), 
            data.get('post_text', ''),
            data['buttons'], 
            data['force_channels'], 
            data['target_channel_id'], 
            user.id,
            data.get('watch_url', '')
        )
        
        if post_id:
            # Construct message with VERIFY button only
            keyboard_buttons = []
            
            # Add only VERIFY button initially
            keyboard_buttons.append([InlineKeyboardButton(
                "🔓 Verify & View", 
                callback_data=f"verify_post_{post_id}"
            )])
            
            keyboard = InlineKeyboardMarkup(keyboard_buttons)
            
            # Create caption
            caption = f"<b>{data['title']}</b>\n\n"
            if data.get('post_text'):
                caption += f"{data['post_text']}\n\n"
            caption += "🔒 <i>Content is locked. Click 'Verify & View' to check access.</i>"
            
            try:
                if 'photo_id' in data and data['photo_id']:
                    await context.bot.send_photo(
                        chat_id=data['target_channel_id'], 
                        photo=data['photo_id'], 
                        caption=caption, 
                        reply_markup=keyboard, 
                        parse_mode=ParseMode.HTML
                    )
                else:
                    await context.bot.send_message(
                        chat_id=data['target_channel_id'], 
                        text=caption, 
                        reply_markup=keyboard, 
                        parse_mode=ParseMode.HTML
                    )
                
                await query.edit_message_text(
                    f"✅ <b>Post Created Successfully!</b>\n\n"
                    f"📊 <b>Post ID:</b> {post_id}\n"
                    f"🎯 <b>Target:</b> {data['target_channel_name']}\n"
                    f"🔒 <b>Force Channels:</b> {len(data['force_channels'])}\n"
                    f"🔗 <b>Buttons:</b> {len(data['buttons'])}",
                    parse_mode=ParseMode.HTML
                )
                
                # Clear security cache for this post
                security.clear_post_cache(post_id)
                
            except Exception as e:
                await query.edit_message_text(f"❌ Error sending to channel: {str(e)}")
        else:
            await query.answer("❌ Database Error!", show_alert=True)
            
        # Clean up
        if user.id in self.active_wizards:
            del self.active_wizards[user.id]
        
        return ConversationHandler.END

post_wizard = EnhancedPostWizard()

# ==============================================================================
# 🎮 COMMAND HANDLERS
# ==============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.add_user(user.id, user.username, user.first_name, user.last_name or "")
    db.update_user_activity(user.id)
    
    if db.get_user(user.id).get('is_blocked'):
        await update.message.reply_text("🚫 Restricted Access.")
        return
    
    missing = await security.check_membership(user.id, context.bot)
    if missing and not missing['all_joined']:
        lock_msg = db.get_config('lock_message')
        buttons = []
        for ch in missing['missing']:
            buttons.append([{"text": f"📢 Join {ch['name']}", "url": ch['link']}])
        buttons.append([{"text": "✅ Verify Membership", "callback": "verify_membership"}])
        
        await update.message.reply_text(
            ui.format_text(lock_msg, user), 
            reply_markup=ui.create_keyboard(buttons, False), 
            parse_mode=ParseMode.HTML
        )
    else:
        await send_welcome(update, user)

async def send_welcome(update, user):
    welcome_msg = db.get_config('welcome_message')
    btn_text = db.get_config('button_text')
    watch_url = db.get_config('watch_url')
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(btn_text, url=watch_url)]
    ])
    
    msg = await update.message.reply_text(
        ui.format_text(welcome_msg, user), 
        reply_markup=kb, 
        parse_mode=ParseMode.HTML
    )
    
    auto_delete = int(db.get_config('auto_delete', Config.DEFAULT_AUTO_DELETE))
    if auto_delete > 0:
        asyncio.create_task(delete_later(msg, auto_delete))

async def delete_later(message, delay):
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except:
        pass

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in Config.ADMIN_IDS:
        return
    
    await update.message.reply_text(
        "👑 <b>Admin Panel</b>", 
        reply_markup=ui.get_admin_menu(), 
        parse_mode=ParseMode.HTML
    )

# ==============================================================================
# 🔄 ENHANCED CALLBACK HANDLER WITH VERIFICATION SYSTEM
# ==============================================================================

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    data = query.data
    
    await query.answer()  # Always answer callback query
    
    db.update_user_activity(user.id)
    
    # Handle membership verification
    if data == "verify_membership":
        security.clear_user_cache(user.id)
        result = await security.check_membership(user.id, context.bot)
        
        if result['all_joined']:
            # All channels joined
            await query.answer("✅ Verified! All channels joined.", show_alert=True)
            await query.message.delete()
            await send_welcome(query, user)
        else:
            # Not all channels joined
            await query.answer(
                "❌ Please join all required channels first!", 
                show_alert=True
            )
    
    # Handle post verification
    elif data.startswith("verify_post_"):
        post_id = int(data.replace("verify_post_", ""))
        await handle_post_verification(update, context, post_id)
    
    # Handle watch now button
    elif data.startswith("watch_now_"):
        post_id = int(data.replace("watch_now_", ""))
        await handle_watch_now(update, context, post_id)
    
    # Admin menu handlers
    elif data == "main_menu":
        if user.id in Config.ADMIN_IDS:
            await query.edit_message_text(
                "👑 <b>Admin Panel</b>", 
                reply_markup=ui.get_admin_menu(), 
                parse_mode=ParseMode.HTML
            )
    
    elif data == "close_panel":
        try:
            await query.message.delete()
        except:
            pass
    
    # Admin Menus
    elif data == "menu_messages":
        buttons = [[
            {"text": "✏️ Welcome Msg", "callback": "edit_welcome_message"},
            {"text": "✏️ Lock Msg", "callback": "edit_lock_message"}
        ]]
        await query.edit_message_text(
            "📝 Select Message to Edit:", 
            reply_markup=ui.create_keyboard(buttons), 
            parse_mode=ParseMode.HTML
        )
    
    elif data == "create_post_start":
        return await post_wizard.start_wizard(update, context)
    
    elif data.startswith("edit_"):
        key = data.replace("edit_", "")
        context.user_data['edit_key'] = key
        await query.message.reply_text(
            f"✏️ Send new value for <b>{key}</b>:", 
            parse_mode=ParseMode.HTML
        )
        return Config.STATE_EDIT_MESSAGE

    elif data == "add_channel":
        await query.message.reply_text(
            "➕ Send Channel ID:", 
            parse_mode=ParseMode.HTML
        )
        return Config.STATE_CHANNEL_ADD_ID
    
    elif data.startswith("select_force_") or data == "select_all_force" or data == "continue_force":
        return await post_wizard.handle_force_channel_selection(update, context)
    
    elif data.startswith("select_target_"):
        return await post_wizard.handle_target_channel_selection(update, context)
    
    elif data == "final_post":
        return await post_wizard.finalize_post(update, context)

# ==============================================================================
# 🔐 POST VERIFICATION SYSTEM
# ==============================================================================

async def handle_post_verification(update: Update, context: ContextTypes.DEFAULT_TYPE, post_id: int):
    query = update.callback_query
    user = query.from_user
    
    # Get post details
    post = db.get_post(post_id)
    if not post:
        await query.answer("❌ Post not found!", show_alert=True)
        return
    
    # Check if user has already been granted access
    if db.has_user_access(user.id, post_id):
        # User already has access, show watch button
        await show_watch_button(query, post_id)
        return
    
    # Check membership for force channels
    force_channels = post.get('force_channels', [])
    if force_channels:
        result = await security.check_membership(user.id, context.bot, force_channels)
        
        if not result['all_joined']:
            # User hasn't joined all channels
            await query.answer(
                Config.VERIFICATION_MESSAGES['not_joined_popup'], 
                show_alert=True
            )
            
            # Show join buttons
            join_buttons = []
            for channel in result['missing']:
                join_buttons.append([
                    InlineKeyboardButton(
                        f"📢 Join {channel['name']}", 
                        url=channel['link']
                    )
                ])
            
            join_buttons.append([
                InlineKeyboardButton(
                    "✅ Verify Again", 
                    callback_data=f"verify_post_{post_id}"
                )
            ])
            
            try:
                await query.edit_message_reply_markup(
                    InlineKeyboardMarkup(join_buttons)
                )
            except:
                pass
            
            return
        else:
            # User has joined all channels
            await query.answer(
                Config.VERIFICATION_MESSAGES['joined_popup'], 
                show_alert=True
            )
    
    # Grant access and show watch button
    db.grant_user_access(user.id, post_id)
    await show_watch_button(query, post_id)

async def show_watch_button(query, post_id):
    # Create WATCH NOW button
    watch_button = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            Config.VERIFICATION_MESSAGES['watch_button_text'],
            callback_data=f"watch_now_{post_id}"
        )]
    ])
    
    try:
        await query.edit_message_reply_markup(watch_button)
    except Exception as e:
        logger.error(f"Error updating button: {e}")

async def handle_watch_now(update: Update, context: ContextTypes.DEFAULT_TYPE, post_id: int):
    query = update.callback_query
    user = query.from_user
    
    # Check if user has access
    if not db.has_user_access(user.id, post_id):
        await query.answer("❌ Access denied! Please verify first.", show_alert=True)
        return
    
    # Get post details
    post = db.get_post(post_id)
    if not post:
        await query.answer("❌ Post not found!", show_alert=True)
        return
    
    # Get watch URL
    watch_url = post.get('watch_url', db.get_config('watch_url'))
    
    if not watch_url:
        await query.answer("❌ Watch URL not set!", show_alert=True)
        return
    
    # Create final buttons with watch URL
    final_buttons = []
    
    # Add post buttons if any
    if post.get('buttons'):
        for btn in post['buttons']:
            final_buttons.append([
                InlineKeyboardButton(btn['name'], url=btn['link'])
            ])
    
    # Add watch button
    final_buttons.append([
        InlineKeyboardButton(
            Config.VERIFICATION_MESSAGES['watch_button_text'],
            url=watch_url
        )
    ])
    
    final_keyboard = InlineKeyboardMarkup(final_buttons)
    
    # Send access granted message
    await query.answer(Config.VERIFICATION_MESSAGES['access_granted'], show_alert=True)
    
    # Update the message with final buttons
    try:
        caption = f"<b>{post['title']}</b>\n\n"
        if post.get('post_text'):
            caption += f"{post['post_text']}\n\n"
        caption += "✅ <i>Access granted! Click the button below to watch.</i>"
        
        if post.get('photo_id'):
            await context.bot.send_photo(
                chat_id=user.id,
                photo=post['photo_id'],
                caption=caption,
                reply_markup=final_keyboard,
                parse_mode=ParseMode.HTML
            )
        else:
            await context.bot.send_message(
                chat_id=user.id,
                text=caption,
                reply_markup=final_keyboard,
                parse_mode=ParseMode.HTML
            )
    except Exception as e:
        logger.error(f"Error sending content: {e}")
        await query.answer("❌ Error sending content!", show_alert=True)

# ==============================================================================
# ✏️ SIMPLE HANDLERS
# ==============================================================================

async def edit_config_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = context.user_data.get('edit_key')
    if db.set_config(key, update.message.text):
        await update.message.reply_text(f"✅ {key} updated!")
    return ConversationHandler.END

async def add_channel_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['cid'] = update.message.text
    await update.message.reply_text("📝 Send Channel Name:")
    return Config.STATE_CHANNEL_ADD_NAME

async def add_channel_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['cname'] = update.message.text
    await update.message.reply_text("🔗 Send Channel Link:")
    return Config.STATE_CHANNEL_ADD_LINK

async def add_channel_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db.add_channel(context.user_data['cid'], context.user_data['cname'], update.message.text)
    await update.message.reply_text("✅ Channel Added!")
    return ConversationHandler.END

async def cancel_op(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Cancelled.")
    return ConversationHandler.END

# ==============================================================================
# 🚀 APP SETUP
# ==============================================================================

def main():
    app = ApplicationBuilder().token(Config.TOKEN).build()
    
    # Handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("admin", admin_command))
    
    # Enhanced Post Wizard
    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(callback_handler, pattern='^create_post_start$')],
        states={
            Config.STATE_POST_TITLE: [MessageHandler(filters.TEXT, post_wizard.handle_title)],
            Config.STATE_POST_PHOTO: [MessageHandler(filters.PHOTO, post_wizard.handle_photo)],
            Config.STATE_POST_TEXT: [MessageHandler(filters.TEXT, post_wizard.handle_text)],
            Config.STATE_POST_BUTTONS: [
                MessageHandler(filters.TEXT, post_wizard.handle_watch_url),
                CallbackQueryHandler(post_wizard.handle_button_management)
            ],
            Config.STATE_POST_BUTTON_NAME: [MessageHandler(filters.TEXT, post_wizard.handle_button_name)],
            Config.STATE_POST_BUTTON_LINK: [MessageHandler(filters.TEXT, post_wizard.handle_button_link)],
            Config.STATE_POST_FORCE_CHANNELS: [CallbackQueryHandler(callback_handler, pattern='^(select_force_|select_all_force|continue_force)')],
            Config.STATE_POST_TARGET_CHANNEL: [CallbackQueryHandler(callback_handler, pattern='^select_target_')],
            Config.STATE_POST_CONFIRM: [CallbackQueryHandler(callback_handler, pattern='^final_post$')]
        },
        fallbacks=[CommandHandler('cancel', cancel_op)]
    ))
    
    # Edit Config
    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(callback_handler, pattern='^edit_')],
        states={Config.STATE_EDIT_MESSAGE: [MessageHandler(filters.TEXT, edit_config_handler)]},
        fallbacks=[CommandHandler('cancel', cancel_op)]
    ))
    
    # Add Channel
    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(callback_handler, pattern='^add_channel$')],
        states={
            Config.STATE_CHANNEL_ADD_ID: [MessageHandler(filters.TEXT, add_channel_id)],
            Config.STATE_CHANNEL_ADD_NAME: [MessageHandler(filters.TEXT, add_channel_name)],
            Config.STATE_CHANNEL_ADD_LINK: [MessageHandler(filters.TEXT, add_channel_link)]
        },
        fallbacks=[CommandHandler('cancel', cancel_op)]
    ))
    
    # Post verification handlers
    app.add_handler(CallbackQueryHandler(callback_handler, pattern='^verify_post_'))
    app.add_handler(CallbackQueryHandler(callback_handler, pattern='^watch_now_'))
    
    # General callback handler
    app.add_handler(CallbackQueryHandler(callback_handler))
    
    print("🤖 Bot Started with Enhanced Verification System...")
    app.run_polling()

if __name__ == "__main__":
    main()
