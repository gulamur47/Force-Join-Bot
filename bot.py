"""
================================================================================
SUPREME GOD BOT - ULTIMATE EDITION v11.0
FULLY WORKING WITH ALL FEATURES + MULTIPLE BUTTONS + ENHANCED POPUPS
BOT.BUILDER.CO OPTIMIZED - STABLE & COMPLETE
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
from typing import List, Dict, Optional, Tuple
from datetime import datetime

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
    # Bot Token - Environment variable থেকে নিবে
    TOKEN = os.environ.get("BOT_TOKEN", "8505466956:AAEubWZLvC-9EumA0b95VxOJlka7ye-RvMk")
    ADMIN_IDS = {int(x) for x in os.environ.get("ADMIN_IDS", "8013042180").split(",")}
    
    # Video Downloader Bot
    VIDEO_BOT_USERNAME = "@viralvideo2026_46_bot"
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
    STATE_POST_BUTTONS_MENU = 4
    STATE_POST_BUTTON_NAME = 5
    STATE_POST_BUTTON_LINK = 6
    STATE_POST_FORCE_CHANNELS = 7
    STATE_POST_TARGET_CHANNELS = 8
    STATE_POST_CONFIRM = 9
    
    STATE_CHANNEL_MANAGEMENT = 10
    STATE_CHANNEL_ADD_ID = 11
    STATE_CHANNEL_ADD_NAME = 12
    STATE_CHANNEL_ADD_LINK = 13
    STATE_EDIT_MESSAGE = 14
    STATE_WELCOME_PHOTO = 15
    STATE_EDIT_CHANNEL = 16
    STATE_BROADCAST = 17
    
    # Popup Messages - Romantic/Hot Love Style
    POPUP_MESSAGES = {
        'verified_success': "Uffff 😍 Tumi verified ❤️ Next surprise unlock 🔥",
        'verified_failed': "Awww 😘 Age sob channel join koro baby 💔",
        'watch_now_locked': "Awww 😘 Age sob channel join koro baby 💔",
        'access_granted': "🎉 Ufff! Access granted baby! 😍 Now enjoy the content! 💋",
        'channel_joined': "💖 OMG! You joined all channels! 😘 Now click Verified! 🔥",
        'post_published': "✅ Post published successfully! All buttons are live! 🚀",
        'button_added': "✅ Button added! Add more or continue! 🔘",
        'channel_added': "✅ Channel added successfully! 📢",
        'channel_deleted': "🗑️ Channel deleted!",
        'welcome_photo_set': "🖼️ Welcome photo set! Users will see this first! 💕",
        'admin_denied': "🚫 Access denied! Only admins can access this!",
        'operation_cancelled': "❌ Operation cancelled!",
        'post_created': "🎯 Post created successfully! Users can verify to unlock! 🔒"
    }
    
    # Emojis for romantic/hot love theme
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
        "target": "🎯",
        "photo": "🖼️",
        "edit": "✏️",
        "delete": "🗑️",
        "telegram": "📱",
        "kiss": "💋",
        "hot": "🥵",
        "smirk": "😏",
        "angel": "😇",
        "devil": "😈",
        "sparkles": "✨",
        "diamond": "💎",
        "rose": "🌹",
        "gift": "🎁",
        "party": "🎉",
        "thunder": "⚡",
        "boom": "💥",
        "lipstick": "💄",
        "ring": "💍",
        "cherry": "🍒",
        "peach": "🍑",
        "eggplant": "🍆",
        "water": "💦"
    }

# ==============================================================================
# 📝 LOGGING
# ==============================================================================

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot_ultimate.log')
    ]
)
logger = logging.getLogger(__name__)

# ==============================================================================
# 🗄️ ENHANCED DATABASE MANAGER
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
                conn.execute("PRAGMA journal_mode=WAL")
                conn.execute("PRAGMA synchronous=NORMAL")
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
                is_blocked BOOLEAN DEFAULT 0,
                verified BOOLEAN DEFAULT 0,
                verified_date DATETIME
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
                target_channels TEXT,
                created_by INTEGER,
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                video_bot_link TEXT,
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
        
        # Welcome photo
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS welcome_photo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                photo_id TEXT,
                added_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Initialize defaults
        self.initialize_defaults()
        conn.commit()
        logger.info("Database initialized successfully")
    
    def initialize_defaults(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Default config with romantic messages
        defaults = [
            ('welcome_message', '''{heart} {fire} <b>💖✨ওগো শুনছো! স্বাগতম জানাই তোমাকে!💖✨</b> {fire} {heart}

{star} <b>❤️তুমি অবশ্যই আমাদের মাঝে এসেছো, আমার হৃদয়টা আনন্দে নেচে উঠলো! 😍💃
তোমাকে ছাড়া আমাদের এই আয়োজন অসম্পূর্ণ ছিল।</b>

{star} <b>💖✨তোমার জন্য যা যা থাকছে::</b>
🎀 এক্সক্লুসিভ ভাইরাল ভিডিও 🔞
🎀 নতুন সব কালেকশন 🔥
🎀 এবং আমার হৃদয়ের ভালোবাসা... ❤️

{link} <b>নিচের Verified বাটনে ক্লিক করে শুরু করুন:</b>'''),
            
            ('lock_message', '''{lock} <b>অ্যাক্সেস লক করা আছে!</b>

{cross} 😢💔ওহ নো বেবি! তুমি এখনো জয়েন করোনি? আমার লক্ষ্মীটা, তুমি যদি নিচের চ্যানেলগুলোতে জয়েন না করো, তাহলে আমি তোমাকে ভিডিওটা দেখাতে পারবো না! 🥺🥀
প্লিজ সোনা, রাগ করো না!

{info} নিচের সবগুলোতে জয়েন করে💖✨ {check} Verified বাটনে ক্লিক করুন। আমি অপেক্ষা করছি... 😘❤️'''),
            
            ('auto_delete', '60'),
            ('video_bot_link', Config.VIDEO_BOT_LINK),
            ('verified_popup_success', Config.POPUP_MESSAGES['verified_success']),
            ('verified_popup_failed', Config.POPUP_MESSAGES['verified_failed']),
            ('watch_now_locked', Config.POPUP_MESSAGES['watch_now_locked'])
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
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO users 
                (user_id, username, first_name, last_name, last_active)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, username, first_name, last_name))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding user: {e}")
            return False
    
    def update_user_activity(self, user_id):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE user_id = ?', (user_id,))
            conn.commit()
        except Exception as e:
            logger.error(f"Error updating user activity: {e}")
    
    def get_user(self, user_id):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    def set_user_verified(self, user_id):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users SET verified = 1, verified_date = CURRENT_TIMESTAMP 
                WHERE user_id = ?
            ''', (user_id,))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error setting user verified: {e}")
            return False
    
    def is_user_verified(self, user_id):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT verified FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            return result[0] == 1 if result else False
        except Exception as e:
            logger.error(f"Error checking user verified: {e}")
            return False
    
    def get_all_users(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users ORDER BY join_date DESC LIMIT 100')
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
    
    # === Channel Management ===
    def get_channels(self, force_only=False, active_only=True):
        try:
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
        except Exception as e:
            logger.error(f"Error getting channels: {e}")
            return []
    
    def get_channel(self, channel_id):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM channels WHERE channel_id = ?', (str(channel_id),))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting channel: {e}")
            return None
    
    def add_channel(self, channel_id, name, link, force_join=True):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO channels (channel_id, name, link, force_join)
                VALUES (?, ?, ?, ?)
            ''', (str(channel_id), name, link, force_join))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding channel: {e}")
            return False
    
    def update_channel(self, channel_id, name=None, link=None, force_join=None):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            updates = []
            params = []
            
            if name is not None:
                updates.append("name = ?")
                params.append(name)
            if link is not None:
                updates.append("link = ?")
                params.append(link)
            if force_join is not None:
                updates.append("force_join = ?")
                params.append(force_join)
            
            if not updates:
                return False
            
            params.append(str(channel_id))
            query = f"UPDATE channels SET {', '.join(updates)} WHERE channel_id = ?"
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating channel: {e}")
            return False
    
    def delete_channel(self, channel_id):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM channels WHERE channel_id = ?", (str(channel_id),))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting channel: {e}")
            return False
    
    def toggle_force_join(self, channel_id):
        try:
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
        except Exception as e:
            logger.error(f"Error toggling force join: {e}")
            return False
    
    # === Config Management ===
    def get_config(self, key, default=""):
        try:
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
        except Exception as e:
            logger.error(f"Error getting config: {e}")
            return default
    
    def set_config(self, key, value):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO config (key, value)
                VALUES (?, ?)
            ''', (key, value))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error setting config: {e}")
            return False
    
    # === Welcome Photo Management ===
    def set_welcome_photo(self, photo_id):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM welcome_photo')
            cursor.execute('INSERT INTO welcome_photo (photo_id) VALUES (?)', (photo_id,))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error setting welcome photo: {e}")
            return False
    
    def get_welcome_photo(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT photo_id FROM welcome_photo ORDER BY id DESC LIMIT 1')
            result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error getting welcome photo: {e}")
            return None
    
    def remove_welcome_photo(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM welcome_photo')
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error removing welcome photo: {e}")
            return False
    
    # === Post Management ===
    def save_post(self, title, photo_id, post_text, buttons, force_channels, target_channels, created_by, video_bot_link=""):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            video_bot_link = video_bot_link or Config.VIDEO_BOT_LINK
            
            cursor.execute('''
                INSERT INTO posts (title, photo_id, post_text, buttons, force_channels, target_channels, created_by, video_bot_link)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (title, photo_id, post_text, json.dumps(buttons), 
                  json.dumps(force_channels), json.dumps(target_channels), created_by, video_bot_link))
            
            post_id = cursor.lastrowid
            conn.commit()
            return post_id
        except Exception as e:
            logger.error(f"Error saving post: {e}")
            return None
    
    def get_post(self, post_id):
        try:
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
                if post.get('target_channels'):
                    post['target_channels'] = json.loads(post['target_channels'])
                return post
            return None
        except Exception as e:
            logger.error(f"Error getting post: {e}")
            return None
    
    def get_all_posts(self, limit=20):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM posts ORDER BY created_date DESC LIMIT ?', (limit,))
            rows = cursor.fetchall()
            posts = []
            for row in rows:
                post = dict(row)
                if post.get('buttons'):
                    post['buttons'] = json.loads(post['buttons'])
                if post.get('force_channels'):
                    post['force_channels'] = json.loads(post['force_channels'])
                if post.get('target_channels'):
                    post['target_channels'] = json.loads(post['target_channels'])
                posts.append(post)
            return posts
        except Exception as e:
            logger.error(f"Error getting all posts: {e}")
            return []
    
    def get_video_bot_link(self, post_id):
        post = self.get_post(post_id)
        return post.get('video_bot_link', Config.VIDEO_BOT_LINK) if post else Config.VIDEO_BOT_LINK
    
    # === User Access Management ===
    def grant_user_access(self, user_id, post_id):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO user_access (user_id, post_id, access_granted, access_date)
                VALUES (?, ?, 1, CURRENT_TIMESTAMP)
            ''', (user_id, post_id))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error granting user access: {e}")
            return False
    
    def has_user_access(self, user_id, post_id):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT access_granted FROM user_access WHERE user_id = ? AND post_id = ?', (user_id, post_id))
            result = cursor.fetchone()
            return result[0] == 1 if result else False
        except Exception as e:
            logger.error(f"Error checking user access: {e}")
            return False
    
    # === Statistics ===
    def get_stats(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            stats = {}
            cursor.execute("SELECT COUNT(*) FROM users")
            stats['total_users'] = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM users WHERE DATE(join_date) = DATE('now')")
            stats['today_users'] = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM users WHERE verified = 1")
            stats['verified_users'] = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM channels WHERE is_active = 1")
            stats['active_channels'] = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM channels WHERE force_join = 1 AND is_active = 1")
            stats['force_channels'] = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM posts")
            stats['total_posts'] = cursor.fetchone()[0]
            return stats
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}

db = DatabaseManager()

# ==============================================================================
# 🎨 ENHANCED UI MANAGER WITH ROMANTIC THEME
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
    def create_keyboard(buttons, add_back=True, add_close=True):
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
                {"text": "📝 Add Post", "callback": "create_post_start"},
                {"text": "📢 Channel Manager", "callback": "menu_channels"}
            ],
            [
                {"text": "🖼️ Welcome Photo", "callback": "menu_welcome_photo"},
                {"text": "✏️ Messages", "callback": "menu_messages"}
            ],
            [
                {"text": "📊 Statistics", "callback": "menu_stats"},
                {"text": "👥 Users", "callback": "menu_users"}
            ],
            [
                {"text": "⚙️ Settings", "callback": "menu_settings"},
                {"text": "🚀 Broadcast", "callback": "broadcast_start"}
            ]
        ]
        return UIManager.create_keyboard(buttons, add_back=False, add_close=True)
    
    @staticmethod
    def create_channel_buttons(channels, prefix="select_channel", include_edit=True):
        buttons = []
        row = []
        for i, channel in enumerate(channels):
            if include_edit:
                row.append({
                    "text": f"📢 {channel['name'][:15]}",
                    "callback": f"view_channel_{channel['channel_id']}"
                })
            else:
                row.append({
                    "text": f"📢 {channel['name'][:15]}",
                    "callback": f"{prefix}_{channel['channel_id']}"
                })
            if len(row) == 2 or i == len(channels) - 1:
                buttons.append(row)
                row = []
        return buttons
    
    @staticmethod
    def create_channel_management_buttons(channel_id):
        buttons = [
            [
                {"text": "✏️ Edit Name", "callback": f"edit_channel_name_{channel_id}"},
                {"text": "✏️ Edit Link", "callback": f"edit_channel_link_{channel_id}"}
            ],
            [
                {"text": "✅ Toggle Force", "callback": f"toggle_channel_force_{channel_id}"},
                {"text": "🗑️ Delete", "callback": f"delete_channel_{channel_id}"}
            ],
            [
                {"text": "🔙 Back to Channels", "callback": "menu_channels"}
            ]
        ]
        return UIManager.create_keyboard(buttons, add_back=False, add_close=True)
    
    @staticmethod
    def create_post_buttons(buttons_list, include_verify=True, post_id=None):
        keyboard = []
        
        # Add custom buttons
        row = []
        for i, btn in enumerate(buttons_list):
            row.append(InlineKeyboardButton(btn['name'], url=btn['link']))
            if len(row) == 2 or i == len(buttons_list) - 1:
                keyboard.append(row)
                row = []
        
        # Add verify button if needed
        if include_verify and post_id:
            keyboard.append([InlineKeyboardButton("✅ Verified ❤️", callback_data=f"verify_post_{post_id}")])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_watch_now_button(post_id):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("▶️ Watch Now 🔥", callback_data=f"watch_now_{post_id}")]
        ])

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
            if time.time() - cached_time < 30:
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
        keys_to_remove = [k for k in self.verification_cache.keys() if k.startswith(f"membership_{user_id}_")]
        for key in keys_to_remove:
            del self.verification_cache[key]
    
    def clear_post_cache(self, post_id):
        keys_to_remove = [k for k in self.verification_cache.keys() if f"post_{post_id}" in k]
        for key in keys_to_remove:
            del self.verification_cache[key]

security = SecurityManager()

# ==============================================================================
# 🎯 POST WIZARD WITH MULTIPLE BUTTONS
# ==============================================================================

class PostWizard:
    def __init__(self):
        self.active_wizards = {}
    
    async def start_wizard(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        user = query.from_user
        
        if user.id not in Config.ADMIN_IDS:
            await query.answer(Config.POPUP_MESSAGES['admin_denied'], show_alert=True)
            return ConversationHandler.END
        
        self.active_wizards[user.id] = {
            'step': 'title',
            'data': {
                'buttons': [],
                'force_channels': [],
                'target_channels': [],
                'video_bot_link': Config.VIDEO_BOT_LINK
            }
        }
        
        await query.answer()
        await query.edit_message_text(
            "📝 <b>Step 1/8: Post Title</b>\n\n"
            "✏️ Please send the <b>POST TITLE</b>:",
            parse_mode=ParseMode.HTML
        )
        return Config.STATE_POST_TITLE
    
    async def handle_title(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if user.id not in self.active_wizards:
            await update.message.reply_text("❌ Session expired.")
            return ConversationHandler.END
        
        title = update.message.text
        self.active_wizards[user.id]['data']['title'] = title
        self.active_wizards[user.id]['step'] = 'photo'
        
        await update.message.reply_text(
            "📸 <b>Step 2/8: Post Media</b>\n\n"
            "🖼️ Please send a <b>PHOTO</b> (or type /skip):",
            parse_mode=ParseMode.HTML
        )
        return Config.STATE_POST_PHOTO
    
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if user.id not in self.active_wizards:
            return ConversationHandler.END
        
        if update.message.text and update.message.text.lower() == '/skip':
            self.active_wizards[user.id]['data']['photo_id'] = ""
            self.active_wizards[user.id]['step'] = 'text'
            await update.message.reply_text(
                "📝 <b>Step 3/8: Post Text</b>\n\n"
                "💬 Please send the <b>POST TEXT</b> (or type /skip):",
                parse_mode=ParseMode.HTML
            )
            return Config.STATE_POST_TEXT
        elif update.message.photo:
            photo_id = update.message.photo[-1].file_id
            self.active_wizards[user.id]['data']['photo_id'] = photo_id
            self.active_wizards[user.id]['step'] = 'text'
            
            await update.message.reply_text(
                "📝 <b>Step 3/8: Post Text</b>\n\n"
                "💬 Please send the <b>POST TEXT</b> (or type /skip):",
                parse_mode=ParseMode.HTML
            )
            return Config.STATE_POST_TEXT
        else:
            await update.message.reply_text("❌ Please send a photo or type /skip!")
            return Config.STATE_POST_PHOTO
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if user.id not in self.active_wizards:
            return ConversationHandler.END
        
        if update.message.text and update.message.text.lower() != '/skip':
            self.active_wizards[user.id]['data']['post_text'] = update.message.text
        else:
            self.active_wizards[user.id]['data']['post_text'] = ""
        
        self.active_wizards[user.id]['step'] = 'buttons_menu'
        return await self.show_buttons_menu(update, context, user)
    
    async def show_buttons_menu(self, update, context, user):
        buttons = self.active_wizards[user.id]['data']['buttons']
        
        if buttons:
            preview = "📋 <b>Current Buttons:</b>\n"
            for i, btn in enumerate(buttons, 1):
                preview += f"{i}. {btn['name']}\n"
        else:
            preview = "📭 <b>No buttons added yet.</b>"
        
        keyboard_buttons = [
            [{"text": "➕ Add Button", "callback": "add_button"}],
            [{"text": "➡️ Continue", "callback": "continue_buttons"}]
        ]
        
        keyboard = ui.create_keyboard(keyboard_buttons, add_back=True, add_close=True)
        
        await update.message.reply_text(
            f"🔘 <b>Step 4/8: Button Management</b>\n\n{preview}\n\n"
            "Click 'Add Button' to add multiple buttons:",
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
        return Config.STATE_POST_BUTTONS_MENU
    
    async def handle_buttons_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        user = query.from_user
        
        if user.id not in self.active_wizards:
            await query.answer("❌ Session expired!")
            return ConversationHandler.END
        
        data = query.data
        
        if data == "add_button":
            await query.edit_message_text(
                "🔘 <b>Add Button - Step 1/2</b>\n\n"
                "✏️ Please send the <b>BUTTON NAME</b>:",
                parse_mode=ParseMode.HTML
            )
            return Config.STATE_POST_BUTTON_NAME
        
        elif data == "continue_buttons":
            self.active_wizards[user.id]['step'] = 'force_channels'
            await self.show_force_channels(update, context, user)
            return Config.STATE_POST_FORCE_CHANNELS
        
        return Config.STATE_POST_BUTTONS_MENU
    
    async def show_force_channels(self, update, context, user):
        force_channels = db.get_channels(force_only=True, active_only=True)
        
        if not force_channels:
            await update.callback_query.edit_message_text(
                "🎯 <b>Step 5/8: Force Channels</b>\n\n"
                "❌ No force channels found. Skipping...",
                parse_mode=ParseMode.HTML
            )
            self.active_wizards[user.id]['step'] = 'target_channels'
            await self.show_target_channels(update, context, user)
            return
        
        channel_buttons = ui.create_channel_buttons(force_channels, prefix="select_force", include_edit=False)
        channel_buttons.append([
            {"text": "✅ Select All", "callback": "select_all_force"},
            {"text": "➡️ Continue", "callback": "continue_force"}
        ])
        
        keyboard = ui.create_keyboard(channel_buttons, add_back=True, add_close=True)
        
        await update.callback_query.edit_message_text(
            "🎯 <b>Step 5/8: Force Channels</b>\n\n"
            "Select channels users MUST join to access content:",
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
    
    async def handle_button_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if user.id not in self.active_wizards:
            return ConversationHandler.END
        
        context.user_data['temp_btn_name'] = update.message.text
        await update.message.reply_text(
            "🔗 <b>Add Button - Step 2/2</b>\n\n"
            "🌐 Send the <b>BUTTON LINK</b>:",
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
        
        await update.message.reply_text(
            Config.POPUP_MESSAGES['button_added'],
            parse_mode=ParseMode.HTML
        )
        return await self.show_buttons_menu(update, context, user)
    
    async def handle_force_channel_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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
            self.active_wizards[user.id]['step'] = 'target_channels'
            await self.show_target_channels(update, context, user)
            return Config.STATE_POST_TARGET_CHANNELS
        
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
        
        await query.edit_message_reply_markup(
            ui.create_keyboard(channel_buttons, add_back=True, add_close=True)
        )
        return Config.STATE_POST_FORCE_CHANNELS
    
    async def show_target_channels(self, update, context, user):
        all_channels = db.get_channels(active_only=True)
        
        if not all_channels:
            await update.callback_query.edit_message_text(
                "❌ No channels found to post!",
                parse_mode=ParseMode.HTML
            )
            return ConversationHandler.END
        
        channel_buttons = ui.create_channel_buttons(all_channels, prefix="select_target", include_edit=False)
        channel_buttons.append([
            {"text": "✅ Select All", "callback": "select_all_target"},
            {"text": "➡️ Continue", "callback": "continue_target"}
        ])
        
        keyboard = ui.create_keyboard(channel_buttons, add_back=True, add_close=True)
        
        await update.callback_query.edit_message_text(
            "📤 <b>Step 6/8: Target Channels</b>\n\n"
            "Select channels where this post will be published:",
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
    
    async def handle_target_channel_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        user = query.from_user
        
        if user.id not in self.active_wizards:
            return ConversationHandler.END
        
        data = query.data
        
        if data == "select_all_target":
            all_channels = db.get_channels(active_only=True)
            self.active_wizards[user.id]['data']['target_channels'] = [ch['channel_id'] for ch in all_channels]
            await query.answer("✅ Selected All")
            
        elif data.startswith("select_target_"):
            cid = data.replace("select_target_", "")
            current = self.active_wizards[user.id]['data']['target_channels']
            if cid in current:
                current.remove(cid)
                await query.answer("❌ Deselected")
            else:
                current.append(cid)
                await query.answer("✅ Selected")
        
        elif data == "continue_target":
            if not self.active_wizards[user.id]['data']['target_channels']:
                await query.answer("❌ Select at least one channel!", show_alert=True)
                return Config.STATE_POST_TARGET_CHANNELS
            
            # Show preview
            return await self.show_preview(update, context, user)
        
        # Refresh buttons
        all_channels = db.get_channels(active_only=True)
        channel_buttons = []
        row = []
        for i, ch in enumerate(all_channels):
            is_sel = ch['channel_id'] in self.active_wizards[user.id]['data']['target_channels']
            emoji = "✅" if is_sel else "📢"
            row.append({"text": f"{emoji} {ch['name'][:12]}", "callback": f"select_target_{ch['channel_id']}"})
            if len(row) == 2 or i == len(all_channels) - 1:
                channel_buttons.append(row)
                row = []
        
        selected_count = len(self.active_wizards[user.id]['data']['target_channels'])
        channel_buttons.append([
            {"text": "✅ Select All", "callback": "select_all_target"},
            {"text": f"➡️ Continue ({selected_count})", "callback": "continue_target"}
        ])
        
        await query.edit_message_reply_markup(
            ui.create_keyboard(channel_buttons, add_back=True, add_close=True)
        )
        return Config.STATE_POST_TARGET_CHANNELS
    
    async def show_preview(self, update, context, user):
        data = self.active_wizards[user.id]['data']
        
        # Create preview text
        preview = "🎯 <b>POST PREVIEW</b>\n\n"
        preview += f"📝 <b>Title:</b> {data['title']}\n"
        preview += f"📸 <b>Media:</b> {'✅ Yes' if data.get('photo_id') else '❌ No'}\n"
        preview += f"💬 <b>Text:</b> {'✅ Yes' if data.get('post_text') else '❌ No'}\n"
        preview += f"🔘 <b>Buttons:</b> {len(data['buttons'])}\n"
        preview += f"🎯 <b>Force Channels:</b> {len(data['force_channels'])}\n"
        preview += f"📤 <b>Target Channels:</b> {len(data['target_channels'])}\n\n"
        
        # Show buttons preview
        if data['buttons']:
            preview += "📋 <b>Button List:</b>\n"
            for i, btn in enumerate(data['buttons'], 1):
                preview += f"{i}. {btn['name']}\n"
        
        # Send media preview if exists
        if data.get('photo_id'):
            try:
                await context.bot.send_photo(
                    chat_id=user.id,
                    photo=data['photo_id'],
                    caption=preview,
                    parse_mode=ParseMode.HTML
                )
            except:
                await update.callback_query.edit_message_text(preview, parse_mode=ParseMode.HTML)
        else:
            await update.callback_query.edit_message_text(preview, parse_mode=ParseMode.HTML)
        
        # Add confirmation buttons
        keyboard_buttons = [
            [{"text": "🚀 Publish Now", "callback": "final_post"}],
            [{"text": "✏️ Edit Post", "callback": "edit_post_preview"}]
        ]
        keyboard = ui.create_keyboard(keyboard_buttons, add_back=True, add_close=True)
        
        await update.callback_query.message.reply_text(
            "⚠️ <b>FINAL CONFIRMATION</b>\n\n"
            "Click 'Publish Now' to publish or 'Edit Post' to make changes:",
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
        return Config.STATE_POST_CONFIRM
    
    async def finalize_post(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        user = query.from_user
        
        if user.id not in self.active_wizards:
            await query.answer("❌ Session expired!")
            return ConversationHandler.END
        
        data = self.active_wizards[user.id]['data']
        
        # Save post to database
        post_id = db.save_post(
            data['title'],
            data.get('photo_id', ''),
            data.get('post_text', ''),
            data['buttons'],
            data['force_channels'],
            data['target_channels'],
            user.id,
            data.get('video_bot_link', Config.VIDEO_BOT_LINK)
        )
        
        if post_id:
            # Create post caption
            caption = f"<b>{data['title']}</b>\n\n"
            if data.get('post_text'):
                caption += f"{data['post_text']}\n\n"
            caption += "🔒 <i>Content locked. Click 'Verified ❤️' to unlock!</i>"
            
            # Create keyboard with verify button
            keyboard = ui.create_post_buttons(data['buttons'], include_verify=True, post_id=post_id)
            
            # Send to all target channels
            success_count = 0
            for channel_id in data['target_channels']:
                try:
                    if data.get('photo_id'):
                        await context.bot.send_photo(
                            chat_id=channel_id,
                            photo=data['photo_id'],
                            caption=caption,
                            reply_markup=keyboard,
                            parse_mode=ParseMode.HTML
                        )
                    else:
                        await context.bot.send_message(
                            chat_id=channel_id,
                            text=caption,
                            reply_markup=keyboard,
                            parse_mode=ParseMode.HTML
                        )
                    success_count += 1
                except Exception as e:
                    logger.error(f"Error posting to channel {channel_id}: {e}")
            
            await query.edit_message_text(
                f"✅ <b>Post Published Successfully!</b>\n\n"
                f"📊 <b>Post ID:</b> {post_id}\n"
                f"📤 <b>Channels:</b> {success_count}/{len(data['target_channels'])}\n"
                f"🔘 <b>Buttons:</b> {len(data['buttons'])}\n"
                f"🎯 <b>Force Channels:</b> {len(data['force_channels'])}",
                parse_mode=ParseMode.HTML
            )
            
            # Clear cache
            security.clear_post_cache(post_id)
            
        else:
            await query.answer("❌ Database Error!", show_alert=True)
        
        # Clean up
        if user.id in self.active_wizards:
            del self.active_wizards[user.id]
        
        return ConversationHandler.END

post_wizard = PostWizard()

# ==============================================================================
# 🎮 USER COMMAND HANDLERS
# ==============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        
        # Add user to database
        db.add_user(user.id, user.username, user.first_name, user.last_name or "")
        db.update_user_activity(user.id)
        
        # Check if user is blocked
        user_data = db.get_user(user.id)
        if user_data and user_data.get('is_blocked'):
            await update.message.reply_text("🚫 Restricted Access.")
            return
        
        # Get welcome photo
        welcome_photo = db.get_welcome_photo()
        
        # Get force channels
        force_channels = db.get_channels(force_only=True, active_only=True)
        
        # Create welcome message
        welcome_msg = db.get_config('welcome_message')
        formatted_msg = ui.format_text(welcome_msg, user)
        
        # Create buttons
        buttons = []
        if force_channels:
            for channel in force_channels:
                buttons.append([{"text": f"📢 Join {channel['name']}", "url": channel['link']}])
        
        buttons.append([{"text": "✅ Verified ❤️", "callback": "verify_membership"}])
        
        # Send welcome message
        if welcome_photo:
            try:
                await update.message.reply_photo(
                    photo=welcome_photo,
                    caption=formatted_msg,
                    reply_markup=ui.create_keyboard(buttons, add_back=False, add_close=False),
                    parse_mode=ParseMode.HTML
                )
                return
            except:
                pass
        
        await update.message.reply_text(
            formatted_msg,
            reply_markup=ui.create_keyboard(buttons, add_back=False, add_close=False),
            parse_mode=ParseMode.HTML
        )
        
    except Exception as e:
        logger.error(f"Error in start_command: {e}")
        await update.message.reply_text("⚠️ An error occurred. Please try again.")

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    if user.id not in Config.ADMIN_IDS:
        await update.message.reply_text("🚫 Access denied!")
        return
    
    await update.message.reply_text(
        "👑 <b>Admin Panel</b>\n\n"
        "Select an option from below:",
        reply_markup=ui.get_admin_menu(),
        parse_mode=ParseMode.HTML
    )

# ==============================================================================
# 🔄 CALLBACK HANDLER
# ==============================================================================

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        user = query.from_user
        data = query.data
        
        await query.answer()
        
        db.update_user_activity(user.id)
        
        # ========== USER SIDE HANDLERS ==========
        
        # Membership verification
        if data == "verify_membership":
            await handle_membership_verification(update, context, user)
        
        # Post verification
        elif data.startswith("verify_post_"):
            post_id = int(data.replace("verify_post_", ""))
            await handle_post_verification(update, context, user, post_id)
        
        # Watch now button
        elif data.startswith("watch_now_"):
            post_id = int(data.replace("watch_now_", ""))
            await handle_watch_now(update, context, user, post_id)
        
        # ========== ADMIN SIDE HANDLERS ==========
        
        # Main menu
        elif data == "main_menu":
            if user.id in Config.ADMIN_IDS:
                await query.edit_message_text(
                    "👑 <b>Admin Panel</b>\n\nSelect an option:",
                    reply_markup=ui.get_admin_menu(),
                    parse_mode=ParseMode.HTML
                )
        
        # Close panel
        elif data == "close_panel":
            try:
                await query.message.delete()
            except:
                pass
        
        # Create post start
        elif data == "create_post_start":
            return await post_wizard.start_wizard(update, context)
        
        # Channel management
        elif data == "menu_channels":
            await handle_channel_management(update, context, user)
        
        # Welcome photo menu
        elif data == "menu_welcome_photo":
            await handle_welcome_photo_menu(update, context, user)
        
        # Messages menu
        elif data == "menu_messages":
            await handle_messages_menu(update, context, user)
        
        # Statistics
        elif data == "menu_stats":
            await handle_stats_menu(update, context, user)
        
        # Users menu
        elif data == "menu_users":
            await handle_users_menu(update, context, user)
        
        # Settings menu
        elif data == "menu_settings":
            await handle_settings_menu(update, context, user)
        
        # View channel details
        elif data.startswith("view_channel_"):
            channel_id = data.replace("view_channel_", "")
            await handle_view_channel(update, context, user, channel_id)
        
        # Edit channel name
        elif data.startswith("edit_channel_name_"):
            channel_id = data.replace("edit_channel_name_", "")
            context.user_data['edit_channel_id'] = channel_id
            context.user_data['edit_channel_type'] = 'name'
            await query.message.reply_text(
                f"✏️ <b>Edit Channel Name</b>\n\n"
                f"Send the new name for this channel:",
                parse_mode=ParseMode.HTML
            )
            return Config.STATE_EDIT_CHANNEL
        
        # Edit channel link
        elif data.startswith("edit_channel_link_"):
            channel_id = data.replace("edit_channel_link_", "")
            context.user_data['edit_channel_id'] = channel_id
            context.user_data['edit_channel_type'] = 'link'
            await query.message.reply_text(
                f"✏️ <b>Edit Channel Link</b>\n\n"
                f"Send the new link for this channel:",
                parse_mode=ParseMode.HTML
            )
            return Config.STATE_EDIT_CHANNEL
        
        # Toggle force join
        elif data.startswith("toggle_channel_force_"):
            channel_id = data.replace("toggle_channel_force_", "")
            new_status = db.toggle_force_join(channel_id)
            status_text = "ON ✅" if new_status else "OFF ❌"
            await query.answer(f"Force join set to: {status_text}", show_alert=True)
            
            # Refresh channel view
            channel = db.get_channel(channel_id)
            if channel:
                await show_channel_details(update, context, user, channel)
        
        # Delete channel
        elif data.startswith("delete_channel_"):
            channel_id = data.replace("delete_channel_", "")
            if db.delete_channel(channel_id):
                await query.answer(Config.POPUP_MESSAGES['channel_deleted'], show_alert=True)
                await handle_channel_management(update, context, user)
        
        # Add channel button
        elif data == "add_channel":
            await query.message.reply_text(
                "➕ <b>Add New Channel</b>\n\n"
                "Send the channel ID (e.g., @channelname or -1001234567890):",
                parse_mode=ParseMode.HTML
            )
            return Config.STATE_CHANNEL_ADD_ID
        
        # Post wizard callbacks
        elif data == "add_button":
            return await post_wizard.handle_buttons_menu(update, context)
        
        elif data == "continue_buttons":
            return await post_wizard.handle_buttons_menu(update, context)
        
        elif data.startswith("select_force_") or data == "select_all_force" or data == "continue_force":
            return await post_wizard.handle_force_channel_selection(update, context)
        
        elif data.startswith("select_target_") or data == "select_all_target" or data == "continue_target":
            return await post_wizard.handle_target_channel_selection(update, context)
        
        elif data == "final_post":
            return await post_wizard.finalize_post(update, context)
        
        elif data == "edit_post_preview":
            # Go back to title step
            if user.id in post_wizard.active_wizards:
                post_wizard.active_wizards[user.id]['step'] = 'title'
                await query.edit_message_text(
                    "📝 <b>Step 1/8: Post Title</b>\n\n"
                    "✏️ Please send the <b>POST TITLE</b>:",
                    parse_mode=ParseMode.HTML
                )
                return Config.STATE_POST_TITLE
        
        # Edit message
        elif data.startswith("edit_"):
            key = data.replace("edit_", "")
            context.user_data['edit_key'] = key
            await query.message.reply_text(
                f"✏️ <b>Edit Message</b>\n\n"
                f"Send new value for <b>{key}</b>:",
                parse_mode=ParseMode.HTML
            )
            return Config.STATE_EDIT_MESSAGE
        
        # Change welcome photo
        elif data == "change_welcome_photo":
            await query.message.reply_text(
                "🖼️ <b>Set Welcome Photo</b>\n\n"
                "Send a photo to set as welcome photo:",
                parse_mode=ParseMode.HTML
            )
            return Config.STATE_WELCOME_PHOTO
        
        # Remove welcome photo
        elif data == "remove_welcome_photo":
            if db.remove_welcome_photo():
                await query.answer(Config.POPUP_MESSAGES['welcome_photo_set'], show_alert=True)
                await query.edit_message_text(
                    "✅ <b>Welcome photo removed!</b>\n\n"
                    "Users will see text-only welcome message.",
                    parse_mode=ParseMode.HTML
                )
    
    except Exception as e:
        logger.error(f"Error in callback_handler: {e}")
        try:
            await query.answer("❌ An error occurred. Please try again.")
        except:
            pass

# ==============================================================================
# 🔐 VERIFICATION HANDLERS
# ==============================================================================

async def handle_membership_verification(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    query = update.callback_query
    
    # Check membership
    result = await security.check_membership(user.id, context.bot)
    
    if result['all_joined']:
        # User verified successfully
        db.set_user_verified(user.id)
        
        # Show success popup
        await query.answer(
            Config.POPUP_MESSAGES['verified_success'],
            show_alert=True
        )
        
        # Update message with watch now button
        video_bot_link = db.get_config('video_bot_link', Config.VIDEO_BOT_LINK)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎬 Download Video Now", url=video_bot_link)],
            [InlineKeyboardButton("▶️ Watch Now 🔥", url=video_bot_link)]
        ])
        
        try:
            await query.edit_message_reply_markup(keyboard)
        except:
            pass
        
    else:
        # User not joined all channels
        await query.answer(
            Config.POPUP_MESSAGES['verified_failed'],
            show_alert=True
        )
        
        # Update join buttons
        join_buttons = []
        for channel in result['missing']:
            join_buttons.append([InlineKeyboardButton(
                f"📢 Join {channel['name']}",
                url=channel['link']
            )])
        
        join_buttons.append([InlineKeyboardButton(
            "✅ Verify Again ❤️",
            callback_data="verify_membership"
        )])
        
        try:
            await query.edit_message_reply_markup(
                InlineKeyboardMarkup(join_buttons)
            )
        except:
            pass

async def handle_post_verification(update: Update, context: ContextTypes.DEFAULT_TYPE, user, post_id):
    query = update.callback_query
    
    # Get post
    post = db.get_post(post_id)
    if not post:
        await query.answer("❌ Post not found!", show_alert=True)
        return
    
    # Check if already has access
    if db.has_user_access(user.id, post_id):
        await query.answer("✅ Already verified! Click Watch Now!", show_alert=True)
        return
    
    # Check force channels
    force_channels = post.get('force_channels', [])
    if force_channels:
        result = await security.check_membership(user.id, context.bot, force_channels)
        
        if not result['all_joined']:
            # Not joined all channels
            await query.answer(
                Config.POPUP_MESSAGES['verified_failed'],
                show_alert=True
            )
            
            # Update join buttons
            join_buttons = []
            for channel in result['missing']:
                join_buttons.append([InlineKeyboardButton(
                    f"📢 Join {channel['name']}",
                    url=channel['link']
                )])
            
            join_buttons.append([InlineKeyboardButton(
                "✅ Verify Again ❤️",
                callback_data=f"verify_post_{post_id}"
            )])
            
            try:
                await query.edit_message_reply_markup(
                    InlineKeyboardMarkup(join_buttons)
                )
            except:
                pass
            
            return
    
    # Grant access
    db.grant_user_access(user.id, post_id)
    
    # Show success popup
    await query.answer(
        Config.POPUP_MESSAGES['verified_success'],
        show_alert=True
    )
    
    # Update to watch now button
    keyboard = ui.create_watch_now_button(post_id)
    try:
        await query.edit_message_reply_markup(keyboard)
    except:
        pass

async def handle_watch_now(update: Update, context: ContextTypes.DEFAULT_TYPE, user, post_id):
    query = update.callback_query
    
    # Check access
    if not db.has_user_access(user.id, post_id):
        await query.answer(
            Config.POPUP_MESSAGES['watch_now_locked'],
            show_alert=True
        )
        return
    
    # Get post
    post = db.get_post(post_id)
    if not post:
        await query.answer("❌ Post not found!", show_alert=True)
        return
    
    # Get video bot link
    video_bot_link = post.get('video_bot_link', Config.VIDEO_BOT_LINK)
    
    # Create final keyboard
    keyboard_buttons = []
    
    # Add post buttons
    if post.get('buttons'):
        for btn in post['buttons']:
            keyboard_buttons.append([InlineKeyboardButton(btn['name'], url=btn['link'])])
    
    # Add video bot button
    keyboard_buttons.append([
        InlineKeyboardButton("🎬 Download Video Now", url=video_bot_link),
        InlineKeyboardButton("▶️ Watch Now 🔥", url=video_bot_link)
    ])
    
    keyboard = InlineKeyboardMarkup(keyboard_buttons)
    
    # Send success popup
    await query.answer(
        Config.POPUP_MESSAGES['access_granted'],
        show_alert=True
    )
    
    # Send content
    caption = f"<b>{post['title']}</b>\n\n"
    if post.get('post_text'):
        caption += f"{post['post_text']}\n\n"
    caption += "✅ <i>Access granted! Enjoy the content! 💋</i>"
    
    try:
        if post.get('photo_id'):
            await context.bot.send_photo(
                chat_id=user.id,
                photo=post['photo_id'],
                caption=caption,
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
        else:
            await context.bot.send_message(
                chat_id=user.id,
                text=caption,
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
    except Exception as e:
        logger.error(f"Error sending content: {e}")
        await query.answer("❌ Error sending content!", show_alert=True)

# ==============================================================================
# 🛠️ ADMIN HANDLERS
# ==============================================================================

async def handle_channel_management(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    query = update.callback_query
    
    channels = db.get_channels(active_only=True)
    
    if not channels:
        text = "📢 <b>Channel Manager</b>\n\n❌ No channels added yet."
        buttons = {"text": "➕ Add Channel", "callback": "add_channel"}
    else:
        text = f"📢 <b>Channel Manager</b>\n\n📊 Total Channels: {len(channels)}\n\nSelect a channel to manage:"
        buttons = ui.create_channel_buttons(channels, include_edit=True)
        buttons.append([{"text": "➕ Add Channel", "callback": "add_channel"}])
    
    buttons.append([{"text": "🔙 Back", "callback": "main_menu"}])
    
    await query.edit_message_text(
        text,
        reply_markup=ui.create_keyboard(buttons, add_back=False, add_close=True),
        parse_mode=ParseMode.HTML
    )

async def show_channel_details(update: Update, context: ContextTypes.DEFAULT_TYPE, user, channel):
    query = update.callback_query
    
    text = f"📢 <b>Channel Details</b>\n\n"
    text += f"<b>Name:</b> {channel['name']}\n"
    text += f"<b>ID:</b> {channel['channel_id']}\n"
    text += f"<b>Link:</b> {channel['link']}\n"
    text += f"<b>Force Join:</b> {'✅ Yes' if channel['force_join'] else '❌ No'}\n"
    text += f"<b>Status:</b> {'✅ Active' if channel['is_active'] else '❌ Inactive'}\n"
    
    await query.edit_message_text(
        text,
        reply_markup=ui.create_channel_management_buttons(channel['channel_id']),
        parse_mode=ParseMode.HTML
    )

async def handle_view_channel(update: Update, context: ContextTypes.DEFAULT_TYPE, user, channel_id):
    channel = db.get_channel(channel_id)
    if channel:
        await show_channel_details(update, context, user, channel)

async def handle_welcome_photo_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    query = update.callback_query
    
    current_photo = db.get_welcome_photo()
    
    if current_photo:
        text = "🖼️ <b>Welcome Photo Settings</b>\n\n✅ A welcome photo is currently set."
        buttons = [
            [{"text": "🔄 Change Photo", "callback": "change_welcome_photo"}],
            [{"text": "🗑️ Remove Photo", "callback": "remove_welcome_photo"}]
        ]
    else:
        text = "🖼️ <b>Welcome Photo Settings</b>\n\n❌ No welcome photo set."
        buttons = [
            [{"text": "➕ Set Photo", "callback": "change_welcome_photo"}]
        ]
    
    buttons.append([{"text": "🔙 Back", "callback": "main_menu"}])
    
    await query.edit_message_text(
        text,
        reply_markup=ui.create_keyboard(buttons, add_back=False, add_close=True),
        parse_mode=ParseMode.HTML
    )

async def handle_messages_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    query = update.callback_query
    
    buttons = [
        [{"text": "✏️ Welcome Message", "callback": "edit_welcome_message"}],
        [{"text": "✏️ Lock Message", "callback": "edit_lock_message"}],
        [{"text": "✏️ Verified Popup (Success)", "callback": "edit_verified_popup_success"}],
        [{"text": "✏️ Verified Popup (Failed)", "callback": "edit_verified_popup_failed"}],
        [{"text": "🔙 Back", "callback": "main_menu"}]
    ]
    
    await query.edit_message_text(
        "📝 <b>Message Editor</b>\n\nSelect a message to edit:",
        reply_markup=ui.create_keyboard(buttons, add_back=False, add_close=True),
        parse_mode=ParseMode.HTML
    )

async def handle_stats_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    query = update.callback_query
    
    stats = db.get_stats()
    
    text = "📊 <b>Bot Statistics</b>\n\n"
    text += f"👥 <b>Total Users:</b> {stats.get('total_users', 0)}\n"
    text += f"📈 <b>Today's Users:</b> {stats.get('today_users', 0)}\n"
    text += f"✅ <b>Verified Users:</b> {stats.get('verified_users', 0)}\n"
    text += f"📢 <b>Active Channels:</b> {stats.get('active_channels', 0)}\n"
    text += f"🔒 <b>Force Channels:</b> {stats.get('force_channels', 0)}\n"
    text += f"📝 <b>Total Posts:</b> {stats.get('total_posts', 0)}\n"
    
    buttons = {"text": "🔙 Back", "callback": "main_menu"}
    
    await query.edit_message_text(
        text,
        reply_markup=ui.create_keyboard(buttons, add_back=False, add_close=True),
        parse_mode=ParseMode.HTML
    )

async def handle_users_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    query = update.callback_query
    
    users = db.get_all_users()[:50]
    
    text = "👥 <b>User Management</b>\n\n"
    text += f"📊 Showing {len(users)} users\n\n"
    
    for i, user_data in enumerate(users[:10], 1):
        status = "✅" if user_data.get('verified') else "❌"
        username = f"@{user_data['username']}" if user_data['username'] else "No username"
        text += f"{i}. {status} {user_data['first_name']} ({username})\n"
    
    if len(users) > 10:
        text += f"\n... and {len(users) - 10} more users"
    
    buttons = {"text": "🔙 Back", "callback": "main_menu"}
    
    await query.edit_message_text(
        text,
        reply_markup=ui.create_keyboard(buttons, add_back=False, add_close=True),
        parse_mode=ParseMode.HTML
    )

async def handle_settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    query = update.callback_query
    
    auto_delete = db.get_config('auto_delete', '60')
    video_bot = db.get_config('video_bot_link', Config.VIDEO_BOT_LINK)
    
    text = "⚙️ <b>Bot Settings</b>\n\n"
    text += f"⏰ <b>Auto Delete:</b> {auto_delete} seconds\n"
    text += f"🤖 <b>Video Bot:</b> {video_bot}\n\n"
    text += "Select an option to change:"
    
    buttons = [
        [{"text": "⏰ Auto Delete", "callback": "edit_auto_delete"}],
        [{"text": "🤖 Video Bot Link", "callback": "edit_video_bot_link"}],
        [{"text": "🔙 Back", "callback": "main_menu"}]
    ]
    
    await query.edit_message_text(
        text,
        reply_markup=ui.create_keyboard(buttons, add_back=False, add_close=True),
        parse_mode=ParseMode.HTML
    )

# ==============================================================================
# ✏️ CONVERSATION HANDLERS
# ==============================================================================

async def edit_config_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = context.user_data.get('edit_key')
    value = update.message.text
    
    if db.set_config(key, value):
        await update.message.reply_text(f"✅ {key} updated successfully!")
    else:
        await update.message.reply_text("❌ Failed to update!")
    
    return ConversationHandler.END

async def set_welcome_photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        photo_id = update.message.photo[-1].file_id
        if db.set_welcome_photo(photo_id):
            await update.message.reply_text(Config.POPUP_MESSAGES['welcome_photo_set'])
        else:
            await update.message.reply_text("❌ Failed to set welcome photo!")
    else:
        await update.message.reply_text("❌ Please send a photo!")
    
    return ConversationHandler.END

async def edit_channel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    channel_id = context.user_data.get('edit_channel_id')
    edit_type = context.user_data.get('edit_channel_type')
    value = update.message.text
    
    if edit_type == 'name':
        if db.update_channel(channel_id, name=value):
            await update.message.reply_text(f"✅ Channel name updated to: {value}")
        else:
            await update.message.reply_text("❌ Failed to update channel name!")
    
    elif edit_type == 'link':
        if value.startswith(('http://', 'https://')):
            if db.update_channel(channel_id, link=value):
                await update.message.reply_text(f"✅ Channel link updated!")
            else:
                await update.message.reply_text("❌ Failed to update channel link!")
        else:
            await update.message.reply_text("❌ Invalid URL! Must start with http:// or https://")
    
    # Clear context
    context.user_data.pop('edit_channel_id', None)
    context.user_data.pop('edit_channel_type', None)
    
    return ConversationHandler.END

async def add_channel_id_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['channel_id'] = update.message.text
    await update.message.reply_text(
        "📝 <b>Step 2/3</b>\n\n"
        "Send the channel name:",
        parse_mode=ParseMode.HTML
    )
    return Config.STATE_CHANNEL_ADD_NAME

async def add_channel_name_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['channel_name'] = update.message.text
    await update.message.reply_text(
        "🔗 <b>Step 3/3</b>\n\n"
        "Send the channel link:",
        parse_mode=ParseMode.HTML
    )
    return Config.STATE_CHANNEL_ADD_LINK

async def add_channel_link_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    channel_id = context.user_data.get('channel_id')
    channel_name = context.user_data.get('channel_name')
    channel_link = update.message.text
    
    if channel_id and channel_name and channel_link:
        if db.add_channel(channel_id, channel_name, channel_link):
            await update.message.reply_text(Config.POPUP_MESSAGES['channel_added'])
        else:
            await update.message.reply_text("❌ Failed to add channel!")
    else:
        await update.message.reply_text("❌ Invalid data!")
    
    # Clear context
    context.user_data.pop('channel_id', None)
    context.user_data.pop('channel_name', None)
    
    return ConversationHandler.END

async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(Config.POPUP_MESSAGES['operation_cancelled'])
    return ConversationHandler.END

# ==============================================================================
# 🚀 MAIN APPLICATION
# ==============================================================================

def main():
    print("=" * 60)
    print("🤖 SUPREME GOD BOT - ULTIMATE EDITION v11.0")
    print("=" * 60)
    print(f"👑 Admin IDs: {Config.ADMIN_IDS}")
    print(f"🔧 Database: {Config.DB_NAME}")
    print(f"🤖 Video Bot: {Config.VIDEO_BOT_USERNAME}")
    print("=" * 60)
    
    # Create application
    app = ApplicationBuilder() \
        .token(Config.TOKEN) \
        .pool_timeout(30) \
        .connect_timeout(30) \
        .read_timeout(30) \
        .write_timeout(30) \
        .build()
    
    # Error handler
    async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.error(f"Update {update} caused error {context.error}")
    
    app.add_error_handler(error_handler)
    
    # ==================== CONVERSATION HANDLERS ====================
    
    # Post creation wizard
    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(callback_handler, pattern='^create_post_start$')],
        states={
            Config.STATE_POST_TITLE: [MessageHandler(filters.TEXT, post_wizard.handle_title)],
            Config.STATE_POST_PHOTO: [MessageHandler(filters.PHOTO | filters.TEXT, post_wizard.handle_photo)],
            Config.STATE_POST_TEXT: [MessageHandler(filters.TEXT, post_wizard.handle_text)],
            Config.STATE_POST_BUTTONS_MENU: [CallbackQueryHandler(callback_handler, pattern='^(add_button|continue_buttons)$')],
            Config.STATE_POST_BUTTON_NAME: [MessageHandler(filters.TEXT, post_wizard.handle_button_name)],
            Config.STATE_POST_BUTTON_LINK: [MessageHandler(filters.TEXT, post_wizard.handle_button_link)],
            Config.STATE_POST_FORCE_CHANNELS: [CallbackQueryHandler(callback_handler, pattern='^(select_force_|select_all_force|continue_force)$')],
            Config.STATE_POST_TARGET_CHANNELS: [CallbackQueryHandler(callback_handler, pattern='^(select_target_|select_all_target|continue_target)$')],
            Config.STATE_POST_CONFIRM: [
                CallbackQueryHandler(callback_handler, pattern='^final_post$'),
                CallbackQueryHandler(callback_handler, pattern='^edit_post_preview$')
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel_handler)]
    ))
    
    # Edit config
    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(callback_handler, pattern='^edit_')],
        states={
            Config.STATE_EDIT_MESSAGE: [MessageHandler(filters.TEXT, edit_config_handler)]
        },
        fallbacks=[CommandHandler('cancel', cancel_handler)]
    ))
    
    # Welcome photo
    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(callback_handler, pattern='^change_welcome_photo$')],
        states={
            Config.STATE_WELCOME_PHOTO: [MessageHandler(filters.PHOTO, set_welcome_photo_handler)]
        },
        fallbacks=[CommandHandler('cancel', cancel_handler)]
    ))
    
    # Edit channel
    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(callback_handler, pattern='^edit_channel_(name|link)_')],
        states={
            Config.STATE_EDIT_CHANNEL: [MessageHandler(filters.TEXT, edit_channel_handler)]
        },
        fallbacks=[CommandHandler('cancel', cancel_handler)]
    ))
    
    # Add channel
    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(callback_handler, pattern='^add_channel$')],
        states={
            Config.STATE_CHANNEL_ADD_ID: [MessageHandler(filters.TEXT, add_channel_id_handler)],
            Config.STATE_CHANNEL_ADD_NAME: [MessageHandler(filters.TEXT, add_channel_name_handler)],
            Config.STATE_CHANNEL_ADD_LINK: [MessageHandler(filters.TEXT, add_channel_link_handler)]
        },
        fallbacks=[CommandHandler('cancel', cancel_handler)]
    ))
    
    # ==================== COMMAND HANDLERS ====================
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("admin", admin_command))
    
    # ==================== CALLBACK HANDLERS ====================
    
    # Post verification
    app.add_handler(CallbackQueryHandler(callback_handler, pattern='^verify_post_'))
    app.add_handler(CallbackQueryHandler(callback_handler, pattern='^watch_now_'))
    
    # Membership verification
    app.add_handler(CallbackQueryHandler(callback_handler, pattern='^verify_membership$'))
    
    # Channel management
    app.add_handler(CallbackQueryHandler(callback_handler, pattern='^view_channel_'))
    app.add_handler(CallbackQueryHandler(callback_handler, pattern='^toggle_channel_force_'))
    app.add_handler(CallbackQueryHandler(callback_handler, pattern='^delete_channel_'))
    
    # General callback handler (must be last)
    app.add_handler(CallbackQueryHandler(callback_handler))
    
    print("✅ Bot setup completed successfully!")
    print("🚀 Starting bot polling...")
    print("=" * 60)
    
    # Start bot
    app.run_polling(
        poll_interval=1.0,
        timeout=30,
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES
    )

if __name__ == "__main__":
    main()
