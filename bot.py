import os
import logging
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load configuration
BOT_TOKEN = os.getenv('8216066342:AAHLCoA0F0HGpdLRykTGcomTY7jN4sQwRwU')
ADMINS = list(map(int, os.getenv('6406804999', '').split(','))) if os.getenv('ADMINS') else []
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'love_bot')

# Initialize bot
bot = telebot.TeleBot(BOT_TOKEN)

# Database connection
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

# Collections
users_col = db['users']
channels_col = db['channels']
posts_col = db['posts']
welcome_col = db['welcome']

# Data classes
@dataclass
class User:
    user_id: int
    username: str
    first_name: str
    verified: bool = False
    joined_channels: List[str] = None
    unlocked_posts: List[str] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.joined_channels is None:
            self.joined_channels = []
        if self.unlocked_posts is None:
            self.unlocked_posts = []
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class Channel:
    channel_id: str
    username: str
    button_name: str
    is_active: bool = True

@dataclass
class Button:
    name: str
    link: str

@dataclass
class Post:
    post_id: str
    title: str
    media_type: str  # 'photo' or 'video'
    media_id: str
    buttons: List[Button]
    force_join_channels: List[str]
    target_channels: List[str]
    created_by: int
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

class BotState(Enum):
    WAITING_TITLE = "waiting_title"
    WAITING_MEDIA = "waiting_media"
    WAITING_BUTTON_NAME = "waiting_button_name"
    WAITING_BUTTON_LINK = "waiting_button_link"
    WAITING_FORCE_JOIN = "waiting_force_join"
    WAITING_TARGET_CHANNELS = "waiting_target_channels"
    PREVIEW_POST = "preview_post"
    WAITING_WELCOME_TEXT = "waiting_welcome_text"
    WAITING_WELCOME_PHOTO = "waiting_welcome_photo"

# State management for admin flows
admin_states = {}

# Helper functions
def get_user(user_id: int) -> Optional[User]:
    """Get user from database or create new"""
    user_data = users_col.find_one({"user_id": user_id})
    if user_data:
        return User(**user_data)
    
    # Get user info from Telegram
    try:
        user = bot.get_chat(user_id)
        new_user = User(
            user_id=user_id,
            username=user.username,
            first_name=user.first_name
        )
        users_col.insert_one(asdict(new_user))
        return new_user
    except:
        return None

def update_user(user: User):
    """Update user in database"""
    users_col.update_one(
        {"user_id": user.user_id},
        {"$set": asdict(user)},
        upsert=True
    )

def get_channels() -> List[Channel]:
    """Get all active channels"""
    channels_data = list(channels_col.find({"is_active": True}))
    return [Channel(**data) for data in channels_data]

def get_channel(channel_id: str) -> Optional[Channel]:
    """Get specific channel"""
    data = channels_col.find_one({"channel_id": channel_id})
    return Channel(**data) if data else None

def save_channel(channel: Channel):
    """Save channel to database"""
    channels_col.update_one(
        {"channel_id": channel.channel_id},
        {"$set": asdict(channel)},
        upsert=True
    )

def delete_channel(channel_id: str):
    """Delete channel from database"""
    channels_col.delete_one({"channel_id": channel_id})

def save_post(post: Post):
    """Save post to database"""
    post_dict = asdict(post)
    post_dict['buttons'] = [asdict(btn) for btn in post.buttons]
    posts_col.insert_one(post_dict)

def get_welcome_config():
    """Get welcome message configuration"""
    config = welcome_col.find_one({"type": "welcome"})
    if not config:
        # Default welcome message
        default_config = {
            "type": "welcome",
            "text": "💖 Hello {first_name}! Welcome to our romantic world! ❤️\n\nClick Verified to unlock surprises! 🔥",
            "photo_id": None
        }
        welcome_col.insert_one(default_config)
        return default_config
    return config

def update_welcome_text(text: str):
    """Update welcome text"""
    welcome_col.update_one(
        {"type": "welcome"},
        {"$set": {"text": text}},
        upsert=True
    )

def update_welcome_photo(photo_id: str):
    """Update welcome photo"""
    welcome_col.update_one(
        {"type": "welcome"},
        {"$set": {"photo_id": photo_id}},
        upsert=True
    )

def check_user_joined_channels(user_id: int, channel_ids: List[str]) -> bool:
    """Check if user has joined all required channels"""
    for channel_id in channel_ids:
        try:
            member = bot.get_chat_member(channel_id, user_id)
            if member.status in ['left', 'kicked']:
                return False
        except Exception as e:
            logger.error(f"Error checking channel membership: {e}")
            return False
    return True

def create_inline_keyboard(buttons: List[Button], row_width: int = 2) -> InlineKeyboardMarkup:
    """Create inline keyboard from buttons"""
    keyboard = InlineKeyboardMarkup(row_width=row_width)
    
    for button in buttons:
        keyboard.add(InlineKeyboardButton(
            text=button.name,
            url=button.link
        ))
    
    return keyboard

def create_channels_keyboard(channels: List[Channel], selected: List[str] = None, 
                           action: str = "select") -> InlineKeyboardMarkup:
    """Create keyboard for channel selection"""
    if selected is None:
        selected = []
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    for channel in channels:
        emoji = "✅" if channel.channel_id in selected else "🔘"
        callback_data = f"{action}_channel_{channel.channel_id}"
        keyboard.add(InlineKeyboardButton(
            text=f"{emoji} {channel.button_name}",
            callback_data=callback_data
        ))
    
    # Add done button
    keyboard.add(InlineKeyboardButton(
        text="✅ Done",
        callback_data=f"{action}_done"
    ))
    
    return keyboard

# User handlers
@bot.message_handler(commands=['start'])
def handle_start(message):
    """Handle /start command"""
    user = get_user(message.from_user.id)
    if not user:
        return
    
    welcome_config = get_welcome_config()
    welcome_text = welcome_config['text'].format(
        first_name=user.first_name,
        username=user.username
    )
    
    # Create welcome keyboard
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    # Add channel join buttons
    channels = get_channels()
    for channel in channels:
        keyboard.add(InlineKeyboardButton(
            text=f"👉 {channel.button_name}",
            url=f"https://t.me/{channel.username.lstrip('@')}"
        ))
    
    # Add Verified button
    keyboard.add(InlineKeyboardButton(
        text="✅ Verified ❤️",
        callback_data="verify_user"
    ))
    
    # Send welcome message with photo if available
    if welcome_config.get('photo_id'):
        bot.send_photo(
            chat_id=message.chat.id,
            photo=welcome_config['photo_id'],
            caption=welcome_text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
    else:
        bot.send_message(
            chat_id=message.chat.id,
            text=welcome_text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )

@bot.callback_query_handler(func=lambda call: call.data == "verify_user")
def handle_verify(call):
    """Handle verify button click"""
    user = get_user(call.from_user.id)
    if not user:
        return
    
    # Check if user has joined all channels
    channels = get_channels()
    channel_ids = [channel.channel_id for channel in channels]
    
    if check_user_joined_channels(user.user_id, channel_ids):
        # User has joined all channels
        user.verified = True
        user.joined_channels = channel_ids
        update_user(user)
        
        # Show success popup
        bot.answer_callback_query(
            call.id,
            text="Uffff 😍 Tumi verified ❤️ Next surprise unlock 🔥",
            show_alert=True
        )
        
        # Remove Verified button and add Watch Now
        keyboard = InlineKeyboardMarkup(row_width=2)
        
        # Add channel buttons
        for channel in channels:
            keyboard.add(InlineKeyboardButton(
                text=f"👉 {channel.button_name}",
                url=f"https://t.me/{channel.username.lstrip('@')}"
            ))
        
        # Add Watch Now button
        keyboard.add(InlineKeyboardButton(
            text="🎬 Watch Now",
            callback_data="watch_now"
        ))
        
        # Edit message
        try:
            bot.edit_message_reply_markup(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=keyboard
            )
        except:
            pass
    else:
        # User hasn't joined all channels
        bot.answer_callback_query(
            call.id,
            text="Awww 😘 Age sob channel join koro baby 💔",
            show_alert=True
        )

@bot.callback_query_handler(func=lambda call: call.data == "watch_now")
def handle_watch_now(call):
    """Handle Watch Now button click"""
    user = get_user(call.from_user.id)
    if not user or not user.verified:
        bot.answer_callback_query(
            call.id,
            text="Awww 😘 Age sob channel join koro baby 💔",
            show_alert=True
        )
        return
    
    # Get posts that user can access
    posts = list(posts_col.find())
    
    if not posts:
        bot.answer_callback_query(
            call.id,
            text="No content available yet! 😔",
            show_alert=True
        )
        return
    
    # Send first post
    post = posts[0]
    buttons = [Button(**btn) for btn in post['buttons']]
    keyboard = create_inline_keyboard(buttons)
    
    if post['media_type'] == 'photo':
        bot.send_photo(
            chat_id=call.message.chat.id,
            photo=post['media_id'],
            caption=post['title'],
            reply_markup=keyboard
        )
    else:  # video
        bot.send_video(
            chat_id=call.message.chat.id,
            video=post['media_id'],
            caption=post['title'],
            reply_markup=keyboard
        )
    
    bot.answer_callback_query(call.id)

# Admin handlers
@bot.message_handler(commands=['admin'])
def handle_admin(message):
    """Handle /admin command"""
    if message.from_user.id not in ADMINS:
        bot.send_message(
            chat_id=message.chat.id,
            text="⚠️ Access Denied!"
        )
        return
    
    # Create admin panel
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        InlineKeyboardButton("➕ Add Post", callback_data="admin_add_post"),
        InlineKeyboardButton("📊 Channel Management", callback_data="admin_channels")
    )
    
    keyboard.add(
        InlineKeyboardButton("✏️ Welcome Message", callback_data="admin_welcome_text"),
        InlineKeyboardButton("🖼 Welcome Photo", callback_data="admin_welcome_photo")
    )
    
    keyboard.add(
        InlineKeyboardButton("📢 Multiple Channel Post", callback_data="admin_multi_post"),
        InlineKeyboardButton("👁 Preview Posts", callback_data="admin_preview")
    )
    
    bot.send_message(
        chat_id=message.chat.id,
        text="🔧 *Admin Panel*\n\nSelect an option:",
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_"))
def handle_admin_panel(call):
    """Handle admin panel buttons"""
    if call.from_user.id not in ADMINS:
        bot.answer_callback_query(call.id, text="Access Denied!", show_alert=True)
        return
    
    action = call.data
    
    if action == "admin_add_post":
        # Start post creation flow
        admin_states[call.from_user.id] = {
            "state": BotState.WAITING_TITLE,
            "post_data": {}
        }
        
        bot.send_message(
            chat_id=call.message.chat.id,
            text="📝 *Add New Post*\n\nPlease send the post title:",
            parse_mode='Markdown'
        )
    
    elif action == "admin_channels":
        # Show channel management
        show_channel_management(call.message.chat.id)
    
    elif action == "admin_welcome_text":
        admin_states[call.from_user.id] = {
            "state": BotState.WAITING_WELCOME_TEXT
        }
        
        bot.send_message(
            chat_id=call.message.chat.id,
            text="✏️ *Set Welcome Text*\n\nSend the new welcome text.\n\nYou can use:\n- `{first_name}` for user's first name\n- `{username}` for username",
            parse_mode='Markdown'
        )
    
    elif action == "admin_welcome_photo":
        admin_states[call.from_user.id] = {
            "state": BotState.WAITING_WELCOME_PHOTO
        }
        
        bot.send_message(
            chat_id=call.message.chat.id,
            text="🖼 *Set Welcome Photo*\n\nSend the new welcome photo:",
            parse_mode='Markdown'
        )
    
    elif action == "admin_multi_post":
        show_multi_channel_post(call.message.chat.id)
    
    elif action == "admin_preview":
        show_post_preview(call.message.chat.id)
    
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("channel_"))
def handle_channel_management(call):
    """Handle channel management actions"""
    if call.from_user.id not in ADMINS:
        bot.answer_callback_query(call.id, text="Access Denied!", show_alert=True)
        return
    
    parts = call.data.split("_")
    action = parts[0]
    channel_id = parts[2] if len(parts) > 2 else None
    
    if action == "add":
        admin_states[call.from_user.id] = {
            "state": "waiting_channel_info"
        }
        
        bot.send_message(
            chat_id=call.message.chat.id,
            text="➕ *Add Channel*\n\nSend channel info in format:\n`@channel_username Channel Name`",
            parse_mode='Markdown'
        )
    
    elif action == "delete" and channel_id:
        delete_channel(channel_id)
        bot.answer_callback_query(call.id, text="✅ Channel deleted!", show_alert=True)
        show_channel_management(call.message.chat.id)
    
    elif action == "edit" and channel_id:
        # Implementation for edit channel
        pass

def show_channel_management(chat_id):
    """Show channel management interface"""
    channels = get_channels()
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    for channel in channels:
        keyboard.add(
            InlineKeyboardButton(
                f"✏️ {channel.button_name}",
                callback_data=f"edit_channel_{channel.channel_id}"
            ),
            InlineKeyboardButton(
                f"❌ Delete",
                callback_data=f"delete_channel_{channel.channel_id}"
            )
        )
    
    keyboard.add(InlineKeyboardButton("➕ Add Channel", callback_data="add_channel"))
    keyboard.add(InlineKeyboardButton("🔙 Back", callback_data="admin_back"))
    
    bot.send_message(
        chat_id=chat_id,
        text="📊 *Channel Management*\n\nCurrent channels:",
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

def show_multi_channel_post(chat_id):
    """Show multi-channel post interface"""
    channels = get_channels()
    
    if not channels:
        bot.send_message(
            chat_id=chat_id,
            text="❌ No channels available. Add channels first.",
            parse_mode='Markdown'
        )
        return
    
    keyboard = create_channels_keyboard(channels, action="post_select")
    keyboard.add(InlineKeyboardButton("🔙 Back", callback_data="admin_back"))
    
    bot.send_message(
        chat_id=chat_id,
        text="📢 *Multiple Channel Post*\n\nSelect channels to post to:",
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

def show_post_preview(chat_id):
    """Show post preview interface"""
    posts = list(posts_col.find().sort("created_at", -1).limit(5))
    
    if not posts:
        bot.send_message(
            chat_id=chat_id,
            text="❌ No posts available.",
            parse_mode='Markdown'
        )
        return
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    for post in posts:
        keyboard.add(InlineKeyboardButton(
            f"📝 {post['title'][:20]}...",
            callback_data=f"preview_post_{post['post_id']}"
        ))
    
    keyboard.add(InlineKeyboardButton("🔙 Back", callback_data="admin_back"))
    
    bot.send_message(
        chat_id=chat_id,
        text="👁 *Preview Posts*\n\nSelect a post to preview:",
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

# Message handlers for admin flows
@bot.message_handler(func=lambda message: message.from_user.id in ADMINS and 
                    message.from_user.id in admin_states)
def handle_admin_flow(message):
    """Handle admin flow states"""
    state_data = admin_states.get(message.from_user.id)
    if not state_data:
        return
    
    state = state_data.get("state")
    
    if state == BotState.WAITING_TITLE:
        # Save title and ask for media
        state_data["post_data"]["title"] = message.text
        state_data["post_data"]["buttons"] = []
        state_data["state"] = BotState.WAITING_MEDIA
        
        bot.send_message(
            chat_id=message.chat.id,
            text="📸 *Add Media*\n\nNow send a photo or video for the post:",
            parse_mode='Markdown'
        )
    
    elif state == BotState.WAITING_MEDIA:
        # Save media and ask for buttons
        if message.photo:
            state_data["post_data"]["media_type"] = "photo"
            state_data["post_data"]["media_id"] = message.photo[-1].file_id
        elif message.video:
            state_data["post_data"]["media_type"] = "video"
            state_data["post_data"]["media_id"] = message.video.file_id
        else:
            bot.send_message(
                chat_id=message.chat.id,
                text="❌ Please send a photo or video!"
            )
            return
        
        state_data["state"] = BotState.WAITING_BUTTON_NAME
        state_data["button_step"] = 1
        
        bot.send_message(
            chat_id=message.chat.id,
            text="🔘 *Add Button*\n\nSend button name for button #1 (or type /done to finish):",
            parse_mode='Markdown'
        )
    
    elif state == BotState.WAITING_BUTTON_NAME:
        if message.text == "/done":
            if not state_data["post_data"]["buttons"]:
                bot.send_message(
                    chat_id=message.chat.id,
                    text="❌ You must add at least one button!"
                )
                return
            
            # Move to force join selection
            state_data["state"] = BotState.WAITING_FORCE_JOIN
            channels = get_channels()
            
            if not channels:
                bot.send_message(
                    chat_id=message.chat.id,
                    text="❌ No channels available. Add channels first.",
                    parse_mode='Markdown'
                )
                del admin_states[message.from_user.id]
                return
            
            keyboard = create_channels_keyboard(channels, action="force_select")
            keyboard.add(InlineKeyboardButton("🔙 Back", callback_data="admin_back"))
            
            bot.send_message(
                chat_id=message.chat.id,
                text="🔗 *Force Join Channels*\n\nSelect channels users must join:",
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        else:
            state_data["temp_button_name"] = message.text
            state_data["state"] = BotState.WAITING_BUTTON_LINK
            
            bot.send_message(
                chat_id=message.chat.id,
                text=f"🔗 *Button Link*\n\nSend link for button '{message.text}':",
                parse_mode='Markdown'
            )
    
    elif state == BotState.WAITING_BUTTON_LINK:
        button = Button(
            name=state_data["temp_button_name"],
            link=message.text
        )
        state_data["post_data"]["buttons"].append(button)
        
        step = state_data["button_step"] + 1
        state_data["button_step"] = step
        state_data["state"] = BotState.WAITING_BUTTON_NAME
        
        bot.send_message(
            chat_id=message.chat.id,
            text=f"✅ Button added!\n\nSend button name for button #{step} (or type /done to finish):",
            parse_mode='Markdown'
        )
    
    elif state == BotState.WAITING_WELCOME_TEXT:
        update_welcome_text(message.text)
        del admin_states[message.from_user.id]
        
        bot.send_message(
            chat_id=message.chat.id,
            text="✅ Welcome text updated!",
            parse_mode='Markdown'
        )
    
    elif state == BotState.WAITING_WELCOME_PHOTO:
        if message.photo:
            update_welcome_photo(message.photo[-1].file_id)
            del admin_states[message.from_user.id]
            
            bot.send_message(
                chat_id=message.chat.id,
                text="✅ Welcome photo updated!",
                parse_mode='Markdown'
            )
        else:
            bot.send_message(
                chat_id=message.chat.id,
                text="❌ Please send a photo!"
            )
    
    elif state == "waiting_channel_info":
        # Parse channel info
        parts = message.text.split(" ", 1)
        if len(parts) != 2:
            bot.send_message(
                chat_id=message.chat.id,
                text="❌ Invalid format! Use:\n`@channel_username Channel Name`",
                parse_mode='Markdown'
            )
            return
        
        username, button_name = parts
        channel_id = username.lstrip('@')
        
        # Create and save channel
        channel = Channel(
            channel_id=channel_id,
            username=username,
            button_name=button_name
        )
        save_channel(channel)
        
        del admin_states[message.from_user.id]
        
        bot.send_message(
            chat_id=message.chat.id,
            text=f"✅ Channel '{button_name}' added!",
            parse_mode='Markdown'
        )
        show_channel_management(message.chat.id)

# Callback handlers for channel selection
@bot.callback_query_handler(func=lambda call: call.data.startswith(("select_", "force_", "post_")))
def handle_channel_selection(call):
    """Handle channel selection in various flows"""
    if call.from_user.id not in ADMINS:
        bot.answer_callback_query(call.id, text="Access Denied!", show_alert=True)
        return
    
    parts = call.data.split("_")
    action_type = parts[0]  # select, force, post
    action = parts[1]  # channel, done
    
    user_id = call.from_user.id
    state_data = admin_states.get(user_id, {})
    
    if action == "done":
        if action_type == "force":
            # Move to target channel selection
            state_data["state"] = BotState.WAITING_TARGET_CHANNELS
            channels = get_channels()
            
            keyboard = create_channels_keyboard(channels, action="target_select")
            keyboard.add(InlineKeyboardButton("🔙 Back", callback_data="admin_back"))
            
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="🎯 *Target Post Channels*\n\nSelect channels to post in:",
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        
        elif action_type == "target":
            # Show preview
            state_data["state"] = BotState.PREVIEW_POST
            
            # Create preview
            post_data = state_data["post_data"]
            buttons = [Button(**btn) if isinstance(btn, dict) else btn for btn in post_data["buttons"]]
            keyboard = create_inline_keyboard(buttons)
            
            preview_text = f"📝 *Preview Post*\n\n*Title:* {post_data['title']}\n\n*Buttons:* {len(buttons)}\n\nConfirm publishing?"
            
            if post_data["media_type"] == "photo":
                bot.send_photo(
                    chat_id=call.message.chat.id,
                    photo=post_data["media_id"],
                    caption=preview_text,
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
            else:
                bot.send_video(
                    chat_id=call.message.chat.id,
                    video=post_data["media_id"],
                    caption=preview_text,
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
            
            # Add confirm buttons
            confirm_keyboard = InlineKeyboardMarkup()
            confirm_keyboard.add(
                InlineKeyboardButton("✅ Publish", callback_data="publish_post"),
                InlineKeyboardButton("❌ Cancel", callback_data="cancel_post")
            )
            
            bot.send_message(
                chat_id=call.message.chat.id,
                text="Confirm publishing this post?",
                reply_markup=confirm_keyboard
            )
    
    elif action == "channel":
        channel_id = parts[2]
        
        if action_type == "force":
            # Toggle force join channel
            if "force_channels" not in state_data:
                state_data["force_channels"] = []
            
            if channel_id in state_data["force_channels"]:
                state_data["force_channels"].remove(channel_id)
            else:
                state_data["force_channels"].append(channel_id)
            
            # Update keyboard
            channels = get_channels()
            keyboard = create_channels_keyboard(
                channels, 
                state_data["force_channels"],
                action="force_select"
            )
            keyboard.add(InlineKeyboardButton("🔙 Back", callback_data="admin_back"))
            
            bot.edit_message_reply_markup(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=keyboard
            )
        
        elif action_type == "target":
            # Toggle target channel
            if "target_channels" not in state_data:
                state_data["target_channels"] = []
            
            if channel_id in state_data["target_channels"]:
                state_data["target_channels"].remove(channel_id)
            else:
                state_data["target_channels"].append(channel_id)
            
            # Update keyboard
            channels = get_channels()
            keyboard = create_channels_keyboard(
                channels,
                state_data["target_channels"],
                action="target_select"
            )
            keyboard.add(InlineKeyboardButton("🔙 Back", callback_data="admin_back"))
            
            bot.edit_message_reply_markup(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=keyboard
            )
    
    admin_states[user_id] = state_data
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data in ["publish_post", "cancel_post", "admin_back"])
def handle_post_confirmation(call):
    """Handle post confirmation"""
    if call.from_user.id not in ADMINS:
        bot.answer_callback_query(call.id, text="Access Denied!", show_alert=True)
        return
    
    user_id = call.from_user.id
    state_data = admin_states.get(user_id, {})
    
    if call.data == "publish_post":
        # Publish the post
        post_data = state_data["post_data"]
        force_channels = state_data.get("force_channels", [])
        target_channels = state_data.get("target_channels", [])
        
        # Create post object
        post = Post(
            post_id=str(datetime.now().timestamp()),
            title=post_data["title"],
            media_type=post_data["media_type"],
            media_id=post_data["media_id"],
            buttons=post_data["buttons"],
            force_join_channels=force_channels,
            target_channels=target_channels,
            created_by=user_id
        )
        
        # Save to database
        save_post(post)
        
        # Publish to target channels
        buttons = post_data["buttons"]
        keyboard = create_inline_keyboard(buttons)
        
        for channel_id in target_channels:
            try:
                if post.media_type == "photo":
                    bot.send_photo(
                        chat_id=channel_id,
                        photo=post.media_id,
                        caption=post.title,
                        reply_markup=keyboard
                    )
                else:
                    bot.send_video(
                        chat_id=channel_id,
                        video=post.media_id,
                        caption=post.title,
                        reply_markup=keyboard
                    )
            except Exception as e:
                logger.error(f"Error posting to channel {channel_id}: {e}")
        
        bot.answer_callback_query(call.id, text="✅ Post published successfully!", show_alert=True)
        
        # Clean up
        if user_id in admin_states:
            del admin_states[user_id]
        
        # Show admin panel again
        handle_admin(call.message)
    
    elif call.data == "cancel_post":
        bot.answer_callback_query(call.id, text="❌ Post cancelled!", show_alert=True)
        
        if user_id in admin_states:
            del admin_states[user_id]
        
        handle_admin(call.message)
    
    elif call.data == "admin_back":
        bot.answer_callback_query(call.id)
        
        if user_id in admin_states:
            del admin_states[user_id]
        
        handle_admin(call.message)

# Error handler
@bot.message_handler(func=lambda message: True)
def handle_other_messages(message):
    """Handle other messages"""
    # Ignore non-command messages
    pass

if __name__ == "__main__":
    print("🤖 Bot is starting...")
    print(f"👑 Admins: {ADMINS}")
    
    # Create necessary collections if they don't exist
    if "welcome" not in db.list_collection_names():
        get_welcome_config()
    
    bot.infinity_polling()
