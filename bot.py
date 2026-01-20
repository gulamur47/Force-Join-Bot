"""
####################################################################################################
#                                                                                                  #
#                       SUPREME LOVER BOT - ENTERPRISE EDITION v69.0                               #
#                       (Hot Messages + Force Join + Auto Redirect)                                #
#                                                                                                  #
# ------------------------------------------------------------------------------------------------ #
#  AUTHOR       : Supreme AI Team                                                                  #
#  STATUS       : Production Ready                                                                 #
#  DATABASE     : SQLite3 (Integrated)                                                             #
#  FRAMEWORK    : python-telegram-bot v20+                                                       #
# ------------------------------------------------------------------------------------------------ #
#                                                                                                  #
#  [ FEATURES ]                                                                                    #
#  1. SPOILER MODE: Channel posts are blurred (Hidden Content).                                    #
#  2. FLIRTY TEXTS: Long, engaging, and seductive messages as requested.                           #
#  3. SMART GATEWAY: Checks channel membership in real-time.                                       #
#  4. AUTO REDIRECT: Moves user from Public Channel -> Private Bot Chat instantly.                 #
#  5. SECURE DELIVERY: Sends unblurred content only after verification.                            #
#                                                                                                  #
####################################################################################################
"""

import sys
import os
import time
import json
import logging
import sqlite3
import asyncio
import threading
from datetime import datetime
from typing import List, Dict, Set, Optional, Any

# --------------------------------------------------------------------------------------------------
# [ DEPENDENCY CHECK ]
# --------------------------------------------------------------------------------------------------
try:
    from telegram import (
        Update, 
        InlineKeyboardButton, 
        InlineKeyboardMarkup, 
        User
    )
    from telegram.constants import ParseMode, ChatAction
    from telegram.ext import (
        ApplicationBuilder, 
        CommandHandler, 
        CallbackQueryHandler, 
        MessageHandler, 
        ContextTypes, 
        ConversationHandler, 
        filters,
        Application
    )
    from telegram.error import BadRequest, Forbidden, TelegramError
except ImportError:
    print("CRITICAL: 'python-telegram-bot' not found. Run: pip install python-telegram-bot")
    sys.exit(1)

# ==================================================================================================
# [ CONFIGURATION ]
# ==================================================================================================

class Config:
    # ⚠️ REPLACE WITH YOUR BOT TOKEN
    BOT_TOKEN = "8007194607:AAHhuMvS3z814Fr2eF_17K1wv8UPXmvA1kY"
    
    # ⚠️ REPLACE WITH YOUR ADMIN ID (Integer)
    ADMIN_IDS = {8013042180} 
    
    DB_NAME = "supreme_love.db"
    
    # Time to cache membership (seconds)
    CACHE_TIME = 300 
    
    # Auto delete warning messages (seconds)
    AUTO_DEL = 25

    # --- TEXT MESSAGES (HOT & LONG VERSION) ---
    
    MSG_WELCOME = (
        "💋 <b>Ooh... Hello there, Darling!</b> {name} \n\n"
        "I've been waiting for someone exactly like you to come here. "
        "You look like someone who enjoys the <i>finer, hotter</i> things in life... 🔥\n\n"
        "I am your personal <b>Pleasure Assistant</b>. I hold the keys to the most "
        "exclusive, heart-pounding content that others can only dream of.\n\n"
        "👇 <i>Don't keep me waiting... explore my world below.</i>"
    )

    MSG_LOCK_CHANNEL = (
        "🔥 <b>OH NO, BABY! YOU ARE LOCKED OUT!</b> 🔒\n\n"
        "Darling, you are trying to touch what isn't yours yet... and you know I love it when you work for it. 😘\n\n"
        "To see this <b>Exclusive, Hot, and Uncensored</b> content, you need to show me some love first.\n\n"
        "👇 <b>Here is what you need to do:</b>\n"
        "1. Join my private channels below.\n"
        "2. Come back and press that big Verify button.\n"
        "3. Let me reward you properly... 😈"
    )

    MSG_POPUP_DENIED = (
        "🚫 Aww, naughty boy!\n"
        "You haven't joined my channels yet! 😢\n"
        "Don't cheat on me... go join them first!"
    )

    MSG_POPUP_SUCCESS = (
        "✅ Mmm... Good boy! 😍\n"
        "You made me happy.\n"
        "Taking you to my private room now..."
    )

    MSG_PRIVATE_DELIVERY = (
        "💖 <b>FINALLY! WE ARE ALONE!</b> 💖\n\n"
        "I promised you a reward, didn't I? And I always keep my promises... 😏\n\n"
        "Here is the content you were craving for. No blur, no limits, just pure satisfaction.\n"
        "Enjoy it, baby... and don't forget to come back for more. 🔥\n\n"
        "<i>(Click the buttons below to watch/download)</i>"
    )

# ==================================================================================================
# [ LOGGING ]
# ==================================================================================================

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("SupremeBot")

# ==================================================================================================
# [ DATABASE MANAGER ]
# ==================================================================================================

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(Config.DB_NAME, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self._init_tables()

    def _init_tables(self):
        # Users
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                name TEXT,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Channels
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS channels (
                cid TEXT PRIMARY KEY,
                name TEXT,
                link TEXT,
                active BOOLEAN DEFAULT 1
            )
        ''')
        # Posts
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                pid INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                photo TEXT,
                caption TEXT,
                buttons TEXT,
                channels TEXT,
                views INTEGER DEFAULT 0
            )
        ''')
        self.conn.commit()

    def add_user(self, u: User):
        self.cursor.execute('INSERT OR REPLACE INTO users (id, username, name) VALUES (?, ?, ?)',
                            (u.id, u.username, u.first_name))
        self.conn.commit()

    def add_channel(self, cid, name, link):
        self.cursor.execute('INSERT OR REPLACE INTO channels (cid, name, link, active) VALUES (?, ?, ?, 1)',
                            (cid, name, link))
        self.conn.commit()

    def get_channels(self):
        self.cursor.execute("SELECT * FROM channels WHERE active = 1")
        return [dict(r) for r in self.cursor.fetchall()]

    def create_post(self, title, photo, caption, buttons, channels):
        self.cursor.execute('''
            INSERT INTO posts (title, photo, caption, buttons, channels)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, photo, caption, json.dumps(buttons), json.dumps(channels)))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_post(self, pid):
        self.cursor.execute("SELECT * FROM posts WHERE pid = ?", (pid,))
        r = self.cursor.fetchone()
        if r:
            d = dict(r)
            d['buttons'] = json.loads(d['buttons'])
            d['channels'] = json.loads(d['channels'])
            return d
        return None

db = Database()

# ==================================================================================================
# [ WIZARD STATES ]
# ==================================================================================================

(
    ST_TITLE, ST_PHOTO, ST_TEXT, ST_BTN_MENU, ST_BTN_NAME, ST_BTN_LINK, ST_TARGET,
    ST_ADD_CID, ST_ADD_CNAME, ST_ADD_CLINK
) = range(10)

# ==================================================================================================
# [ POST CREATION LOGIC ]
# ==================================================================================================

class PostWizard:
    @staticmethod
    async def start(update, context):
        q = update.callback_query
        await q.answer()
        context.user_data['post'] = {'btns': []}
        await q.message.reply_text("📝 <b>Step 1: Enter Title (Make it HOT):</b>", parse_mode=ParseMode.HTML)
        return ST_TITLE

    @staticmethod
    async def title(update, context):
        context.user_data['post']['title'] = update.message.text
        await update.message.reply_text("📸 <b>Step 2: Send the Photo (Cover Image):</b>", parse_mode=ParseMode.HTML)
        return ST_PHOTO

    @staticmethod
    async def photo(update, context):
        if not update.message.photo:
            await update.message.reply_text("❌ Baby, send a photo please!")
            return ST_PHOTO
        context.user_data['post']['photo'] = update.message.photo[-1].file_id
        await update.message.reply_text("💬 <b>Step 3: Send the Caption (Use /skip if needed):</b>", parse_mode=ParseMode.HTML)
        return ST_TEXT

    @staticmethod
    async def text(update, context):
        txt = update.message.text
        context.user_data['post']['caption'] = "" if txt == "/skip" else txt
        return await PostWizard.render_menu(update, context)

    @staticmethod
    async def render_menu(update, context):
        btns = context.user_data['post']['btns']
        msg = f"🔘 <b>Buttons Added: {len(btns)}</b>\n"
        for b in btns: msg += f"- {b['name']} -> {b['link']}\n"
        
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add Button", callback_data="add")],
            [InlineKeyboardButton("✅ Done & Post", callback_data="done")]
        ])
        
        if update.callback_query:
            await update.callback_query.message.edit_text(msg, reply_markup=kb, parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(msg, reply_markup=kb, parse_mode=ParseMode.HTML)
        return ST_BTN_MENU

    @staticmethod
    async def menu_cb(update, context):
        q = update.callback_query
        if q.data == "add":
            await q.message.reply_text("✏️ Enter Button Name:")
            return ST_BTN_NAME
        elif q.data == "done":
            chs = db.get_channels()
            if not chs:
                await q.message.reply_text("❌ No channels found! Add one first.")
                return ConversationHandler.END
            kb = InlineKeyboardMarkup([[InlineKeyboardButton(f"📢 {c['name']}", callback_data=f"tgt_{c['cid']}")] for c in chs])
            await q.message.edit_text("📤 <b>Select Channel to Post:</b>", reply_markup=kb, parse_mode=ParseMode.HTML)
            return ST_TARGET

    @staticmethod
    async def btn_name(update, context):
        context.user_data['tmp_name'] = update.message.text
        await update.message.reply_text("🔗 Enter Link (http...):")
        return ST_BTN_LINK

    @staticmethod
    async def btn_link(update, context):
        context.user_data['post']['btns'].append({
            'name': context.user_data['tmp_name'], 'link': update.message.text
        })
        return await PostWizard.render_menu(update, context)

    @staticmethod
    async def finalize(update, context):
        q = update.callback_query
        target = q.data.replace("tgt_", "")
        d = context.user_data['post']
        
        # Save to DB
        all_cids = [c['cid'] for c in db.get_channels()]
        pid = db.create_post(d['title'], d['photo'], d['caption'], d['btns'], all_cids)
        
        # KEY LOGIC: BLURRED IMAGE + FAKE BUTTON
        verify_kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("🔞 UNLOCK FULL VIDEO 🍑", callback_data=f"verify_{pid}")
        ]])
        
        caption_public = (
            f"<b>{d['title']}</b>\n\n"
            f"{d['caption'][:100]}...\n\n"
            f"🔒 <b>PREMIUM CONTENT LOCKED</b>\n"
            f"<i>Tap below to verify and remove censorship...</i>"
        )
        
        try:
            await context.bot.send_photo(
                chat_id=target,
                photo=d['photo'],
                caption=caption_public,
                reply_markup=verify_kb,
                has_spoiler=True, # BLURS THE IMAGE
                parse_mode=ParseMode.HTML
            )
            await q.message.edit_text(f"✅ <b>Post Successfully Created!</b>\nID: {pid}")
        except Exception as e:
            await q.message.edit_text(f"❌ Error: {e}")
            
        return ConversationHandler.END

# ==================================================================================================
# [ CHANNEL WIZARD ]
# ==================================================================================================

class ChannelWizard:
    @staticmethod
    async def start(update, context):
        await update.callback_query.message.reply_text("🆔 Enter Channel ID (e.g. -100...):")
        return ST_ADD_CID
    @staticmethod
    async def get_id(update, context):
        context.user_data['cid'] = update.message.text
        await update.message.reply_text("📝 Enter Channel Name:")
        return ST_ADD_CNAME
    @staticmethod
    async def get_name(update, context):
        context.user_data['cname'] = update.message.text
        await update.message.reply_text("🔗 Enter Invite Link:")
        return ST_ADD_CLINK
    @staticmethod
    async def get_link(update, context):
        db.add_channel(context.user_data['cid'], context.user_data['cname'], update.message.text)
        await update.message.reply_text("✅ Channel Saved Successfully!")
        return ConversationHandler.END

# ==================================================================================================
# [ CORE LOGIC: VERIFY & REDIRECT ]
# ==================================================================================================

async def verify_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    user = q.from_user
    pid = int(q.data.replace("verify_", ""))
    
    # Get Post
    post = db.get_post(pid)
    if not post:
        await q.answer("❌ This content is no longer available.", show_alert=True)
        return

    # Check Membership
    missing = []
    all_chs = {c['cid']: c for c in db.get_channels()}
    
    for cid in post['channels']:
        if cid not in all_chs: continue
        try:
            mem = await context.bot.get_chat_member(cid, user.id)
            if mem.status in ['left', 'kicked', 'banned']:
                missing.append(all_chs[cid])
        except Exception:
            missing.append(all_chs[cid])

    # 🛑 CASE: NOT JOINED
    if missing:
        await q.answer(Config.MSG_POPUP_DENIED, show_alert=True)
        
        btns = [[InlineKeyboardButton(f"📢 Join {c['name']}", url=c['link'])] for c in missing]
        btns.append([InlineKeyboardButton("🔄 TRY AGAIN NOW 🔄", callback_data=f"verify_{pid}")])
        
        msg = await context.bot.send_message(
            chat_id=q.message.chat_id,
            text=Config.MSG_LOCK_CHANNEL,
            reply_to_message_id=q.message.message_id,
            reply_markup=InlineKeyboardMarkup(btns),
            parse_mode=ParseMode.HTML
        )
        # Auto Delete
        asyncio.create_task(delete_later(msg))
        return

    # ✅ CASE: VERIFIED -> REDIRECT TO BOT
    bot_url = f"https://t.me/{context.bot.username}?start=show_{pid}"
    await q.answer(Config.MSG_POPUP_SUCCESS, show_alert=False, url=bot_url)

async def deep_link_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.add_user(user)
    
    args = context.args
    
    # Standard Welcome
    if not args:
        await update.message.reply_text(
            Config.MSG_WELCOME.format(name=user.first_name),
            parse_mode=ParseMode.HTML
        )
        return

    # Content Delivery
    payload = args[0]
    if payload.startswith("show_"):
        try:
            pid = int(payload.replace("show_", ""))
            post = db.get_post(pid)
            if not post: return

            # Double Check (Security)
            for cid in post['channels']:
                try:
                    m = await context.bot.get_chat_member(cid, user.id)
                    if m.status in ['left', 'kicked']: 
                        await update.message.reply_text("❌ Nice try! Join channels first.")
                        return
                except: pass

            # SEND REAL CONTENT
            real_kb = InlineKeyboardMarkup([
                [InlineKeyboardButton(b['name'], url=b['link'])] for b in post['buttons']
            ])
            
            # Combine custom caption with Hot delivery text
            full_caption = (
                f"{Config.MSG_PRIVATE_DELIVERY}\n"
                f"➖➖➖➖➖➖➖➖➖➖\n"
                f"<b>🎬 {post['title']}</b>\n"
                f"{post['caption']}"
            )
            
            await context.bot.send_photo(
                chat_id=user.id,
                photo=post['photo'],
                caption=full_caption,
                reply_markup=real_kb,
                parse_mode=ParseMode.HTML
            )
            
        except Exception as e:
            logger.error(f"Deep link error: {e}")
            await update.message.reply_text("❌ An error occurred.")

# ==================================================================================================
# [ UTILITIES ]
# ==================================================================================================

async def delete_later(msg):
    await asyncio.sleep(Config.AUTO_DEL)
    try: await msg.delete()
    except: pass

async def admin_panel(update, context):
    if update.effective_user.id not in Config.ADMIN_IDS: return
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 Create Hot Post", callback_data="wiz_post")],
        [InlineKeyboardButton("➕ Add Channel", callback_data="wiz_ch")]
    ])
    await update.message.reply_text("👑 <b>MASTER CONTROL PANEL</b>", reply_markup=kb, parse_mode=ParseMode.HTML)

async def cancel(update, context):
    await update.message.reply_text("🚫 Cancelled.")
    return ConversationHandler.END

# ==================================================================================================
# [ MAIN LOOP ]
# ==================================================================================================

def main():
    print(">>> 🔥 LOVER BOT SYSTEMS ONLINE...")
    app = ApplicationBuilder().token(Config.BOT_TOKEN).build()

    # Wizards
    post_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(PostWizard.start, pattern='^wiz_post$')],
        states={
            ST_TITLE: [MessageHandler(filters.TEXT, PostWizard.title)],
            ST_PHOTO: [MessageHandler(filters.PHOTO, PostWizard.photo)],
            ST_TEXT: [MessageHandler(filters.TEXT, PostWizard.text)],
            ST_BTN_MENU: [CallbackQueryHandler(PostWizard.menu_cb)],
            ST_BTN_NAME: [MessageHandler(filters.TEXT, PostWizard.btn_name)],
            ST_BTN_LINK: [MessageHandler(filters.TEXT, PostWizard.btn_link)],
            ST_TARGET: [CallbackQueryHandler(PostWizard.finalize, pattern='^tgt_')]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    ch_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(ChannelWizard.start, pattern='^wiz_ch$')],
        states={
            ST_ADD_CID: [MessageHandler(filters.TEXT, ChannelWizard.get_id)],
            ST_ADD_CNAME: [MessageHandler(filters.TEXT, ChannelWizard.get_name)],
            ST_ADD_CLINK: [MessageHandler(filters.TEXT, ChannelWizard.get_link)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # Handlers
    app.add_handler(CommandHandler("start", deep_link_handler))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(post_conv)
    app.add_handler(ch_conv)
    app.add_handler(CallbackQueryHandler(verify_handler, pattern='^verify_'))

    app.run_polling()

if __name__ == "__main__":
    main()
