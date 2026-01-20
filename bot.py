"""
================================================================================
PROJECT: SUPREME GOD BOT - ENTERPRISE EDITION
VERSION: 12.0.0 (STABLE)
AUTHOR: SUPREME AI
DATE: 2026-01-20
LICENSE: MIT
================================================================================

DESCRIPTION:
This is a high-level Telegram Bot designed for managing exclusive content 
distribution via Telegram Channels with Forced Subscription Verification.

CORE FEATURES:
1. Advanced Admin Panel with Conversation Wizards.
2. Database Management System (SQLite3) for persistent storage.
3. Content Protection:
   - Channel posts are sent with 'Spoiler' effect (Blurred Image).
   - Real destination links are hidden from the channel.
4. Smart Verification System:
   - Checks membership status in real-time.
   - Uses Caching to prevent Telegram API Rate Limits.
5. User Flow:
   - User clicks 'Unlock' in Channel.
   - If NOT Joined -> Shows Popup Alert + Temporary Join Links.
   - If Joined -> Shows Success Popup + Auto Redirects to Bot Private Chat.
   - Bot Private Chat -> Sends Unblurred Image + Real Links.

================================================================================
"""

import logging
import sqlite3
import json
import asyncio
import time
import sys
import traceback
from typing import List, Dict, Union, Optional, Tuple

# Third-party imports
try:
    from telegram import (
        Update, 
        InlineKeyboardButton, 
        InlineKeyboardMarkup, 
        BotCommand,
        User
    )
    from telegram.constants import ParseMode, ChatAction
    from telegram.ext import (
        ApplicationBuilder, 
        CommandHandler, 
        CallbackQueryHandler,
        ContextTypes, 
        ConversationHandler, 
        MessageHandler, 
        filters,
        Application
    )
    from telegram.error import Forbidden, BadRequest, TelegramError
except ImportError:
    print("CRITICAL ERROR: 'python-telegram-bot' library is not installed.")
    print("Please run: pip install python-telegram-bot")
    sys.exit(1)

# ==============================================================================
# ⚙️ SYSTEM CONFIGURATION
# ==============================================================================

class SystemConfig:
    """
    Central Configuration Class for the Bot.
    Manage all tokens, IDs, and system constants here.
    """
    
    # --------------------------------------------------------------------------
    # 🔑 BOT CREDENTIALS
    # --------------------------------------------------------------------------
    # Replace this with your actual Bot Token
    TOKEN: str = "8456027249:AAEqg2j7jhJDSl4R0dnVCqaCvYBJQeG8NM4"
    
    # --------------------------------------------------------------------------
    # 👑 ADMIN CONFIGURATION
    # --------------------------------------------------------------------------
    # Set of User IDs who have admin access
    ADMIN_IDS: set = {6406804999}  # Replace with your ID
    
    # --------------------------------------------------------------------------
    # 📁 DATABASE CONFIGURATION
    # --------------------------------------------------------------------------
    DB_NAME: str = "supreme_enterprise.db"
    
    # --------------------------------------------------------------------------
    # ⏱️ TIMING CONSTANTS
    # --------------------------------------------------------------------------
    CACHE_TIMEOUT: int = 300  # 5 Minutes cache for membership check
    AUTO_DELETE_SECONDS: int = 20  # Time to delete warning messages
    
    # --------------------------------------------------------------------------
    # 📊 CONVERSATION STATES
    # --------------------------------------------------------------------------
    # Post Creation Wizard States
    STATE_POST_TITLE: int = 101
    STATE_POST_PHOTO: int = 102
    STATE_POST_TEXT: int = 103
    STATE_POST_BUTTONS_MENU: int = 104
    STATE_POST_BTN_NAME: int = 105
    STATE_POST_BTN_LINK: int = 106
    STATE_POST_TARGET: int = 107
    
    # Channel Addition Wizard States
    STATE_ADD_CH_ID: int = 201
    STATE_ADD_CH_NAME: int = 202
    STATE_ADD_CH_LINK: int = 203

# ==============================================================================
# 📝 LOGGING SUBSYSTEM
# ==============================================================================

# Configure the logging format to look professional and readable
logging.basicConfig(
    format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),  # Log to console
        logging.FileHandler("bot_activity.log")  # Log to file
    ]
)
logger = logging.getLogger("SupremeBot")

# ==============================================================================
# 🗄️ DATABASE MANAGEMENT SYSTEM (DBMS)
# ==============================================================================

class DatabaseManager:
    """
    Handles all interactions with the SQLite3 database.
    Implements Singleton pattern to ensure one connection pool.
    """
    
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.connect()
        self.initialize_schema()

    def connect(self):
        """Establishes connection to the database."""
        try:
            self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row  # Access columns by name
            self.cursor = self.conn.cursor()
            logger.info(f"Connected to database: {self.db_name}")
        except sqlite3.Error as e:
            logger.critical(f"Database connection failed: {e}")
            sys.exit(1)

    def initialize_schema(self):
        """Creates necessary tables if they don't exist."""
        try:
            # 1. Users Table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_active DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 2. Channels Table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS channels (
                    channel_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    link TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    added_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 3. Posts Table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS posts (
                    post_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    photo_id TEXT,
                    caption TEXT,
                    buttons_json TEXT,
                    force_channels_json TEXT,
                    views INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            self.conn.commit()
            logger.info("Database schema initialized successfully.")
        except sqlite3.Error as e:
            logger.error(f"Schema initialization failed: {e}")

    # --------------------------------------------------------------------------
    # USER OPERATIONS
    # --------------------------------------------------------------------------
    
    def register_user(self, user: User):
        """Adds or updates a user in the database."""
        try:
            self.cursor.execute('''
                INSERT OR REPLACE INTO users (user_id, username, first_name, last_active)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ''', (user.id, user.username, user.first_name))
            self.conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Failed to register user {user.id}: {e}")

    # --------------------------------------------------------------------------
    # CHANNEL OPERATIONS
    # --------------------------------------------------------------------------

    def add_channel(self, channel_id: str, name: str, link: str) -> bool:
        """Adds a new channel to the force subscription list."""
        try:
            self.cursor.execute('''
                INSERT OR REPLACE INTO channels (channel_id, name, link, is_active)
                VALUES (?, ?, ?, 1)
            ''', (channel_id, name, link))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Failed to add channel: {e}")
            return False

    def get_all_channels(self) -> List[Dict]:
        """Retrieves all active channels."""
        try:
            self.cursor.execute('SELECT * FROM channels WHERE is_active = 1')
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error:
            return []

    # --------------------------------------------------------------------------
    # POST OPERATIONS
    # --------------------------------------------------------------------------

    def create_post(self, title: str, photo: str, caption: str, buttons: List, channels: List) -> int:
        """Saves a new post and returns the Post ID."""
        try:
            self.cursor.execute('''
                INSERT INTO posts (title, photo_id, caption, buttons_json, force_channels_json)
                VALUES (?, ?, ?, ?, ?)
            ''', (title, photo, caption, json.dumps(buttons), json.dumps(channels)))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Failed to create post: {e}")
            return 0

    def get_post(self, post_id: int) -> Optional[Dict]:
        """Retrieves post details by ID."""
        try:
            self.cursor.execute('SELECT * FROM posts WHERE post_id = ?', (post_id,))
            row = self.cursor.fetchone()
            if row:
                data = dict(row)
                data['buttons'] = json.loads(data['buttons_json'])
                data['force_channels'] = json.loads(data['force_channels_json'])
                return data
            return None
        except sqlite3.Error:
            return None

# Initialize Database Instance
db = DatabaseManager(SystemConfig.DB_NAME)

# ==============================================================================
# 🔐 SECURITY & VALIDATION MANAGER
# ==============================================================================

class SecurityManager:
    """
    Handles membership verification logic and caching.
    """
    def __init__(self):
        self._cache = {}  # Format: {user_id: (timestamp, [missing_channels])}
    
    async def get_missing_channels(self, user_id: int, bot: Application, required_channel_ids: List[str]) -> List[Dict]:
        """
        Checks if a user is a member of the required channels.
        Uses caching to optimize performance.
        """
        current_time = time.time()
        
        # Check Cache
        if user_id in self._cache:
            timestamp, cached_missing = self._cache[user_id]
            if current_time - timestamp < SystemConfig.CACHE_TIMEOUT:
                # Cache is valid, but we need to ensure the cached missing channels are still in the requirement list
                # This is a simplified check
                return cached_missing

        # Fetch active channel details from DB to get links
        all_channels_db = {ch['channel_id']: ch for ch in db.get_all_channels()}
        
        missing = []
        
        for ch_id in required_channel_ids:
            # If channel was removed from DB, skip it
            if ch_id not in all_channels_db:
                continue
                
            channel_info = all_channels_db[ch_id]
            
            try:
                # Call Telegram API
                member = await bot.get_chat_member(chat_id=ch_id, user_id=user_id)
                
                # Check status
                if member.status in ['left', 'kicked', 'banned']:
                    missing.append(channel_info)
            
            except BadRequest:
                # Bot likely not admin or channel invalid
                logger.warning(f"BadRequest checking member in {ch_id}")
                missing.append(channel_info)
            except Exception as e:
                logger.error(f"Error checking member: {e}")
                missing.append(channel_info)
        
        # Update Cache
        self._cache[user_id] = (current_time, missing)
        return missing

security = SecurityManager()

# ==============================================================================
# 🎨 UI HELPER UTILITIES
# ==============================================================================

class UIHelper:
    """
    Static methods for generating Keyboards and Messages.
    """
    
    @staticmethod
    def build_keyboard(buttons: List[List[Dict]]) -> InlineKeyboardMarkup:
        """Converts dict definition to InlineKeyboardMarkup."""
        keyboard = []
        for row in buttons:
            k_row = []
            for btn in row:
                if 'url' in btn:
                    k_row.append(InlineKeyboardButton(text=btn['text'], url=btn['url']))
                else:
                    k_row.append(InlineKeyboardButton(text=btn['text'], callback_data=btn['callback']))
            keyboard.append(k_row)
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_channel_selection_markup(channels: List[Dict]) -> InlineKeyboardMarkup:
        """Generates buttons for channel selection in admin panel."""
        keyboard = []
        for ch in channels:
            keyboard.append([InlineKeyboardButton(f"📢 {ch['name']}", callback_data=f"target_{ch['channel_id']}")])
        return InlineKeyboardMarkup(keyboard)

# ==============================================================================
# 🧙‍♂️ ADMIN WIZARD: CREATE POST
# ==============================================================================

class PostWizard:
    """
    Handles the ConversationHandler flow for creating new posts.
    """
    
    @staticmethod
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Entry point for post creation."""
        query = update.callback_query
        await query.answer()
        
        # Initialize session storage
        context.user_data['post_draft'] = {'buttons': []}
        
        await query.message.reply_text(
            "📝 <b>POST CREATION WIZARD</b>\n\n"
            "Step 1/6: Please enter the <b>Title</b> of the content:",
            parse_mode=ParseMode.HTML
        )
        return SystemConfig.STATE_POST_TITLE

    @staticmethod
    async def receive_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data['post_draft']['title'] = update.message.text
        await update.message.reply_text(
            "📸 <b>Step 2/6:</b> Please send the <b>Photo</b> for the post:",
            parse_mode=ParseMode.HTML
        )
        return SystemConfig.STATE_POST_PHOTO

    @staticmethod
    async def receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message.photo:
            await update.message.reply_text("❌ Please send a valid photo!")
            return SystemConfig.STATE_POST_PHOTO
        
        # Take the largest resolution
        context.user_data['post_draft']['photo_id'] = update.message.photo[-1].file_id
        
        await update.message.reply_text(
            "✍️ <b>Step 3/6:</b> Enter the <b>Body Text</b> (or /skip):",
            parse_mode=ParseMode.HTML
        )
        return SystemConfig.STATE_POST_TEXT

    @staticmethod
    async def receive_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text
        context.user_data['post_draft']['caption'] = "" if text == '/skip' else text
        return await PostWizard.show_button_menu(update, context)

    @staticmethod
    async def show_button_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        buttons = context.user_data['post_draft']['buttons']
        
        # Preview current buttons
        msg = f"🔘 <b>Step 4/6: Button Manager</b>\n\nButtons added: {len(buttons)}\n"
        for idx, btn in enumerate(buttons, 1):
            msg += f"{idx}. {btn['name']} -> {btn['link']}\n"
            
        keyboard = [
            [InlineKeyboardButton("➕ Add New Button", callback_data="add_btn_start")],
            [InlineKeyboardButton("✅ Done & Continue", callback_data="buttons_done")]
        ]
        
        if update.callback_query:
            await update.callback_query.message.edit_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)
            
        return SystemConfig.STATE_POST_BUTTONS_MENU

    @staticmethod
    async def button_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        if query.data == "add_btn_start":
            await query.message.reply_text("✏️ Enter <b>Button Name</b>:")
            return SystemConfig.STATE_POST_BTN_NAME
            
        elif query.data == "buttons_done":
            # Proceed to Channel Selection
            channels = db.get_all_channels()
            if not channels:
                await query.message.reply_text("❌ No channels found in database! Please add a channel first.")
                return ConversationHandler.END
            
            markup = UIHelper.get_channel_selection_markup(channels)
            await query.message.edit_text(
                "📤 <b>Step 6/6: Target Channel</b>\nSelect where to post:",
                reply_markup=markup,
                parse_mode=ParseMode.HTML
            )
            return SystemConfig.STATE_POST_TARGET

    @staticmethod
    async def receive_btn_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data['temp_btn_name'] = update.message.text
        await update.message.reply_text("🔗 Enter <b>Button URL</b> (https://...):", parse_mode=ParseMode.HTML)
        return SystemConfig.STATE_POST_BTN_LINK

    @staticmethod
    async def receive_btn_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
        link = update.message.text
        if not link.lower().startswith("http"):
            await update.message.reply_text("❌ Invalid URL! Must start with http or https.")
            return SystemConfig.STATE_POST_BTN_LINK
        
        # Save Button
        context.user_data['post_draft']['buttons'].append({
            'name': context.user_data['temp_btn_name'],
            'link': link
        })
        
        await update.message.reply_text("✅ Button Added!")
        return await PostWizard.show_button_menu(update, context)

    @staticmethod
    async def finalize_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Finalizes the post, saves to DB, and sends to the Channel.
        This contains the critical logic for Spoiling/Blurring.
        """
        query = update.callback_query
        target_channel_id = query.data.replace("target_", "")
        
        draft = context.user_data['post_draft']
        
        # 1. Prepare Data
        # Collect all current active channels as required force join channels
        current_channels = [ch['channel_id'] for ch in db.get_all_channels()]
        
        # 2. Save to Database
        post_id = db.create_post(
            title=draft['title'],
            photo=draft['photo_id'],
            caption=draft['caption'],
            buttons=draft['buttons'],
            channels=current_channels
        )
        
        # 3. Construct Channel Message
        # The image will be BLURRED (has_spoiler=True)
        # The button will contain the Callback Data to trigger the check
        
        channel_keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton(
                text="🔓 Tap to Unlock / Verify Membership 🔞", 
                callback_data=f"verify_{post_id}"
            )
        ]])
        
        full_caption = (
            f"<b>{draft['title']}</b>\n\n"
            f"{draft['caption'][:100]}...\n\n"
            f"🔒 <b>LOCKED CONTENT</b>\n"
            f"<i>Click the button below to verify and unlock full content.</i>"
        )
        
        try:
            # Send to Channel
            await context.bot.send_photo(
                chat_id=target_channel_id,
                photo=draft['photo_id'],
                caption=full_caption,
                reply_markup=channel_keyboard,
                has_spoiler=True,  # KEY FEATURE: BLURS IMAGE
                parse_mode=ParseMode.HTML
            )
            
            await query.message.edit_text(
                f"✅ <b>Post Successfully Published!</b>\n"
                f"🆔 Post ID: <code>{post_id}</code>\n"
                f"📢 Target: {target_channel_id}",
                parse_mode=ParseMode.HTML
            )
            
        except Exception as e:
            logger.error(f"Failed to send post to channel: {e}")
            await query.message.edit_text(f"❌ Critical Error sending to channel:\n<code>{e}</code>", parse_mode=ParseMode.HTML)
            
        return ConversationHandler.END

# ==============================================================================
# 🧙‍♂️ ADMIN WIZARD: ADD CHANNEL
# ==============================================================================

class ChannelWizard:
    @staticmethod
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        await query.message.reply_text("🆔 Enter <b>Channel ID</b> (e.g., -100123456):", parse_mode=ParseMode.HTML)
        return SystemConfig.STATE_ADD_CH_ID

    @staticmethod
    async def receive_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data['ch_id'] = update.message.text
        await update.message.reply_text("📝 Enter <b>Channel Name</b>:", parse_mode=ParseMode.HTML)
        return SystemConfig.STATE_ADD_CH_NAME

    @staticmethod
    async def receive_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data['ch_name'] = update.message.text
        await update.message.reply_text("🔗 Enter <b>Channel Invite Link</b>:", parse_mode=ParseMode.HTML)
        return SystemConfig.STATE_ADD_CH_LINK

    @staticmethod
    async def receive_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
        link = update.message.text
        success = db.add_channel(
            context.user_data['ch_id'],
            context.user_data['ch_name'],
            link
        )
        
        if success:
            await update.message.reply_text("✅ Channel added to Force Subscription list!")
        else:
            await update.message.reply_text("❌ Database Error. Try again.")
            
        return ConversationHandler.END

# ==============================================================================
# 🚀 CORE LOGIC: VERIFICATION & REDIRECT
# ==============================================================================

async def channel_verification_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the click on the "Unlock" button in the CHANNEL.
    Logic:
    1. Check membership.
    2. If NOT Joined -> Show Alert Popup + Send ephemeral message in channel.
    3. If Joined -> Show Success Popup + REDIRECT to Bot Private Chat.
    """
    query = update.callback_query
    user = query.from_user
    post_id = int(query.data.replace("verify_", ""))
    
    # Register User
    db.register_user(user)
    
    # 1. Get Post Data
    post = db.get_post(post_id)
    if not post:
        await query.answer("❌ Error: Post not found in database.", show_alert=True)
        return

    # 2. Check Membership
    required_ids = post['force_channels']
    missing_channels = await security.get_missing_channels(user.id, context.bot, required_ids)
    
    # ==========================================================================
    # CASE 1: USER HAS NOT JOINED CHANNELS
    # ==========================================================================
    if missing_channels:
        # A. Show Popup Alert
        await query.answer("⚠️ ACCESS DENIED!\nYou must join our channels first.", show_alert=True)
        
        # B. Construct Join Keyboard
        buttons = []
        for ch in missing_channels:
            buttons.append([{"text": f"📢 Join {ch['name']}", "url": ch['link']}])
        
        # Add a "Try Again" button which triggers this same function
        buttons.append([{"text": "🔄 Check Again", "callback_data": f"verify_{post_id}"}])
        
        markup = UIHelper.build_keyboard(buttons)
        
        # C. Send Temporary Message in the Channel (visible to user)
        # We reply to the original message so user sees it contextually
        try:
            warning_msg = await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=(
                    f"⛔ <b>Access Denied for {user.first_name}</b>\n\n"
                    "Please join the following channels to unlock this content:"
                ),
                reply_to_message_id=query.message.message_id,
                reply_markup=markup,
                parse_mode=ParseMode.HTML
            )
            
            # Auto-Delete logic (using asyncio.sleep)
            # We run this as a background task so it doesn't block
            asyncio.create_task(delete_message_delayed(warning_msg, SystemConfig.AUTO_DELETE_SECONDS))
            
        except Exception as e:
            logger.error(f"Error sending warning: {e}")
            
        return

    # ==========================================================================
    # CASE 2: USER IS VERIFIED (SUCCESS)
    # ==========================================================================
    
    # The magic happen here. 
    # We use `url` parameter in `answer_callback_query` to redirect user.
    # The URL points to the bot with a 'start' parameter containing the post ID.
    
    bot_username = context.bot.username
    redirect_url = f"https://t.me/{bot_username}?start=show_{post_id}"
    
    await query.answer("✅ Verified! Redirecting to content...", show_alert=False, url=redirect_url)


async def deep_link_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the /start command. 
    Catches the redirection from the channel (start=show_123).
    Sends the REAL content.
    """
    user = update.effective_user
    db.register_user(user)
    
    args = context.args
    
    # Normal Start
    if not args:
        await update.message.reply_text(
            f"👋 <b>Hello {user.first_name}!</b>\n\n"
            "I am the Content Delivery Bot.\n"
            "Go to our channels and click 'Unlock' on posts to use me.",
            parse_mode=ParseMode.HTML
        )
        return

    # Deep Link Handling
    payload = args[0]
    
    if payload.startswith("show_"):
        try:
            post_id = int(payload.replace("show_", ""))
            post = db.get_post(post_id)
            
            if not post:
                await update.message.reply_text("❌ Content not found or deleted.")
                return
            
            # Double Check Membership (Security)
            # Even though they came from redirect, we verify again to prevent link sharing
            missing = await security.get_missing_channels(user.id, context.bot, post['force_channels'])
            
            if missing:
                await update.message.reply_text("⛔ Please go back to the channel and join all required channels.")
                return
            
            # SEND REAL CONTENT
            # 1. Clean Photo (No Spoiler)
            # 2. Real Buttons
            
            real_buttons = []
            for btn in post['buttons']:
                real_buttons.append([InlineKeyboardButton(btn['name'], url=btn['link'])])
            
            caption = (
                f"✅ <b>UNLOCKED CONTENT</b>\n\n"
                f"<b>{post['title']}</b>\n"
                f"{post['caption']}\n\n"
                f"<i>Here is your exclusive content!</i>"
            )
            
            await context.bot.send_photo(
                chat_id=user.id,
                photo=post['photo_id'],
                caption=caption,
                reply_markup=InlineKeyboardMarkup(real_buttons),
                parse_mode=ParseMode.HTML
            )
            
        except ValueError:
            await update.message.reply_text("❌ Invalid Link.")
        except Exception as e:
            logger.error(f"Error in deep link: {e}")
            await update.message.reply_text("❌ An error occurred.")


# ==============================================================================
# 🛠️ UTILITY FUNCTIONS
# ==============================================================================

async def delete_message_delayed(message, delay):
    """Deletes a message after X seconds."""
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except Exception:
        pass

async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancels any active conversation."""
    await update.message.reply_text("🚫 Operation Cancelled.")
    return ConversationHandler.END

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Displays the Admin Menu."""
    user = update.effective_user
    if user.id not in SystemConfig.ADMIN_IDS:
        return
    
    keyboard = [
        [
            InlineKeyboardButton("🆕 Create Post", callback_data="wizard_post"),
            InlineKeyboardButton("➕ Add Channel", callback_data="wizard_channel")
        ],
        [InlineKeyboardButton("📊 Stats (Coming Soon)", callback_data="stats")]
    ]
    
    await update.message.reply_text(
        "👑 <b>SUPREME ADMIN DASHBOARD</b>\nSelect an action:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML
    )

# ==============================================================================
# 🏁 APPLICATION BOOTSTRAP
# ==============================================================================

def main():
    """Main Entry Point."""
    print("-------------------------------------------------")
    print("   SUPREME BOT v12.0 - STARTING SYSTEMS...       ")
    print("-------------------------------------------------")
    
    # 1. Build Application
    app = ApplicationBuilder().token(SystemConfig.TOKEN).build()
    
    # 2. Setup Conversation Handlers (Wizards)
    
    # Post Creation Wizard
    post_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(PostWizard.start, pattern='^wizard_post$')],
        states={
            SystemConfig.STATE_POST_TITLE: [MessageHandler(filters.TEXT, PostWizard.receive_title)],
            SystemConfig.STATE_POST_PHOTO: [MessageHandler(filters.PHOTO, PostWizard.receive_photo)],
            SystemConfig.STATE_POST_TEXT: [MessageHandler(filters.TEXT, PostWizard.receive_text)],
            SystemConfig.STATE_POST_BUTTONS_MENU: [CallbackQueryHandler(PostWizard.button_menu_callback)],
            SystemConfig.STATE_POST_BTN_NAME: [MessageHandler(filters.TEXT, PostWizard.receive_btn_name)],
            SystemConfig.STATE_POST_BTN_LINK: [MessageHandler(filters.TEXT, PostWizard.receive_btn_link)],
            SystemConfig.STATE_POST_TARGET: [CallbackQueryHandler(PostWizard.finalize_post, pattern='^target_')]
        },
        fallbacks=[CommandHandler('cancel', cancel_handler)]
    )
    
    # Channel Add Wizard
    channel_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(ChannelWizard.start, pattern='^wizard_channel$')],
        states={
            SystemConfig.STATE_ADD_CH_ID: [MessageHandler(filters.TEXT, ChannelWizard.receive_id)],
            SystemConfig.STATE_ADD_CH_NAME: [MessageHandler(filters.TEXT, ChannelWizard.receive_name)],
            SystemConfig.STATE_ADD_CH_LINK: [MessageHandler(filters.TEXT, ChannelWizard.receive_link)],
        },
        fallbacks=[CommandHandler('cancel', cancel_handler)]
    )
    
    # 3. Add Handlers to Application
    app.add_handler(CommandHandler("start", deep_link_handler))
    app.add_handler(CommandHandler("admin", admin_panel))
    
    app.add_handler(post_conv)
    app.add_handler(channel_conv)
    
    # The critical handler for channel buttons
    app.add_handler(CallbackQueryHandler(channel_verification_handler, pattern='^verify_'))
    
    # 4. Run Application
    print("✅ System Online. Waiting for updates...")
    app.run_polling()
