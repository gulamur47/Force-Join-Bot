"""
####################################################################################################
#                                                                                                  #
#                     সুপ্রিম লাভ ডিস্ট্রিবিউশন সিস্টেম (Supreme Love System)                        #
#                            এন্টারপ্রাইজ এডিশন v69.0 (বাংলা ভার্সন)                                 #
#                                                                                                  #
# ------------------------------------------------------------------------------------------------ #
#  কপিরাইট      : (C) ২০২৬ সুপ্রিম এআই সলিউশনস                                                       #
#  লাইসেন্স     : এমআইটি (MIT) ওপেন সোর্স                                                            #
#  ভাষা         : পাইথন ৩.১১+                                                                     #
#  ফ্রেমওয়ার্ক  : পাইথন-টেলিগ্রাম-বট (v20.x+)                                                      #
#  ডাটাবেস      : এসকিউলাইট ৩ (SQLite3) - WAL মোড                                                  #
# ------------------------------------------------------------------------------------------------ #
#                                                                                                  #
#  [ প্রজেক্টের বিবরণ ]                                                                            #
#  এটি একটি হাই-পারফরমেন্স টেলিগ্রাম বট যা রোমান্টিক এবং হট কন্টেন্ট ডেলিভারির জন্য তৈরি।          #
#  এটি ব্যবহারকারীদের সাথে ফ্লার্ট করে এবং চ্যানেল ভেরিফিকেশন নিশ্চিত করে।                         #
#                                                                                                  #
#  [ লজিক ফ্লো ]                                                                                   #
#  ১. এডমিন প্যানেল থেকে পোস্ট তৈরি করা হয়।                                                        #
#  ২. বট চ্যানেলে ব্লার (Spoiler) করা ছবি পোস্ট করে যাতে ইউজাররা আগ্রহী হয়।                        #
#  ৩. ইউজার "আনলক" বাটনে ক্লিক করলে বট মেম্বারশিপ চেক করে।                                         #
#     - যদি জয়েন না থাকে: একটি দুষ্টু/হট ওয়ার্নিং পপ-আপ দেয়।                                       #
#     - যদি জয়েন থাকে: একটি রোমান্টিক ওয়েলকাম পপ-আপ দেয় এবং ইনবক্সে নিয়ে যায়।                      #
#  ৪. ইনবক্সে বট অরিজিনাল আন-ব্লার ছবি এবং ভিডিও লিংক উপহার দেয়।                                   #
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
import traceback
import threading
import datetime
import signal
import uuid
import re
from typing import List, Dict, Any, Optional, Union, Set, Tuple
from enum import Enum, auto
from dataclasses import dataclass, field

# ==================================================================================================
# [ সেকশন ১ ] : সিস্টেম চেকিং এবং ডিপেন্ডেন্সি লোড
# ==================================================================================================

print(">>> [সিস্টেম] লাভ বট সিস্টেম চালু হচ্ছে...")
print(">>> [সিস্টেম] মডিউল লোড করা হচ্ছে...")

try:
    from telegram import (
        Update, 
        InlineKeyboardButton, 
        InlineKeyboardMarkup, 
        User,
        Chat,
        BotCommand,
        MenuButtonCommands,
        InputMediaPhoto,
        CallbackQuery
    )
    from telegram.constants import ParseMode, ChatAction, ChatType
    from telegram.ext import (
        ApplicationBuilder, 
        Application,
        CommandHandler, 
        CallbackQueryHandler, 
        MessageHandler, 
        ContextTypes, 
        ConversationHandler, 
        filters,
        Defaults,
        TypeHandler
    )
    from telegram.error import (
        TelegramError, 
        Forbidden, 
        BadRequest, 
        TimedOut, 
        NetworkError
    )
    print(">>> [সাকসেস] সকল লাইব্রেরি সফলভাবে লোড হয়েছে।")
except ImportError as e:
    print(f">>> [ত্রুটি] ক্রিটিকাল এরর: {e}")
    print(">>> [সমাধান] দয়া করে ইন্সটল করুন: pip install python-telegram-bot")
    sys.exit(1)

# ==================================================================================================
# [ সেকশন ২ ] : সিস্টেম কনফিগারেশন এবং বাংলা হট মেসেজ
# ==================================================================================================

class EnvConfig:
    """
    গ্লোবাল এনভায়রনমেন্ট কনফিগারেশন।
    এখানে সব সিক্রেট কি এবং বাংলা টেক্সট রাখা হয়েছে।
    """
    
    # -------------------------------------------------------------------------
    # ক্রেডেনশিয়ালস (অবশ্যই পরিবর্তন করবেন)
    # -------------------------------------------------------------------------
    BOT_TOKEN: str = "8456027249:AAEqg2j7jhJDSl4R0dnVCqaCvYBJQeG8NM4"
    
    # এডমিন আইডি (সংখ্যা হতে হবে)
    ADMIN_IDS: Set[int] = {6406804999}
    
    # -------------------------------------------------------------------------
    # ফাইল পাথ এবং সেটিংস
    # -------------------------------------------------------------------------
    DB_PATH: str = "supreme_love_v1.db"
    LOG_PATH: str = "love_audit.log"
    
    # মেম্বারশিপ চেক ক্যাশ টাইম (সেকেন্ড)
    CACHE_TTL: int = 300  
    
    # ওয়ার্নিং মেসেজ ডিলিট হওয়ার সময়
    AUTO_DELETE_DELAY: int = 25
    
    # -------------------------------------------------------------------------
    # কনভারসেশন স্টেট
    # -------------------------------------------------------------------------
    (
        WIZ_TITLE, WIZ_PHOTO, WIZ_TEXT, WIZ_BTN_MENU, 
        WIZ_BTN_NAME, WIZ_BTN_LINK, WIZ_TARGET,
        ADD_CH_ID, ADD_CH_NAME, ADD_CH_LINK
    ) = range(10)

    # -------------------------------------------------------------------------
    # 🔥 বাংলা হট লাভ মেসেজ কালেকশন (ROMANTIC & TEASING) 🔥
    # -------------------------------------------------------------------------
    
    # যখন ইউজার প্রথম স্টার্ট করবে
    MSG_WELCOME = (
        "💋 <b>ওহে হ্যান্ডসাম... {name}!</b>\n\n"
        "উফফ! অবশেষে তুমি এলে। আমি তোমার জন্যই অপেক্ষা করছিলাম সোনা। 😘\n\n"
        "আমি তোমার <b>পার্সোনাল প্লেজার অ্যাসিস্ট্যান্ট</b>। "
        "আমার কাছে এমন কিছু কালেকশন আছে যা দেখলে তোমার হৃদস্পন্দন বেড়ে যাবে... 🔥\n\n"
        "👇 <i>লজ্জা পেয়ো না, নিচের বাটনে চাপ দাও... আমি তৈরি আছি।</i>"
    )
    
    # চ্যানেলে পোস্টের ভেরিফাই বাটন টেক্সট
    BTN_VERIFY_TEXT = "🔥 আনলক করতে এখানে চাপ দাও সোনা 💋"
    
    # যখন ইউজার চ্যানেলে জয়েন না করে ভেরিফাই চাপবে (Teasing Alert)
    MSG_ACCESS_DENIED_POPUP = "আহ্! আস্তে... আগে জয়েন করো দুষ্টু ছেলে! 😈"
    
    # চ্যানেলে টেম্পোরারি ওয়ার্নিং মেসেজ
    MSG_ACCESS_DENIED_BODY = (
        "⛔ <b>উফফ! তুমি বড্ড তাড়াহুড়ো করছো!</b> ⛔\n\n"
        "প্রিয় {name}, তুমি এখনো আমার প্রাইভেট চ্যানেলে জয়েন করোনি কেন? 🥺\n"
        "তুমি যদি জয়েন না করো, তাহলে আমি তোমাকে আমার <b>স্পেশাল ভিডিওটা</b> দেখাবো না!\n\n"
        "👇 <b>প্লিজ সোনা, নিচে জয়েন করো। আমি অপেক্ষা করছি...</b>"
    )
    
    # যখন ভেরিফিকেশন সাকসেস হবে
    MSG_SUCCESS_REDIRECT = "উফফ দারুণ! চলো আমার বেডরুমে (ইনবক্সে) যাই... 🏃‍♂️💕"
    
    # ইনবক্সে ফাইনাল কন্টেন্ট ডেলিভারি মেসেজ
    MSG_CONTENT_HEADER = (
        "💖 <b>অবশেষে আমরা একা!</b> 💖\n\n"
        "কথা দিয়েছিলাম না তোমাকে খুশি করবো? এই নাও তোমার উপহার।\n"
        "একদম আনসেন্সরড এবং ক্লিয়ার... শুধু তোমার জন্য। উপভোগ করো জান! 💋🔥\n"
        "➖➖➖➖➖➖➖➖➖➖"
    )

# ==================================================================================================
# [ সেকশন ৩ ] : লগিং ম্যানেজার
# ==================================================================================================

class LogManager:
    """
    সিস্টেম লগিং কন্ট্রোলার।
    """
    _instance = None

    @staticmethod
    def get_logger():
        if LogManager._instance is None:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s | %(levelname)-8s | %(message)s',
                handlers=[
                    logging.FileHandler(EnvConfig.LOG_PATH, encoding='utf-8'),
                    logging.StreamHandler(sys.stdout)
                ]
            )
            logging.getLogger("httpx").setLevel(logging.WARNING)
            logging.getLogger("telegram").setLevel(logging.INFO)
            LogManager._instance = logging.getLogger("SupremeLoveBot")
        return LogManager._instance

logger = LogManager.get_logger()

# ==================================================================================================
# [ সেকশন ৪ ] : ডাটাবেস লেয়ার (SQLite3)
# ==================================================================================================

class DatabaseController:
    """
    ডাটাবেস কন্ট্রোলার। ব্যবহারকারীর তথ্য এবং চ্যানেলের ডাটা ম্যানেজ করে।
    """
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._initialize_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize_db(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            # ইউজার টেবিল
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            # চ্যানেল টেবিল
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS channels (
                    channel_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    invite_link TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            # পোস্ট টেবিল
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    photo_file_id TEXT,
                    caption TEXT,
                    buttons_json TEXT,
                    required_channels_json TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            logger.info("ডাটাবেস ইনিশিয়ালাইজেশন সম্পন্ন হয়েছে।")
        except Exception as e:
            logger.error(f"ডাটাবেস এরর: {e}")
        finally:
            conn.close()

    def upsert_user(self, user: User):
        conn = self._get_connection()
        try:
            conn.execute('''
                INSERT OR REPLACE INTO users (user_id, username, first_name)
                VALUES (?, ?, ?)
            ''', (user.id, user.username, user.first_name))
            conn.commit()
        except Exception as e:
            logger.error(f"ইউজার সেভ এরর: {e}")
        finally:
            conn.close()

    def add_channel(self, c_id, name, link):
        conn = self._get_connection()
        try:
            conn.execute('''
                INSERT OR REPLACE INTO channels (channel_id, name, invite_link, is_active)
                VALUES (?, ?, ?, 1)
            ''', (c_id, name, link))
            conn.commit()
            return True
        except Exception:
            return False
        finally:
            conn.close()

    def get_active_channels(self) -> List[Dict]:
        conn = self._get_connection()
        try:
            cursor = conn.execute("SELECT * FROM channels WHERE is_active = 1")
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def create_post(self, title, photo, caption, buttons, channels) -> int:
        conn = self._get_connection()
        try:
            cursor = conn.execute('''
                INSERT INTO posts (title, photo_file_id, caption, buttons_json, required_channels_json)
                VALUES (?, ?, ?, ?, ?)
            ''', (title, photo, caption, json.dumps(buttons), json.dumps(channels)))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"পোস্ট তৈরি এরর: {e}")
            return 0
        finally:
            conn.close()

    def get_post(self, post_id: int) -> Optional[Dict]:
        conn = self._get_connection()
        try:
            cursor = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
            row = cursor.fetchone()
            if row:
                d = dict(row)
                d['buttons'] = json.loads(d['buttons_json'])
                d['channels'] = json.loads(d['required_channels_json'])
                return d
            return None
        finally:
            conn.close()

db = DatabaseController(EnvConfig.DB_PATH)

# ==================================================================================================
# [ সেকশন ৫ ] : সিকিউরিটি এবং ভেরিফিকেশন গার্ড
# ==================================================================================================

class SecurityGuard:
    """
    মেম্বারশিপ চেক এবং ক্যাশিং সিস্টেম।
    """
    def __init__(self):
        self._cache = {}
        self._lock = threading.Lock()

    async def check_membership(self, user_id: int, bot: Application, required_ids: List[str]) -> List[Dict]:
        # ১. ক্যাশ চেক করা
        current_time = time.time()
        with self._lock:
            if user_id in self._cache:
                if current_time - self._cache[user_id]['time'] < EnvConfig.CACHE_TTL:
                    return self._cache[user_id]['missing']

        # ২. লাইভ এপিআই চেক
        db_channels = {ch['channel_id']: ch for ch in db.get_active_channels()}
        missing = []
        
        for ch_id in required_ids:
            if ch_id not in db_channels: continue
            
            try:
                member = await bot.get_chat_member(chat_id=ch_id, user_id=user_id)
                if member.status in ['left', 'kicked', 'banned']:
                    missing.append(db_channels[ch_id])
            except BadRequest:
                missing.append(db_channels[ch_id]) # বট এডমিন না থাকলে
            except Exception:
                missing.append(db_channels[ch_id])

        # ৩. ক্যাশ আপডেট
        with self._lock:
            self._cache[user_id] = {'time': current_time, 'missing': missing}
        
        return missing

    def clear_cache(self, user_id: int):
        with self._lock:
            if user_id in self._cache:
                del self._cache[user_id]

security = SecurityGuard()

# ==================================================================================================
# [ সেকশন ৬ ] : এডমিন উইজার্ড (পোস্ট তৈরি)
# ==================================================================================================

class AdminWizard:
    """
    এডমিনদের জন্য পোস্ট তৈরির অটোমেটেড সিস্টেম।
    """
    
    # --- পোস্ট ক্রিয়েশন ---
    @staticmethod
    async def start_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        context.user_data['post'] = {'buttons': []}
        await query.message.reply_text("📝 <b>ধাপ ১: পোস্টের একটি হট টাইটেল দিন:</b>", parse_mode=ParseMode.HTML)
        return EnvConfig.WIZ_TITLE

    @staticmethod
    async def get_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data['post']['title'] = update.message.text
        await update.message.reply_text("📸 <b>ধাপ ২: একটি আকর্ষণীয় ছবি (Cover Photo) দিন:</b>", parse_mode=ParseMode.HTML)
        return EnvConfig.WIZ_PHOTO

    @staticmethod
    async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message.photo:
            await update.message.reply_text("❌ দয়া করে একটি ছবি পাঠান।")
            return EnvConfig.WIZ_PHOTO
        
        context.user_data['post']['photo'] = update.message.photo[-1].file_id
        await update.message.reply_text("💬 <b>ধাপ ৩: ক্যাপশন দিন (অথবা /skip লিখুন):</b>", parse_mode=ParseMode.HTML)
        return EnvConfig.WIZ_TEXT

    @staticmethod
    async def get_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text
        context.user_data['post']['caption'] = "" if text == '/skip' else text
        return await AdminWizard.render_buttons(update, context)

    @staticmethod
    async def render_buttons(update, context):
        buttons = context.user_data['post']['buttons']
        msg = f"🔘 <b>ধাপ ৪: বাটন ম্যানেজমেন্ট</b>\nযুক্ত হয়েছে: {len(buttons)} টি\n"
        for b in buttons: msg += f"▫️ {b['name']} -> {b['link']}\n"
            
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ বাটন যুক্ত করুন", callback_data="add_btn")],
            [InlineKeyboardButton("✅ পোস্ট করুন", callback_data="finish")]
        ])
        
        if update.callback_query:
            await update.callback_query.message.edit_text(msg, reply_markup=kb, parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(msg, reply_markup=kb, parse_mode=ParseMode.HTML)
        return EnvConfig.WIZ_BTN_MENU

    @staticmethod
    async def menu_callback(update, context):
        query = update.callback_query
        if query.data == "add_btn":
            await query.message.reply_text("✏️ বাটনের নাম লিখুন:")
            return EnvConfig.WIZ_BTN_NAME
        elif query.data == "finish":
            channels = db.get_active_channels()
            if not channels:
                await query.message.reply_text("❌ ডাটাবেসে কোনো চ্যানেল পাওয়া যায়নি।")
                return ConversationHandler.END
            
            kb = [[InlineKeyboardButton(f"📢 {ch['name']}", callback_data=f"tgt_{ch['channel_id']}")] for ch in channels]
            await query.message.edit_text("📤 <b>ধাপ ৫: কোন চ্যানেলে পোস্ট করবেন?</b>", reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)
            return EnvConfig.WIZ_TARGET

    @staticmethod
    async def btn_name(update, context):
        context.user_data['temp'] = update.message.text
        await update.message.reply_text("🔗 বাটনের লিংক দিন:")
        return EnvConfig.WIZ_BTN_LINK

    @staticmethod
    async def btn_link(update, context):
        context.user_data['post']['buttons'].append({
            'name': context.user_data['temp'], 'link': update.message.text
        })
        return await AdminWizard.render_buttons(update, context)

    @staticmethod
    async def finalize(update, context):
        query = update.callback_query
        target = query.data.replace("tgt_", "")
        data = context.user_data['post']
        
        # ডাটাবেসে সেভ
        channels = [ch['channel_id'] for ch in db.get_active_channels()]
        pid = db.create_post(data['title'], data['photo'], data['caption'], data['buttons'], channels)
        
        # ভেরিফাই বাটন
        verify_kb = InlineKeyboardMarkup([[
            InlineKeyboardButton(EnvConfig.BTN_VERIFY_TEXT, callback_data=f"verify_{pid}")
        ]])
        
        # পাবলিক ক্যাপশন (টিজার)
        public_caption = (
            f"<b>{data['title']}</b>\n\n"
            f"{data['caption'][:60]}...\n\n"
            f"🔒 <b>এই কন্টেন্টটি লক করা আছে!</b>\n"
            f"<i>ভিতরের দৃশ্য দেখতে নিচের বাটনে চাপ দিয়ে ভেরিফাই করুন।</i> 🔥"
        )
        
        try:
            # ব্লার বা স্পয়লার ইফেক্ট সহ পাঠানো
            await context.bot.send_photo(
                chat_id=target,
                photo=data['photo'],
                caption=public_caption,
                reply_markup=verify_kb,
                has_spoiler=True,  # <--- ব্লার ফিচার
                parse_mode=ParseMode.HTML
            )
            await query.message.edit_text(f"✅ <b>সফলভাবে পোস্ট করা হয়েছে!</b>\nID: {pid}")
        except Exception as e:
            await query.message.edit_text(f"❌ এরর: {e}")
            
        return ConversationHandler.END

    # --- চ্যানেল অ্যাড ---
    @staticmethod
    async def ch_start(update, context):
        await update.callback_query.message.reply_text("🆔 চ্যানেলের আইডি দিন (যেমন: -100...):")
        return EnvConfig.ADD_CH_ID
    @staticmethod
    async def ch_id(update, context):
        context.user_data['cid'] = update.message.text
        await update.message.reply_text("📝 চ্যানেলের নাম দিন:")
        return EnvConfig.ADD_CH_NAME
    @staticmethod
    async def ch_name(update, context):
        context.user_data['cname'] = update.message.text
        await update.message.reply_text("🔗 চ্যানেলের ইনভাইট লিংক দিন:")
        return EnvConfig.ADD_CH_LINK
    @staticmethod
    async def ch_link(update, context):
        db.add_channel(context.user_data['cid'], context.user_data['cname'], update.message.text)
        await update.message.reply_text("✅ চ্যানেল সফলভাবে অ্যাড হয়েছে!")
        return ConversationHandler.END

# ==================================================================================================
# [ সেকশন ৭ ] : ইউজার হ্যান্ডলিং (ভেরিফিকেশন ও রিডাইরেক্ট)
# ==================================================================================================

async def verify_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    ইউজার যখন 'আনলক' বাটনে চাপ দেয়।
    """
    query = update.callback_query
    user = query.from_user
    
    # ইউজার রেজিস্টার
    db.upsert_user(user)
    
    try:
        pid = int(query.data.replace("verify_", ""))
    except:
        await query.answer("❌ এরর!", show_alert=True)
        return

    post = db.get_post(pid)
    if not post:
        await query.answer("❌ কন্টেন্ট পাওয়া যাচ্ছে না।", show_alert=True)
        return

    # মেম্বারশিপ চেক
    missing = await security.check_membership(user.id, context.bot, post['channels'])
    
    # কেইস ১: জয়েন করেনি (Access Denied)
    if missing:
        # দুষ্টু অ্যালার্ট
        await query.answer(EnvConfig.MSG_ACCESS_DENIED_POPUP, show_alert=True)
        
        # জয়েন বাটন
        btns = [[InlineKeyboardButton(f"📢 জয়েন করো: {ch['name']}", url=ch['invite_link'])] for ch in missing]
        btns.append([InlineKeyboardButton("🔄 চেক করুন", callback_data=f"verify_{pid}")])
        
        try:
            msg = await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=EnvConfig.MSG_ACCESS_DENIED_BODY.format(name=user.first_name),
                reply_to_message_id=query.message.message_id,
                reply_markup=InlineKeyboardMarkup(btns),
                parse_mode=ParseMode.HTML
            )
            asyncio.create_task(delete_later(msg))
        except: pass
        return

    # কেইস ২: ভেরিফাইড -> রিডাইরেক্ট
    security.clear_cache(user.id)
    bot_url = f"https://t.me/{context.bot.username}?start=show_{pid}"
    await query.answer(EnvConfig.MSG_SUCCESS_REDIRECT, show_alert=False, url=bot_url)


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /start কমান্ড এবং ডিপ লিংক হ্যান্ডলার।
    """
    user = update.effective_user
    db.upsert_user(user)
    args = context.args
    
    if not args:
        await update.message.reply_text(
            EnvConfig.MSG_WELCOME.format(name=user.first_name),
            parse_mode=ParseMode.HTML
        )
        return

    payload = args[0]
    if payload.startswith("show_"):
        try:
            pid = int(payload.replace("show_", ""))
            post = db.get_post(pid)
            if not post: return
            
            # ডাবল চেক (সিকিউরিটি)
            missing = await security.check_membership(user.id, context.bot, post['channels'])
            if missing:
                await update.message.reply_text("⛔ চালাকি করো না সোনা! আগে চ্যানেলে জয়েন করো।")
                return
            
            # --- ডেলিভারি ---
            # অরিজিনাল বাটন রিস্টোর
            real_btns = [[InlineKeyboardButton(b['name'], url=b['link'])] for b in post['buttons']]
            
            # ফাইনাল মেসেজ
            final_caption = (
                f"{EnvConfig.MSG_CONTENT_HEADER}\n"
                f"🎬 <b>{post['title']}</b>\n\n"
                f"{post['caption']}"
            )
            
            # আন-ব্লার ছবি পাঠানো
            await context.bot.send_photo(
                chat_id=user.id,
                photo=post['photo_file_id'],
                caption=final_caption,
                reply_markup=InlineKeyboardMarkup(real_btns),
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"ডিপ লিংক এরর: {e}")

# ==================================================================================================
# [ সেকশন ৮ ] : ইউটিলিটি এবং এডমিন প্যানেল
# ==================================================================================================

async def delete_later(msg):
    await asyncio.sleep(EnvConfig.AUTO_DELETE_DELAY)
    try: await msg.delete()
    except: pass

async def admin_panel(update, context):
    if update.effective_user.id not in EnvConfig.ADMIN_IDS: return
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 নতুন পোস্ট তৈরি করুন", callback_data="wiz_post")],
        [InlineKeyboardButton("➕ চ্যানেল যুক্ত করুন", callback_data="wiz_ch")]
    ])
    await update.message.reply_text(EnvConfig.MSG_ADMIN_PANEL, reply_markup=kb, parse_mode=ParseMode.HTML)

async def cancel(update, context):
    await update.message.reply_text("🚫 বাতিল করা হয়েছে।")
    return ConversationHandler.END

# ==================================================================================================
# [ সেকশন ৯ ] : মেইন অ্যাপ্লিকেশন রানার
# ==================================================================================================

def main():
    print(">>> [বট] লাভ বট চালু হচ্ছে...")
    app = ApplicationBuilder().token(EnvConfig.BOT_TOKEN).build()

    # উইজার্ড হ্যান্ডলারস
    post_h = ConversationHandler(
        entry_points=[CallbackQueryHandler(AdminWizard.start_post, pattern='^wiz_post$')],
        states={
            EnvConfig.WIZ_TITLE: [MessageHandler(filters.TEXT, AdminWizard.get_title)],
            EnvConfig.WIZ_PHOTO: [MessageHandler(filters.PHOTO, AdminWizard.get_photo)],
            EnvConfig.WIZ_TEXT: [MessageHandler(filters.TEXT, AdminWizard.get_text)],
            EnvConfig.WIZ_BTN_MENU: [CallbackQueryHandler(AdminWizard.menu_callback)],
            EnvConfig.WIZ_BTN_NAME: [MessageHandler(filters.TEXT, AdminWizard.btn_name)],
            EnvConfig.WIZ_BTN_LINK: [MessageHandler(filters.TEXT, AdminWizard.btn_link)],
            EnvConfig.WIZ_TARGET: [CallbackQueryHandler(AdminWizard.finalize, pattern='^tgt_')]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    ch_h = ConversationHandler(
        entry_points=[CallbackQueryHandler(AdminWizard.ch_start, pattern='^wiz_ch$')],
        states={
            EnvConfig.ADD_CH_ID: [MessageHandler(filters.TEXT, AdminWizard.ch_id)],
            EnvConfig.ADD_CH_NAME: [MessageHandler(filters.TEXT, AdminWizard.ch_name)],
            EnvConfig.ADD_CH_LINK: [MessageHandler(filters.TEXT, AdminWizard.ch_link)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # হ্যান্ডলার রেজিস্টার
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(post_h)
    app.add_handler(ch_h)
    app.add_handler(CallbackQueryHandler(verify_handler, pattern='^verify_'))

    print(">>> [বট] অনলাইনে আছে।")
    app.run_polling()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
