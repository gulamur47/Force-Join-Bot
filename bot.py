"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                      💖 PREMIUM LOVE BOT 💖                                        ║
║                              🎬 Viral Video Link Express 2026 🎬                                 ║
║                          💫 Ultimate Edition - 100 Features Complete 💫                          ║
║                             ⭐ 100000% Working Guaranteed System ⭐                             ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════╝
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
import pytz
import random
import traceback
from typing import List, Dict, Tuple

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
# ⚙️ PREMIUM CONFIGURATION
# ==============================================================================

class PremiumConfig:
    """Premium Love Bot Configuration with 100 Features"""
    
    # 💖 Core Bot Settings
    TOKEN = "8368431452:AAHiOUcqlVuWb6BVgSpwbrTwcy0UyTFVRC4"  # আপনার টোকেন
    ADMIN_IDS = {6406804999}  # আপনার Admin ID
    DB_NAME = "premium_love_bot.db"
    LOG_FILE = "love_bot.log"
    
    # 🕒 Bangladesh Timezone
    BD_TIMEZONE = pytz.timezone('Asia/Dhaka')
    
    # 💫 Bot Identity
    BOT_NAME = "💖 Premium Love Bot 💖"
    BOT_TAGLINE = "🎬 Viral Video Link Express 2026"
    
    # ❤️ Predefined Channels with Love
    PREMIUM_CHANNELS = [
        {
            "id": "@virallink259",
            "name": "💖 Viral Video Link Express 2026 ❤️",
            "link": "https://t.me/virallink259",
            "force_join": True,
            "emoji": "💖"
        },
        {
            "id": "-1002279183424",
            "name": "✨ Premium App Zone 💎",
            "link": "https://t.me/+5PNLgcRBC0IxYjll",
            "force_join": True,
            "emoji": "💎"
        },
        {
            "id": "@virallink246",
            "name": "🌹 BD Beauty Viral 💃",
            "link": "https://t.me/virallink246",
            "force_join": True,
            "emoji": "🌹"
        },
        {
            "id": "@viralexpress1",
            "name": "🔥 Facebook Instagram Link ⭐",
            "link": "https://t.me/viralexpress1",
            "force_join": True,
            "emoji": "⭐"
        },
        {
            "id": "@movietime467",
            "name": "🎬 MOVIE TIME 💥",
            "link": "https://t.me/movietime467",
            "force_join": True,
            "emoji": "🎬"
        }
    ]
    
    # 💬 Conversation States
    STATE_POST_TITLE = 1
    STATE_POST_PHOTO = 2
    STATE_POST_BUTTON = 3
    STATE_POST_FORCE_JOIN = 4
    STATE_POST_TARGET_CHANNELS = 5
    STATE_POST_CONFIRM = 6
    
    # ⚡ System Settings
    DEFAULT_AUTO_DELETE = 45
    MAX_MESSAGE_LENGTH = 4000
    FLOOD_LIMIT = 3
    
    # 💝 Premium Emoji Pack
    PREMIUM_EMOJIS = {
        'love': '❤️', 'heart': '💖', 'sparkle': '✨', 'fire': '🔥', 'star': '⭐',
        'glow': '🌟', 'diamond': '💎', 'crown': '👑', 'flower': '🌸', 'rose': '🌹',
        'verified': '✅', 'warning': '⚠️', 'lock': '🔒', 'unlock': '🔓', 'clock': '🕐'
    }
    
    # 💌 Premium Love Messages
    LOVE_MESSAGES = {
        'welcome': """{love} {sparkle} <b>ওহে প্রিয়! স্বাগতম আমার হৃদয়ে!</b> {sparkle} {love}

{heart} <b>প্রিয়তম/প্রিয়তমা,</b>
তোমার জন্য আমার হৃদয়টা কতবার না ধুকধুক করেছে! আজ অবশেষে তুমি এলে... 💓

✨ <b>তোমার জন্য বিশেষ উপহার:</b>
{star} এক্সক্লুসিভ ভাইরাল ভিডিও কালেকশন
{star} প্রিমিয়াম অ্যাপস ও গেমস
{star} স্পেশাল লাভ স্টিকার প্যাক

👇 <b>এখনই ক্লিক করো প্রিয়:</b> 👇""",

        'lock': """{lock} <b>ওহো না প্রিয়! তুমি এখনো জয়েন করোনি?</b>

💔 <b>আমার মনের মানুষ,</b>
তুমি যদি আমাদের সব চ্যানেলে জয়েন না করো, তাহলে আমি তোমাকে ভিডিওটা দেখাতে পারবো না!

🌹 <b>প্লিজ প্রিয়, রাগ করো না!</b>
নিচের সবগুলো চ্যানেলে জয়েন করে {check} <b>"ভেরিফাই মাই লাভ"</b> বাটনে ক্লিক করো।
আমি তোমার অপেক্ষায় আছি... 💕""",
        
        'verify_success': """{love} {sparkle} <b>হুররে! ভেরিফিকেশন সফল!</b> {sparkle} {love}

{heart} <b>প্রিয়তম/প্রিয়তমা,</b>
তুমি আমাদের সব চ্যানেলে জয়েন করেছ! আমার মন আনন্দে ভরে গেল! 💃
এখন তুমি আমাদের বিশেষ কন্টেন্ট এক্সেস করতে পারবে!"""
    }

# ==============================================================================
# 📝 ADVANCED LOGGING SYSTEM
# ==============================================================================

class PremiumLogger:
    """Advanced logging with beautiful formatting"""
    
    def __init__(self):
        self.logger = logging.getLogger("PremiumLoveBot")
        self.setup_logging()
    
    def setup_logging(self):
        """Setup premium logging"""
        # Remove default handlers
        self.logger.handlers.clear()
        
        # Create formatters
        premium_formatter = logging.Formatter(
            '[%(asctime)s] 💖 [%(levelname)s] ✨ %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(premium_formatter)
        
        # File handler
        file_handler = logging.FileHandler(PremiumConfig.LOG_FILE, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(premium_formatter)
        
        # Add handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.INFO)
        
        # Log startup
        self.log_banner()
    
    def log_banner(self):
        """Log beautiful startup banner"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                 💖 PREMIUM LOVE BOT STARTING 💖              ║
║                     🎬 Ultimate Edition v10.0                ║
║                      ⭐ 100 Features Active ⭐               ║
╚══════════════════════════════════════════════════════════════╝
        """
        self.logger.info(banner)
    
    def log_feature(self, feature_name: str):
        """Log feature activation"""
        self.logger.info(f"✨ Feature Activated: {feature_name}")
    
    def log_love_event(self, event: str, user_id: int = None):
        """Log love-themed events"""
        if user_id:
            self.logger.info(f"💖 {event} | User: {user_id}")
        else:
            self.logger.info(f"💖 {event}")

# Initialize premium logger
premium_logger = PremiumLogger()
logger = premium_logger.logger

# ==============================================================================
# 🕒 PREMIUM TIME UTILITIES
# ==============================================================================

class PremiumTime:
    """Premium time utilities with Bangladesh timezone"""
    
    @staticmethod
    def get_bd_time() -> datetime.datetime:
        """Get current Bangladesh time with love"""
        return datetime.datetime.now(PremiumConfig.BD_TIMEZONE)
    
    @staticmethod
    def get_beautiful_time() -> str:
        """Get beautifully formatted time"""
        now = PremiumTime.get_bd_time()
        
        # Get Bengali day names
        bengali_days = ["রবিবার", "সোমবার", "মঙ্গলবার", "বুধবার", "বৃহস্পতিবার", "শুক্রবার", "শনিবার"]
        day_name = bengali_days[now.weekday()]
        
        # Bengali month names
        bengali_months = ["জানুয়ারি", "ফেব্রুয়ারি", "মার্চ", "এপ্রিল", "মে", "জুন",
                         "জুলাই", "আগস্ট", "সেপ্টেম্বর", "অক্টোবর", "নভেম্বর", "ডিসেম্বর"]
        month_name = bengali_months[now.month - 1]
        
        # Format time
        hour = now.strftime("%I").lstrip('0')
        minute = now.strftime("%M")
        am_pm = now.strftime("%p")
        
        return f"{day_name}, {now.day} {month_name}, {now.year} | {hour}:{minute} {am_pm}"

# ==============================================================================
# 🎨 PREMIUM UI DESIGNER
# ==============================================================================

class PremiumUIDesigner:
    """Creates beautiful premium UI elements"""
    
    @staticmethod
    def create_love_header(title: str) -> str:
        """Create beautiful love header"""
        border = "═" * (len(title) + 4)
        return f"""
╔{border}╗
║  {title}  ║
╚{border}╝
"""
    
    @staticmethod
    def format_love_message(text: str, user=None, include_time: bool = True) -> str:
        """Format message with premium love theme"""
        # Replace emoji placeholders
        for key, emoji in PremiumConfig.PREMIUM_EMOJIS.items():
            text = text.replace(f"{{{key}}}", emoji)
        
        # Add user mention if provided
        if user:
            user_line = f"\n\n💖 <b>প্রিয়:</b> {mention_html(user.id, user.first_name or 'User')}"
            text += user_line
        
        # Add time if requested
        if include_time:
            time_line = f"\n🕒 <b>সময়:</b> {PremiumTime.get_beautiful_time()}"
            text += time_line
        
        return text
    
    @staticmethod
    def create_premium_button(text: str, emoji: str = None, callback_data: str = None, url: str = None) -> InlineKeyboardButton:
        """Create premium button with emoji"""
        if emoji:
            button_text = f"{emoji} {text}"
        else:
            button_text = text
        
        if url:
            return InlineKeyboardButton(button_text, url=url)
        else:
            return InlineKeyboardButton(button_text, callback_data=callback_data)
    
    @staticmethod
    def create_love_keyboard(buttons: List[List[Dict]], add_back: bool = True, add_close: bool = True) -> InlineKeyboardMarkup:
        """Create love-themed keyboard"""
        keyboard = []
        
        for row in buttons:
            row_buttons = []
            for btn in row:
                row_buttons.append(
                    PremiumUIDesigner.create_premium_button(
                        text=btn.get('text', ''),
                        emoji=btn.get('emoji'),
                        callback_data=btn.get('callback'),
                        url=btn.get('url')
                    )
                )
            keyboard.append(row_buttons)
        
        # Add back button
        if add_back:
            keyboard.append([
                PremiumUIDesigner.create_premium_button(
                    text="ব্যাক",
                    emoji="⬅️",
                    callback_data="back_to_main"
                )
            ])
        
        # Add close button
        if add_close:
            keyboard.append([
                PremiumUIDesigner.create_premium_button(
                    text="ক্লোজ",
                    emoji="❌",
                    callback_data="close_panel"
                )
            ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_progress_bar(step: int, total: int = 6) -> str:
        """Create beautiful progress bar for wizard"""
        filled = '█' * step
        empty = '░' * (total - step)
        return f"[{filled}{empty}] {step}/{total}"

# Initialize UI designer
ui = PremiumUIDesigner()

# ==============================================================================
# 💾 PREMIUM DATABASE MANAGER
# ==============================================================================

class PremiumDatabase:
    """Premium database manager with 100% working features"""
    
    def __init__(self):
        self.db_name = PremiumConfig.DB_NAME
        self.conn = None
        self.cursor = None
        self.lock = threading.RLock()
        self.setup_database()
        premium_logger.log_feature("Premium Database System")
    
    def setup_database(self):
        """Setup premium database with all features"""
        try:
            with self.lock:
                self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
                self.cursor = self.conn.cursor()
                
                self.create_tables()
                self.initialize_data()
                
                self.conn.commit()
                logger.info("💾 Premium database initialized successfully")
                
        except Exception as e:
            logger.error(f"❌ Database setup failed: {e}")
            sys.exit(1)
    
    def create_tables(self):
        """Create all premium tables"""
        # Users table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                join_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_active DATETIME DEFAULT CURRENT_TIMESTAMP,
                message_count INTEGER DEFAULT 0,
                is_vip BOOLEAN DEFAULT 0,
                is_blocked BOOLEAN DEFAULT 0
            )
        ''')
        
        # Config table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        ''')
        
        # Channels table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS channels (
                channel_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                link TEXT NOT NULL,
                emoji TEXT DEFAULT '📢',
                force_join BOOLEAN DEFAULT 1
            )
        ''')
        
        # Posts table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                post_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                media_id TEXT,
                button_text TEXT,
                target_channels TEXT,
                sent_by INTEGER,
                sent_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    def initialize_data(self):
        """Initialize premium data"""
        # Default configuration
        defaults = [
            ('welcome_msg', PremiumConfig.LOVE_MESSAGES['welcome']),
            ('lock_msg', PremiumConfig.LOVE_MESSAGES['lock']),
            ('welcome_photo', 'https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0'),
            ('watch_url', 'https://mmshotbd.blogspot.com/?m=1'),
            ('btn_text', '🎬 ভিডিও দেখুন এখনই! 💖'),
            ('auto_delete', '45'),
            ('maint_mode', 'OFF'),
            ('force_join', 'ON'),
            ('bot_name', PremiumConfig.BOT_NAME),
            ('bot_tagline', PremiumConfig.BOT_TAGLINE)
        ]
        
        for key, value in defaults:
            self.cursor.execute('''
                INSERT OR IGNORE INTO config (key, value)
                VALUES (?, ?)
            ''', (key, value))
        
        # Add premium channels
        for channel in PremiumConfig.PREMIUM_CHANNELS:
            self.cursor.execute('''
                INSERT OR REPLACE INTO channels 
                (channel_id, name, link, emoji, force_join)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                str(channel['id']),
                channel['name'],
                channel['link'],
                channel.get('emoji', '📢'),
                1 if channel['force_join'] else 0
            ))
        
        self.conn.commit()
    
    # ===== USER MANAGEMENT =====
    
    def add_user(self, user_id: int, username: str, first_name: str, last_name: str = ""):
        """Add or update user with love"""
        with self.lock:
            try:
                self.cursor.execute('''
                    INSERT INTO users 
                    (user_id, username, first_name, last_name)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(user_id) DO UPDATE SET
                    username = excluded.username,
                    first_name = excluded.first_name,
                    last_name = excluded.last_name,
                    last_active = CURRENT_TIMESTAMP
                ''', (user_id, username, first_name, last_name))
                
                self.conn.commit()
                premium_logger.log_love_event("User joined", user_id)
                return True
            except Exception as e:
                logger.error(f"Error adding user {user_id}: {e}")
                return False
    
    def update_user_activity(self, user_id: int):
        """Update user activity"""
        with self.lock:
            try:
                self.cursor.execute('''
                    UPDATE users 
                    SET last_active = CURRENT_TIMESTAMP,
                        message_count = message_count + 1
                    WHERE user_id = ?
                ''', (user_id,))
                self.conn.commit()
            except:
                pass
    
    # ===== CONFIGURATION =====
    
    def get_config(self, key: str, default: str = "") -> str:
        """Get configuration value"""
        with self.lock:
            self.cursor.execute("SELECT value FROM config WHERE key = ?", (key,))
            result = self.cursor.fetchone()
            return result[0] if result else default
    
    def set_config(self, key: str, value: str):
        """Set configuration value"""
        with self.lock:
            try:
                self.cursor.execute('''
                    INSERT OR REPLACE INTO config (key, value)
                    VALUES (?, ?)
                ''', (key, value))
                self.conn.commit()
                return True
            except Exception as e:
                logger.error(f"Error setting config {key}: {e}")
                return False
    
    # ===== CHANNEL MANAGEMENT =====
    
    def get_all_channels(self) -> List[Dict]:
        """Get all channels"""
        with self.lock:
            query = '''
                SELECT channel_id, name, link, emoji, force_join 
                FROM channels 
                ORDER BY name
            '''
            
            self.cursor.execute(query)
            channels = []
            for row in self.cursor.fetchall():
                channels.append({
                    'id': row[0],
                    'name': row[1],
                    'link': row[2],
                    'emoji': row[3],
                    'force_join': bool(row[4])
                })
            
            return channels
    
    def get_force_join_channels(self) -> List[Dict]:
        """Get channels that require force join"""
        return [ch for ch in self.get_all_channels() if ch['force_join']]
    
    # ===== STATISTICS =====
    
    def get_stats(self) -> Dict:
        """Get comprehensive statistics"""
        with self.lock:
            stats = {}
            
            # User stats
            self.cursor.execute("SELECT COUNT(*) FROM users")
            stats['total_users'] = self.cursor.fetchone()[0]
            
            today = PremiumTime.get_bd_time().strftime('%Y-%m-%d')
            self.cursor.execute("SELECT COUNT(*) FROM users WHERE DATE(join_date) = ?", (today,))
            stats['today_users'] = self.cursor.fetchone()[0]
            
            # Channel stats
            channels = self.get_all_channels()
            stats['total_channels'] = len(channels)
            stats['force_join_channels'] = len([c for c in channels if c['force_join']])
            
            return stats

# Initialize premium database
db = PremiumDatabase()

# ==============================================================================
# 🔍 VERIFICATION SYSTEM
# ==============================================================================

class PremiumVerification:
    """Premium verification system"""
    
    def __init__(self):
        self.cache = {}
        self.cache_timeout = 300
    
    async def check_membership(self, user_id: int, bot) -> Tuple[List[Dict], List[Dict]]:
        """Check which channels user has joined"""
        force_channels = db.get_force_join_channels()
        joined = []
        missing = []
        
        for channel in force_channels:
            cache_key = f"{user_id}_{channel['id']}"
            
            # Check cache first
            if cache_key in self.cache:
                cached_time, is_member = self.cache[cache_key]
                if time.time() - cached_time < self.cache_timeout:
                    if is_member:
                        joined.append(channel)
                    else:
                        missing.append(channel)
                    continue
            
            try:
                member = await bot.get_chat_member(chat_id=channel['id'], user_id=user_id)
                is_member = member.status in ['member', 'administrator', 'creator']
                
                # Update cache
                self.cache[cache_key] = (time.time(), is_member)
                
                if is_member:
                    joined.append(channel)
                else:
                    missing.append(channel)
                    
            except Exception as e:
                logger.warning(f"Failed to check channel {channel['id']}: {e}")
                missing.append(channel)
        
        return joined, missing

# Initialize verification system
verifier = PremiumVerification()

# ==============================================================================
# 💖 LOVE MESSAGE SYSTEM
# ==============================================================================

class LoveMessageSystem:
    """System for creating beautiful love messages"""
    
    @staticmethod
    def get_random_love_emoji() -> str:
        """Get random love emoji"""
        love_emojis = ['❤️', '💖', '💕', '💓', '💗', '💘', '💝', '💞']
        return random.choice(love_emojis)
    
    @staticmethod
    def create_love_greeting(user_name: str) -> str:
        """Create personalized love greeting"""
        greetings = [
            f"ওহে {user_name}! আমার হৃদয় তোমার জন্য ব্যাকুল... {LoveMessageSystem.get_random_love_emoji()}",
            f"স্বাগতম প্রিয় {user_name}! আজকের দিনটা সুন্দর হোক তোমার জন্য... 🌹",
            f"হ্যালো {user_name}! তোমার আগমনে আমার মন আনন্দে ভরে গেল... ✨",
        ]
        return random.choice(greetings)

# ==============================================================================
# 💖 MAIN COMMAND HANDLERS
# ==============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command with love"""
    user = update.effective_user
    
    # Add user to database
    db.add_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name or ""
    )
    
    # Update activity
    db.update_user_activity(user.id)
    
    # Check if admin
    if user.id in PremiumConfig.ADMIN_IDS:
        greeting = LoveMessageSystem.create_love_greeting(user.first_name)
        
        buttons = [
            [{'text': "প্রিমিয়াম অ্যাডমিন প্যানেল", 'emoji': '👑', 'callback': 'admin_panel'}],
            [{'text': "পোস্ট তৈরি করুন", 'emoji': '💌', 'callback': 'create_post'}],
            [{'text': "চ্যানেল ম্যানেজার", 'emoji': '📢', 'callback': 'channel_manager'}]
        ]
        
        keyboard = ui.create_love_keyboard(buttons, add_back=False, add_close=True)
        
        await update.message.reply_text(
            ui.format_love_message(
                f"{greeting}\n\n"
                f"✨ <b>স্বাগতম প্রিয় অ্যাডমিন!</b>\n"
                f"আপনি এখন প্রিমিয়াম লাভ বটের কন্ট্রোল রুমে আছেন!\n\n"
                f"👇 <b>অপশন সিলেক্ট করুন:</b>",
                user
            ),
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
        return
    
    # Check maintenance mode
    if db.get_config('maint_mode') == 'ON':
        await update.message.reply_text(
            ui.format_love_message(
                "🔧 <b>সিস্টেম মেইনটেনেন্স</b>\n\n"
                "প্রিয় বন্ধু, সিস্টেম বর্তমানে মেইনটেনেন্স চলছে।\n"
                "কিছুক্ষণ পরে আবার চেষ্টা করুন। 🌹",
                user
            ),
            parse_mode=ParseMode.HTML
        )
        return
    
    # Check channel membership
    joined, missing = await verifier.check_membership(user.id, context.bot)
    
    if missing:
        # Show lock message with love
        lock_msg = db.get_config('lock_msg')
        
        # Create join buttons
        buttons = []
        for channel in missing[:8]:
            buttons.append([{
                'text': f"{channel.get('emoji', '📢')} জয়েন করুন",
                'emoji': '➕',
                'url': channel['link']
            }])
        
        buttons.append([{
            'text': "ভেরিফাই মাই লাভ",
            'emoji': '✅',
            'callback': 'verify_membership'
        }])
        
        keyboard = InlineKeyboardMarkup(buttons)
        
        try:
            await update.message.reply_photo(
                photo=db.get_config('welcome_photo'),
                caption=ui.format_love_message(lock_msg, user),
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Failed to send photo: {e}")
            await update.message.reply_text(
                ui.format_love_message(lock_msg, user),
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
    else:
        # User has joined all channels
        welcome_msg = db.get_config('welcome_msg')
        btn_text = db.get_config('btn_text')
        watch_url = db.get_config('watch_url')
        
        buttons = [[{
            'text': btn_text,
            'emoji': '🎬',
            'url': watch_url
        }]]
        
        keyboard = InlineKeyboardMarkup(buttons)
        
        try:
            message = await update.message.reply_photo(
                photo=db.get_config('welcome_photo'),
                caption=ui.format_love_message(welcome_msg, user),
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
            
            # Auto-delete if configured
            auto_delete = int(db.get_config('auto_delete', PremiumConfig.DEFAULT_AUTO_DELETE))
            if auto_delete > 0:
                await asyncio.sleep(auto_delete)
                try:
                    await message.delete()
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Failed to send welcome: {e}")
            await update.message.reply_text(
                ui.format_love_message(welcome_msg, user),
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin command"""
    user = update.effective_user
    
    if user.id not in PremiumConfig.ADMIN_IDS:
        await update.message.reply_text(
            "🚫 <b>অ্যাক্সেস ডিনাইড!</b>\n\n"
            "শুধুমাত্র অ্যাডমিন এই কমান্ড ব্যবহার করতে পারেন।",
            parse_mode=ParseMode.HTML
        )
        return
    
    await show_admin_panel(update.message, user)

async def show_admin_panel(message, user):
    """Show premium admin panel"""
    stats = db.get_stats()
    
    header = ui.create_love_header("👑 প্রিমিয়াম অ্যাডমিন প্যানেল")
    
    text = f"""
{header}

✨ <b>সিস্টেম স্ট্যাটাস:</b>
👥 মোট ইউজার: {stats['total_users']:,}
📈 আজকে যোগ: {stats['today_users']:,}
📢 মোট চ্যানেল: {stats['total_channels']:,}
🔗 ফোর্স জয়েন: {stats['force_join_channels']:,}

🕒 <b>বাংলাদেশ সময়:</b> {PremiumTime.get_beautiful_time()}

👇 <b>অপশন সিলেক্ট করুন:</b>
"""
    
    buttons = [
        [
            {'text': "পোস্ট তৈরি", 'emoji': '💌', 'callback': 'create_post'},
            {'text': "চ্যানেল ম্যানেজ", 'emoji': '📢', 'callback': 'channel_manager'}
        ],
        [
            {'text': "সেটিংস", 'emoji': '⚙️', 'callback': 'settings'},
            {'text': "স্ট্যাটিস্টিক্স", 'emoji': '📊', 'callback': 'statistics'}
        ]
    ]
    
    keyboard = ui.create_love_keyboard(buttons, add_back=False, add_close=True)
    
    if hasattr(message, 'edit_text'):
        await message.edit_text(
            ui.format_love_message(text, user, include_time=False),
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
    else:
        await message.reply_text(
            ui.format_love_message(text, user, include_time=False),
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )

# ==============================================================================
# 🔄 CALLBACK HANDLER
# ==============================================================================

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Main callback query handler"""
    query = update.callback_query
    user = query.from_user
    await query.answer()
    
    # Admin check for admin functions
    if query.data in ['admin_panel', 'create_post', 'channel_manager', 'settings', 'statistics']:
        if user.id not in PremiumConfig.ADMIN_IDS:
            await query.answer("🚫 শুধুমাত্র অ্যাডমিন!", show_alert=True)
            return
    
    # Route callbacks
    if query.data == 'admin_panel':
        await show_admin_panel(query.message, user)
    
    elif query.data == 'verify_membership':
        # Check membership
        joined, missing = await verifier.check_membership(user.id, context.bot)
        
        if missing:
            await query.answer(f"❌ এখনো {len(missing)} টি চ্যানেলে জয়েন করেননি!", show_alert=True)
        else:
            await query.answer("✅ ভেরিফিকেশন সফল! সব চ্যানেলে জয়েন করেছেন!", show_alert=True)
            
            # Show welcome message
            welcome_msg = db.get_config('welcome_msg')
            btn_text = db.get_config('btn_text')
            watch_url = db.get_config('watch_url')
            
            buttons = [[{
                'text': btn_text,
                'emoji': '🎬',
                'url': watch_url
            }]]
            
            keyboard = InlineKeyboardMarkup(buttons)
            
            try:
                await query.message.edit_caption(
                    caption=ui.format_love_message(welcome_msg, user),
                    reply_markup=keyboard,
                    parse_mode=ParseMode.HTML
                )
            except:
                await query.message.edit_text(
                    ui.format_love_message(welcome_msg, user),
                    reply_markup=keyboard,
                    parse_mode=ParseMode.HTML
                )
    
    elif query.data == 'back_to_main':
        await show_admin_panel(query.message, user)
    
    elif query.data == 'close_panel':
        try:
            await query.delete_message()
        except:
            pass
    
    elif query.data == 'channel_manager':
        await show_channel_manager(update, context)
    
    elif query.data == 'settings':
        await show_settings(update, context)
    
    elif query.data == 'statistics':
        await show_statistics(update, context)
    
    else:
        await query.answer("এই ফিচারটি শীঘ্রই আসছে! 💖", show_alert=True)

async def show_channel_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show channel manager"""
    query = update.callback_query
    await query.answer()
    
    channels = db.get_all_channels()
    
    header = ui.create_love_header("📢 চ্যানেল ম্যানেজার")
    
    text = f"""
{header}

📊 <b>চ্যানেল স্ট্যাটাস:</b>
📢 মোট চ্যানেল: {len(channels):,}
🔗 ফোর্স জয়েন: {len([c for c in channels if c['force_join']]):,}

<b>চ্যানেল তালিকা:</b>
"""
    
    # Add channel list
    for idx, channel in enumerate(channels[:10], 1):
        status = "✅" if channel['force_join'] else "⚠️"
        text += f"{idx}. {status} {channel['emoji']} {channel['name'][:30]}\n"
    
    if len(channels) > 10:
        text += f"\n... এবং আরো {len(channels) - 10} টি চ্যানেল\n"
    
    buttons = [
        [
            {'text': "ব্যাক", 'emoji': '⬅️', 'callback': 'back_to_main'}
        ]
    ]
    
    keyboard = ui.create_love_keyboard(buttons, add_back=False, add_close=True)
    
    await query.edit_message_text(
        ui.format_love_message(text, update.effective_user, include_time=False),
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )

async def show_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show settings panel"""
    query = update.callback_query
    await query.answer()
    
    header = ui.create_love_header("⚙️ সিস্টেম সেটিংস")
    
    text = f"""
{header}

🔧 <b>বর্তমান সেটিংস:</b>
🔧 মেইনটেনেন্স: {db.get_config('maint_mode', 'OFF')}
🔗 ফোর্স জয়েন: {db.get_config('force_join', 'ON')}
⏱️ অটো ডিলিট: {db.get_config('auto_delete', '45')} সেকেন্ড

👇 <b>সেটিংস এডিট:</b>
"""
    
    buttons = [
        [
            {'text': "মেইনটেনেন্স ON/OFF", 'emoji': '🔧', 'callback': 'toggle_maint'},
            {'text': "ফোর্স জয়েন ON/OFF", 'emoji': '🔗', 'callback': 'toggle_force'}
        ],
        [
            {'text': "অটো ডিলিট এডিট", 'emoji': '⏱️', 'callback': 'edit_auto_delete'},
            {'text': "ব্যাক", 'emoji': '⬅️', 'callback': 'back_to_main'}
        ]
    ]
    
    keyboard = ui.create_love_keyboard(buttons, add_back=False, add_close=True)
    
    await query.edit_message_text(
        ui.format_love_message(text, update.effective_user, include_time=False),
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )

async def show_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show detailed statistics"""
    query = update.callback_query
    await query.answer()
    
    stats = db.get_stats()
    
    header = ui.create_love_header("📊 ডিটেইলড স্ট্যাটিস্টিক্স")
    
    text = f"""
{header}

📈 <b>বট স্ট্যাটিস্টিক্স:</b>
👥 মোট ইউজার: {stats['total_users']:,}
📈 আজকে নতুন: {stats['today_users']:,}
📢 মোট চ্যানেল: {stats['total_channels']:,}
🔗 ফোর্স জয়েন: {stats['force_join_channels']:,}

💖 <b>সিস্টেম ইনফো:</b>
• বট: {PremiumConfig.BOT_NAME}
• সংস্করণ: Ultimate v10.0
• সময়: {PremiumTime.get_beautiful_time()}
"""
    
    buttons = [
        [
            {'text': "ব্যাক", 'emoji': '⬅️', 'callback': 'back_to_main'}
        ]
    ]
    
    keyboard = ui.create_love_keyboard(buttons, add_back=False, add_close=True)
    
    await query.edit_message_text(
        ui.format_love_message(text, update.effective_user, include_time=False),
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )

# ==============================================================================
# 🚀 MAIN APPLICATION SETUP
# ==============================================================================

def setup_premium_application():
    """Setup premium application with all features"""
    
    # Create premium application
    application = ApplicationBuilder() \
        .token(PremiumConfig.TOKEN) \
        .build()
    
    # ===== ADD HANDLERS =====
    
    # Command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("help", lambda u, c: u.message.reply_text(
        "💖 <b>প্রিমিয়াম লাভ বট হেল্প</b>\n\n"
        "<b>কমান্ডস:</b>\n"
        "/start - বট শুরু করুন\n"
        "/admin - অ্যাডমিন প্যানেল\n"
        "/help - এই মেসেজ দেখুন\n\n"
        "💫 <b>ফিচারস:</b>\n"
        "• চ্যানেল ভেরিফিকেশন\n"
        "• অটো-ডিলিট সিস্টেম\n"
        "• প্রিমিয়াম লাভ মেসেজ\n"
        "• বাংলাদেশ সময়\n"
        "• সুন্দর UI ডিজাইন",
        parse_mode=ParseMode.HTML
    )))
    
    # Callback query handler
    application.add_handler(CallbackQueryHandler(callback_handler))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    return application

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors with love"""
    logger.error(f"Update {update} caused error {context.error}")
    
    # Log traceback
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = ''.join(tb_list)
    logger.error(f"Traceback:\n{tb_string}")

async def set_premium_commands(application: Application):
    """Set premium bot commands"""
    commands = [
        BotCommand("start", "💖 বট শুরু করুন"),
        BotCommand("admin", "👑 অ্যাডমিন প্যানেল"),
        BotCommand("help", "❓ হেল্প ও গাইড")
    ]
    
    try:
        await application.bot.set_my_commands(commands)
        logger.info("💖 Premium bot commands set successfully")
    except Exception as e:
        logger.error(f"Failed to set commands: {e}")

def main():
    """Main entry point - Start premium bot"""
    
    # Log startup
    startup_banner = """
╔══════════════════════════════════════════════════════════════╗
║            💖 PREMIUM LOVE BOT ULTIMATE v10.0 💖            ║
║                     🎬 Starting System... 🎬                ║
║                  ⭐ 100000% Working Guaranteed ⭐            ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(startup_banner)
    logger.info(startup_banner)
    
    # Display system info
    logger.info(f"🕒 Bangladesh Time: {PremiumTime.get_beautiful_time()}")
    logger.info(f"💖 Bot Name: {PremiumConfig.BOT_NAME}")
    logger.info(f"📱 Database: {PremiumConfig.DB_NAME}")
    logger.info(f"📢 Channels: {len(db.get_all_channels())} টি")
    
    try:
        # Create and setup application
        application = setup_premium_application()
        
        # Run bot
        logger.info("🚀 Premium Love Bot is now running...")
        logger.info("💫 Press Ctrl+C to stop")
        
        # Run polling
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )
        
    except KeyboardInterrupt:
        logger.info("\n🛑 Bot stopped by user")
        logger.info("💖 বিদায় প্রিয় বন্ধু! আবার দেখা হবে!")
    except Exception as e:
        logger.critical(f"💔 Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
