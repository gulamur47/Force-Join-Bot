"""
================================================================================
SUPREME GOD BOT - PREMIUM EDITION v10.0
FULLY WORKING WITH ALL FEATURES
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
import datetime
import secrets
import string
from typing import List, Dict, Optional
from collections import defaultdict

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
    # Bot Token (Replace with your token)
    TOKEN = "8456027249:AAEqg2j7jhJDSl4R0dnVCqaCvYBJQeG8NM4"
    ADMIN_IDS = {6406804999}  # Add your admin ID here
    
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
    STATE_POST_FORCE_CHANNELS = 5
    STATE_POST_TARGET_CHANNEL = 6
    STATE_POST_CONFIRM = 7
    STATE_CHANNEL_ADD_ID = 8
    STATE_CHANNEL_ADD_NAME = 9
    STATE_CHANNEL_ADD_LINK = 10
    STATE_BLOCK_USER = 11
    STATE_ADD_VIP = 12
    STATE_EDIT_MESSAGE = 13
    STATE_BROADCAST = 14
    
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
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP
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

{star} <b>❤️তুমি অবশেষে আমাদের মাঝে এসেছো, আমার হৃদয়টা আনন্দে নেচে উঠলো! 😍💃
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
            ('auto_delete', '60')
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
        params = []
        
        if active_only:
            query += " AND is_active = 1"
        
        if force_only:
            query += " AND force_join = 1"
        
        query += " ORDER BY name"
        
        cursor.execute(query, params)
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
            # Replace emoji placeholders
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
    def save_post(self, title, photo_id, post_text, buttons, force_channels, target_channel_id, created_by):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO posts (title, photo_id, post_text, buttons, force_channels, target_channel_id, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (title, photo_id, post_text, json.dumps(buttons), 
                  json.dumps(force_channels), target_channel_id, created_by))
            
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
            # Parse JSON fields
            if post.get('buttons'):
                post['buttons'] = json.loads(post['buttons'])
            if post.get('force_channels'):
                post['force_channels'] = json.loads(post['force_channels'])
            return post
        return None
    
    def get_all_posts(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT post_id, title, target_channel_id, created_date FROM posts ORDER BY created_date DESC')
        return cursor.fetchall()
    
    # === Statistics ===
    def get_stats(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # User stats
        cursor.execute("SELECT COUNT(*) FROM users")
        stats['total_users'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE DATE(join_date) = DATE('now')")
        stats['today_users'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_blocked = 1")
        stats['blocked_users'] = cursor.fetchone()[0]
        
        # Channel stats
        cursor.execute("SELECT COUNT(*) FROM channels WHERE is_active = 1")
        stats['active_channels'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM channels WHERE force_join = 1 AND is_active = 1")
        stats['force_channels'] = cursor.fetchone()[0]
        
        # Post stats
        cursor.execute("SELECT COUNT(*) FROM posts")
        stats['total_posts'] = cursor.fetchone()[0]
        
        return stats

# Initialize database
db = DatabaseManager()

# ==============================================================================
# 🎨 UI MANAGER
# ==============================================================================

class UIManager:
    @staticmethod
    def format_text(text: str, user=None):
        """Format text with user info and emojis"""
        # Replace emoji placeholders
        for key, emoji in Config.EMOJIS.items():
            text = text.replace(f"{{{key}}}", emoji)
        
        # Add user info if provided
        if user:
            user_mention = mention_html(user.id, user.first_name or 'User')
            text = text.replace("@UserName", user_mention)
        
        return text
    
    @staticmethod
    def create_keyboard(buttons, add_back=True, add_close=False):
        """Create inline keyboard"""
        keyboard = []
        
        for row in buttons:
            keyboard_row = []
            for btn in row:
                if 'url' in btn:
                    keyboard_row.append(InlineKeyboardButton(btn['text'], url=btn['url']))
                else:
                    keyboard_row.append(InlineKeyboardButton(btn['text'], callback_data=btn['callback']))
            keyboard.append(keyboard_row)
        
        # Add back button
        if add_back:
            keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="main_menu")])
        
        # Add close button
        if add_close:
            keyboard.append([InlineKeyboardButton("❌ Close", callback_data="close_panel")])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_admin_menu():
        """Get admin main menu"""
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
        """Create 2-row channel selection buttons"""
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
# 🔐 SECURITY MANAGER
# ==============================================================================

class SecurityManager:
    def __init__(self):
        self.verification_cache = {}
    
    async def check_membership(self, user_id, bot, channel_ids=None):
        """Check if user is member of channels"""
        cache_key = f"membership_{user_id}"
        
        # Check cache first
        if cache_key in self.verification_cache:
            cached_time, result = self.verification_cache[cache_key]
            if time.time() - cached_time < 300:  # 5 minute cache
                return result
        
        missing_channels = []
        
        if not channel_ids:
            # Check all force channels
            channels = db.get_channels(force_only=True, active_only=True)
        else:
            # Check specific channels
            all_channels = db.get_channels(active_only=True)
            channels = [ch for ch in all_channels if ch['channel_id'] in channel_ids]
        
        for channel in channels:
            try:
                member = await bot.get_chat_member(
                    chat_id=channel['channel_id'],
                    user_id=user_id
                )
                
                if member.status in ['left', 'kicked']:
                    missing_channels.append(channel)
            except Exception as e:
                logger.warning(f"Failed to check channel {channel['channel_id']}: {e}")
                missing_channels.append(channel)
        
        # Update cache
        self.verification_cache[cache_key] = (time.time(), missing_channels)
        
        return missing_channels
    
    def clear_user_cache(self, user_id):
        """Clear cache for user"""
        cache_key = f"membership_{user_id}"
        if cache_key in self.verification_cache:
            del self.verification_cache[cache_key]

security = SecurityManager()

# ==============================================================================
# 🎯 POST WIZARD
# ==============================================================================

class PostWizard:
    def __init__(self):
        self.active_wizards = {}
    
    async def start_wizard(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start post creation wizard"""
        query = update.callback_query
        user = query.from_user
        
        # Initialize wizard
        self.active_wizards[user.id] = {
            'step': 'title',
            'data': {
                'buttons': []
            }
        }
        
        await query.answer()
        await query.edit_message_text(
            ui.format_text("📝 <b>🎯 Create New Post - Step 1/6</b>\n\n"
                          "✏️ Please send the <b>POST TITLE</b>:", user),
            parse_mode=ParseMode.HTML
        )
        
        return Config.STATE_POST_TITLE
    
    async def handle_title(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle post title"""
        user = update.effective_user
        
        if user.id not in self.active_wizards:
            await update.message.reply_text("❌ Session expired. Please start again.")
            return ConversationHandler.END
        
        title = update.message.text
        self.active_wizards[user.id]['data']['title'] = title
        self.active_wizards[user.id]['step'] = 'photo'
        
        await update.message.reply_text(
            ui.format_text("📸 <b>🎯 Create New Post - Step 2/6</b>\n\n"
                          "🖼️ Please send the <b>POST PHOTO</b>:", user),
            parse_mode=ParseMode.HTML
        )
        
        return Config.STATE_POST_PHOTO
    
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle post photo"""
        user = update.effective_user
        
        if user.id not in self.active_wizards:
            await update.message.reply_text("❌ Session expired. Please start again.")
            return ConversationHandler.END
        
        if update.message.photo:
            photo_id = update.message.photo[-1].file_id
            self.active_wizards[user.id]['data']['photo_id'] = photo_id
            self.active_wizards[user.id]['step'] = 'text'
            
            await update.message.reply_text(
                ui.format_text("📝 <b>🎯 Create New Post - Step 3/6</b>\n\n"
                              "💬 Please send the <b>POST TEXT</b> (or type /skip):", user),
                parse_mode=ParseMode.HTML
            )
            
            return Config.STATE_POST_TEXT
        else:
            await update.message.reply_text("❌ Please send a photo!")
            return Config.STATE_POST_PHOTO
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle post text"""
        user = update.effective_user
        
        if user.id not in self.active_wizards:
            await update.message.reply_text("❌ Session expired. Please start again.")
            return ConversationHandler.END
        
        if update.message.text and update.message.text.lower() != '/skip':
            self.active_wizards[user.id]['data']['post_text'] = update.message.text
        
        # Move to button management
        self.active_wizards[user.id]['step'] = 'buttons'
        
        buttons = [
            [
                {"text": "➕ Add Button", "callback": "add_button"}
            ]
        ]
        
        if self.active_wizards[user.id]['data']['buttons']:
            buttons.append([
                {"text": "➡️ Continue", "callback": "continue_buttons"}
            ])
        
        keyboard = ui.create_keyboard(buttons, add_back=True, add_close=True)
        
        await update.message.reply_text(
            ui.format_text("🔘 <b>🎯 Create New Post - Step 4/6</b>\n\n"
                          "🔗 <b>Button Management</b>\n\n"
                          f"Current buttons: {len(self.active_wizards[user.id]['data']['buttons'])}\n\n"
                          "Click 'Add Button' to add button or 'Continue' to proceed:", user),
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
        
        return Config.STATE_POST_BUTTONS
    
    async def handle_button_management(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button management callbacks"""
        query = update.callback_query
        user = query.from_user
        
        if user.id not in self.active_wizards:
            await query.answer("❌ Session expired!")
            return ConversationHandler.END
        
        data = query.data
        
        if data == "add_button":
            # Start adding button
            await query.message.edit_text(
                ui.format_text("🔘 <b>Add Button - Step 1/2</b>\n\n"
                              "✏️ Please send the <b>BUTTON NAME</b>:", user),
                parse_mode=ParseMode.HTML
            )
            # Store that we're adding a button
            context.user_data['adding_button'] = True
            return Config.STATE_POST_BUTTONS
        
        elif data == "continue_buttons":
            if not self.active_wizards[user.id]['data']['buttons']:
                await query.answer("❌ Please add at least one button!")
                return
            
            # Move to force channel selection
            self.active_wizards[user.id]['step'] = 'force_channels'
            
            # Get force channels
            force_channels = db.get_channels(force_only=True, active_only=True)
            
            if not force_channels:
                await query.answer("❌ No force channels found!")
                del self.active_wizards[user.id]
                return ConversationHandler.END
            
            # Create channel selection buttons
            channel_buttons = ui.create_channel_buttons(force_channels, prefix="select_force")
            
            # Add select all and continue
            channel_buttons.append([
                {"text": "✅ Select All", "callback": "select_all_force"},
                {"text": "➡️ Continue", "callback": "continue_force"}
            ])
            
            keyboard = ui.create_keyboard(channel_buttons, add_back=True, add_close=True)
            
            # Initialize selected channels
            self.active_wizards[user.id]['data']['force_channels'] = []
            
            await query.edit_message_text(
                ui.format_text("🎯 <b>🎯 Create New Post - Step 5/6</b>\n\n"
                              "📢 Select <b>FORCE JOIN CHANNELS</b> (Users must join these):\n\n"
                              f"Found {len(force_channels)} force channels.", user),
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
            
            return Config.STATE_POST_FORCE_CHANNELS
        
        return Config.STATE_POST_BUTTONS
    
    async def handle_button_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button name input"""
        user = update.effective_user
        
        if user.id not in self.active_wizards:
            await update.message.reply_text("❌ Session expired. Please start again.")
            return ConversationHandler.END
        
        button_name = update.message.text
        context.user_data['button_name'] = button_name
        
        await update.message.reply_text(
            ui.format_text("🔗 <b>Add Button - Step 2/2</b>\n\n"
                          "🌐 Please send the <b>BUTTON LINK</b> (URL):", user),
            parse_mode=ParseMode.HTML
        )
        
        return Config.STATE_POST_BUTTONS
    
    async def handle_button_link(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button link input"""
        user = update.effective_user
        
        if user.id not in self.active_wizards:
            await update.message.reply_text("❌ Session expired. Please start again.")
            return ConversationHandler.END
        
        button_link = update.message.text
        
        # Validate URL
        if not button_link.startswith(('http://', 'https://')):
            await update.message.reply_text("❌ Please send a valid URL (starting with http:// or https://)")
            return Config.STATE_POST_BUTTONS
        
        # Add button to wizard data
        button_name = context.user_data.get('button_name', 'Button')
        self.active_wizards[user.id]['data']['buttons'].append({
            'name': button_name,
            'link': button_link
        })
        
        # Clear temporary data
        context.user_data.pop('button_name', None)
        context.user_data.pop('adding_button', None)
        
        # Return to button management
        self.active_wizards[user.id]['step'] = 'buttons'
        
        # Create updated buttons list
        current_buttons = self.active_wizards[user.id]['data']['buttons']
        
        buttons_list = [
            [
                {"text": "➕ Add Another Button", "callback": "add_button"}
            ]
        ]
        
        # Show current buttons
        for i, btn in enumerate(current_buttons, 1):
            buttons_list.append([
                {"text": f"🔘 {i}. {btn['name'][:20]}", "callback": f"view_button_{i}"}
            ])
        
        buttons_list.append([
            {"text": "➡️ Continue", "callback": "continue_buttons"}
        ])
        
        keyboard = ui.create_keyboard(buttons_list, add_back=True, add_close=True)
        
        await update.message.reply_text(
            ui.format_text("✅ <b>Button Added Successfully!</b>\n\n"
                          f"🔘 <b>Current Buttons ({len(current_buttons)}):</b>\n"
                          + "\n".join([f"{i}. {btn['name']}" for i, btn in enumerate(current_buttons, 1)]) + "\n\n"
                          "Click 'Add Another Button' or 'Continue' to proceed:", user),
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
        
        return Config.STATE_POST_BUTTONS
    
    async def handle_force_channel_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle force channel selection"""
        query = update.callback_query
        user = query.from_user
        
        if user.id not in self.active_wizards:
            await query.answer("❌ Session expired!")
            return ConversationHandler.END
        
        data = query.data
        
        if data == "select_all_force":
            # Select all force channels
            force_channels = db.get_channels(force_only=True, active_only=True)
            self.active_wizards[user.id]['data']['force_channels'] = [ch['channel_id'] for ch in force_channels]
            
            await query.answer(f"✅ Selected all {len(force_channels)} channels")
            
        elif data.startswith("select_force_"):
            channel_id = data.replace("select_force_", "")
            
            if channel_id in self.active_wizards[user.id]['data']['force_channels']:
                # Deselect
                self.active_wizards[user.id]['data']['force_channels'].remove(channel_id)
                await query.answer("❌ Channel deselected")
            else:
                # Select
                self.active_wizards[user.id]['data']['force_channels'].append(channel_id)
                await query.answer("✅ Channel selected")
        
        elif data == "continue_force":
            if not self.active_wizards[user.id]['data']['force_channels']:
                await query.answer("❌ Please select at least one force channel!")
                return
            
            # Move to target channel selection
            self.active_wizards[user.id]['step'] = 'target_channel'
            
            # Get all channels for posting
            all_channels = db.get_channels(active_only=True)
            
            if not all_channels:
                await query.answer("❌ No channels available for posting!")
                del self.active_wizards[user.id]
                return ConversationHandler.END
            
            # Create channel selection buttons
            channel_buttons = ui.create_channel_buttons(all_channels, prefix="select_target")
            
            keyboard = ui.create_keyboard(channel_buttons, add_back=True, add_close=True)
            
            await query.edit_message_text(
                ui.format_text("📤 <b>🎯 Create New Post - Step 6/6</b>\n\n"
                              "📤 Select <b>TARGET CHANNEL</b> to post:", user),
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
            
            return Config.STATE_POST_TARGET_CHANNEL
        
        # Update selection display
        selected_count = len(self.active_wizards[user.id]['data']['force_channels'])
        force_channels = db.get_channels(force_only=True, active_only=True)
        
        # Recreate buttons with selection indicators
        channel_buttons = []
        row = []
        
        for i, channel in enumerate(force_channels):
            is_selected = channel['channel_id'] in self.active_wizards[user.id]['data']['force_channels']
            emoji = "✅" if is_selected else "📢"
            
            row.append({
                "text": f"{emoji} {channel['name'][:12]}",
                "callback": f"select_force_{channel['channel_id']}"
            })
            
            if len(row) == 2 or i == len(force_channels) - 1:
                channel_buttons.append(row)
                row = []
        
        # Add select all and continue
        channel_buttons.append([
            {"text": "✅ Select All", "callback": "select_all_force"},
            {"text": f"➡️ Continue ({selected_count} selected)", "callback": "continue_force"}
        ])
        
        keyboard = ui.create_keyboard(channel_buttons, add_back=True, add_close=True)
        
        await query.edit_message_reply_markup(keyboard)
        return Config.STATE_POST_FORCE_CHANNELS
    
    async def handle_target_channel_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle target channel selection"""
        query = update.callback_query
        user = query.from_user
        
        if user.id not in self.active_wizards:
            await query.answer("❌ Session expired!")
            return ConversationHandler.END
        
        if query.data.startswith("select_target_"):
            channel_id = query.data.replace("select_target_", "")
            
            # Get channel info
            channels = db.get_channels(active_only=True)
            channel = next((ch for ch in channels if ch['channel_id'] == channel_id), None)
            
            if not channel:
                await query.answer("❌ Channel not found!")
                return
            
            self.active_wizards[user.id]['data']['target_channel_id'] = channel_id
            self.active_wizards[user.id]['data']['target_channel_name'] = channel['name']
            
            # Show final confirmation
            wizard_data = self.active_wizards[user.id]['data']
            
            # Create preview
            preview = f"📝 <b>Title:</b> {wizard_data['title']}\n"
            preview += f"🖼️ <b>Has Photo:</b> {'Yes' if 'photo_id' in wizard_data else 'No'}\n"
            preview += f"🔘 <b>Buttons:</b> {len(wizard_data['buttons'])}\n"
            preview += f"🎯 <b>Force Channels:</b> {len(wizard_data['force_channels'])}\n"
            preview += f"📤 <b>Target Channel:</b> {wizard_data['target_channel_name']}\n"
            
            buttons = [
                [{"text": "🚀 Post Now", "callback": "final_post"}],
                [{"text": "✏️ Edit Again", "callback": "edit_post"}]
            ]
            
            keyboard = ui.create_keyboard(buttons, add_back=True, add_close=True)
            
            await query.edit_message_text(
                ui.format_text(f"🎯 <b>FINAL CONFIRMATION</b>\n\n"
                              f"{preview}\n\n"
                              f"⚠️ <b>Click 'Post Now' to confirm:</b>", user),
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
            
            return Config.STATE_POST_CONFIRM
        
        return Config.STATE_POST_TARGET_CHANNEL
    
    async def finalize_post(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Finalize and send post"""
        query = update.callback_query
        user = query.from_user
        
        if user.id not in self.active_wizards:
            await query.answer("❌ Session expired!")
            return ConversationHandler.END
        
        wizard_data = self.active_wizards[user.id]['data']
        
        # Save post to database
        post_id = db.save_post(
            title=wizard_data['title'],
            photo_id=wizard_data.get('photo_id', ''),
            post_text=wizard_data.get('post_text', ''),
            buttons=wizard_data['buttons'],
            force_channels=wizard_data['force_channels'],
            target_channel_id=wizard_data['target_channel_id'],
            created_by=user.id
        )
        
        if not post_id:
            await query.answer("❌ Failed to save post!")
            return ConversationHandler.END
        
        # Send to target channel
        try:
            # Create keyboard with buttons
            keyboard_buttons = []
            for btn in wizard_data['buttons']:
                keyboard_buttons.append([InlineKeyboardButton(btn['name'], url=btn['link'])])
            
            # Add verification button
            keyboard_buttons.append([
                InlineKeyboardButton("🔓 Verify & View", callback_data=f"view_post_{post_id}")
            ])
            
            keyboard = InlineKeyboardMarkup(keyboard_buttons)
            
            # Create caption
            caption = f"<b>{wizard_data['title']}</b>\n\n"
            if wizard_data.get('post_text'):
                caption += f"{wizard_data['post_text']}\n\n"
            caption += f"🔒 <i>Click 'Verify & View' to access content after joining required channels.</i>"
            
            # Send post
            if 'photo_id' in wizard_data and wizard_data['photo_id']:
                await context.bot.send_photo(
                    chat_id=wizard_data['target_channel_id'],
                    photo=wizard_data['photo_id'],
                    caption=caption,
                    reply_markup=keyboard,
                    parse_mode=ParseMode.HTML
                )
            else:
                await context.bot.send_message(
                    chat_id=wizard_data['target_channel_id'],
                    text=caption,
                    reply_markup=keyboard,
                    parse_mode=ParseMode.HTML
                )
            
            # Cleanup wizard
            del self.active_wizards[user.id]
            
            await query.edit_message_text(
                f"✅ <b>Post Created Successfully!</b>\n\n"
                f"📝 Post ID: <code>{post_id}</code>\n"
                f"📤 Posted to: {wizard_data['target_channel_name']}\n"
                f"🔒 Force Channels: {len(wizard_data['force_channels'])}\n"
                f"🔘 Buttons: {len(wizard_data['buttons'])}",
                parse_mode=ParseMode.HTML
            )
            
        except Exception as e:
            logger.error(f"Failed to post: {e}")
            await query.answer(f"❌ Failed to post: {e}")
        
        return ConversationHandler.END

# Initialize post wizard
post_wizard = PostWizard()

# ==============================================================================
# 🎮 COMMAND HANDLERS
# ==============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    
    # Add/update user
    db.add_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name or ""
    )
    db.update_user_activity(user.id)
    
    # Check if blocked
    user_data = db.get_user(user.id)
    if user_data and user_data.get('is_blocked'):
        await update.message.reply_text(
            "🚫 Your access has been restricted. Contact admin for assistance.",
            parse_mode=ParseMode.HTML
        )
        return
    
    # Check channel membership
    missing_channels = await security.check_membership(user.id, context.bot)
    
    if missing_channels:
        # Show lock message
        lock_msg = db.get_config('lock_message')
        
        # Create channel join buttons
        buttons = []
        for channel in missing_channels:
            buttons.append([
                {"text": f"📢 Join {channel['name']}", "url": channel['link']}
            ])
        
        buttons.append([
            {"text": "✅ Verify Membership", "callback": "verify_membership"}
        ])
        
        keyboard = ui.create_keyboard(buttons, add_back=False, add_close=False)
        
        await update.message.reply_text(
            ui.format_text(lock_msg, user),
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
    else:
        # User has joined all channels - show welcome
        welcome_msg = db.get_config('welcome_message')
        btn_text = db.get_config('button_text')
        watch_url = db.get_config('watch_url')
        
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton(btn_text, url=watch_url)
        ]])
        
        message = await update.message.reply_text(
            ui.format_text(welcome_msg, user),
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
        
        # Auto-delete after configured time
        auto_delete = int(db.get_config('auto_delete', Config.DEFAULT_AUTO_DELETE))
        if auto_delete > 0:
            await asyncio.sleep(auto_delete)
            try:
                await message.delete()
            except:
                pass

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin command"""
    user = update.effective_user
    
    if user.id not in Config.ADMIN_IDS:
        await update.message.reply_text("🚫 Access denied!")
        return
    
    db.update_user_activity(user.id)
    
    stats = db.get_stats()
    
    text = f"""
{Config.EMOJIS['admin']} <b>SUPREME ADMIN PANEL</b>

{Config.EMOJIS['chart']} <b>Statistics:</b>
• Users: {stats['total_users']:,}
• Today: {stats['today_users']:,}
• Blocked: {stats['blocked_users']:,}
• Channels: {stats['active_channels']:,}
• Posts: {stats['total_posts']:,}

👇 <b>Select an option:</b>
"""
    
    await update.message.reply_text(
        text,
        reply_markup=ui.get_admin_menu(),
        parse_mode=ParseMode.HTML
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command"""
    user = update.effective_user
    
    if user.id not in Config.ADMIN_IDS:
        await update.message.reply_text("🚫 Admin only command!")
        return
    
    stats = db.get_stats()
    
    text = f"""
{Config.EMOJIS['chart']} <b>BOT STATISTICS</b>

{Config.EMOJIS['users']} <b>User Stats:</b>
• Total Users: {stats['total_users']:,}
• Today New: {stats['today_users']:,}
• Blocked: {stats['blocked_users']:,}

{Config.EMOJIS['megaphone']} <b>Channel Stats:</b>
• Active Channels: {stats['active_channels']:,}
• Force Channels: {stats['force_channels']:,}

{Config.EMOJIS['camera']} <b>Post Stats:</b>
• Total Posts: {stats['total_posts']:,}
"""
    
    await update.message.reply_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=ui.create_keyboard([], add_back=True, add_close=True)
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    user = update.effective_user
    
    text = f"""
{Config.EMOJIS['info']} <b>Supreme Bot Commands</b>

<b>User Commands:</b>
/start - Start the bot
/help - Show this help

<b>Admin Commands:</b>
/admin - Admin panel
/stats - Show statistics
/post - Create new post

<b>Features:</b>
• Force channel join verification
• Auto-delete messages (60s)
• Advanced post creation
• Channel management
• User management
• Premium styling
"""
    
    await update.message.reply_text(
        text,
        parse_mode=ParseMode.HTML
    )

async def post_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /post command"""
    user = update.effective_user
    
    if user.id not in Config.ADMIN_IDS:
        await update.message.reply_text("🚫 Admin only command!")
        return
    
    # Check if wizard already active
    if user.id in post_wizard.active_wizards:
        await update.message.reply_text("⚠️ You have an active post creation. Please complete or cancel it first.")
        return
    
    # Initialize wizard
    post_wizard.active_wizards[user.id] = {
        'step': 'title',
        'data': {'buttons': []}
    }
    
    await update.message.reply_text(
        ui.format_text("📝 <b>🎯 Create New Post - Step 1/6</b>\n\n"
                      "✏️ Please send the <b>POST TITLE</b>:", user),
        parse_mode=ParseMode.HTML
    )
    
    return Config.STATE_POST_TITLE

# ==============================================================================
# 🔄 CALLBACK HANDLER
# ==============================================================================

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all callback queries"""
    query = update.callback_query
    user = query.from_user
    data = query.data
    
    # Update user activity
    db.update_user_activity(user.id)
    
    # Admin check for admin functions
    if data in ['main_menu', 'menu_', 'create_post', 'broadcast', 'block_user', 
                'add_vip', 'edit_', 'toggle_', 'remove_', 'select_', 'add_channel']:
        if user.id not in Config.ADMIN_IDS:
            await query.answer("🚫 Admin access required!", show_alert=True)
            return
    
    # Handle callbacks
    if data == "main_menu":
        await query.answer()
        await show_admin_panel(query, context)
    
    elif data == "close_panel":
        await query.answer()
        try:
            await query.delete_message()
        except:
            pass
    
    elif data == "verify_membership":
        # Handle verification
        await handle_verification(query, context)
    
    elif data == "menu_messages":
        await query.answer()
        await show_message_menu(query, context)
    
    elif data == "menu_channels":
        await query.answer()
        await show_channel_menu(query, context)
    
    elif data == "menu_users":
        await query.answer()
        await show_user_menu(query, context)
    
    elif data == "menu_stats":
        await query.answer()
        await stats_command(update, context)
    
    elif data == "menu_settings":
        await query.answer()
        await show_settings_menu(query, context)
    
    elif data == "create_post_start":
        return await post_wizard.start_wizard(update, context)
    
    elif data == "broadcast_start":
        await query.answer()
        await query.message.reply_text(
            "📢 <b>Broadcast Message</b>\n\n"
            "Please send the message to broadcast:",
            parse_mode=ParseMode.HTML
        )
        context.user_data['broadcast'] = True
        return Config.STATE_BROADCAST
    
    elif data.startswith("edit_"):
        key = data.replace("edit_", "")
        context.user_data['edit_key'] = key
        current_value = db.get_config(key)
        
        await query.answer()
        await query.message.reply_text(
            f"✏️ <b>Editing:</b> {key}\n"
            f"<b>Current:</b> {current_value[:100]}...\n\n"
            f"Please send the new value:",
            parse_mode=ParseMode.HTML
        )
        return Config.STATE_EDIT_MESSAGE
    
    elif data.startswith("toggle_force_"):
        channel_id = data.replace("toggle_force_", "")
        new_status = db.toggle_force_join(channel_id)
        
        await query.answer(f"✅ Force join {'enabled' if new_status else 'disabled'}!")
        # Refresh channel menu
        await show_channel_menu(query, context)
    
    elif data.startswith("remove_channel_"):
        channel_id = data.replace("remove_channel_", "")
        if db.remove_channel(channel_id):
            await query.answer("✅ Channel removed!")
        else:
            await query.answer("❌ Failed to remove!")
        # Refresh
        await show_channel_menu(query, context)
    
    elif data == "add_channel":
        await query.answer()
        await query.message.reply_text(
            "➕ <b>Add New Channel</b>\n\n"
            "Please send the Channel ID (e.g., @channelname or -1001234567890):",
            parse_mode=ParseMode.HTML
        )
        return Config.STATE_CHANNEL_ADD_ID
    
    elif data.startswith("block_user_"):
        user_id = int(data.replace("block_user_", ""))
        if db.block_user(user_id):
            await query.answer("✅ User blocked!")
        else:
            await query.answer("❌ Failed to block!")
    
    elif data.startswith("unblock_user_"):
        user_id = int(data.replace("unblock_user_", ""))
        if db.unblock_user(user_id):
            await query.answer("✅ User unblocked!")
        else:
            await query.answer("❌ Failed to unblock!")
    
    elif data.startswith("view_post_"):
        return await handle_post_view(update, context)
    
    elif data.startswith("verify_post_"):
        return await handle_post_verification(update, context)
    
    else:
        await query.answer("❌ Unknown action!")

async def show_admin_panel(query, context):
    """Show admin panel"""
    stats = db.get_stats()
    
    text = f"""
{Config.EMOJIS['admin']} <b>SUPREME ADMIN PANEL</b>

{Config.EMOJIS['chart']} <b>Statistics:</b>
• Users: {stats['total_users']:,}
• Today: {stats['today_users']:,}
• Blocked: {stats['blocked_users']:,}
• Channels: {stats['active_channels']:,}
• Posts: {stats['total_posts']:,}

👇 <b>Select an option:</b>
"""
    
    await query.edit_message_text(
        text,
        reply_markup=ui.get_admin_menu(),
        parse_mode=ParseMode.HTML
    )

async def show_message_menu(query, context):
    """Show message editor menu"""
    buttons = [
        [
            {"text": "✏️ Welcome Message", "callback": "edit_welcome_message"},
            {"text": "✏️ Lock Message", "callback": "edit_lock_message"}
        ],
        [
            {"text": "✏️ Success Message", "callback": "edit_success_message"},
            {"text": "✏️ Failed Message", "callback": "edit_failed_message"}
        ],
        [
            {"text": "🔗 Watch URL", "callback": "edit_watch_url"},
            {"text": "🔘 Button Text", "callback": "edit_button_text"}
        ]
    ]
    
    await query.edit_message_text(
        "📝 <b>Message Editor</b>\nSelect message to edit:",
        reply_markup=ui.create_keyboard(buttons),
        parse_mode=ParseMode.HTML
    )

async def show_channel_menu(query, context):
    """Show channel manager menu"""
    channels = db.get_channels(active_only=True)
    
    text = "📢 <b>Channel Manager</b>\n\n"
    
    if channels:
        text += "<b>Current Channels:</b>\n"
        for idx, channel in enumerate(channels, 1):
            force_emoji = "🔒" if channel['force_join'] else "🔓"
            text += f"{idx}. {force_emoji} {channel['name']}\n"
    else:
        text += "No channels added.\n"
    
    buttons = []
    
    # Add channel toggle/remove buttons
    for channel in channels:
        force_text = "🔓 Disable Force" if channel['force_join'] else "🔒 Enable Force"
        buttons.append([
            {"text": f"🔄 {force_text}", "callback": f"toggle_force_{channel['channel_id']}"},
            {"text": f"❌ Remove", "callback": f"remove_channel_{channel['channel_id']}"}
        ])
    
    buttons.append([
        {"text": "➕ Add Channel", "callback": "add_channel"}
    ])
    
    await query.edit_message_text(
        text,
        reply_markup=ui.create_keyboard(buttons),
        parse_mode=ParseMode.HTML
    )

async def show_user_menu(query, context):
    """Show user management menu"""
    # Get recent users
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, username, first_name, is_blocked FROM users ORDER BY last_active DESC LIMIT 20')
    users = cursor.fetchall()
    
    text = "👥 <b>User Management</b>\n\n"
    text += "<b>Recent Users (Last 20):</b>\n"
    
    buttons = []
    
    for user in users:
        user_id, username, first_name, is_blocked = user
        status = "🚫" if is_blocked else "✅"
        display_name = username or first_name or f"User {user_id}"
        
        text += f"{status} {display_name} (ID: {user_id})\n"
        
        if is_blocked:
            buttons.append([{"text": f"✅ Unblock {display_name[:10]}", "callback": f"unblock_user_{user_id}"}])
        else:
            buttons.append([{"text": f"🚫 Block {display_name[:10]}", "callback": f"block_user_{user_id}"}])
    
    await query.edit_message_text(
        text,
        reply_markup=ui.create_keyboard(buttons),
        parse_mode=ParseMode.HTML
    )

async def show_settings_menu(query, context):
    """Show settings menu"""
    auto_delete = db.get_config('auto_delete', '60')
    
    text = f"""
⚙️ <b>System Settings</b>

<b>Current Settings:</b>
• Auto Delete: {auto_delete} seconds

<b>Actions:</b>
"""
    
    buttons = [
        [
            {"text": "⏱️ Edit Auto Delete", "callback": "edit_auto_delete"}
        ]
    ]
    
    await query.edit_message_text(
        text,
        reply_markup=ui.create_keyboard(buttons),
        parse_mode=ParseMode.HTML
    )

# ==============================================================================
# 🔄 VERIFICATION HANDLERS
# ==============================================================================

async def handle_verification(query, context):
    """Handle membership verification"""
    user = query.from_user
    
    try:
        # Clear cache and check
        security.clear_user_cache(user.id)
        missing_channels = await security.check_membership(user.id, context.bot)
        
        if not missing_channels:
            # Success - show welcome
            await query.answer("✅ Verified successfully!", show_alert=True)
            
            welcome_msg = db.get_config('welcome_message')
            btn_text = db.get_config('button_text')
            watch_url = db.get_config('watch_url')
            
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton(btn_text, url=watch_url)
            ]])
            
            message = await query.message.reply_text(
                ui.format_text(welcome_msg, user),
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
            
            # Auto-delete both messages
            auto_delete = int(db.get_config('auto_delete', Config.DEFAULT_AUTO_DELETE))
            if auto_delete > 0:
                await asyncio.sleep(auto_delete)
                try:
                    await message.delete()
                    await query.message.delete()
                except:
                    pass
        else:
            # Still missing channels
            await query.answer(
                "❌ 😢💔ওহ নো বেবি! তুমি এখনো সব চেনেল জয়েন করোনি?!😢💔\n"
                "💖✨আমার লক্ষ্মীটা, তুমি যদি নিচের চ্যানেলগুলোতে জয়েন না করো, তাহলে আমি তোমাকে ভিডিওটা দেখাতে পারবো না! 🥺🥀",
                show_alert=True
            )
    except Exception as e:
        logger.error(f"Verification error: {e}")
        await query.answer("⚠️ Error verifying. Please try again.", show_alert=True)

async def handle_post_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle post view requests"""
    query = update.callback_query
    user = query.from_user
    
    post_id = int(query.data.replace("view_post_", ""))
    
    # Get post
    post = db.get_post(post_id)
    if not post:
        await query.answer("❌ Post not found!")
        return
    
    # Check force channels
    force_channels = post.get('force_channels', [])
    
    if force_channels:
        missing_channels = await security.check_membership(user.id, context.bot, force_channels)
        
        if missing_channels:
            # Show failed message
            failed_msg = db.get_config('failed_message')
            
            buttons = []
            for channel in missing_channels:
                channel_data = next((ch for ch in db.get_channels() if ch['channel_id'] == channel['channel_id']), None)
                if channel_data:
                    buttons.append([{
                        "text": f"📢 Join {channel_data['name'][:15]}",
                        "url": channel_data['link']
                    }])
            
            buttons.append([{
                "text": "✅ Verify Now",
                "callback": f"verify_post_{post_id}"
            }])
            
            keyboard = ui.create_keyboard(buttons, add_back=False, add_close=False)
            
            # Send failed message
            message = await query.message.reply_text(
                ui.format_text(failed_msg, user),
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
            
            # Auto-delete after 60 seconds
            await asyncio.sleep(60)
            try:
                await message.delete()
            except:
                pass
            
            await query.answer("❌ Join required channels first!")
            return
    
    # User has access - show success and content
    success_msg = db.get_config('success_message')
    
    # Send success message
    success_message = await query.message.reply_text(
        ui.format_text(success_msg, user),
        parse_mode=ParseMode.HTML
    )
    
    # Create buttons from post
    keyboard_buttons = []
    for btn in post.get('buttons', []):
        keyboard_buttons.append([InlineKeyboardButton(btn['name'], url=btn['link'])])
    
    keyboard = InlineKeyboardMarkup(keyboard_buttons)
    
    # Send post content
    caption = f"<b>{post['title']}</b>\n\n"
    if post.get('post_text'):
        caption += f"{post['post_text']}\n\n"
    caption += "✅ <i>Access granted! Enjoy the content.</i>"
    
    if post.get('photo_id'):
        content_message = await context.bot.send_photo(
            chat_id=user.id,
            photo=post['photo_id'],
            caption=caption,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
    else:
        content_message = await context.bot.send_message(
            chat_id=user.id,
            text=caption,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
    
    # Auto-delete after 60 seconds
    await asyncio.sleep(60)
    try:
        await success_message.delete()
        await content_message.delete()
    except:
        pass
    
    await query.answer("✅ Access granted!")

async def handle_post_verification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle post verification"""
    query = update.callback_query
    user = query.from_user
    
    post_id = int(query.data.replace("verify_post_", ""))
    
    # Clear cache and check
    security.clear_user_cache(user.id)
    
    # Get post
    post = db.get_post(post_id)
    if not post:
        await query.answer("❌ Post not found!")
        return
    
    force_channels = post.get('force_channels', [])
    missing_channels = await security.check_membership(user.id, context.bot, force_channels)
    
    if not missing_channels:
        # Success - show content
        success_msg = db.get_config('success_message')
        
        # Send success message
        success_message = await query.message.reply_text(
            ui.format_text(success_msg, user),
            parse_mode=ParseMode.HTML
        )
        
        # Create buttons
        keyboard_buttons = []
        for btn in post.get('buttons', []):
            keyboard_buttons.append([InlineKeyboardButton(btn['name'], url=btn['link'])])
        
        keyboard = InlineKeyboardMarkup(keyboard_buttons)
        
        # Send content
        caption = f"<b>{post['title']}</b>\n\n"
        if post.get('post_text'):
            caption += f"{post['post_text']}\n\n"
        caption += "✅ <i>Access granted! Enjoy the content.</i>"
        
        if post.get('photo_id'):
            content_message = await context.bot.send_photo(
                chat_id=user.id,
                photo=post['photo_id'],
                caption=caption,
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
        else:
            content_message = await context.bot.send_message(
                chat_id=user.id,
                text=caption,
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
        
        # Auto-delete
        await asyncio.sleep(60)
        try:
            await success_message.delete()
            await content_message.delete()
            await query.message.delete()
        except:
            pass
        
        await query.answer("✅ Verified successfully!")
    else:
        # Still missing
        await query.answer("❌ Still missing some channels!")

# ==============================================================================
# ✏️ CONVERSATION HANDLERS
# ==============================================================================

async def edit_config_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle config editing"""
    key = context.user_data.get('edit_key')
    new_value = update.message.text
    
    if key:
        if db.set_config(key, new_value):
            await update.message.reply_text(
                f"✅ <b>{key}</b> updated successfully!",
                parse_mode=ParseMode.HTML
            )
        else:
            await update.message.reply_text(
                f"❌ Failed to update {key}!",
                parse_mode=ParseMode.HTML
            )
    else:
        await update.message.reply_text("❌ Error: No key specified!")
    
    context.user_data.clear()
    return ConversationHandler.END

async def add_channel_id_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Step 1: Get channel ID"""
    context.user_data['channel_id'] = update.message.text.strip()
    
    await update.message.reply_text(
        "📝 <b>Step 2/3</b>\n\n"
        "Please send the channel name:",
        parse_mode=ParseMode.HTML
    )
    return Config.STATE_CHANNEL_ADD_NAME

async def add_channel_name_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Step 2: Get channel name"""
    context.user_data['channel_name'] = update.message.text
    
    await update.message.reply_text(
        "🔗 <b>Step 3/3</b>\n\n"
        "Please send the channel link (t.me/...):",
        parse_mode=ParseMode.HTML
    )
    return Config.STATE_CHANNEL_ADD_LINK

async def add_channel_link_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Step 3: Get channel link"""
    channel_id = context.user_data.get('channel_id')
    channel_name = context.user_data.get('channel_name')
    channel_link = update.message.text
    
    if db.add_channel(channel_id, channel_name, channel_link):
        await update.message.reply_text(
            f"✅ <b>Channel added successfully!</b>\n\n"
            f"• ID: <code>{channel_id}</code>\n"
            f"• Name: {channel_name}\n"
            f"• Link: {channel_link}",
            parse_mode=ParseMode.HTML
        )
    else:
        await update.message.reply_text("❌ Failed to add channel!")
    
    context.user_data.clear()
    return ConversationHandler.END

async def broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle broadcast"""
    if not context.user_data.get('broadcast'):
        return ConversationHandler.END
    
    # Get all users
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE is_blocked = 0")
    users = [row[0] for row in cursor.fetchall()]
    
    if not users:
        await update.message.reply_text("❌ No users to broadcast!")
        context.user_data.clear()
        return ConversationHandler.END
    
    total = len(users)
    status = await update.message.reply_text(f"📤 Starting broadcast to {total} users...")
    
    success = 0
    failed = 0
    
    for user_id in users:
        try:
            await update.message.copy(user_id)
            success += 1
        except:
            failed += 1
        
        # Update every 20 users
        if (success + failed) % 20 == 0:
            await status.edit_text(f"📤 Broadcasting... {success + failed}/{total}")
    
    await status.edit_text(
        f"✅ <b>Broadcast Complete!</b>\n\n"
        f"• Total: {total}\n"
        f"• Success: {success}\n"
        f"• Failed: {failed}",
        parse_mode=ParseMode.HTML
    )
    
    context.user_data.clear()
    return ConversationHandler.END

async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel conversation"""
    await update.message.reply_text("❌ Operation cancelled.")
    context.user_data.clear()
    
    # Cleanup wizard if exists
    user_id = update.effective_user.id
    if user_id in post_wizard.active_wizards:
        del post_wizard.active_wizards[user_id]
    
    return ConversationHandler.END

# ==============================================================================
# 🚀 APPLICATION SETUP
# ==============================================================================

def setup_application():
    """Setup the application with all handlers"""
    application = ApplicationBuilder().token(Config.TOKEN).build()
    
    # ===== COMMAND HANDLERS =====
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("post", post_command))
    
    # ===== POST WIZARD CONVERSATION =====
    post_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(callback_handler, pattern='^create_post_start$'),
            CommandHandler('post', post_command)
        ],
        states={
            Config.STATE_POST_TITLE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, post_wizard.handle_title)
            ],
            Config.STATE_POST_PHOTO: [
                MessageHandler(filters.PHOTO, post_wizard.handle_photo)
            ],
            Config.STATE_POST_TEXT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, post_wizard.handle_text)
            ],
            Config.STATE_POST_BUTTONS: [
                CallbackQueryHandler(post_wizard.handle_button_management, pattern='^add_button$|^continue_buttons$'),
                MessageHandler(filters.TEXT & ~filters.COMMAND, post_wizard.handle_button_name)
            ],
            Config.STATE_POST_FORCE_CHANNELS: [
                CallbackQueryHandler(post_wizard.handle_force_channel_selection, 
                                   pattern='^select_force_|^select_all_force|^continue_force$')
            ],
            Config.STATE_POST_TARGET_CHANNEL: [
                CallbackQueryHandler(post_wizard.handle_target_channel_selection, pattern='^select_target_')
            ],
            Config.STATE_POST_CONFIRM: [
                CallbackQueryHandler(post_wizard.finalize_post, pattern='^final_post$')
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel_handler)]
    )
    application.add_handler(post_conv)
    
    # ===== EDIT CONFIG CONVERSATION =====
    edit_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(callback_handler, pattern='^edit_')],
        states={
            Config.STATE_EDIT_MESSAGE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, edit_config_handler)
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel_handler)]
    )
    application.add_handler(edit_conv)
    
    # ===== CHANNEL ADD CONVERSATION =====
    channel_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(callback_handler, pattern='^add_channel$')],
        states={
            Config.STATE_CHANNEL_ADD_ID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_channel_id_handler)
            ],
            Config.STATE_CHANNEL_ADD_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_channel_name_handler)
            ],
            Config.STATE_CHANNEL_ADD_LINK: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_channel_link_handler)
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel_handler)]
    )
    application.add_handler(channel_conv)
    
    # ===== BROADCAST CONVERSATION =====
    broadcast_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(callback_handler, pattern='^broadcast_start$')],
        states={
            Config.STATE_BROADCAST: [
                MessageHandler(filters.ALL & ~filters.COMMAND, broadcast_handler)
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel_handler)]
    )
    application.add_handler(broadcast_conv)
    
    # ===== POST VIEW HANDLERS =====
    application.add_handler(CallbackQueryHandler(handle_post_view, pattern='^view_post_'))
    application.add_handler(CallbackQueryHandler(handle_post_verification, pattern='^verify_post_'))
    
    # ===== MAIN CALLBACK HANDLER =====
    application.add_handler(CallbackQueryHandler(callback_handler))
    
    # ===== ERROR HANDLER =====
    application.add_error_handler(error_handler)
    
    return application

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Exception: {context.error}")
    
    try:
        # Notify admin
        error_msg = f"⚠️ <b>Bot Error:</b>\n<code>{context.error}</code>"
        
        for admin_id in Config.ADMIN_IDS:
            try:
                await context.bot.send_message(admin_id, error_msg, parse_mode=ParseMode.HTML)
            except:
                pass
    except:
        pass

# ==============================================================================
# 🚀 MAIN FUNCTION
# ==============================================================================

def main():
    """Main function"""
    logger.info("🚀 Starting Supreme Bot v10.0...")
    logger.info("=" * 60)
    
    # Display stats
    stats = db.get_stats()
    logger.info(f"Total Users: {stats['total_users']}")
    logger.info(f"Active Channels: {stats['active_channels']}")
    logger.info(f"Total Posts: {stats['total_posts']}")
    logger.info("=" * 60)
    
    try:
        # Setup and run application
        application = setup_application()
        application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
        
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
