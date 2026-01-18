"""
================================================================================
SUPREME GOD MODE BOT - ULTIMATE EDITION (70 FEATURES)
VERSION: v12.0 (Enterprise Grade with Romantic Bengali Messages)
AUTHOR: AI ASSISTANT
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
import random
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import List, Dict, Union, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import traceback
import pickle
import base64
import pytz
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
    TOKEN = "8173181203:AAEDcda58agIZZic4uC8tSQVzKbrk6pYnU4"
    ADMIN_IDS = {6406804999}
    DB_NAME = "supreme_bot_v12.db"
    BACKUP_DIR = "backups"
    LOG_FILE = "bot_activity.log"
    
    # System Constants
    DEFAULT_AUTO_DELETE = 45  # seconds
    MAX_MESSAGE_LENGTH = 4000
    FLOOD_LIMIT = 3  # messages per second
    SESSION_TIMEOUT = 300  # 5 minutes
    
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
    
    # Enhanced Emoji Pack
    EMOJIS = {
        "heart": "❤️",
        "star": "⭐",
        "fire": "🔥",
        "lock": "🔒",
        "unlock": "🔓",
        "gear": "⚙️",
        "bell": "🔔",
        "chart": "📊",
        "users": "👥",
        "admin": "👑",
        "camera": "📸",
        "video": "🎬",
        "link": "🔗",
        "time": "⏰",
        "check": "✅",
        "cross": "❌",
        "warn": "⚠️",
        "info": "ℹ️",
        "up": "⬆️",
        "down": "⬇️",
        "left": "⬅️",
        "right": "➡️",
        "refresh": "🔄",
        "plus": "➕",
        "minus": "➖",
        "question": "❓",
        "exclamation": "❗",
        "money": "💰",
        "gift": "🎁",
        "crown": "👑",
        "shield": "🛡️",
        "rocket": "🚀",
        "target": "🎯",
        "megaphone": "📢",
        "pencil": "✏️",
        "trash": "🗑️",
        "database": "💾",
        "cloud": "☁️",
        "sun": "☀️",
        "moon": "🌙",
        "earth": "🌍",
        "flower": "🌸",
        "rose": "🌹",
        "tada": "🎉",
        "sparkles": "✨",
        "rainbow": "🌈",
        "bouquet": "💐",
        "kiss": "💋",
        "love": "💝",
        "cupid": "💘",
        "heartbeat": "💓",
        "hearts": "💕",
        "heartpulse": "💗",
        "twohearts": "💖",
        "smile": "😊",
        "laugh": "😄",
        "wink": "😉",
        "blush": "😊",
        "relaxed": "☺️",
        "kissing": "😗",
        "kissingheart": "😘",
        "relieved": "😌",
        "sunglasses": "😎"
    }
    
    # Conversation States
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

# ==============================================================================
# 💖 ROMANTIC MESSAGE SYSTEM WITH BANGLADESH CONTEXT
# ==============================================================================

class RomanticMessageManager:
    """বাংলা রোমান্টিক মেসেজ ম্যানেজার"""
    
    ROMANTIC_TEMPLATES = {
        "morning": [
            "সুপ্রভাত প্রিয়! ☀️\nআপনার দিনটি হোক মধুর, রঙিন ও ভালোবাসায় ভরা।",
            "ভোরের শিশিরের মতো স্নিগ্ধ হোক আপনার দিনটা 🌄\nসুপ্রভাত, আমার ভালোবাসা!",
            "সকালের কাঁচা রোদ্দুরে প্রথম ভাবনা আপনার জন্য 💫\nশুভ সকাল!",
            "প্রিয়তমা/প্রিয়তম, সকালের আলোয় আপনার জন্য অপেক্ষায় রইলাম 🌅",
            "সকালের এই নির্মল মুহূর্তে আপনার জন্য রইলো অসংখ্য দোয়া 🙏"
        ],
        "afternoon": [
            "দুপুরের রোদে আপনার জন্য একটু ছায়া 🌳\nভালোবাসা রইলো দোয়া সহ!",
            "দুপুরের খাবারের সাথে খেয়ে নিন আমার ভালোবাসা 🍛\nশুভ দুপুর!",
            "দুপুরের বিরতিতে একটু ভাবুন আমার কথা 💭\nমিস ইউ!",
            "দুপুরের ক্লান্তি দূর করতে পাঠালাম আমার ভালোবাসা 💝"
        ],
        "evening": [
            "সন্ধ্যার শান্ত হাওয়ায় উড়ে যাক আমার ভালোবাসা 🌇\nশুভ সন্ধ্যা, প্রিয়তমা!",
            "সন্ধ্যার তারা আসার আগেই বলি, আপনি আমার আকাশের সবচেয়ে উজ্জ্বল তারা 🌟",
            "সন্ধ্যার এই লালিমায় মিশে আছে আপনার জন্য আমার ভালোবাসা 🌆",
            "দিনের শেষে শুধু আপনার কথাই ভাবি... 💭\nশুভ সন্ধ্যা!"
        ],
        "night": [
            "রাতের নীরবতা ভেঙে শুনুন আমার হৃদয়ের ধ্বনি 🌙\nশুভ রাত্রি, ঘুম ভালো হোক!",
            "চাঁদের আলোয় মোড়া এই রাতে আপনার জন্য রইলো অসংখ্য ভালোবাসা 🌕",
            "রাতের তারা গুনতে গুনতে আপনার কথা মনে পড়ে ✨\nগুড নাইট!",
            "ঘুমানোর আগে জানিয়ে রাখি, আপনি আমার স্বপ্নের রানী/রাজা 👑\nশুভ রাত্রি!"
        ],
        "special": [
            "আপনার হাসি আমার জীবনের সবচেয়ে সুন্দর কবিতা 💖",
            "প্রতিটি মুহূর্তে আপনার স্মৃতি ভরিয়ে রাখে আমার মন 🎶",
            "আপনার কথা ভাবলে মনে হয়, ভালোবাসা কোনো শব্দ নয়, এক অনুভূতি 🌹",
            "আপনার চোখে আমি খুঁজে পাই আমার স্বর্গের দরজা 👁️✨",
            "আপনার একটি হাসিতেই উড়ে যায় আমার সকল দুঃখ 😊",
            "আপনাকে পেয়েই বুঝেছি, ভালোবাসা মানে কী ❤️",
            "আপনার সঙ্গে প্রতিটি মুহূর্তই আমার জন্য বিশেষ 🕰️",
            "আপনি হচ্ছেন আমার জীবনের সবচেয়ে সুন্দর অধ্যায় 📖"
        ],
        "seasonal": {
            "summer": "গরমের এই দিনে আপনার জন্য শীতল ভালোবাসা ❄️💓",
            "rainy": "বৃষ্টির ফোঁটার মতো আমার ভালোবাসা পড়বে আপনার জীবনে 🌧️💘",
            "winter": "শীতের কুয়াশায় মোড়া এই দিনে আপনার জন্য উষ্ণ ভালোবাসা 🔥❤️",
            "spring": "বসন্তের ফুলের মতো প্রস্ফুটিত হোক আমাদের ভালোবাসা 🌸💕"
        }
    }
    
    BANGLA_MESSAGES = {
        "welcome": [
            "স্বাগতম প্রিয়! ❤️\nআপনার আগমনে আমার দিনটি উজ্জ্বল হয়ে উঠলো ✨",
            "আপনাকে পেয়ে আজ আমার সমস্ত পৃথিবী আলোকিত 🌟\nস্বাগতম রাজকুমার/রাজকুমারী!",
            "হ্যালো! আপনার জন্য অপেক্ষা করছিলাম 😊\nভালো লাগলো আপনাকে দেখে!",
            "আসসালামু আলাইকুম! আপনার আগমন স্বাগতম 🤲\nআল্লাহ আপনার দিন বরকতময় করুন।"
        ],
        "motivation": [
            "আপনি পারবেন! বিশ্বাস রাখুন নিজের উপর 💪\nআপনার সফলতা নিয়ে অপেক্ষায় রইলাম 🌈",
            "যত বড় বাধাই আসুক না কেন, আপনি জয়ী হবেন 🏆\nআমি আপনার পাশে আছি",
            "সফলতার পথে চলুন, আমি আপনার সঙ্গে আছি 👣\nবিশ্বাস রাখুন নিজের উপর!",
            "আজকের ছোট প্রচেষ্টা আগামীর বড় সফলতা 🌱\nচেষ্টা চালিয়ে যান!"
        ],
        "anniversary": [
            "এই বিশেষ দিনে আপনার জন্য রইলো অসংখ্য শুভেচ্ছা 🎉\nভালোবাসা দিয়ে ভরিয়ে রাখুন দিনটা 💝",
            "প্রতিটি মুহূর্ত হোক স্মরণীয় এই দিনে 📅\nশুভ বার্ষিকী!",
            "ভালোবাসার এই দিনে আপনার জয় হোক 🏆\nশুভ বার্ষিকী প্রিয়!"
        ]
    }
    
    @staticmethod
    def get_time_based_greeting():
        """বাংলাদেশ সময় অনুযায়ী গ্রিটিং"""
        dhaka_tz = pytz.timezone('Asia/Dhaka')
        now = datetime.datetime.now(dhaka_tz)
        hour = now.hour
        
        if 5 <= hour < 12:
            return "সুপ্রভাত", "morning"
        elif 12 <= hour < 16:
            return "শুভ দুপুর", "afternoon"
        elif 16 <= hour < 19:
            return "শুভ সন্ধ্যা", "evening"
        else:
            return "শুভ রাত্রি", "night"
    
    @staticmethod
    def generate_romantic_message(user_name: str = "", category: str = "auto"):
        """রোমান্টিক মেসেজ জেনারেট করুন"""
        greeting, time_category = RomanticMessageManager.get_time_based_greeting()
        
        if category == "auto":
            # 70% সময়ভিত্তিক, 30% বিশেষ মেসেজ
            if random.random() < 0.7:
                messages = RomanticMessageManager.ROMANTIC_TEMPLATES[time_category]
            else:
                messages = RomanticMessageManager.ROMANTIC_TEMPLATES["special"]
        else:
            messages = RomanticMessageManager.ROMANTIC_TEMPLATES.get(category, RomanticMessageManager.ROMANTIC_TEMPLATES["special"])
        
        message = random.choice(messages)
        
        if user_name:
            message = f"প্রিয় {user_name},\n{message}"
        
        # বাংলাদেশের ঋতু অনুযায়ী মেসেজ
        month = datetime.datetime.now().month
        if 3 <= month <= 5:  # গ্রীষ্ম
            seasonal_msg = RomanticMessageManager.ROMANTIC_TEMPLATES["seasonal"]["summer"]
        elif 6 <= month <= 9:  # বর্ষা
            seasonal_msg = RomanticMessageManager.ROMANTIC_TEMPLATES["seasonal"]["rainy"]
        elif 10 <= month <= 11:  # শরৎ
            seasonal_msg = "শরতের নির্মলতা ছড়িয়ে পড়ুক আপনার মনের কোণে 🍁"
        else:  # শীত
            seasonal_msg = RomanticMessageManager.ROMANTIC_TEMPLATES["seasonal"]["winter"]
        
        return f"{greeting}! {message}\n\n{seasonal_msg}"

# Initialize romantic manager
romantic_manager = RomanticMessageManager()

# ==============================================================================
# 📝 ADVANCED LOGGING SYSTEM
# ==============================================================================

class SupremeLogger:
    def __init__(self):
        self.logger = logging.getLogger("SupremeBot")
        self.setup_logging()
        
    def setup_logging(self):
        # Create handlers
        console_handler = logging.StreamHandler(sys.stdout)
        file_handler = logging.FileHandler(Config.LOG_FILE, encoding='utf-8')
        error_handler = logging.FileHandler('errors.log', encoding='utf-8')
        
        # Set levels
        console_handler.setLevel(logging.INFO)
        file_handler.setLevel(logging.DEBUG)
        error_handler.setLevel(logging.ERROR)
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Set formatters
        console_handler.setFormatter(simple_formatter)
        file_handler.setFormatter(detailed_formatter)
        error_handler.setFormatter(detailed_formatter)
        
        # Add handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)
        self.logger.setLevel(logging.DEBUG)
        
        # Log startup
        self.logger.info("=" * 60)
        self.logger.info("💖 SUPREME GOD BOT v12.0 (ROMANTIC EDITION) STARTING...")
        self.logger.info("=" * 60)
    
    def get_logger(self):
        return self.logger

logger_instance = SupremeLogger()
logger = logger_instance.get_logger()

# ==============================================================================
# 🗄️ ENTERPRISE DATABASE MANAGER
# ==============================================================================

class DatabaseManager:
    """Advanced multi-threaded database manager with encryption and backup"""
    
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
        self.backup_dir = Config.BACKUP_DIR
        self.setup_directories()
        self.connection_pool = {}
        self.init_database()
        self._initialized = True
        
    def setup_directories(self):
        """Create necessary directories"""
        os.makedirs(self.backup_dir, exist_ok=True)
        
    def get_connection(self, thread_id=None):
        """Get database connection for thread (thread-safe)"""
        if thread_id is None:
            thread_id = threading.get_ident()
            
        with self._lock:
            if thread_id not in self.connection_pool:
                conn = sqlite3.connect(
                    self.db_path,
                    check_same_thread=False,
                    timeout=30
                )
                conn.execute("PRAGMA journal_mode=WAL")
                conn.execute("PRAGMA synchronous=NORMAL")
                conn.execute("PRAGMA foreign_keys=ON")
                conn.execute("PRAGMA cache_size=-2000")  # 2MB cache
                self.connection_pool[thread_id] = conn
                
            return self.connection_pool[thread_id]
    
    def init_database(self):
        """Initialize database with all tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table with level tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                join_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_active DATETIME DEFAULT CURRENT_TIMESTAMP,
                message_count INTEGER DEFAULT 0,
                user_level INTEGER DEFAULT 1,
                is_vip BOOLEAN DEFAULT 0,
                is_blocked BOOLEAN DEFAULT 0,
                metadata TEXT DEFAULT '{}'
            )
        ''')
        
        # Config table with encryption flag
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                encrypted BOOLEAN DEFAULT 0,
                category TEXT DEFAULT 'general',
                description TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Channels table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS channels (
                channel_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                link TEXT NOT NULL,
                is_private BOOLEAN DEFAULT 0,
                force_join BOOLEAN DEFAULT 1,
                added_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_checked DATETIME,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        # Posts history with force join info
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                post_id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id TEXT,
                post_type TEXT,
                content_hash TEXT,
                sent_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT,
                views INTEGER DEFAULT 0,
                force_channels TEXT DEFAULT '[]',
                FOREIGN KEY (channel_id) REFERENCES channels(channel_id)
            )
        ''')
        
        # User sessions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id INTEGER,
                data TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                expires_at DATETIME,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Activity logs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT,
                details TEXT,
                ip_address TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # VIP users
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vip_users (
                vip_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                level INTEGER DEFAULT 1,
                perks TEXT DEFAULT '{}',
                assigned_by INTEGER,
                assigned_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                expires_at DATETIME,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Flood control
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS flood_control (
                user_id INTEGER PRIMARY KEY,
                message_count INTEGER DEFAULT 0,
                last_message DATETIME DEFAULT CURRENT_TIMESTAMP,
                warning_count INTEGER DEFAULT 0,
                is_temporarily_blocked BOOLEAN DEFAULT 0
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_active ON users(last_active)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_vip ON users(is_vip)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_date ON posts(sent_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_expire ON sessions(expires_at)')
        
        conn.commit()
        self.initialize_defaults()
        logger.info("Database initialized successfully")
    
    def initialize_defaults(self):
        """Initialize default configuration"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Romantic welcome messages
        romantic_welcome = random.choice([
            '''{heart} {star} <b>স্বাগতম প্রিয়!</b> {star} {heart}

{sparkles} <b>আমাদের কমিউনিটিতে যুক্ত হওয়ার জন্য ধন্যবাদ!</b>

{tada} <b>বিশেষ সুবিধা:</b>
• এক্সক্লুসিভ রোমান্টিক কন্টেন্ট
• প্রিমিয়াম ফিচার এক্সেস
• লাইভ আপডেট

{link} <b>নিচের বাটনে ক্লিক করে শুরু করুন:</b>''',
            
            '''🌸 <b>হ্যালো প্রিয় বন্ধু!</b> 🌸

💖 আপনার আগমন আমাদের বিশেষ অনুভূতিতে ভরিয়ে দিয়েছে!

✨ <b>আপনি পাচ্ছেন:</b>
• বিশেষ রোমান্টিক মেসেজ
• এক্সক্লুসিভ কন্টেন্ট
• ভিআইপি সুবিধা

👇 <b>শুরু করতে ক্লিক করুন:</b>''',
            
            '''🌹 <b>স্বাগতম রাজকুমার/রাজকুমারী!</b> 🌹

💝 আপনার জন্য অপেক্ষা করছিলাম!

🎁 <b>বোনাস গিফট:</b>
• ডেইলি রোমান্টিক মেসেজ
• স্পেশাল সিরপ্রাইজ
• প্রিমিয়াম এক্সেস

🔗 <b>শুরু করতে নিচের বাটনে ক্লিক করুন:</b>'''
        ])
        
        defaults = [
            ('welcome_msg', romantic_welcome, 0, 'messages', 'Welcome message for new users'),
            
            ('lock_msg', '''{lock} <b>অ্যাক্সেস লক করা আছে!</b>

{cross} আপনি এখনো আমাদের সব চ্যানেলে জয়েন করেননি।

{info} দয়া করে নিচের চ্যানেলগুলোতে জয়েন করে {check} ভেরিফাই বাটনে ক্লিক করুন।''', 0, 'messages', 'Message shown when user hasn\'t joined channels'),
            
            ('welcome_photo', 'https://images.unsplash.com/photo-1618005198919-d3d4b5a92ead', 0, 'media', 'Welcome photo URL'),
            ('watch_url', 'https://mmshotbd.blogspot.com/?m=1', 0, 'links', 'Main watch URL'),
            ('btn_text', '{video} ভিডিও দেখুন এখনই! {fire}', 0, 'buttons', 'Button text'),
            ('auto_delete', '45', 0, 'settings', 'Auto delete timer in seconds'),
            ('maint_mode', 'OFF', 0, 'security', 'Maintenance mode status'),
            ('force_join', 'ON', 0, 'security', 'Force join channels'),
            ('max_users_per_day', '1000', 0, 'limits', 'Maximum users per day'),
            ('vip_access_level', '2', 0, 'vip', 'VIP access level required'),
            ('backup_interval', '86400', 0, 'system', 'Backup interval in seconds'),
            ('flood_threshold', '5', 0, 'security', 'Flood threshold messages per minute'),
            ('session_timeout', '300', 0, 'security', 'Session timeout in seconds'),
            ('romantic_messages', 'ON', 0, 'features', 'Enable romantic messages'),
            ('bangla_timezone', 'ON', 0, 'features', 'Show Bangladesh time')
        ]
        
        for key, value, encrypted, category, description in defaults:
            cursor.execute('''
                INSERT OR IGNORE INTO config (key, value, encrypted, category, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (key, value, encrypted, category, description))
        
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
    def add_user(self, user_id: int, username: str, first_name: str, last_name: str = ""):
        """Add or update user in database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (user_id, username, first_name, last_name, join_date, last_active)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id) DO UPDATE SET
                username = excluded.username,
                first_name = excluded.first_name,
                last_name = excluded.last_name,
                last_active = CURRENT_TIMESTAMP
            ''', (user_id, username, first_name, last_name))
            
            # Log activity
            cursor.execute('''
                INSERT INTO activity_logs (user_id, action, details)
                VALUES (?, ?, ?)
            ''', (user_id, 'user_join', f'Username: {username}'))
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding user {user_id}: {e}")
            conn.rollback()
            return False
    
    def update_user_activity(self, user_id: int):
        """Update user's last activity timestamp"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE users 
                SET last_active = CURRENT_TIMESTAMP,
                    message_count = message_count + 1
                WHERE user_id = ?
            ''', (user_id,))
            conn.commit()
        except Exception as e:
            logger.error(f"Error updating activity for {user_id}: {e}")
    
    def get_user(self, user_id: int):
        """Get user details"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        columns = [desc[0] for desc in cursor.description]
        row = cursor.fetchone()
        
        if row:
            return dict(zip(columns, row))
        return None
    
    def get_all_users(self, active_only: bool = True):
        """Get all users"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if active_only:
            cursor.execute('''
                SELECT user_id FROM users 
                WHERE is_blocked = 0 
                ORDER BY last_active DESC
            ''')
        else:
            cursor.execute('SELECT user_id FROM users')
            
        return [row[0] for row in cursor.fetchall()]
    
    # === Configuration Management ===
    def get_config(self, key: str, default: str = ""):
        """Get configuration value"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT value FROM config WHERE key = ?", (key,))
        result = cursor.fetchone()
        
        if result:
            value = result[0]
            # Process emoji placeholders
            for emoji_key, emoji in Config.EMOJIS.items():
                value = value.replace(f"{{{emoji_key}}}", emoji)
            return value
        
        return default
    
    def set_config(self, key: str, value: str, encrypted: bool = False, category: str = "general"):
        """Set configuration value"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO config (key, value, encrypted, category, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (key, value, encrypted, category))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error setting config {key}: {e}")
            return False
    
    # === Channel Management ===
    def get_channels(self, force_join_only: bool = False):
        """Get all channels"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if force_join_only:
            cursor.execute('''
                SELECT channel_id, name, link, is_private 
                FROM channels 
                WHERE status = 'active' AND force_join = 1
                ORDER BY name
            ''')
        else:
            cursor.execute('''
                SELECT channel_id, name, link, is_private 
                FROM channels 
                WHERE status = 'active'
                ORDER BY name
            ''')
        
        channels = []
        for row in cursor.fetchall():
            channels.append({
                'id': row[0],
                'name': row[1],
                'link': row[2],
                'is_private': bool(row[3])
            })
        
        return channels
    
    def add_channel(self, channel_id: str, name: str, link: str, is_private: bool = False):
        """Add a new channel"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO channels (channel_id, name, link, is_private, added_date)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (channel_id, name, link, is_private))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding channel {channel_id}: {e}")
            return False
    
    def remove_channel(self, channel_id: str):
        """Remove a channel (soft delete)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("UPDATE channels SET status = 'inactive' WHERE channel_id = ?", (channel_id,))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error removing channel {channel_id}: {e}")
            return False
    
    # === VIP Management ===
    def add_vip(self, user_id: int, level: int = 1, expires_at: str = None):
        """Add user to VIP"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Update users table
            cursor.execute('UPDATE users SET is_vip = 1 WHERE user_id = ?', (user_id,))
            
            # Add to vip_users table
            cursor.execute('''
                INSERT OR REPLACE INTO vip_users (user_id, level, expires_at)
                VALUES (?, ?, ?)
            ''', (user_id, level, expires_at))
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding VIP {user_id}: {e}")
            return False
    
    def is_vip(self, user_id: int):
        """Check if user is VIP"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT is_vip FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        return result and result[0] == 1
    
    # === Statistics ===
    def get_stats(self):
        """Get comprehensive statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # User stats
        cursor.execute("SELECT COUNT(*) FROM users")
        stats['total_users'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE DATE(join_date) = DATE('now')")
        stats['today_users'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_vip = 1")
        stats['vip_users'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_blocked = 1")
        stats['blocked_users'] = cursor.fetchone()[0]
        
        # Channel stats
        cursor.execute("SELECT COUNT(*) FROM channels WHERE status = 'active'")
        stats['active_channels'] = cursor.fetchone()[0]
        
        # Post stats
        cursor.execute("SELECT COUNT(*) FROM posts WHERE DATE(sent_date) = DATE('now')")
        stats['today_posts'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM posts")
        stats['total_posts'] = cursor.fetchone()[0]
        
        return stats

# Initialize database
db = DatabaseManager()

# ==============================================================================
# 🔧 SYSTEM MONITOR
# ==============================================================================

class SystemMonitor:
    """Monitor system resources"""
    
    def __init__(self):
        self.start_time = time.time()
        self.message_count = 0
        self.error_count = 0
        self.user_activity = defaultdict(int)
        
    def get_uptime(self):
        """Get formatted uptime"""
        uptime = time.time() - self.start_time
        days = uptime // (24 * 3600)
        uptime = uptime % (24 * 3600)
        hours = uptime // 3600
        uptime %= 3600
        minutes = uptime // 60
        seconds = uptime % 60
        
        return f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"
    
    def get_system_stats(self):
        """Get comprehensive system statistics"""
        stats = {
            'uptime': self.get_uptime(),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'message_count': self.message_count,
            'error_count': self.error_count,
            'active_users': len(self.user_activity),
        }
        return stats
    
    def increment_message(self):
        """Increment message counter"""
        self.message_count += 1
    
    def increment_error(self):
        """Increment error counter"""
        self.error_count += 1
    
    def update_user_activity(self, user_id: int):
        """Update user activity"""
        self.user_activity[user_id] = time.time()

system_monitor = SystemMonitor()

# ==============================================================================
# 🇧🇩 BANGLADESH TIMEZONE SYSTEM
# ==============================================================================

class BangladeshTimeManager:
    """বাংলাদেশ সময় ব্যবস্থাপনা"""
    
    @staticmethod
    def get_bd_time():
        """বর্তমান বাংলাদেশ সময় পান"""
        dhaka_tz = pytz.timezone('Asia/Dhaka')
        bd_time = datetime.datetime.now(dhaka_tz)
        
        return {
            'time': bd_time.strftime("%I:%M %p"),
            'date': bd_time.strftime("%d %B, %Y"),
            'day': bd_time.strftime("%A"),
            'bangla_day': BangladeshTimeManager.get_bangla_day(bd_time.weekday()),
            'bangla_month': BangladeshTimeManager.get_bangla_month(bd_time.month),
            'full': bd_time.strftime("%d %B, %Y %I:%M %p")
        }
    
    @staticmethod
    def get_bangla_day(weekday):
        """ইংরেজি দিন থেকে বাংলা দিন"""
        days = {
            0: "সোমবার",
            1: "মঙ্গলবার",
            2: "বুধবার",
            3: "বৃহস্পতিবার",
            4: "শুক্রবার",
            5: "শনিবার",
            6: "রবিবার"
        }
        return days.get(weekday, "")
    
    @staticmethod
    def get_bangla_month(month):
        """ইংরেজি মাস থেকে বাংলা মাস"""
        months = {
            1: "জানুয়ারি",
            2: "ফেব্রুয়ারি",
            3: "মার্চ",
            4: "এপ্রিল",
            5: "মে",
            6: "জুন",
            7: "জুলাই",
            8: "আগস্ট",
            9: "সেপ্টেম্বর",
            10: "অক্টোবর",
            11: "নভেম্বর",
            12: "ডিসেম্বর"
        }
        return months.get(month, "")

bd_time_manager = BangladeshTimeManager()

# ==============================================================================
# 🎨 ENHANCED UI MANAGER
# ==============================================================================

class EnhancedUIManager:
    """উন্নত UI ম্যানেজার"""
    
    @staticmethod
    def format_text(text: str, user=None, emojis: bool = True):
        """Format text with user info and emojis"""
        # Replace emoji placeholders
        if emojis:
            for key, emoji in Config.EMOJIS.items():
                text = text.replace(f"{{{key}}}", emoji)
        
        # Add user info if provided
        if user:
            user_info = f"\n\n{Config.EMOJIS['users']} User: {mention_html(user.id, user.first_name or 'User')}"
            text += user_info
        
        # Add Bangladesh time if enabled
        if db.get_config('bangla_timezone') == 'ON':
            bd_time = bd_time_manager.get_bd_time()
            text += f"\n{Config.EMOJIS['time']} বাংলাদেশ সময়: {bd_time['time']}"
        
        return text
    
    @staticmethod
    def create_keyboard(buttons: List[List[Dict]], add_back: bool = True, add_close: bool = False):
        """Create inline keyboard from button configuration"""
        keyboard = []
        
        for row in buttons:
            row_buttons = []
            for btn in row:
                row_buttons.append(
                    InlineKeyboardButton(
                        text=EnhancedUIManager.format_text(btn.get('text', ''), emojis=True),
                        callback_data=btn.get('callback', ''),
                        url=btn.get('url', None)
                    )
                )
            keyboard.append(row_buttons)
        
        # Add back button
        if add_back:
            keyboard.append([
                InlineKeyboardButton("🔙 Back", callback_data="main_menu")
            ])
        
        # Add close button
        if add_close:
            keyboard.append([
                InlineKeyboardButton("❌ Close", callback_data="close_panel")
            ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_beautiful_menu():
        """সুন্দর মেনু তৈরি করুন"""
        buttons = [
            [
                {"text": "💖 রোমান্টিক মেসেজ", "callback": "romantic_menu"},
                {"text": "📅 বাংলাদেশ সময়", "callback": "bd_time_menu"}
            ],
            [
                {"text": "📝 পোস্ট তৈরি করুন", "callback": "enhanced_post_wizard"},
                {"text": "🔗 চ্যানেল ম্যানেজার", "callback": "enhanced_channels"}
            ],
            [
                {"text": "🛡️ সিকিউরিটি প্যানেল", "callback": "security_panel"},
                {"text": "📊 স্ট্যাটিস্টিক্স", "callback": "statistics_panel"}
            ],
            [
                {"text": "⚙️ সেটিংস", "callback": "settings_panel"},
                {"text": "🆘 সাহায্য", "callback": "help_panel"}
            ]
        ]
        
        return EnhancedUIManager.create_keyboard(buttons, add_back=False, add_close=True)
    
    @staticmethod
    def create_gradient_header(text: str):
        """গ্রেডিয়েন্ট হেডার তৈরি করুন"""
        return f"""
✨ <b>{text}</b>
━━━━━━━━━━━━━━━━━━
"""
    
    @staticmethod
    def create_info_box(title: str, content: str, emoji: str = "ℹ️"):
        """ইনফো বক্স তৈরি করুন"""
        return f"""
{emoji} <b>{title}</b>
┌─────────────────
│ {content}
└─────────────────
"""

ui = EnhancedUIManager()

# ==============================================================================
# 🔐 SECURITY MANAGER WITH VERIFICATION
# ==============================================================================

class SecurityManager:
    """Advanced security manager with flood control and verification"""
    
    def __init__(self):
        self.verification_cache = {}
        self.last_verification = {}
    
    async def check_membership(self, user_id: int, bot) -> List[Dict]:
        """Check if user is member of required channels"""
        if db.get_config('force_join') != 'ON':
            return []
        
        # Check cache first
        cache_key = f"membership_{user_id}"
        if cache_key in self.verification_cache:
            cached_time, result = self.verification_cache[cache_key]
            if time.time() - cached_time < 300:  # 5 minute cache
                return result
        
        missing_channels = []
        channels = db.get_channels(force_join_only=True)
        
        for channel in channels:
            try:
                member = await bot.get_chat_member(
                    chat_id=channel['id'],
                    user_id=user_id
                )
                
                if member.status in ['left', 'kicked']:
                    missing_channels.append(channel)
            except Exception as e:
                logger.warning(f"Failed to check channel {channel['id']}: {e}")
                missing_channels.append(channel)
        
        # Update cache
        self.verification_cache[cache_key] = (time.time(), missing_channels)
        
        return missing_channels
    
    async def verify_user_membership(self, user_id: int, bot) -> Tuple[bool, str, List[Dict]]:
        """Verify user membership and return result with message"""
        missing_channels = await self.check_membership(user_id, bot)
        
        if not missing_channels:
            # All channels joined
            greeting, _ = romantic_manager.get_time_based_greeting()
            message = f"{greeting}! 🎉\n\n✅ <b>সকল চ্যানেলে সফলভাবে জয়েন করেছেন!</b>\n\nআপনি এখন সব কন্টেন্ট এক্সেস করতে পারবেন।"
            return True, message, []
        else:
            # Some channels missing
            channel_list = "\n".join([f"• {ch['name']}" for ch in missing_channels])
            message = f"❌ <b>কিছু চ্যানেলে জয়েন করা হয়নি!</b>\n\nনিচের চ্যানেলগুলোতে জয়েন করুন:\n{channel_list}"
            return False, message, missing_channels

security = SecurityManager()

# ==============================================================================
# 🧹 MESSAGE CLEANUP MANAGER
# ==============================================================================

class MessageCleanupManager:
    """ইন্টেলিজেন্ট মেসেজ ক্লিনআপ ম্যানেজার"""
    
    def __init__(self):
        self.user_messages = defaultdict(list)
        self.conversation_states = {}
    
    def add_message(self, chat_id: int, message_id: int):
        """মেসেজ যোগ করুন ট্র্যাক করার জন্য"""
        self.user_messages[chat_id].append(message_id)
        
        # 20টির বেশি মেসেজ হলে পুরনোগুলো মুছে ফেলুন
        if len(self.user_messages[chat_id]) > 20:
            self.user_messages[chat_id] = self.user_messages[chat_id][-10:]

cleanup_manager = MessageCleanupManager()

# ==============================================================================
# 🎮 COMMAND HANDLERS WITH ROMANTIC MESSAGES
# ==============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command with romantic messages"""
    user = update.effective_user
    system_monitor.update_user_activity(user.id)
    system_monitor.increment_message()
    
    # Add user to database
    db.add_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name or ""
    )
    
    # Check maintenance mode
    if user.id not in Config.ADMIN_IDS and db.get_config('maint_mode') == 'ON':
        await update.message.reply_text(
            ui.format_text(
                "🔧 <b>System Maintenance</b>\n\n"
                "We're currently performing maintenance. Please try again later.",
                user
            ),
            parse_mode=ParseMode.HTML
        )
        return
    
    # Check if blocked
    user_data = db.get_user(user.id)
    if user_data and user_data.get('is_blocked'):
        await update.message.reply_text(
            "🚫 Your access has been restricted. Contact admin for assistance.",
            parse_mode=ParseMode.HTML
        )
        return
    
    # Check channel membership
    is_verified, message, missing_channels = await security.verify_user_membership(user.id, context.bot)
    
    if not is_verified:
        # Show lock message with romantic touch
        lock_msg = db.get_config('lock_msg')
        
        # Create channel join buttons
        buttons = []
        for channel in missing_channels:
            buttons.append([
                {
                    "text": f"📢 {channel['name']} এ জয়েন করুন",
                    "url": channel['link']
                }
            ])
        
        buttons.append([
            {
                "text": "✅ আমি জয়েন করেছি",
                "callback": "verify_membership"
            }
        ])
        
        keyboard = ui.create_keyboard(buttons, add_back=False, add_close=False)
        
        # Add romantic element to lock message
        romantic_part = romantic_manager.generate_romantic_message(user.first_name)
        full_message = f"{romantic_part}\n\n{lock_msg}"
        
        try:
            sent_msg = await update.message.reply_photo(
                photo=db.get_config('welcome_photo'),
                caption=ui.format_text(full_message, user),
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
            cleanup_manager.add_message(update.effective_chat.id, sent_msg.message_id)
        except Exception as e:
            logger.error(f"Failed to send photo: {e}")
            sent_msg = await update.message.reply_text(
                ui.format_text(full_message, user),
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
            cleanup_manager.add_message(update.effective_chat.id, sent_msg.message_id)
    else:
        # Show romantic welcome message
        if db.get_config('romantic_messages') == 'ON':
            welcome_msg = romantic_manager.generate_romantic_message(user.first_name)
        else:
            welcome_msg = db.get_config('welcome_msg')
        
        btn_text = db.get_config('btn_text')
        watch_url = db.get_config('watch_url')
        
        # Add Bangladesh time
        bd_time = bd_time_manager.get_bd_time()
        time_info = f"\n\n⏰ বাংলাদেশ সময়: {bd_time['time']}\n📅 তারিখ: {bd_time['date']}"
        
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton(btn_text, url=watch_url)
        ], [
            InlineKeyboardButton("💖 আরও রোমান্টিক মেসেজ", callback_data="more_romantic"),
            InlineKeyboardButton("📅 বাংলাদেশ সময়", callback_data="bdtime_now")
        ]])
        
        try:
            sent_msg = await update.message.reply_photo(
                photo=db.get_config('welcome_photo'),
                caption=ui.format_text(welcome_msg + time_info, user),
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
            cleanup_manager.add_message(update.effective_chat.id, sent_msg.message_id)
            
            # Auto-delete after configured time
            auto_delete = int(db.get_config('auto_delete', Config.DEFAULT_AUTO_DELETE))
            if auto_delete > 0 and user.id not in Config.ADMIN_IDS:
                await asyncio.sleep(auto_delete)
                try:
                    await sent_msg.delete()
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Failed to send welcome: {e}")
            sent_msg = await update.message.reply_text(
                ui.format_text(welcome_msg + time_info, user),
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
            cleanup_manager.add_message(update.effective_chat.id, sent_msg.message_id)

async def romantic_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """রোমান্টিক মেসেজ কমান্ড"""
    user = update.effective_user
    system_monitor.update_user_activity(user.id)
    
    # রোমান্টিক মেসেজ জেনারেট করুন
    romantic_msg = romantic_manager.generate_romantic_message(user.first_name)
    
    # বাংলাদেশ সময় যোগ করুন
    bd_time = bd_time_manager.get_bd_time()
    
    message = f"{romantic_msg}\n\n"
    message += f"⏰ বাংলাদেশ সময়: {bd_time['time']}\n"
    message += f"📅 তারিখ: {bd_time['date']}\n"
    message += f"✨ দিন: {bd_time['bangla_day']}"
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💖 আরেকটি মেসেজ", callback_data="more_romantic")],
        [InlineKeyboardButton("💌 বিশেষ মেসেজ", callback_data="special_message")],
        [InlineKeyboardButton("🔙 মেনু", callback_data="main_menu")]
    ])
    
    sent_msg = await update.message.reply_text(
        message,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )
    cleanup_manager.add_message(update.effective_chat.id, sent_msg.message_id)

async def bdtime_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """বাংলাদেশ সময় কমান্ড"""
    user = update.effective_user
    system_monitor.update_user_activity(user.id)
    
    bd_time = bd_time_manager.get_bd_time()
    
    message = f"""
🇧🇩 <b>বাংলাদেশ সময়</b>

🕐 সময়: <b>{bd_time['time']}</b>
📅 তারিখ: <b>{bd_time['date']}</b>
📆 দিন: <b>{bd_time['bangla_day']}</b>
🗓️ মাস: <b>{bd_time['bangla_month']}</b>

<i>বাংলাদেশের সরকারী সময় অনুযায়ী</i>
"""
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 আপডেট", callback_data="refresh_time")],
        [InlineKeyboardButton("🔙 মেনু", callback_data="main_menu")]
    ])
    
    sent_msg = await update.message.reply_text(
        message,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )
    cleanup_manager.add_message(update.effective_chat.id, sent_msg.message_id)

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin command"""
    user = update.effective_user
    
    if user.id not in Config.ADMIN_IDS:
        await update.message.reply_text("🚫 Access denied!")
        return
    
    system_monitor.update_user_activity(user.id)
    
    stats = db.get_stats()
    sys_stats = system_monitor.get_system_stats()
    
    text = f"""
{Config.EMOJIS['admin']} <b>SUPREME ADMIN PANEL</b>

{Config.EMOJIS['chart']} <b>Bot Statistics:</b>
• Users: {stats['total_users']:,}
• Today: {stats['today_users']:,}
• VIP: {stats['vip_users']:,}

{Config.EMOJIS['gear']} <b>System Status:</b>
• Uptime: {sys_stats['uptime']}
• CPU: {sys_stats['cpu_percent']}%
• Memory: {sys_stats['memory_percent']}%
• Messages: {sys_stats['message_count']:,}

👇 <b>Select an option:</b>
"""
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Statistics", callback_data="menu_stats")],
        [InlineKeyboardButton("📝 Post Wizard", callback_data="enhanced_post_wizard")],
        [InlineKeyboardButton("🔗 Channel Manager", callback_data="menu_channels")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="menu_system")],
        [InlineKeyboardButton("❌ Close", callback_data="close_panel")]
    ])
    
    sent_msg = await update.message.reply_text(
        text,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )
    cleanup_manager.add_message(update.effective_chat.id, sent_msg.message_id)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command"""
    user = update.effective_user
    
    if user.id not in Config.ADMIN_IDS:
        await update.message.reply_text("🚫 Admin only command!")
        return
    
    stats = db.get_stats()
    sys_stats = system_monitor.get_system_stats()
    
    text = f"""
{Config.EMOJIS['chart']} <b>SYSTEM STATISTICS</b>

{Config.EMOJIS['users']} <b>User Stats:</b>
• Total Users: {stats.get('total_users', 0):,}
• Today New: {stats.get('today_users', 0):,}
• VIP Users: {stats.get('vip_users', 0):,}
• Blocked: {stats.get('blocked_users', 0):,}

{Config.EMOJIS['megaphone']} <b>Channel Stats:</b>
• Active Channels: {stats.get('active_channels', 0):,}

{Config.EMOJIS['camera']} <b>Post Stats:</b>
• Total Posts: {stats.get('total_posts', 0):,}
• Today Posts: {stats.get('today_posts', 0):,}

{Config.EMOJIS['gear']} <b>System Info:</b>
• Uptime: {sys_stats['uptime']}
• CPU: {sys_stats['cpu_percent']}%
• Memory: {sys_stats['memory_percent']}%
"""
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Refresh", callback_data="refresh_stats")],
        [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
    ])
    
    sent_msg = await update.message.reply_text(
        ui.format_text(text, user),
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard
    )
    cleanup_manager.add_message(update.effective_chat.id, sent_msg.message_id)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    user = update.effective_user
    system_monitor.update_user_activity(user.id)
    
    text = f"""
{Config.EMOJIS['info']} <b>Supreme Bot Commands</b>

<b>User Commands:</b>
/start - Start the bot
/romantic - Romantic messages
/bdtime - Bangladesh time
/help - Show this help message

<b>Admin Commands:</b>
/admin - Open admin panel
/stats - Show statistics
/backup - Create backup

<b>Features:</b>
• Romantic Bengali messages
• Bangladesh timezone
• Channel verification
• VIP access system
• Auto-delete messages
"""
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💖 Romantic Messages", callback_data="romantic_menu")],
        [InlineKeyboardButton("📅 Bangladesh Time", callback_data="bd_time_menu")],
        [InlineKeyboardButton("🔙 Menu", callback_data="main_menu")]
    ])
    
    sent_msg = await update.message.reply_text(
        ui.format_text(text, user),
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard
    )
    cleanup_manager.add_message(update.effective_chat.id, sent_msg.message_id)

# ==============================================================================
# 🔄 CALLBACK QUERY HANDLER WITH POPUP MESSAGES
# ==============================================================================

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all callback queries with popup messages"""
    query = update.callback_query
    user = query.from_user
    data = query.data
    
    system_monitor.update_user_activity(user.id)
    
    # Admin check for admin functions
    admin_functions = {
        'menu_', 'edit_', 'toggle_', 'remove_', 'add_',
        'broadcast', 'create_post', 'block_user', 'unblock_user',
        'add_vip', 'remove_vip', 'backup_', 'restore_',
        'enhanced_post_wizard'
    }
    
    if any(data.startswith(func) for func in admin_functions) and user.id not in Config.ADMIN_IDS:
        await query.answer("🚫 Admin access required!", show_alert=True)
        return
    
    # Route callbacks
    if data == "verify_membership":
        # Show popup message while checking
        await query.answer("🔍 চ্যানেল চেক করা হচ্ছে...", show_alert=False)
        
        # Check membership
        is_verified, message, missing_channels = await security.verify_user_membership(user.id, query.bot)
        
        if is_verified:
            # Success popup
            await query.answer("✅ সকল চ্যানেলে জয়েন করেছেন! 🎉", show_alert=True)
            
            # Update message with success
            greeting, _ = romantic_manager.get_time_based_greeting()
            welcome_msg = romantic_manager.generate_romantic_message(user.first_name)
            btn_text = db.get_config('btn_text')
            watch_url = db.get_config('watch_url')
            
            bd_time = bd_time_manager.get_bd_time()
            time_info = f"\n\n⏰ বাংলাদেশ সময়: {bd_time['time']}\n📅 তারিখ: {bd_time['date']}"
            
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton(btn_text, url=watch_url)
            ], [
                InlineKeyboardButton("💖 আরও রোমান্টিক মেসেজ", callback_data="more_romantic"),
                InlineKeyboardButton("📅 বাংলাদেশ সময়", callback_data="bdtime_now")
            ]])
            
            try:
                await query.message.edit_caption(
                    caption=ui.format_text(f"{greeting}! 🎉\n\n{welcome_msg}{time_info}", user),
                    reply_markup=keyboard,
                    parse_mode=ParseMode.HTML
                )
            except:
                await query.message.edit_text(
                    ui.format_text(f"{greeting}! 🎉\n\n{welcome_msg}{time_info}", user),
                    reply_markup=keyboard,
                    parse_mode=ParseMode.HTML
                )
        else:
            # Failed popup
            await query.answer("❌ কিছু চ্যানেল মিসিং! আবার চেষ্টা করুন।", show_alert=True)
            
            # Update message with missing channels
            channel_list = "\n".join([f"• {ch['name']}" for ch in missing_channels])
            message = f"❌ <b>কিছু চ্যানেলে জয়েন করা হয়নি!</b>\n\nনিচের চ্যানেলগুলোতে জয়েন করুন:\n{channel_list}"
            
            buttons = []
            for channel in missing_channels:
                buttons.append([
                    {
                        "text": f"📢 {channel['name']} এ জয়েন করুন",
                        "url": channel['link']
                    }
                ])
            
            buttons.append([
                {
                    "text": "✅ আমি জয়েন করেছি",
                    "callback": "verify_membership"
                }
            ])
            
            keyboard = ui.create_keyboard(buttons, add_back=False, add_close=False)
            
            try:
                await query.message.edit_caption(
                    caption=ui.format_text(message, user),
                    reply_markup=keyboard,
                    parse_mode=ParseMode.HTML
                )
            except:
                await query.message.edit_text(
                    ui.format_text(message, user),
                    reply_markup=keyboard,
                    parse_mode=ParseMode.HTML
                )
    
    elif data == "more_romantic":
        await query.answer("💖 নতুন রোমান্টিক মেসেজ লোড হচ্ছে...", show_alert=False)
        
        # Generate new romantic message
        romantic_msg = romantic_manager.generate_romantic_message(user.first_name)
        bd_time = bd_time_manager.get_bd_time()
        
        message = f"{romantic_msg}\n\n"
        message += f"⏰ বাংলাদেশ সময়: {bd_time['time']}\n"
        message += f"📅 তারিখ: {bd_time['date']}"
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("💖 আরেকটি মেসেজ", callback_data="more_romantic")],
            [InlineKeyboardButton("💌 বিশেষ মেসেজ", callback_data="special_message")],
            [InlineKeyboardButton("🔙 মেনু", callback_data="main_menu")]
        ])
        
        await query.edit_message_text(
            message,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
    
    elif data == "bdtime_now" or data == "refresh_time":
        await query.answer("🔄 সময় আপডেট করা হচ্ছে...", show_alert=False)
        
        bd_time = bd_time_manager.get_bd_time()
        
        message = f"""
🇧🇩 <b>বাংলাদেশ সময়</b>

🕐 সময়: <b>{bd_time['time']}</b>
📅 তারিখ: <b>{bd_time['date']}</b>
📆 দিন: <b>{bd_time['bangla_day']}</b>
🗓️ মাস: <b>{bd_time['bangla_month']}</b>

<i>বাংলাদেশের সরকারী সময় অনুযায়ী</i>
"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 আপডেট", callback_data="refresh_time")],
            [InlineKeyboardButton("🔙 মেনু", callback_data="main_menu")]
        ])
        
        await query.edit_message_text(
            message,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
    
    elif data == "romantic_menu":
        await query.answer("💖 রোমান্টিক মেসেজ মেনু", show_alert=False)
        
        romantic_msg = romantic_manager.generate_romantic_message(user.first_name)
        bd_time = bd_time_manager.get_bd_time()
        
        message = f"{romantic_msg}\n\n"
        message += f"⏰ বাংলাদেশ সময়: {bd_time['time']}\n"
        message += f"📅 তারিখ: {bd_time['date']}\n"
        message += f"✨ দিন: {bd_time['bangla_day']}"
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("💖 আরেকটি মেসেজ", callback_data="more_romantic")],
            [InlineKeyboardButton("💌 বিশেষ মেসেজ", callback_data="special_message")],
            [InlineKeyboardButton("📅 বাংলাদেশ সময়", callback_data="bd_time_menu")],
            [InlineKeyboardButton("🔙 মেনু", callback_data="main_menu")]
        ])
        
        await query.edit_message_text(
            message,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
    
    elif data == "bd_time_menu":
        await query.answer("📅 বাংলাদেশ সময় মেনু", show_alert=False)
        
        bd_time = bd_time_manager.get_bd_time()
        
        message = f"""
🇧🇩 <b>বাংলাদেশ সময়</b>

🕐 সময়: <b>{bd_time['time']}</b>
📅 তারিখ: <b>{bd_time['date']}</b>
📆 দিন: <b>{bd_time['bangla_day']}</b>
🗓️ মাস: <b>{bd_time['bangla_month']}</b>

<i>বাংলাদেশের সরকারী সময় অনুযায়ী</i>
"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 আপডেট", callback_data="refresh_time")],
            [InlineKeyboardButton("💖 রোমান্টিক মেসেজ", callback_data="romantic_menu")],
            [InlineKeyboardButton("🔙 মেনু", callback_data="main_menu")]
        ])
        
        await query.edit_message_text(
            message,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
    
    elif data == "special_message":
        await query.answer("💌 বিশেষ মেসেজ লোড হচ্ছে...", show_alert=False)
        
        # Special romantic message
        special_messages = [
            "আপনার একটি হাসি আমার সমস্ত দুঃখ দূর করে দেয় 😊",
            "আপনাকে দেখলে মনে হয়, সবকিছু সম্ভব 💪",
            "আপনার সাথে থাকার প্রতিটি মুহূর্তই আমার জন্য স্বর্গ 🏰",
            "আপনি হচ্ছেন আমার জীবনের সবচেয়ে সুন্দর উপহার 🎁"
        ]
        
        romantic_msg = random.choice(special_messages)
        bd_time = bd_time_manager.get_bd_time()
        
        message = f"💌 <b>বিশেষ মেসেজ:</b>\n\n{romantic_msg}\n\n"
        message += f"⏰ বাংলাদেশ সময়: {bd_time['time']}\n"
        message += f"📅 তারিখ: {bd_time['date']}"
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("💖 আরেকটি মেসেজ", callback_data="more_romantic")],
            [InlineKeyboardButton("📅 বাংলাদেশ সময়", callback_data="bd_time_menu")],
            [InlineKeyboardButton("🔙 মেনু", callback_data="main_menu")]
        ])
        
        await query.edit_message_text(
            message,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
    
    elif data == "main_menu":
        await query.answer("🏠 মেনুতে ফিরছেন...", show_alert=False)
        
        # Generate romantic welcome
        welcome_msg = romantic_manager.generate_romantic_message(user.first_name)
        bd_time = bd_time_manager.get_bd_time()
        
        message = f"{welcome_msg}\n\n"
        message += f"⏰ বাংলাদেশ সময়: {bd_time['time']}\n"
        message += f"📅 তারিখ: {bd_time['date']}\n\n"
        message += "👇 <b>নিচের মেনু থেকে নির্বাচন করুন:</b>"
        
        await query.edit_message_text(
            message,
            reply_markup=ui.create_beautiful_menu(),
            parse_mode=ParseMode.HTML
        )
    
    elif data == "close_panel":
        await query.answer("❌ প্যানেল বন্ধ করা হয়েছে", show_alert=False)
        try:
            await query.delete_message()
        except:
            pass
    
    elif data == "menu_stats":
        await query.answer("📊 স্ট্যাটিস্টিক্স লোড হচ্ছে...", show_alert=False)
        
        stats = db.get_stats()
        sys_stats = system_monitor.get_system_stats()
        
        text = f"""
{Config.EMOJIS['chart']} <b>SYSTEM STATISTICS</b>

{Config.EMOJIS['users']} <b>User Stats:</b>
• Total Users: {stats.get('total_users', 0):,}
• Today New: {stats.get('today_users', 0):,}
• VIP Users: {stats.get('vip_users', 0):,}

{Config.EMOJIS['megaphone']} <b>Channel Stats:</b>
• Active Channels: {stats.get('active_channels', 0):,}

{Config.EMOJIS['gear']} <b>System Info:</b>
• Uptime: {sys_stats['uptime']}
• CPU: {sys_stats['cpu_percent']}%
• Memory: {sys_stats['memory_percent']}%
"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Refresh", callback_data="refresh_stats")],
            [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
        ])
        
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard
        )
    
    elif data == "refresh_stats":
        await query.answer("🔄 স্ট্যাটিস্টিক্স আপডেট করা হচ্ছে...", show_alert=False)
        query.data = "menu_stats"
        await callback_handler(update, context)
    
    elif data == "enhanced_post_wizard":
        await query.answer("📝 পোস্ট উইজার্ড শুরু হচ্ছে...", show_alert=True)
        await start_post_wizard_handler(update, context)
    
    elif data == "menu_channels":
        await query.answer("🔗 চ্যানেল ম্যানেজার", show_alert=False)
        
        channels = db.get_channels()
        text = "📢 <b>Channel Manager</b>\n\n"
        
        if channels:
            text += "<b>Current Channels:</b>\n"
            for idx, channel in enumerate(channels[:10], 1):  # Show first 10 only
                text += f"{idx}. {channel['name']}\n"
        else:
            text += "No channels added.\n"
        
        if len(channels) > 10:
            text += f"\n... and {len(channels) - 10} more channels"
        
        keyboard = [
            [InlineKeyboardButton("➕ Add Channel", callback_data="add_channel_start")],
            [InlineKeyboardButton("📋 Channel List", callback_data="channel_list_full")],
            [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
        ]
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )
    
    elif data == "menu_system":
        await query.answer("⚙️ সিস্টেম সেটিংস", show_alert=False)
        
        sys_stats = system_monitor.get_system_stats()
        maint_status = db.get_config('maint_mode')
        romantic_status = db.get_config('romantic_messages')
        timezone_status = db.get_config('bangla_timezone')
        
        text = f"""
⚙️ <b>System Settings</b>

<b>System Status:</b>
• Uptime: {sys_stats['uptime']}
• CPU: {sys_stats['cpu_percent']}%
• Memory: {sys_stats['memory_percent']}%

<b>Feature Status:</b>
• Maintenance Mode: {maint_status}
• Romantic Messages: {romantic_status}
• Bangladesh Timezone: {timezone_status}

<b>Actions:</b>
"""
        
        keyboard = [
            [
                InlineKeyboardButton(f"🔧 Maintenance: {maint_status}", callback_data=f"toggle_maint"),
                InlineKeyboardButton(f"💖 Romantic: {romantic_status}", callback_data=f"toggle_romantic")
            ],
            [
                InlineKeyboardButton(f"🇧🇩 Timezone: {timezone_status}", callback_data=f"toggle_timezone"),
                InlineKeyboardButton("💾 Backup", callback_data="backup_now")
            ],
            [
                InlineKeyboardButton("🔙 Back", callback_data="main_menu")
            ]
        ]
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )
    
    elif data.startswith("toggle_"):
        key = data.replace("toggle_", "")
        current = db.get_config(key)
        new_value = "ON" if current == "OFF" else "OFF"
        db.set_config(key, new_value)
        
        await query.answer(f"✅ {key} set to {new_value}", show_alert=True)
        # Refresh menu
        if key == "maint_mode":
            query.data = "menu_system"
        elif key in ["romantic_messages", "bangla_timezone"]:
            query.data = "menu_system"
        await callback_handler(update, context)
    
    elif data == "backup_now":
        await query.answer("💾 ব্যাকআপ তৈরি করা হচ্ছে...", show_alert=True)
        
        # Create backup in background
        backup_file = db.create_backup()
        
        if backup_file:
            await query.message.reply_text(
                f"✅ <b>Backup created successfully!</b>\n\n"
                f"File: {os.path.basename(backup_file)}\n"
                f"Size: {os.path.getsize(backup_file) // 1024} KB",
                parse_mode=ParseMode.HTML
            )
        else:
            await query.message.reply_text("❌ Failed to create backup!")
    
    else:
        await query.answer("❌ Unknown action!", show_alert=True)

# ==============================================================================
# 📝 ENHANCED POST WIZARD HANDLERS
# ==============================================================================

async def start_post_wizard_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start enhanced post wizard"""
    query = update.callback_query
    if query:
        await query.answer()
        user = query.from_user
        message = query.message
    else:
        user = update.effective_user
        message = update.message
    
    context.user_data['post_wizard'] = {
        'step': 1,
        'data': {},
        'force_channels': [],
        'target_channels': []
    }
    
    text = """
📝 <b>পোস্ট উইজার্ড - ধাপ ১/৬</b>

✨ <b>পোস্টের টাইটেল লিখুন:</b>
HTML ফরম্যাট সাপোর্টেড:
<code>&lt;b&gt;বোল্ড&lt;/b&gt;</code>
<code>&lt;i&gt;ইটালিক&lt;/i&gt;</code>
<code>&lt;u&gt;আন্ডারলাইন&lt;/u&gt;</code>
<code>&lt;a href='লিঙ্ক'&gt;টেক্সট&lt;/a&gt;</code>

<b>উদাহরণ:</b>
<i>আজকের বিশেষ অফার!</i>

আপনার টাইটেল লিখুন:
"""
    
    if query:
        await message.edit_text(text, parse_mode=ParseMode.HTML)
        await message.reply_text("আপনার টাইটেল লিখুন:")
    else:
        await message.reply_text(text, parse_mode=ParseMode.HTML)
    
    return "POST_TITLE"

async def post_title_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle post title"""
    title = update.message.text_html
    context.user_data['post_wizard']['data']['title'] = title
    context.user_data['post_wizard']['step'] = 2
    
    await update.message.reply_text(
        "🖼️ <b>পোস্ট উইজার্ড - ধাপ ২/৬</b>\n\n"
        "📸 <b>ফটো আপলোড করুন:</b>\n"
        "একটি ফটো বা ছবি পাঠান (স্কিপ করতে 'skip' লিখুন):",
        parse_mode=ParseMode.HTML
    )
    
    # Delete user message
    try:
        await update.message.delete()
    except:
        pass
    
    return "POST_PHOTO"

async def post_photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle post photo"""
    if update.message.text and update.message.text.lower() == 'skip':
        context.user_data['post_wizard']['data']['photo'] = None
        context.user_data['post_wizard']['data']['has_media'] = False
    elif update.message.photo:
        context.user_data['post_wizard']['data']['photo'] = update.message.photo[-1].file_id
        context.user_data['post_wizard']['data']['has_media'] = True
    else:
        await update.message.reply_text("❌ দয়া করে একটি ফটো পাঠান বা 'skip' লিখুন")
        return "POST_PHOTO"
    
    context.user_data['post_wizard']['step'] = 3
    
    # Delete user message
    try:
        await update.message.delete()
    except:
        pass
    
    await update.message.reply_text(
        "🔘 <b>পোস্ট উইজার্ড - ধাপ ৩/৬</b>\n\n"
        "🛠️ <b>বাটন কাস্টমাইজ করুন:</b>\n"
        "বাটনের টেক্সট লিখুন (ডিফল্ট ব্যবহার করতে 'default' লিখুন):\n\n"
        f"বর্তমান ডিফল্ট: <code>{db.get_config('btn_text')}</code>",
        parse_mode=ParseMode.HTML
    )
    return "POST_BUTTON"

async def post_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button text"""
    if update.message.text and update.message.text.lower() == 'default':
        context.user_data['post_wizard']['data']['button_text'] = db.get_config('btn_text')
    else:
        context.user_data['post_wizard']['data']['button_text'] = update.message.text
    
    context.user_data['post_wizard']['step'] = 4
    
    # Delete user message
    try:
        await update.message.delete()
    except:
        pass
    
    # Get force join channels
    channels = db.get_channels(force_join_only=True)
    
    if not channels:
        await update.message.reply_text(
            "ℹ️ <b>কোন ফোর্স জয়েন চ্যানেল নেই</b>\n\n"
            "পরবর্তী ধাপে যাচ্ছেন...",
            parse_mode=ParseMode.HTML
        )
        context.user_data['post_wizard']['data']['force_channels'] = []
        return await post_force_channels_handler(update, context)
    
    # Create channel selection
    channel_list = "\n".join([f"{i+1}. {ch['name']}" for i, ch in enumerate(channels)])
    
    keyboard = []
    for channel in channels:
        keyboard.append([
            InlineKeyboardButton(
                f"⬜ {channel['name']}",
                callback_data=f"wiz_force_{channel['id']}"
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton("✅ সব সিলেক্ট", callback_data="wiz_force_all"),
        InlineKeyboardButton("❌ সব আনসিলেক্ট", callback_data="wiz_force_none")
    ])
    
    keyboard.append([
        InlineKeyboardButton("👉 পরবর্তী ধাপ", callback_data="wiz_force_next")
    ])
    
    await update.message.reply_text(
        f"🔐 <b>পোস্ট উইজার্ড - ধাপ ৪/৬</b>\n\n"
        f"🎯 <b>ফোর্স জয়েন চ্যানেল সিলেক্ট করুন:</b>\n"
        f"এই চ্যানেলগুলোতে জয়েন না করলে ইউজাররা পোস্ট দেখতে পারবে না\n\n"
        f"<b>চ্যানেল লিস্ট:</b>\n{channel_list}\n\n"
        f"সিলেক্ট করুন (একাধিক সিলেক্ট করা যাবে):",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML
    )
    return "POST_FORCE_CHANNELS"

async def post_force_channels_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle force channel selection"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "wiz_force_next":
        context.user_data['post_wizard']['step'] = 5
        
        # Get target channels
        channels = db.get_channels()
        
        if not channels:
            await query.message.edit_text(
                "❌ <b>কোন চ্যানেল নেই!</b>\n\n"
                "পোস্ট করার জন্য দয়া করে আগে চ্যানেল যোগ করুন।",
                parse_mode=ParseMode.HTML
            )
            return ConversationHandler.END
        
        # Create target channel selection
        channel_list = "\n".join([f"{i+1}. {ch['name']}" for i, ch in enumerate(channels[:10])])
        if len(channels) > 10:
            channel_list += f"\n... এবং আরও {len(channels)-10} টি চ্যানেল"
        
        keyboard = []
        for channel in channels:
            keyboard.append([
                InlineKeyboardButton(
                    f"⬜ {channel['name']}",
                    callback_data=f"wiz_target_{channel['id']}"
                )
            ])
        
        keyboard.append([
            InlineKeyboardButton("📤 সব চ্যানেল", callback_data="wiz_target_all"),
            InlineKeyboardButton("👑 ভিআইপি চ্যানেল", callback_data="wiz_target_vip")
        ])
        
        keyboard.append([
            InlineKeyboardButton("👉 পরবর্তী ধাপ", callback_data="wiz_target_next")
        ])
        
        await query.message.edit_text(
            f"📤 <b>পোস্ট উইজার্ড - ধাপ ৫/৬</b>\n\n"
            f"🎯 <b>টার্গেট চ্যানেল সিলেক্ট করুন:</b>\n"
            f"এই চ্যানেলগুলোতে পোস্টটি শেয়ার করা হবে\n\n"
            f"<b>চ্যানেল লিস্ট:</b>\n{channel_list}\n\n"
            f"সিলেক্ট করুন (একাধিক সিলেক্ট করা যাবে):",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )
        return "POST_TARGET_CHANNELS"
    
    elif data.startswith("wiz_force_"):
        channel_id = data.replace("wiz_force_", "")
        
        if channel_id == "all":
            channels = db.get_channels(force_join_only=True)
            context.user_data['post_wizard']['force_channels'] = [ch['id'] for ch in channels]
        elif channel_id == "none":
            context.user_data['post_wizard']['force_channels'] = []
        else:
            if channel_id in context.user_data['post_wizard']['force_channels']:
                context.user_data['post_wizard']['force_channels'].remove(channel_id)
            else:
                context.user_data['post_wizard']['force_channels'].append(channel_id)
        
        # Update buttons
        channels = db.get_channels(force_join_only=True)
        keyboard = []
        for channel in channels:
            is_selected = channel['id'] in context.user_data['post_wizard']['force_channels']
            keyboard.append([
                InlineKeyboardButton(
                    f"{'✅' if is_selected else '⬜'} {channel['name']}",
                    callback_data=f"wiz_force_{channel['id']}"
                )
            ])
        
        keyboard.append([
            InlineKeyboardButton("✅ সব সিলেক্ট", callback_data="wiz_force_all"),
            InlineKeyboardButton("❌ সব আনসিলেক্ট", callback_data="wiz_force_none")
        ])
        
        keyboard.append([
            InlineKeyboardButton("👉 পরবর্তী ধাপ", callback_data="wiz_force_next")
        ])
        
        selected_count = len(context.user_data['post_wizard']['force_channels'])
        
        await query.message.edit_text(
            f"🔐 <b>পোস্ট উইজার্ড - ধাপ ৪/৬</b>\n\n"
            f"🎯 <b>ফোর্স জয়েন চ্যানেল সিলেক্ট করুন:</b>\n"
            f"সিলেক্টেড: {selected_count} টি চ্যানেল\n\n"
            f"সিলেক্ট করুন (একাধিক সিলেক্ট করা যাবে):",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )
    
    return "POST_FORCE_CHANNELS"

async def post_target_channels_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle target channel selection"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "wiz_target_next":
        context.user_data['post_wizard']['step'] = 6
        
        # Create preview
        data = context.user_data['post_wizard']['data']
        force_channels = context.user_data['post_wizard']['force_channels']
        target_channels = context.user_data['post_wizard']['target_channels']
        
        preview = "🎯 <b>পোস্ট প্রিভিউ - ধাপ ৬/৬</b>\n\n"
        preview += f"<b>টাইটেল:</b>\n{data.get('title', 'N/A')[:200]}...\n\n"
        
        if data.get('has_media'):
            preview += "🖼️ <b>ফটো:</b> আছে\n"
        else:
            preview += "🖼️ <b>ফটো:</b> নেই\n"
        
        preview += f"🔘 <b>বাটন টেক্সট:</b> {data.get('button_text', 'N/A')[:50]}\n\n"
        
        preview += f"🔐 <b>ফোর্স জয়েন চ্যানেল:</b> {len(force_channels)} টি\n"
        preview += f"📤 <b>টার্গেট চ্যানেল:</b> {len(target_channels)} টি\n\n"
        
        preview += "👇 <b>নিচের অপশন থেকে একটি সিলেক্ট করুন:</b>"
        
        keyboard = [
            [
                InlineKeyboardButton("✅ পোস্ট করুন", callback_data="wiz_post_confirm"),
                InlineKeyboardButton("✏️ এডিট করুন", callback_data="wiz_post_edit")
            ],
            [
                InlineKeyboardButton("↩️ নতুন করে শুরু", callback_data="wiz_post_restart"),
                InlineKeyboardButton("❌ বাতিল করুন", callback_data="wiz_post_cancel")
            ]
        ]
        
        await query.message.edit_text(
            preview,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )
        return "POST_PREVIEW"
    
    elif data.startswith("wiz_target_"):
        channel_id = data.replace("wiz_target_", "")
        
        if channel_id == "all":
            channels = db.get_channels()
            context.user_data['post_wizard']['target_channels'] = [ch['id'] for ch in channels]
        elif channel_id == "vip":
            vip_channels = [ch for ch in db.get_channels() if ch.get('is_private', False)]
            context.user_data['post_wizard']['target_channels'] = [ch['id'] for ch in vip_channels]
        else:
            if channel_id in context.user_data['post_wizard']['target_channels']:
                context.user_data['post_wizard']['target_channels'].remove(channel_id)
            else:
                context.user_data['post_wizard']['target_channels'].append(channel_id)
        
        # Update buttons
        channels = db.get_channels()
        keyboard = []
        for channel in channels:
            is_selected = channel['id'] in context.user_data['post_wizard']['target_channels']
            keyboard.append([
                InlineKeyboardButton(
                    f"{'📤' if is_selected else '⬜'} {channel['name']}",
                    callback_data=f"wiz_target_{channel['id']}"
                )
            ])
        
        keyboard.append([
            InlineKeyboardButton("📤 সব চ্যানেল", callback_data="wiz_target_all"),
            InlineKeyboardButton("👑 ভিআইপি চ্যানেল", callback_data="wiz_target_vip")
        ])
        
        keyboard.append([
            InlineKeyboardButton("👉 পরবর্তী ধাপ", callback_data="wiz_target_next")
        ])
        
        selected_count = len(context.user_data['post_wizard']['target_channels'])
        
        await query.message.edit_text(
            f"📤 <b>পোস্ট উইজার্ড - ধাপ ৫/৬</b>\n\n"
            f"🎯 <b>টার্গেট চ্যানেল সিলেক্ট করুন:</b>\n"
            f"সিলেক্টেড: {selected_count} টি চ্যানেল\n\n"
            f"সিলেক্ট করুন (একাধিক সিলেক্ট করা যাবে):",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )
    
    return "POST_TARGET_CHANNELS"

async def post_preview_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle post preview"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "wiz_post_confirm":
        await query.answer("📤 পোস্ট করা হচ্ছে...", show_alert=True)
        await send_final_post(query, context)
        return ConversationHandler.END
    
    elif data == "wiz_post_edit":
        await query.answer("✏️ এডিট মেনু", show_alert=False)
        
        keyboard = [
            [
                InlineKeyboardButton("✏️ টাইটেল এডিট", callback_data="wiz_edit_title"),
                InlineKeyboardButton("🖼️ ফটো এডিট", callback_data="wiz_edit_photo")
            ],
            [
                InlineKeyboardButton("🔘 বাটন এডিট", callback_data="wiz_edit_button"),
                InlineKeyboardButton("🔐 ফোর্স চ্যানেল", callback_data="wiz_edit_force")
            ],
            [
                InlineKeyboardButton("📤 টার্গেট চ্যানেল", callback_data="wiz_edit_target"),
                InlineKeyboardButton("↩️ প্রিভিউ", callback_data="wiz_back_preview")
            ]
        ]
        
        await query.edit_message_text(
            "✏️ <b>কোনটি এডিট করতে চান?</b>",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )
        return "POST_EDIT"
    
    elif data == "wiz_post_restart":
        await query.answer("🔄 নতুন পোস্ট শুরু হচ্ছে...", show_alert=False)
        context.user_data.clear()
        await start_post_wizard_handler(update, context)
    
    elif data == "wiz_post_cancel":
        await query.answer("❌ পোস্ট বাতিল করা হয়েছে", show_alert=True)
        await query.edit_message_text("❌ পোস্ট বাতিল করা হয়েছে!")
        context.user_data.clear()
        return ConversationHandler.END
    
    elif data == "wiz_back_preview":
        query.data = "wiz_target_next"
        await post_target_channels_handler(update, context)
    
    return "POST_PREVIEW"

async def send_final_post(query, context):
    """Send final post to channels"""
    data = context.user_data['post_wizard']['data']
    force_channels = context.user_data['post_wizard']['force_channels']
    target_channels = context.user_data['post_wizard']['target_channels']
    
    if not target_channels:
        await query.edit_message_text("❌ কোনো টার্গেট চ্যানেল সিলেক্ট করা হয়নি!")
        return
    
    button_text = data.get('button_text', db.get_config('btn_text'))
    watch_url = db.get_config('watch_url')
    
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(button_text, url=watch_url)
    ]])
    
    post_message = data.get('title', '')
    
    # Add force join info if any
    if force_channels:
        force_text = "\n\n🔐 <b>ফোর্স জয়েন চ্যানেল:</b>\n"
        for channel_id in force_channels[:5]:  # Show first 5 only
            channel = next((ch for ch in db.get_channels() if ch['id'] == channel_id), None)
            if channel:
                force_text += f"• {channel['name']}\n"
        if len(force_channels) > 5:
            force_text += f"... এবং আরও {len(force_channels)-5} টি\n"
        post_message += force_text
    
    # Show preview to admin
    preview_msg = await query.message.reply_text(
        "📤 <b>পোস্ট প্রিভিউ:</b>\n" + post_message[:500] + ("..." if len(post_message) > 500 else ""),
        parse_mode=ParseMode.HTML
    )
    
    status_msg = await query.message.reply_text(f"⏳ {len(target_channels)} টি চ্যানেলে পোস্ট করা হচ্ছে...")
    
    success = 0
    failed = 0
    
    for channel_id in target_channels:
        try:
            channel = next((ch for ch in db.get_channels() if ch['id'] == channel_id), None)
            if not channel:
                failed += 1
                continue
            
            if data.get('has_media') and data.get('photo'):
                await context.bot.send_photo(
                    chat_id=channel_id,
                    photo=data['photo'],
                    caption=post_message,
                    reply_markup=keyboard,
                    parse_mode=ParseMode.HTML
                )
            else:
                await context.bot.send_message(
                    chat_id=channel_id,
                    text=post_message,
                    reply_markup=keyboard,
                    parse_mode=ParseMode.HTML
                )
            success += 1
        except Exception as e:
            failed += 1
            logger.error(f"Failed to post to {channel_id}: {e}")
        
        await asyncio.sleep(1)  # Rate limiting
    
    await status_msg.edit_text(
        f"✅ <b>পোস্টিং সম্পন্ন!</b>\n\n"
        f"• সফল: {success}\n"
        f"• ব্যর্থ: {failed}\n"
        f"• মোট: {len(target_channels)}",
        parse_mode=ParseMode.HTML
    )
    
    # Delete preview
    try:
        await preview_msg.delete()
    except:
        pass
    
    context.user_data.clear()

async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel conversation"""
    await update.message.reply_text("❌ Operation cancelled.")
    context.user_data.clear()
    return ConversationHandler.END

# ==============================================================================
# 🚀 MAIN APPLICATION SETUP
# ==============================================================================

def setup_application():
    """Setup the Telegram application with all handlers"""
    
    # Create application
    application = ApplicationBuilder() \
        .token(Config.TOKEN) \
        .connection_pool_size(10) \
        .pool_timeout(30) \
        .read_timeout(30) \
        .write_timeout(30) \
        .get_updates_read_timeout(30) \
        .http_version("1.1") \
        .build()
    
    # ===== CONVERSATION HANDLERS =====
    
    # Enhanced post wizard conversation
    post_wizard_conv = ConversationHandler(
        entry_points=[
            CommandHandler("post", start_post_wizard_handler),
            CallbackQueryHandler(start_post_wizard_handler, pattern='^enhanced_post_wizard$')
        ],
        states={
            "POST_TITLE": [MessageHandler(filters.TEXT & ~filters.COMMAND, post_title_handler)],
            "POST_PHOTO": [MessageHandler(filters.PHOTO | filters.TEXT, post_photo_handler)],
            "POST_BUTTON": [MessageHandler(filters.TEXT & ~filters.COMMAND, post_button_handler)],
            "POST_FORCE_CHANNELS": [CallbackQueryHandler(post_force_channels_handler, pattern='^wiz_force_')],
            "POST_TARGET_CHANNELS": [CallbackQueryHandler(post_target_channels_handler, pattern='^wiz_target_')],
            "POST_PREVIEW": [CallbackQueryHandler(post_preview_handler, pattern='^wiz_post_')],
            "POST_EDIT": [CallbackQueryHandler(post_preview_handler, pattern='^wiz_edit_|^wiz_back_')]
        },
        fallbacks=[CommandHandler('cancel', cancel_handler)]
    )
    
    # ===== ADD HANDLERS =====
    
    # Command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("romantic", romantic_command))
    application.add_handler(CommandHandler("bdtime", bdtime_command))
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # Conversation handlers
    application.add_handler(post_wizard_conv)
    
    # Callback query handler (must be last)
    application.add_handler(CallbackQueryHandler(callback_handler))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    return application

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors gracefully"""
    system_monitor.increment_error()
    
    # Log error
    logger.error(f"Exception while handling update: {context.error}")
    
    # Send traceback to log file
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = ''.join(tb_list)
    logger.error(f"Traceback:\n{tb_string}")
    
    # Try to send error message to user
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ An error occurred. The admin has been notified.",
                parse_mode=ParseMode.HTML
            )
    except:
        pass

async def set_bot_commands(application: Application):
    """Set bot commands for menu"""
    commands = [
        BotCommand("start", "Start the bot with romantic welcome"),
        BotCommand("romantic", "Get romantic Bengali messages"),
        BotCommand("bdtime", "Check Bangladesh time"),
        BotCommand("admin", "Admin panel"),
        BotCommand("stats", "View statistics"),
        BotCommand("help", "Show help"),
        BotCommand("post", "Create new post (Admin only)")
    ]
    
    try:
        await application.bot.set_my_commands(commands)
        logger.info("Bot commands set successfully")
    except Exception as e:
        logger.error(f"Failed to set bot commands: {e}")

def main():
    """Main entry point"""
    logger.info("🚀 Starting Supreme God Bot v12.0 (Romantic Edition)...")
    logger.info("=" * 60)
    
    # Display system info
    stats = system_monitor.get_system_stats()
    logger.info(f"System Uptime: {stats['uptime']}")
    
    # Display bot info
    db_stats = db.get_stats()
    logger.info(f"Total Users: {db_stats['total_users']:,}")
    logger.info(f"Active Channels: {db_stats['active_channels']:,}")
    
    logger.info("✨ Features:")
    logger.info("1. Romantic Bengali Messages")
    logger.info("2. Bangladesh Timezone")
    logger.info("3. 6-Step Post Wizard")
    logger.info("4. Popup Verification")
    logger.info("5. Intelligent Cleanup")
    
    logger.info("=" * 60)
    
    try:
        # Create and setup application
        application = setup_application()
        
        # Set bot commands
        asyncio.run(set_bot_commands(application))
        
        # Start polling
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
            close_loop=False
        )
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
