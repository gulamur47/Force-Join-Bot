"""
================================================================================
SUPREME GOD MODE BOT - ULTIMATE EDITION (100 FEATURES)
VERSION: v10.0 (Enterprise Grade)
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
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import List, Dict, Union, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import traceback
import pickle
import base64
from contextlib import contextmanager
from collections import defaultdict, deque
import pytz
import calendar
import csv
import io
from pathlib import Path

# Telegram imports
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    InputMediaPhoto, InputMediaVideo, BotCommand, Bot
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
    DB_NAME = "supreme_bot_v10.db"
    BACKUP_DIR = "backups"
    LOG_FILE = "bot_activity.log"
    BOT_NAME = "Supreme God Bot v10.0"
    BOT_USERNAME = "@SupremeGodBot"
    
    # Timezone Configuration
    TIMEZONE = pytz.timezone('Asia/Dhaka')
    BANGLA_MONTHS = [
        "বৈশাখ", "জ্যৈষ্ঠ", "আষাঢ়", "শ্রাবণ", 
        "ভাদ্র", "আশ্বিন", "কার্তিক", "অগ্রহায়ণ", 
        "পৌষ", "মাঘ", "ফাল্গুন", "চৈত্র"
    ]
    
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
    
    # Emoji Pack - Enhanced with more emojis
    EMOJIS = {
        # Basic emojis
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
        
        # New emojis for better UI
        "tada": "🎉",
        "confetti": "🎊",
        "medal": "🏅",
        "trophy": "🏆",
        "diamond": "💎",
        "sparkles": "✨",
        "rainbow": "🌈",
        "clap": "👏",
        "muscle": "💪",
        "brain": "🧠",
        "light": "💡",
        "key": "🔑",
        "mag": "🔍",
        "phone": "📱",
        "comp": "💻",
        "disk": "💿",
        "mail": "📧",
        "book": "📚",
        "note": "📝",
        "cal": "📅",
        "clock": "🕒",
        "stopwatch": "⏱️",
        "timer": "⏲️",
        "alarm": "⏰",
        "bell": "🔔",
        "mute": "🔇",
        "sound": "🔊",
        "vol": "🔉",
        "loud": "🔈",
        "mike": "🎤",
        "headphone": "🎧",
        "radio": "📻",
        "sat": "📡",
        "battery": "🔋",
        "electric": "⚡",
        "bomb": "💣",
        "pill": "💊",
        "syringe": "💉",
        "door": "🚪",
        "bed": "🛏️",
        "chair": "🪑",
        "toilet": "🚽",
        "shower": "🚿",
        "bathtub": "🛁",
        "razor": "🪒",
        "lotion": "🧴",
        "safety": "🧷",
        "broom": "🧹",
        "basket": "🧺",
        "roll": "🧻",
        "soap": "🧼",
        "sponge": "🧽",
        "fire": "🔥",
        "water": "💧",
        "wave": "🌊",
        "mountain": "⛰️",
        "volcano": "🌋",
        "island": "🏝️",
        "desert": "🏜️",
        "park": "🏞️",
        "stadium": "🏟️",
        "house": "🏠",
        "office": "🏢",
        "post": "🏣",
        "hospital": "🏥",
        "bank": "🏦",
        "hotel": "🏨",
        "store": "🏪",
        "school": "🏫",
        "factory": "🏭",
        "castle": "🏰",
        "wedding": "💒",
        "tokyo": "🗼",
        "statue": "🗽",
        "church": "⛪",
        "mosque": "🕌",
        "synagogue": "🕍",
        "shrine": "⛩️",
        "kaaba": "🕋",
        "fountain": "⛲",
        "tent": "⛺",
        "fog": "🌁",
        "night": "🌃",
        "sunrise": "🌅",
        "sunset": "🌇",
        "bridge": "🌉",
        "carousel": "🎠",
        "ferris": "🎡",
        "coaster": "🎢",
        "boat": "⛵",
        "ship": "🚢",
        "plane": "✈️",
        "rocket": "🚀",
        "helicopter": "🚁",
        "steam": "🚂",
        "train": "🚆",
        "metro": "🚇",
        "tram": "🚊",
        "bus": "🚌",
        "ambulance": "🚑",
        "fire_engine": "🚒",
        "police": "🚓",
        "taxi": "🚕",
        "car": "🚗",
        "truck": "🚚",
        "bike": "🚲",
        "fuel": "⛽",
        "light": "🚦",
        "sign": "🚧",
        "construction": "🚧",
        "anchor": "⚓",
        "sail": "⛵",
        "wheel": "🛞",
        "bellhop": "🛎️",
        "luggage": "🧳",
        "hourglass": "⏳",
        "watch": "⌚",
        "alarm": "⏰",
        "stopwatch": "⏱️",
        "timer": "⏲️",
        "calendar": "📅",
        "date": "📆",
        "card": "🗃️",
        "file": "📁",
        "folder": "📂",
        "clipboard": "📋",
        "pushpin": "📌",
        "pin": "📍",
        "round_pushpin": "📍",
        "paperclip": "📎",
        "straight_ruler": "📏",
        "triangular_ruler": "📐",
        "scissors": "✂️",
        "card_box": "🗃️",
        "file_cabinet": "🗄️",
        "wastebasket": "🗑️",
        "lock": "🔒",
        "unlock": "🔓",
        "lock_with_ink": "🔏",
        "closed_lock": "🔐",
        "key": "🔑",
        "old_key": "🗝️",
        "hammer": "🔨",
        "axe": "🪓",
        "pick": "⛏️",
        "hammer_pick": "⚒️",
        "hammer_wrench": "🛠️",
        "dagger": "🗡️",
        "crossed_swords": "⚔️",
        "gun": "🔫",
        "bow_arrow": "🏹",
        "shield": "🛡️",
        "wrench": "🔧",
        "nut_bolt": "🔩",
        "gear": "⚙️",
        "clamp": "🗜️",
        "balance": "⚖️",
        "probing_cane": "🦯",
        "link": "🔗",
        "chains": "⛓️",
        "hook": "🪝",
        "toolbox": "🧰",
        "magnet": "🧲",
        "ladder": "🪜",
        "alembic": "⚗️",
        "test_tube": "🧪",
        "petri_dish": "🧫",
        "dna": "🧬",
        "microscope": "🔬",
        "telescope": "🔭",
        "satellite": "📡",
        "syringe": "💉",
        "drop": "💧",
        "pill": "💊",
        "adhesive": "🩹",
        "stethoscope": "🩺",
        "door": "🚪",
        "elevator": "🛗",
        "mirror": "🪞",
        "window": "🪟",
        "bed": "🛏️",
        "couch": "🛋️",
        "chair": "🪑",
        "toilet": "🚽",
        "plunger": "🪠",
        "shower": "🚿",
        "bathtub": "🛁",
        "mouse_trap": "🪤",
        "razor": "🪒",
        "lotion": "🧴",
        "safety_pin": "🧷",
        "broom": "🧹",
        "basket": "🧺",
        "roll": "🧻",
        "soap": "🧼",
        "sponge": "🧽",
        "fire_extinguisher": "🧯",
        "shopping_cart": "🛒",
        "cigarette": "🚬",
        "coffin": "⚰️",
        "headstone": "🪦",
        "urn": "⚱️",
        "moyai": "🗿",
        "placard": "🪧",
        "atm": "🏧",
        "put_litter": "🚮",
        "potable_water": "🚰",
        "wheelchair": "♿",
        "mens": "🚹",
        "womens": "🚺",
        "restroom": "🚻",
        "baby": "🚼",
        "wc": "🚾",
        "passport": "🛂",
        "customs": "🛃",
        "baggage": "🛄",
        "left_luggage": "🛅",
        "warning": "⚠️",
        "children": "🚸",
        "no_entry": "⛔",
        "no_entry2": "🚫",
        "no_bicycles": "🚳",
        "no_smoking": "🚭",
        "do_not_litter": "🚯",
        "non-potable_water": "🚱",
        "no_pedestrians": "🚷",
        "no_mobile": "📵",
        "underage": "🔞",
        "radioactive": "☢️",
        "biohazard": "☣️",
        "arrow_up": "⬆️",
        "arrow_down": "⬇️",
        "arrow_left": "⬅️",
        "arrow_right": "➡️",
        "arrow_upper_right": "↗️",
        "arrow_lower_right": "↘️",
        "arrow_lower_left": "↙️",
        "arrow_upper_left": "↖️",
        "arrow_up_down": "↕️",
        "left_right_arrow": "↔️",
        "leftwards_arrow": "⬅️",
        "rightwards_arrow": "➡️",
        "arrow_right_hook": "↪️",
        "leftwards_arrow_hook": "↩️",
        "arrow_heading_up": "⤴️",
        "arrow_heading_down": "⤵️",
        "arrows_clockwise": "🔃",
        "arrows_counterclockwise": "🔄",
        "back": "🔙",
        "end": "🔚",
        "on": "🔛",
        "soon": "🔜",
        "top": "🔝",
        "place_of_worship": "🛐",
        "atom": "⚛️",
        "om": "🕉️",
        "star_of_david": "✡️",
        "wheel_of_dharma": "☸️",
        "yin_yang": "☯️",
        "latin_cross": "✝️",
        "orthodox_cross": "☦️",
        "star_and_crescent": "☪️",
        "peace": "☮️",
        "menorah": "🕎",
        "six_pointed_star": "🔯",
        "aries": "♈",
        "taurus": "♉",
        "gemini": "♊",
        "cancer": "♋",
        "leo": "♌",
        "virgo": "♍",
        "libra": "♎",
        "scorpius": "♏",
        "sagittarius": "♐",
        "capricorn": "♑",
        "aquarius": "♒",
        "pisces": "♓",
        "ophiuchus": "⛎",
        "twisted_rightwards_arrows": "🔀",
        "repeat": "🔁",
        "repeat_one": "🔂",
        "arrow_forward": "▶️",
        "fast_forward": "⏩",
        "next_track": "⏭️",
        "play_pause": "⏯️",
        "arrow_backward": "◀️",
        "rewind": "⏪",
        "previous_track": "⏮️",
        "arrow_up_small": "🔼",
        "arrow_double_up": "⏫",
        "arrow_down_small": "🔽",
        "arrow_double_down": "⏬",
        "pause_button": "⏸️",
        "stop_button": "⏹️",
        "record_button": "⏺️",
        "eject": "⏏️",
        "cinema": "🎦",
        "low_brightness": "🔅",
        "high_brightness": "🔆",
        "signal_strength": "📶",
        "vibration_mode": "📳",
        "mobile_phone_off": "📴",
        "female_sign": "♀️",
        "male_sign": "♂️",
        "medical_symbol": "⚕️",
        "infinity": "♾️",
        "recycle": "♻️",
        "fleur_de_lis": "⚜️",
        "trident": "🔱",
        "name_badge": "📛",
        "beginner": "🔰",
        "o": "⭕",
        "white_check_mark": "✅",
        "ballot_box_with_check": "☑️",
        "heavy_check_mark": "✔️",
        "heavy_multiplication_x": "✖️",
        "x": "❌",
        "negative_squared_cross_mark": "❎",
        "heavy_plus_sign": "➕",
        "heavy_minus_sign": "➖",
        "heavy_division_sign": "➗",
        "curly_loop": "➰",
        "loop": "➿",
        "part_alternation_mark": "〽️",
        "eight_spoked_asterisk": "✳️",
        "eight_pointed_black_star": "✴️",
        "sparkle": "❇️",
        "copyright": "©️",
        "registered": "®️",
        "tm": "™️",
        "hash": "#️⃣",
        "asterisk": "*️⃣",
        "zero": "0️⃣",
        "one": "1️⃣",
        "two": "2️⃣",
        "three": "3️⃣",
        "four": "4️⃣",
        "five": "5️⃣",
        "six": "6️⃣",
        "seven": "7️⃣",
        "eight": "8️⃣",
        "nine": "9️⃣",
        "keycap_ten": "🔟",
        "100": "💯",
        "capital_abcd": "🔠",
        "abcd": "🔡",
        "1234": "🔢",
        "symbols": "🔣",
        "abc": "🔤",
        "a": "🅰️",
        "ab": "🆎",
        "b": "🅱️",
        "cl": "🆑",
        "cool": "🆒",
        "free": "🆓",
        "information_source": "ℹ️",
        "id": "🆔",
        "m": "Ⓜ️",
        "new": "🆕",
        "ng": "🆖",
        "o2": "🅾️",
        "ok": "🆗",
        "parking": "🅿️",
        "sos": "🆘",
        "up": "🆙",
        "vs": "🆚",
        "koko": "🈁",
        "sa": "🈂️",
        "u6708": "🈷️",
        "u6709": "🈶",
        "u6307": "🈯",
        "ideograph_advantage": "🉐",
        "u5272": "🈹",
        "u7121": "🈚",
        "u7981": "🈲",
        "accept": "🉑",
        "u7533": "🈸",
        "u5408": "🈴",
        "u7a7a": "🈳",
        "congratulations": "㊗️",
        "secret": "㊙️",
        "u55b6": "🈺",
        "u6e80": "🈵",
        "red_circle": "🔴",
        "orange_circle": "🟠",
        "yellow_circle": "🟡",
        "green_circle": "🟢",
        "large_blue_circle": "🔵",
        "purple_circle": "🟣",
        "brown_circle": "🟤",
        "black_circle": "⚫",
        "white_circle": "⚪",
        "red_square": "🟥",
        "orange_square": "🟧",
        "yellow_square": "🟨",
        "green_square": "🟩",
        "blue_square": "🟦",
        "purple_square": "🟪",
        "brown_square": "🟫",
        "black_large_square": "⬛",
        "white_large_square": "⬜",
        "black_medium_square": "◼️",
        "white_medium_square": "◻️",
        "black_medium_small_square": "◾",
        "white_medium_small_square": "◽",
        "black_small_square": "▪️",
        "white_small_square": "▫️",
        "large_orange_diamond": "🔶",
        "large_blue_diamond": "🔷",
        "small_orange_diamond": "🔸",
        "small_blue_diamond": "🔹",
        "small_red_triangle": "🔺",
        "small_red_triangle_down": "🔻",
        "diamond_with_a_dot": "💠",
        "radio_button": "🔘",
        "white_square_button": "🔳",
        "black_square_button": "🔲",
        "speaker": "🔈",
        "sound": "🔉",
        "loud_sound": "🔊",
        "mute": "🔇",
        "mega": "📣",
        "loudspeaker": "📢",
        "bell": "🔔",
        "no_bell": "🔕",
        "musical_note": "🎵",
        "notes": "🎶",
        "chart_with_upwards_trend": "📈",
        "chart_with_downwards_trend": "📉",
        "bar_chart": "📊",
        "clipboard": "📋",
        "pushpin": "📌",
        "round_pushpin": "📍",
        "paperclip": "📎",
        "paperclips": "🖇️",
        "straight_ruler": "📏",
        "triangular_ruler": "📐",
        "scissors": "✂️",
        "card_file_box": "🗃️",
        "file_cabinet": "🗄️",
        "wastebasket": "🗑️",
        "lock": "🔒",
        "unlock": "🔓",
        "lock_with_ink_pen": "🔏",
        "closed_lock_with_key": "🔐",
        "key": "🔑",
        "old_key": "🗝️",
        "hammer": "🔨",
        "axe": "🪓",
        "pick": "⛏️",
        "hammer_and_pick": "⚒️",
        "hammer_and_wrench": "🛠️",
        "dagger": "🗡️",
        "crossed_swords": "⚔️",
        "gun": "🔫",
        "bow_and_arrow": "🏹",
        "shield": "🛡️",
        "wrench": "🔧",
        "nut_and_bolt": "🔩",
        "gear": "⚙️",
        "clamp": "🗜️",
        "balance_scale": "⚖️",
        "probing_cane": "🦯",
        "link": "🔗",
        "chains": "⛓️",
        "hook": "🪝",
        "toolbox": "🧰",
        "magnet": "🧲",
        "ladder": "🪜",
        "alembic": "⚗️",
        "test_tube": "🧪",
        "petri_dish": "🧫",
        "dna": "🧬",
        "microscope": "🔬",
        "telescope": "🔭",
        "satellite": "📡",
        "syringe": "💉",
        "drop_of_blood": "🩸",
        "pill": "💊",
        "adhesive_bandage": "🩹",
        "stethoscope": "🩺",
        "door": "🚪",
        "elevator": "🛗",
        "mirror": "🪞",
        "window": "🪟",
        "bed": "🛏️",
        "couch_and_lamp": "🛋️",
        "chair": "🪑",
        "toilet": "🚽",
        "plunger": "🪠",
        "shower": "🚿",
        "bathtub": "🛁",
        "mouse_trap": "🪤",
        "razor": "🪒",
        "lotion_bottle": "🧴",
        "safety_pin": "🧷",
        "broom": "🧹",
        "basket": "🧺",
        "roll_of_paper": "🧻",
        "soap": "🧼",
        "sponge": "🧽",
        "fire_extinguisher": "🧯",
        "shopping_cart": "🛒",
        "smoking": "🚬",
        "coffin": "⚰️",
        "headstone": "🪦",
        "funeral_urn": "⚱️",
        "moyai": "🗿",
        "placard": "🪧"
    }
    
    # Conversation States
    STATE_EDIT_CONFIG = 1
    STATE_POST_CAPTION = 2
    STATE_POST_MEDIA = 3
    STATE_POST_BUTTON = 4
    STATE_POST_BUTTON_URL = 5
    STATE_POST_CONFIRM = 6
    STATE_BROADCAST = 7
    STATE_CHANNEL_ADD_ID = 8
    STATE_CHANNEL_ADD_NAME = 9
    STATE_CHANNEL_ADD_LINK = 10
    STATE_USER_BLOCK = 11
    STATE_VIP_ADD = 12
    STATE_BACKUP_RESTORE = 13
    STATE_CHANNEL_EDIT = 14
    STATE_CHANNEL_EDIT_NAME = 15
    STATE_CHANNEL_EDIT_LINK = 16
    STATE_CHANNEL_EDIT_STATUS = 17
    STATE_POST_WIZARD = 18
    STATE_CHANNEL_BULK_ADD = 19

# ==============================================================================
# 📝 ENHANCED LOGGING SYSTEM WITH ASCII ART
# ==============================================================================

class SupremeLogger:
    def __init__(self):
        self.logger = logging.getLogger("SupremeBot")
        self.ascii_art = """
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║  ███████╗██╗   ██╗██████╗ ██████╗ ███████╗███╗   ███╗  ║
║  ██╔════╝██║   ██║██╔══██╗██╔══██╗██╔════╝████╗ ████║  ║
║  ███████╗██║   ██║██████╔╝██████╔╝█████╗  ██╔████╔██║  ║
║  ╚════██║██║   ██║██╔═══╝ ██╔═══╝ ██╔══╝  ██║╚██╔╝██║  ║
║  ███████║╚██████╔╝██║     ██║     ███████╗██║ ╚═╝ ██║  ║
║  ╚══════╝ ╚═════╝ ╚═╝     ╚═╝     ╚══════╝╚═╝     ╚═╝  ║
║                                                          ║
║  ██████╗  ██████╗ ████████╗   v10.0                     ║
║  ██╔══██╗██╔═══██╗╚══██╔══╝   Ultimate Edition          ║
║  ██████╔╝██║   ██║   ██║      100 Features              ║
║  ██╔══██╗██║   ██║   ██║      Bangladesh Timezone       ║
║  ██████╔╝╚██████╔╝   ██║      © 2024 Supreme Team       ║
║  ╚═════╝  ╚═════╝    ╚═╝                                ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
        """
        self.setup_logging()
        
    def setup_logging(self):
        # Create handlers
        console_handler = logging.StreamHandler(sys.stdout)
        file_handler = logging.FileHandler(Config.LOG_FILE, encoding='utf-8')
        error_handler = logging.FileHandler('errors.log', encoding='utf-8')
        
        # Create colorful formatter for console
        class ColorFormatter(logging.Formatter):
            COLORS = {
                'DEBUG': '\033[94m',      # Blue
                'INFO': '\033[92m',       # Green
                'WARNING': '\033[93m',    # Yellow
                'ERROR': '\033[91m',      # Red
                'CRITICAL': '\033[95m',   # Magenta
                'RESET': '\033[0m'        # Reset
            }
            
            def format(self, record):
                levelname = record.levelname
                if levelname in self.COLORS:
                    record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
                    record.msg = f"{self.COLORS[levelname]}{record.msg}{self.COLORS['RESET']}"
                return super().format(record)
        
        # Set levels
        console_handler.setLevel(logging.INFO)
        file_handler.setLevel(logging.DEBUG)
        error_handler.setLevel(logging.ERROR)
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s'
        )
        color_formatter = ColorFormatter(
            '%(asctime)s | %(levelname)s | %(message)s'
        )
        
        # Set formatters
        console_handler.setFormatter(color_formatter)
        file_handler.setFormatter(detailed_formatter)
        error_handler.setFormatter(detailed_formatter)
        
        # Add handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)
        self.logger.setLevel(logging.DEBUG)
        
        # Log startup with ASCII art
        print(self.ascii_art)
        self.logger.info("=" * 80)
        self.logger.info("SUPREME GOD BOT v10.0 STARTING...")
        self.logger.info(f"Bot Name: {Config.BOT_NAME}")
        self.logger.info(f"Timezone: {Config.TIMEZONE}")
        self.logger.info("=" * 80)
    
    def get_logger(self):
        return self.logger

logger_instance = SupremeLogger()
logger = logger_instance.get_logger()

# ==============================================================================
# 🗄️ ENHANCED DATABASE MANAGER WITH NEW FEATURES
# ==============================================================================

class DatabaseManager:
    """Enhanced multi-threaded database manager with encryption and backup"""
    
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
        self.cache = {}
        self.setup_directories()
        self.connection_pool = {}
        self.init_database()
        self._initialized = True
        
    def setup_directories(self):
        """Create necessary directories"""
        os.makedirs(self.backup_dir, exist_ok=True)
        os.makedirs('media', exist_ok=True)
        os.makedirs('templates', exist_ok=True)
        os.makedirs('exports', exist_ok=True)
        
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
        
        # Users table with enhanced tracking
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
                language_code TEXT DEFAULT 'en',
                timezone TEXT DEFAULT 'Asia/Dhaka',
                metadata TEXT DEFAULT '{}',
                activity_score INTEGER DEFAULT 0,
                last_command TEXT,
                daily_usage INTEGER DEFAULT 0
            )
        ''')
        
        # Enhanced config table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                encrypted BOOLEAN DEFAULT 0,
                category TEXT DEFAULT 'general',
                description TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_by INTEGER,
                version INTEGER DEFAULT 1
            )
        ''')
        
        # Enhanced channels table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS channels (
                channel_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                link TEXT NOT NULL,
                is_private BOOLEAN DEFAULT 0,
                force_join BOOLEAN DEFAULT 1,
                added_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_checked DATETIME,
                status TEXT DEFAULT 'active',
                category TEXT DEFAULT 'general',
                priority INTEGER DEFAULT 0,
                post_count INTEGER DEFAULT 0,
                last_post_date DATETIME,
                metadata TEXT DEFAULT '{}'
            )
        ''')
        
        # Enhanced posts history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                post_id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id TEXT,
                post_type TEXT,
                content_hash TEXT,
                sent_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT,
                views INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                engagement_rate REAL DEFAULT 0,
                template_name TEXT,
                scheduled_for DATETIME,
                FOREIGN KEY (channel_id) REFERENCES channels(channel_id)
            )
        ''')
        
        # Enhanced user sessions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id INTEGER,
                data TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                expires_at DATETIME,
                ip_address TEXT,
                user_agent TEXT,
                last_activity DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Enhanced activity logs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT,
                details TEXT,
                ip_address TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                response_time REAL,
                success BOOLEAN DEFAULT 1,
                error_message TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Enhanced VIP users
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vip_users (
                vip_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                level INTEGER DEFAULT 1,
                perks TEXT DEFAULT '{}',
                assigned_by INTEGER,
                assigned_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                expires_at DATETIME,
                renewal_count INTEGER DEFAULT 0,
                total_spent REAL DEFAULT 0,
                notes TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Enhanced flood control
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS flood_control (
                user_id INTEGER PRIMARY KEY,
                message_count INTEGER DEFAULT 0,
                last_message DATETIME DEFAULT CURRENT_TIMESTAMP,
                warning_count INTEGER DEFAULT 0,
                is_temporarily_blocked BOOLEAN DEFAULT 0,
                block_until DATETIME,
                daily_message_count INTEGER DEFAULT 0,
                last_reset_date DATE DEFAULT CURRENT_DATE
            )
        ''')
        
        # Post templates
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS post_templates (
                template_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT DEFAULT 'general',
                caption TEXT,
                media_url TEXT,
                button_text TEXT,
                button_url TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                used_count INTEGER DEFAULT 0,
                last_used DATETIME,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Scheduled tasks
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scheduled_tasks (
                task_id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_type TEXT NOT NULL,
                data TEXT,
                scheduled_for DATETIME NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                executed_at DATETIME,
                result TEXT,
                retry_count INTEGER DEFAULT 0
            )
        ''')
        
        # Analytics data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics (
                date DATE PRIMARY KEY,
                new_users INTEGER DEFAULT 0,
                active_users INTEGER DEFAULT 0,
                messages_sent INTEGER DEFAULT 0,
                posts_sent INTEGER DEFAULT 0,
                vip_added INTEGER DEFAULT 0,
                errors_count INTEGER DEFAULT 0,
                avg_response_time REAL DEFAULT 0,
                peak_concurrent_users INTEGER DEFAULT 0
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_active ON users(last_active)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_vip ON users(is_vip)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_date ON posts(sent_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_expire ON sessions(expires_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_channels_status ON channels(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_status ON scheduled_tasks(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_activity_date ON activity_logs(timestamp)')
        
        conn.commit()
        self.initialize_defaults()
        logger.info("Enhanced database initialized successfully")
    
    def initialize_defaults(self):
        """Initialize default configuration"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        defaults = [
            ('welcome_msg', '''{heart} {star} <b>স্বাগতম প্রিয় বন্ধু!</b> {star} {heart}

{fire} <b>আমাদের কমিউনিটিতে যুক্ত হওয়ার জন্য ধন্যবাদ!</b>

{tada} <b>বিশেষ সুবিধা:</b>
• এক্সক্লুসিভ কন্টেন্ট
• প্রিমিয়াম ফিচার এক্সেস
• লাইভ আপডেট

{link} <b>নিচের বাটনে ক্লিক করে শুরু করুন:</b>''', 0, 'messages', 'Welcome message for new users'),
            
            ('lock_msg', '''{lock} <b>অ্যাক্সেস লক করা আছে!</b>

{cross} আপনি এখনো আমাদের সব চ্যানেলে জয়েন করেননি।

{info} দয়া করে নিচের চ্যানেলগুলোতে জয়েন করে {check} ভেরিফাই বাটনে ক্লিক করুন।''', 0, 'messages', 'Message shown when user hasn\'t joined channels'),
            
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
            ('timezone', 'Asia/Dhaka', 0, 'system', 'System timezone'),
            ('bot_name', Config.BOT_NAME, 0, 'system', 'Bot display name'),
            ('enable_cache', 'ON', 0, 'performance', 'Enable caching'),
            ('max_concurrent_tasks', '10', 0, 'performance', 'Maximum concurrent tasks'),
            ('analytics_enabled', 'ON', 0, 'analytics', 'Enable analytics tracking'),
            ('auto_backup_count', '7', 0, 'backup', 'Number of backups to keep'),
            ('notification_enabled', 'ON', 0, 'notifications', 'Enable admin notifications')
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
    
    # ==================== ENHANCED USER MANAGEMENT ====================
    
    def add_user(self, user_id: int, username: str, first_name: str, last_name: str = "", language_code: str = "en"):
        """Add or update user in database with enhanced tracking"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Get current date in Bangladesh timezone
            now_bd = datetime.datetime.now(Config.TIMEZONE)
            
            cursor.execute('''
                INSERT INTO users (user_id, username, first_name, last_name, join_date, last_active, language_code)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                username = excluded.username,
                first_name = excluded.first_name,
                last_name = excluded.last_name,
                last_active = excluded.last_active,
                language_code = excluded.language_code,
                daily_usage = CASE 
                    WHEN DATE(last_active) < DATE(?) THEN 1 
                    ELSE daily_usage + 1 
                END
            ''', (user_id, username, first_name, last_name, now_bd, now_bd, language_code, now_bd))
            
            # Update analytics
            cursor.execute('''
                INSERT OR IGNORE INTO analytics (date) VALUES (DATE(?))
            ''', (now_bd,))
            
            cursor.execute('''
                UPDATE analytics 
                SET new_users = new_users + 1
                WHERE date = DATE(?)
            ''', (now_bd,))
            
            # Log activity
            cursor.execute('''
                INSERT INTO activity_logs (user_id, action, details, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (user_id, 'user_join', f'Username: {username}', now_bd))
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding user {user_id}: {e}")
            conn.rollback()
            return False
    
    def update_user_activity(self, user_id: int, command: str = None):
        """Update user's last activity timestamp with command tracking"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            now_bd = datetime.datetime.now(Config.TIMEZONE)
            
            cursor.execute('''
                UPDATE users 
                SET last_active = ?,
                    message_count = message_count + 1,
                    last_command = ?,
                    activity_score = activity_score + 1,
                    daily_usage = CASE 
                        WHEN DATE(last_active) < DATE(?) THEN 1 
                        ELSE daily_usage + 1 
                    END
                WHERE user_id = ?
            ''', (now_bd, command, now_bd, user_id))
            
            # Update analytics for active users
            cursor.execute('''
                INSERT OR IGNORE INTO analytics (date) VALUES (DATE(?))
            ''', (now_bd,))
            
            cursor.execute('''
                UPDATE analytics 
                SET active_users = active_users + 1,
                    messages_sent = messages_sent + 1
                WHERE date = DATE(?)
            ''', (now_bd,))
            
            conn.commit()
        except Exception as e:
            logger.error(f"Error updating activity for {user_id}: {e}")
    
    def get_user_stats(self, user_id: int):
        """Get detailed user statistics"""
        user = self.get_user(user_id)
        if not user:
            return None
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get additional stats
        cursor.execute('''
            SELECT 
                COUNT(*) as total_days_active,
                MAX(timestamp) as last_seen,
                COUNT(DISTINCT DATE(timestamp)) as unique_days
            FROM activity_logs 
            WHERE user_id = ?
        ''', (user_id,))
        
        activity_stats = cursor.fetchone()
        
        cursor.execute('''
            SELECT 
                SUM(warning_count) as total_warnings,
                MAX(block_until) as currently_blocked_until
            FROM flood_control 
            WHERE user_id = ?
        ''', (user_id,))
        
        flood_stats = cursor.fetchone()
        
        return {
            **user,
            'total_days_active': activity_stats[0] if activity_stats else 0,
            'last_seen': activity_stats[1] if activity_stats else None,
            'unique_days': activity_stats[2] if activity_stats else 0,
            'total_warnings': flood_stats[0] if flood_stats else 0,
            'currently_blocked': flood_stats[1] if flood_stats and flood_stats[1] and datetime.datetime.now() < datetime.datetime.fromisoformat(flood_stats[1]) else None
        }
    
    # ==================== ENHANCED CONFIG MANAGEMENT ====================
    
    def get_config_with_cache(self, key: str, default: str = ""):
        """Get configuration value with caching"""
        cache_key = f"config_{key}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        value = self.get_config(key, default)
        if self.get_config('enable_cache') == 'ON':
            self.cache[cache_key] = value
        
        return value
    
    def clear_config_cache(self):
        """Clear configuration cache"""
        self.cache.clear()
    
    # ==================== ENHANCED CHANNEL MANAGEMENT ====================
    
    def update_channel_stats(self, channel_id: str):
        """Update channel statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE channels 
            SET post_count = post_count + 1,
                last_post_date = CURRENT_TIMESTAMP
            WHERE channel_id = ?
        ''', (channel_id,))
        
        conn.commit()
    
    def export_channels_csv(self):
        """Export channels to CSV"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT channel_id, name, link, is_private, force_join, status, category, priority
            FROM channels 
            ORDER BY priority DESC, name
        ''')
        
        channels = cursor.fetchall()
        
        # Create CSV content
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Channel ID', 'Name', 'Link', 'Private', 'Force Join', 'Status', 'Category', 'Priority'])
        
        # Write data
        for channel in channels:
            writer.writerow(channel)
        
        return output.getvalue()
    
    def import_channels_csv(self, csv_content: str):
        """Import channels from CSV"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        reader = csv.reader(io.StringIO(csv_content))
        header = next(reader)  # Skip header
        
        imported = 0
        errors = 0
        
        for row in reader:
            try:
                channel_id, name, link, is_private, force_join, status, category, priority = row
                
                cursor.execute('''
                    INSERT OR REPLACE INTO channels 
                    (channel_id, name, link, is_private, force_join, status, category, priority)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (channel_id, name, link, int(is_private), int(force_join), status, category, int(priority)))
                
                imported += 1
            except Exception as e:
                logger.error(f"Error importing channel: {e}")
                errors += 1
        
        conn.commit()
        return imported, errors
    
    # ==================== POST TEMPLATES ====================
    
    def save_template(self, name: str, caption: str, media_url: str = None, button_text: str = None, button_url: str = None, category: str = 'general'):
        """Save a post template"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO post_templates (name, category, caption, media_url, button_text, button_url)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, category, caption, media_url, button_text, button_url))
            
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error saving template: {e}")
            return None
    
    def get_templates(self, category: str = None):
        """Get post templates"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if category:
            cursor.execute('''
                SELECT * FROM post_templates 
                WHERE category = ? AND is_active = 1
                ORDER BY used_count DESC, last_used DESC
            ''', (category,))
        else:
            cursor.execute('''
                SELECT * FROM post_templates 
                WHERE is_active = 1
                ORDER BY used_count DESC, last_used DESC
            ''')
        
        columns = [desc[0] for desc in cursor.description]
        templates = []
        
        for row in cursor.fetchall():
            templates.append(dict(zip(columns, row)))
        
        return templates
    
    def use_template(self, template_id: int):
        """Mark template as used"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE post_templates 
            SET used_count = used_count + 1,
                last_used = CURRENT_TIMESTAMP
            WHERE template_id = ?
        ''', (template_id,))
        
        conn.commit()
    
    # ==================== SCHEDULED TASKS ====================
    
    def schedule_task(self, task_type: str, data: dict, scheduled_for: datetime.datetime):
        """Schedule a task for future execution"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO scheduled_tasks (task_type, data, scheduled_for)
                VALUES (?, ?, ?)
            ''', (task_type, json.dumps(data), scheduled_for))
            
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error scheduling task: {e}")
            return None
    
    def get_pending_tasks(self):
        """Get pending tasks that are due"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        now = datetime.datetime.now()
        
        cursor.execute('''
            SELECT * FROM scheduled_tasks 
            WHERE status = 'pending' AND scheduled_for <= ?
            ORDER BY scheduled_for ASC
            LIMIT 10
        ''', (now,))
        
        columns = [desc[0] for desc in cursor.description]
        tasks = []
        
        for row in cursor.fetchall():
            tasks.append(dict(zip(columns, row)))
        
        return tasks
    
    def mark_task_completed(self, task_id: int, result: str = "completed"):
        """Mark task as completed"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE scheduled_tasks 
            SET status = 'completed',
                executed_at = CURRENT_TIMESTAMP,
                result = ?
            WHERE task_id = ?
        ''', (result, task_id))
        
        conn.commit()
    
    # ==================== ENHANCED STATISTICS ====================
    
    def get_detailed_stats(self, days: int = 7):
        """Get detailed statistics for the last N days"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Daily stats
        cursor.execute('''
            SELECT 
                date,
                new_users,
                active_users,
                messages_sent,
                posts_sent,
                vip_added,
                errors_count,
                avg_response_time
            FROM analytics 
            WHERE date >= DATE('now', ?)
            ORDER BY date DESC
        ''', (f'-{days} days',))
        
        stats['daily_stats'] = []
        columns = [desc[0] for desc in cursor.description]
        
        for row in cursor.fetchall():
            stats['daily_stats'].append(dict(zip(columns, row)))
        
        # User growth
        cursor.execute('''
            SELECT 
                COUNT(*) as total_users,
                COUNT(CASE WHEN DATE(join_date) = DATE('now') THEN 1 END) as today_users,
                COUNT(CASE WHEN is_vip = 1 THEN 1 END) as vip_users,
                COUNT(CASE WHEN is_blocked = 1 THEN 1 END) as blocked_users,
                COUNT(CASE WHEN DATE(last_active) = DATE('now') THEN 1 END) as active_today
            FROM users
        ''')
        
        user_stats = cursor.fetchone()
        stats['user_growth'] = {
            'total_users': user_stats[0],
            'today_users': user_stats[1],
            'vip_users': user_stats[2],
            'blocked_users': user_stats[3],
            'active_today': user_stats[4]
        }
        
        # Channel stats
        cursor.execute('''
            SELECT 
                COUNT(*) as total_channels,
                COUNT(CASE WHEN status = 'active' THEN 1 END) as active_channels,
                COUNT(CASE WHEN force_join = 1 THEN 1 END) as force_join_channels,
                COUNT(CASE WHEN is_private = 1 THEN 1 END) as private_channels
            FROM channels
        ''')
        
        channel_stats = cursor.fetchone()
        stats['channel_stats'] = {
            'total_channels': channel_stats[0],
            'active_channels': channel_stats[1],
            'force_join_channels': channel_stats[2],
            'private_channels': channel_stats[3]
        }
        
        # Performance stats
        cursor.execute('''
            SELECT 
                COUNT(*) as total_posts,
                AVG(engagement_rate) as avg_engagement,
                SUM(views) as total_views,
                SUM(likes) as total_likes
            FROM posts 
            WHERE DATE(sent_date) >= DATE('now', ?)
        ''', (f'-{days} days',))
        
        perf_stats = cursor.fetchone()
        stats['performance_stats'] = {
            'total_posts': perf_stats[0] or 0,
            'avg_engagement': round(perf_stats[1] or 0, 2),
            'total_views': perf_stats[2] or 0,
            'total_likes': perf_stats[3] or 0
        }
        
        return stats
    
    # ==================== TIMEZONE HANDLING ====================
    
    def get_bangladesh_time(self):
        """Get current Bangladesh time"""
        return datetime.datetime.now(Config.TIMEZONE)
    
    def format_bangladesh_time(self, dt=None):
        """Format datetime in Bangladesh style"""
        if dt is None:
            dt = self.get_bangladesh_time()
        
        # Convert to Bangladesh timezone if not already
        if dt.tzinfo is None:
            dt = Config.TIMEZONE.localize(dt)
        elif dt.tzinfo != Config.TIMEZONE:
            dt = dt.astimezone(Config.TIMEZONE)
        
        # Format with Bengali style
        bangla_date = f"{dt.day} {Config.BANGLA_MONTHS[dt.month - 1]}, {dt.year}"
        time_str = dt.strftime("%I:%M %p")
        
        return f"{bangla_date} - {time_str}"
    
    # ==================== ENHANCED BACKUP SYSTEM ====================
    
    def create_smart_backup(self):
        """Create smart backup with compression"""
        backup_time = self.get_bangladesh_time()
        backup_file = os.path.join(
            self.backup_dir,
            f"backup_{backup_time.strftime('%Y%m%d_%H%M%S')}.db"
        )
        
        try:
            # Create backup connection
            backup_conn = sqlite3.connect(backup_file)
            with self.get_connection() as source:
                source.backup(backup_conn)
            backup_conn.close()
            
            # Compress backup
            compressed_file = f"{backup_file}.gz"
            import gzip
            import shutil
            
            with open(backup_file, 'rb') as f_in:
                with gzip.open(compressed_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Remove uncompressed backup
            os.remove(backup_file)
            
            logger.info(f"Smart backup created: {compressed_file}")
            
            # Cleanup old backups
            self.cleanup_old_backups()
            
            return compressed_file
        except Exception as e:
            logger.error(f"Error creating smart backup: {e}")
            return None
    
    def cleanup_old_backups(self):
        """Cleanup old backups based on configuration"""
        try:
            max_backups = int(self.get_config('auto_backup_count', '7'))
            
            backups = sorted([
                f for f in os.listdir(self.backup_dir)
                if f.startswith('backup_') and (f.endswith('.db') or f.endswith('.db.gz'))
            ])
            
            if len(backups) > max_backups:
                for old_backup in backups[:-max_backups]:
                    os.remove(os.path.join(self.backup_dir, old_backup))
                    logger.debug(f"Removed old backup: {old_backup}")
        except Exception as e:
            logger.error(f"Error cleaning up backups: {e}")
    
    # ==================== ENHANCED FLOOD CONTROL ====================
    
    def check_enhanced_flood(self, user_id: int):
        """Enhanced flood control with daily limits"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        now = datetime.datetime.now()
        today = now.date()
        
        cursor.execute('''
            SELECT message_count, last_message, warning_count, is_temporarily_blocked, 
                   block_until, daily_message_count, last_reset_date
            FROM flood_control WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        
        if result:
            message_count, last_message, warning_count, is_blocked, block_until, daily_count, last_reset = result
            
            # Reset daily count if it's a new day
            if last_reset and last_reset != str(today):
                daily_count = 0
                cursor.execute('''
                    UPDATE flood_control 
                    SET daily_message_count = 0,
                        last_reset_date = DATE('now')
                    WHERE user_id = ?
                ''', (user_id,))
            
            # Check if user is blocked
            if block_until and now < datetime.datetime.fromisoformat(block_until):
                return True, "User is temporarily blocked"
            
            # Reset if last message was more than 1 minute ago
            last_msg_time = datetime.datetime.fromisoformat(last_message)
            if (now - last_msg_time).seconds > 60:
                cursor.execute('''
                    UPDATE flood_control 
                    SET message_count = 1, 
                        last_message = ?,
                        daily_message_count = daily_message_count + 1
                    WHERE user_id = ?
                ''', (now, user_id))
                conn.commit()
                return False, "OK"
            
            # Check flood thresholds
            flood_threshold = int(self.get_config('flood_threshold', '5'))
            daily_threshold = 100  # Maximum messages per day
            
            if message_count >= flood_threshold:
                # Block for increasing durations based on warning count
                block_duration = min(300 * (warning_count + 1), 3600)  # Max 1 hour
                block_until_time = now + datetime.timedelta(seconds=block_duration)
                
                cursor.execute('''
                    UPDATE flood_control 
                    SET warning_count = warning_count + 1,
                        is_temporarily_blocked = 1,
                        block_until = ?
                    WHERE user_id = ?
                ''', (block_until_time, user_id))
                
                conn.commit()
                return True, f"Flood detected. Blocked for {block_duration} seconds"
            
            if daily_count >= daily_threshold:
                return True, "Daily message limit exceeded"
            
            # Increment message count
            cursor.execute('''
                UPDATE flood_control 
                SET message_count = message_count + 1,
                    last_message = ?,
                    daily_message_count = daily_message_count + 1
                WHERE user_id = ?
            ''', (now, user_id))
            conn.commit()
        else:
            # First message from user
            cursor.execute('''
                INSERT INTO flood_control (user_id, message_count, last_message, daily_message_count)
                VALUES (?, 1, ?, 1)
            ''', (user_id, now))
            conn.commit()
        
        return False, "OK"
    
    # Keep existing methods for backward compatibility
    def check_flood(self, user_id: int):
        """Legacy flood check (for backward compatibility)"""
        is_blocked, reason = self.check_enhanced_flood(user_id)
        return is_blocked

# Initialize enhanced database
db = DatabaseManager()

# ==============================================================================
# 🔧 ENHANCED SYSTEM MONITOR
# ==============================================================================

class EnhancedSystemMonitor:
    """Enhanced system monitor with more metrics"""
    
    def __init__(self):
        self.start_time = time.time()
        self.message_count = 0
        self.error_count = 0
        self.user_activity = defaultdict(int)
        self.command_stats = defaultdict(int)
        self.response_times = deque(maxlen=100)
        self.peak_concurrent = 0
        self.current_concurrent = 0
        
    def get_uptime(self):
        """Get formatted uptime"""
        uptime = time.time() - self.start_time
        days = uptime // (24 * 3600)
        uptime = uptime % (24 * 3600)
        hours = uptime // 3600
        uptime %= 3600
        minutes = uptime // 60
        seconds = uptime % 60
        
        return f"{int(days)} দিন {int(hours)} ঘণ্টা {int(minutes)} মিনিট {int(seconds)} সেকেন্ড"
    
    def get_detailed_system_stats(self):
        """Get comprehensive system statistics"""
        stats = {
            'uptime': self.get_uptime(),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'cpu_count': psutil.cpu_count(),
            'cpu_freq': psutil.cpu_freq().current if psutil.cpu_freq() else None,
            'memory_percent': psutil.virtual_memory().percent,
            'memory_used_gb': round(psutil.virtual_memory().used / (1024**3), 2),
            'memory_total_gb': round(psutil.virtual_memory().total / (1024**3), 2),
            'memory_available_gb': round(psutil.virtual_memory().available / (1024**3), 2),
            'disk_percent': psutil.disk_usage('/').percent,
            'disk_used_gb': round(psutil.disk_usage('/').used / (1024**3), 2),
            'disk_total_gb': round(psutil.disk_usage('/').total / (1024**3), 2),
            'message_count': self.message_count,
            'error_count': self.error_count,
            'active_users': len(self.user_activity),
            'current_concurrent': self.current_concurrent,
            'peak_concurrent': self.peak_concurrent,
            'avg_response_time': sum(self.response_times) / len(self.response_times) if self.response_times else 0,
            'top_commands': sorted(self.command_stats.items(), key=lambda x: x[1], reverse=True)[:5]
        }
        return stats
    
    def increment_message(self):
        """Increment message counter"""
        self.message_count += 1
    
    def increment_error(self):
        """Increment error counter"""
        self.error_count += 1
    
    def record_response_time(self, response_time: float):
        """Record response time"""
        self.response_times.append(response_time)
    
    def update_user_activity(self, user_id: int):
        """Update user activity"""
        self.user_activity[user_id] = time.time()
        self.current_concurrent = len(self.user_activity)
        self.peak_concurrent = max(self.peak_concurrent, self.current_concurrent)
        
        # Cleanup old entries (older than 5 minutes)
        current_time = time.time()
        self.user_activity = defaultdict(int, {
            uid: ts for uid, ts in self.user_activity.items()
            if current_time - ts < 300
        })
        self.current_concurrent = len(self.user_activity)
    
    def record_command(self, command: str):
        """Record command usage"""
        self.command_stats[command] = self.command_stats.get(command, 0) + 1

# Initialize enhanced system monitor
system_monitor = EnhancedSystemMonitor()

# ==============================================================================
# 🌐 ENHANCED HEALTH SERVER WITH BANGLADESH TIME
# ==============================================================================

class EnhancedHealthCheckHandler(BaseHTTPRequestHandler):
    """Enhanced HTTP handler for health checks with Bangladesh time"""
    
    def do_GET(self):
        if self.path == '/health':
            # Get system stats
            stats = system_monitor.get_detailed_system_stats()
            db_stats = db.get_detailed_stats(1)
            
            # Get Bangladesh time
            bd_time = db.get_bangladesh_time()
            formatted_time = db.format_bangladesh_time(bd_time)
            
            response = {
                'status': 'online',
                'timestamp': datetime.datetime.now().isoformat(),
                'bangladesh_time': {
                    'raw': bd_time.isoformat(),
                    'formatted': formatted_time,
                    'timezone': str(Config.TIMEZONE)
                },
                'system': stats,
                'database': db_stats,
                'version': 'v10.0',
                'bot_name': Config.BOT_NAME,
                'features': 100
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(json.dumps(response, indent=2).encode())
        
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            
            # Get stats for display
            stats = system_monitor.get_detailed_system_stats()
            db_stats = db.get_detailed_stats(1)
            bd_time = db.get_bangladesh_time()
            formatted_time = db.format_bangladesh_time(bd_time)
            
            html = f'''
            <!DOCTYPE html>
            <html>
            <head>
                <title>{Config.BOT_NAME} - Status</title>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }}
                    .container {{ max-width: 1200px; margin: 0 auto; background: rgba(255, 255, 255, 0.1); padding: 30px; border-radius: 15px; backdrop-filter: blur(10px); }}
                    .header {{ text-align: center; margin-bottom: 30px; }}
                    .status {{ padding: 20px; margin: 20px 0; border-radius: 10px; background: rgba(255, 255, 255, 0.2); }}
                    .online {{ background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%); }}
                    .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0; }}
                    .stat-box {{ background: rgba(255, 255, 255, 0.15); padding: 20px; border-radius: 10px; border-left: 5px solid #667eea; transition: transform 0.3s; }}
                    .stat-box:hover {{ transform: translateY(-5px); }}
                    h1 {{ color: white; font-size: 2.5em; margin-bottom: 10px; }}
                    h2 {{ color: white; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
                    .emoji {{ font-size: 32px; margin-right: 10px; }}
                    .bangla-time {{ font-size: 1.2em; background: rgba(255, 255, 255, 0.2); padding: 15px; border-radius: 10px; text-align: center; margin: 20px 0; }}
                    .feature-badge {{ display: inline-block; background: #ff6b6b; color: white; padding: 5px 10px; border-radius: 20px; font-size: 0.9em; margin: 5px; }}
                    .progress-bar {{ height: 10px; background: rgba(255, 255, 255, 0.2); border-radius: 5px; margin: 10px 0; }}
                    .progress-fill {{ height: 100%; background: #4cd964; border-radius: 5px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🤖 {Config.BOT_NAME}</h1>
                        <p>Version 10.0 | 100 Features | Bangladesh Timezone</p>
                    </div>
                    
                    <div class="status online">
                        <strong>🟢 SYSTEM ONLINE</strong> - Running normally since {stats['uptime']}
                    </div>
                    
                    <div class="bangla-time">
                        <strong>🇧🇩 বাংলাদেশ সময়:</strong> {formatted_time}
                    </div>
                    
                    <h2>📊 System Statistics</h2>
                    <div class="stats">
                        <div class="stat-box">
                            <div class="emoji">👥</div>
                            <h3>Users</h3>
                            <p>{db_stats['user_growth']['total_users']:,} total users</p>
                            <p>{db_stats['user_growth']['active_today']:,} active today</p>
                        </div>
                        <div class="stat-box">
                            <div class="emoji">💾</div>
                            <h3>Memory</h3>
                            <p>{stats['memory_percent']}% used</p>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: {stats['memory_percent']}%"></div>
                            </div>
                            <p>{stats['memory_used_gb']}GB / {stats['memory_total_gb']}GB</p>
                        </div>
                        <div class="stat-box">
                            <div class="emoji">⚡</div>
                            <h3>CPU</h3>
                            <p>{stats['cpu_percent']}% load</p>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: {stats['cpu_percent']}%"></div>
                            </div>
                            <p>{stats['cpu_count']} cores</p>
                        </div>
                        <div class="stat-box">
                            <div class="emoji">📈</div>
                            <h3>Performance</h3>
                            <p>{stats['message_count']:,} messages</p>
                            <p>{stats['avg_response_time']:.2f}ms avg response</p>
                        </div>
                    </div>
                    
                    <h2>✨ Features</h2>
                    <div>
                        <span class="feature-badge">Auto-Delete System</span>
                        <span class="feature-badge">Admin Panel</span>
                        <span class="feature-badge">11 Master Channels</span>
                        <span class="feature-badge">Membership Verification</span>
                        <span class="feature-badge">Post Wizard</span>
                        <span class="feature-badge">Bangladesh Timezone</span>
                        <span class="feature-badge">Smart Backup</span>
                        <span class="feature-badge">Enhanced Security</span>
                        <span class="feature-badge">VIP Management</span>
                        <span class="feature-badge">100+ Total Features</span>
                    </div>
                    
                    <p style="text-align: center; margin-top: 30px; opacity: 0.8;">
                        <em>Last updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em><br>
                        <em>© 2024 Supreme Team | All rights reserved</em>
                    </p>
                </div>
            </body>
            </html>
            '''
            self.wfile.write(html.encode())
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        logger.debug(f"HTTP {args[0]} {args[1]}")

def run_enhanced_health_server():
    """Run enhanced HTTP health check server"""
    port = int(os.environ.get('PORT', 8080))
    
    try:
        server = HTTPServer(('0.0.0.0', port), EnhancedHealthCheckHandler)
        logger.info(f"🌐 Enhanced health server started on port {port}")
        logger.info(f"🔗 Status URL: http://0.0.0.0:{port}/health")
        logger.info(f"🔗 Dashboard URL: http://0.0.0.0:{port}/")
        server.serve_forever()
    except Exception as e:
        logger.error(f"Failed to start enhanced health server: {e}")

# Start enhanced health server in background
server_thread = threading.Thread(target=run_enhanced_health_server, daemon=True)
server_thread.start()

# ==============================================================================
# 🎨 ENHANCED UI MANAGER WITH BANGLADESH TIME
# ==============================================================================

class EnhancedUIManager:
    """Enhanced UI manager with Bangladesh time support"""
    
    @staticmethod
    def get_bangladesh_time_display():
        """Get formatted Bangladesh time for display"""
        bd_time = db.get_bangladesh_time()
        return db.format_bangladesh_time(bd_time)
    
    @staticmethod
    def format_text_with_time(text: str, user=None, emojis: bool = True):
        """Format text with Bangladesh time"""
        # Replace emoji placeholders
        if emojis:
            for key, emoji in Config.EMOJIS.items():
                text = text.replace(f"{{{key}}}", emoji)
        
        # Add Bangladesh time
        bangla_time = EnhancedUIManager.get_bangladesh_time_display()
        text += f"\n\n🕒 বাংলাদেশ সময়: {bangla_time}"
        
        # Add user info if provided
        if user:
            user_info = f"\n👤 User: {mention_html(user.id, user.first_name or 'User')}"
            text += user_info
        
        return text
    
    @staticmethod
    def create_enhanced_keyboard(buttons: List[List[Dict]], 
                                 add_back: bool = True, 
                                 add_close: bool = False,
                                 add_home: bool = False,
                                 row_width: int = 2):
        """Create enhanced inline keyboard with better layout"""
        keyboard = []
        
        # Organize buttons in rows
        for row in buttons:
            row_buttons = []
            for btn in row:
                button_text = EnhancedUIManager.format_text(btn.get('text', ''), emojis=True)
                
                # Create button with appropriate parameters
                if btn.get('url'):
                    row_buttons.append(
                        InlineKeyboardButton(
                            text=button_text,
                            url=btn.get('url')
                        )
                    )
                else:
                    row_buttons.append(
                        InlineKeyboardButton(
                            text=button_text,
                            callback_data=btn.get('callback', '')
                        )
                    )
            
            # Add row to keyboard
            if row_buttons:
                keyboard.append(row_buttons)
        
        # Add navigation buttons
        nav_buttons = []
        
        if add_back:
            nav_buttons.append(InlineKeyboardButton("🔙 Back", callback_data="main_menu"))
        
        if add_home:
            nav_buttons.append(InlineKeyboardButton("🏠 Home", callback_data="main_menu"))
        
        if add_close:
            nav_buttons.append(InlineKeyboardButton("❌ Close", callback_data="close_panel"))
        
        if nav_buttons:
            # Distribute nav buttons in a single row
            keyboard.append(nav_buttons)
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def format_text(text: str, user=None, emojis: bool = True):
        """Format text with user info and emojis"""
        # Replace emoji placeholders
        if emojis:
            for key, emoji in Config.EMOJIS.items():
                text = text.replace(f"{{{key}}}", emoji)
        
        # Add user info if provided
        if user:
            user_info = f"\n\n👤 User: {mention_html(user.id, user.first_name or 'User')}"
            text += user_info
        
        return text
    
    @staticmethod
    def create_keyboard(buttons: List[List[Dict]], add_back: bool = True, add_close: bool = False):
        """Create inline keyboard from button configuration"""
        return EnhancedUIManager.create_enhanced_keyboard(buttons, add_back, add_close)
    
    @staticmethod
    def get_admin_menu():
        """Get enhanced admin main menu"""
        buttons = [
            [
                {"text": "📝 Message Editor", "callback": "menu_messages"},
                {"text": "🔗 Link Settings", "callback": "menu_links"}
            ],
            [
                {"text": "📢 Channel Manager", "callback": "menu_channels"},
                {"text": "🛡️ Security Panel", "callback": "menu_security"}
            ],
            [
                {"text": "📡 Marketing Tools", "callback": "menu_marketing"},
                {"text": "📊 Statistics", "callback": "menu_stats"}
            ],
            [
                {"text": "👑 VIP Management", "callback": "menu_vip"},
                {"text": "⚙️ System Settings", "callback": "menu_system"}
            ],
            [
                {"text": "🎨 Post Templates", "callback": "menu_templates"},
                {"text": "⏰ Scheduled Tasks", "callback": "menu_schedule"}
            ]
        ]
        return EnhancedUIManager.create_enhanced_keyboard(buttons, add_back=False, add_close=True, add_home=True)
    
    @staticmethod
    def get_stats_display(stats: Dict):
        """Format statistics for display with enhanced layout"""
        # Get Bangladesh time
        bangla_time = EnhancedUIManager.get_bangladesh_time_display()
        
        text = f"""
{Config.EMOJIS['chart']} <b>📊 ENHANCED SYSTEM STATISTICS</b>
{Config.EMOJIS['time']} <i>{bangla_time}</i>

{Config.EMOJIS['users']} <b>👥 User Statistics:</b>
├─ Total Users: <code>{stats.get('total_users', 0):,}</code>
├─ Today New: <code>{stats.get('today_users', 0):,}</code>
├─ VIP Users: <code>{stats.get('vip_users', 0):,}</code>
├─ Blocked: <code>{stats.get('blocked_users', 0):,}</code>
└─ Active Today: <code>{stats.get('active_today', 0):,}</code>

{Config.EMOJIS['megaphone']} <b>📢 Channel Statistics:</b>
├─ Total Channels: <code>{stats.get('active_channels', 0):,}</code>
└─ Force Join: <code>{stats.get('active_channels', 0):,}</code>

{Config.EMOJIS['camera']} <b>📸 Post Statistics:</b>
├─ Total Posts: <code>{stats.get('total_posts', 0):,}</code>
└─ Today Posts: <code>{stats.get('today_posts', 0):,}</code>

{Config.EMOJIS['gear']} <b>⚙️ System Information:</b>
├─ Uptime: {system_monitor.get_uptime()}
├─ CPU Usage: {system_monitor.get_detailed_system_stats()['cpu_percent']}%
└─ Memory Usage: {system_monitor.get_detailed_system_stats()['memory_percent']}%

📈 <b>Performance Metrics:</b>
• Avg Response Time: {system_monitor.get_detailed_system_stats()['avg_response_time']:.2f}ms
• Messages Processed: {system_monitor.get_detailed_system_stats()['message_count']:,}
• Active Connections: {system_monitor.get_detailed_system_stats()['current_concurrent']}
"""
        return text
    
    @staticmethod
    def create_progress_bar(percentage: float, width: int = 20):
        """Create a progress bar for display"""
        filled = int(width * percentage / 100)
        empty = width - filled
        return f"[{'█' * filled}{'░' * empty}] {percentage:.1f}%"
    
    @staticmethod
    def get_welcome_ui(user):
        """Get welcome UI with Bangladesh time"""
        welcome_msg = db.get_config('welcome_msg')
        btn_text = db.get_config('btn_text')
        watch_url = db.get_config('watch_url')
        
        # Add Bangladesh time to welcome message
        bangla_time = EnhancedUIManager.get_bangladesh_time_display()
        enhanced_welcome = f"{welcome_msg}\n\n🇧🇩 বাংলাদেশ সময়: {bangla_time}"
        
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton(btn_text, url=watch_url)
        ]])
        
        return enhanced_welcome, keyboard
    
    @staticmethod
    def get_channel_management_ui(channels):
        """Get channel management UI"""
        if not channels:
            return "📢 <b>Channel Manager</b>\n\nNo channels added yet.", []
        
        text = "📢 <b>Channel Manager</b>\n\n"
        text += "<b>Current Channels:</b>\n"
        
        buttons = []
        for idx, channel in enumerate(channels, 1):
            status_emoji = "🔒" if channel.get('is_private') else "🔓"
            force_emoji = "✅" if channel.get('force_join', True) else "❌"
            
            text += f"{idx}. {status_emoji} {channel['name']} {force_emoji}\n"
            
            # Add management buttons for each channel
            channel_buttons = [
                {"text": f"✏️ Edit {channel['name'][:10]}", "callback": f"edit_channel_{channel['id']}"},
                {"text": f"❌ Remove", "callback": f"remove_channel_{channel['id']}"}
            ]
            buttons.append(channel_buttons)
        
        # Add general buttons
        buttons.append([
            {"text": "➕ Add Channel", "callback": "add_channel_start"},
            {"text": "📤 Export CSV", "callback": "export_channels"}
        ])
        buttons.append([
            {"text": "📥 Import CSV", "callback": "import_channels_start"},
            {"text": "🔄 Bulk Edit", "callback": "bulk_edit_channels"}
        ])
        
        return text, buttons

# Initialize enhanced UI manager
ui = EnhancedUIManager()

# ==============================================================================
# 🔐 ENHANCED SECURITY MANAGER
# ==============================================================================

class EnhancedSecurityManager:
    """Enhanced security manager with intelligent flood detection"""
    
    def __init__(self):
        self.last_verification = {}
        self.verification_cache = {}
        self.blocked_ips = set()
        self.suspicious_activity = defaultdict(list)
        self.login_attempts = defaultdict(int)
        
    async def check_membership(self, user_id: int, bot) -> List[Dict]:
        """Check if user is member of required channels with caching"""
        if db.get_config('force_join') != 'ON':
            return []
        
        # Check cache first
        cache_key = f"membership_{user_id}"
        current_time = time.time()
        
        if cache_key in self.verification_cache:
            cached_time, result = self.verification_cache[cache_key]
            if current_time - cached_time < 300:  # 5 minute cache
                return result
        
        missing_channels = []
        channels = db.get_channels(force_join_only=True)
        
        # Check membership in parallel (simulated with asyncio)
        for channel in channels:
            try:
                # Use get_chat_member with timeout
                member = await asyncio.wait_for(
                    bot.get_chat_member(chat_id=channel['id'], user_id=user_id),
                    timeout=5.0
                )
                
                if member.status in ['left', 'kicked']:
                    missing_channels.append(channel)
            except asyncio.TimeoutError:
                logger.warning(f"Timeout checking channel {channel['id']}")
                missing_channels.append(channel)
            except Exception as e:
                logger.warning(f"Failed to check channel {channel['id']}: {e}")
                missing_channels.append(channel)
        
        # Update cache
        self.verification_cache[cache_key] = (current_time, missing_channels)
        
        # Clean old cache entries
        self.clean_old_cache()
        
        return missing_channels
    
    def clean_old_cache(self):
        """Clean old cache entries"""
        current_time = time.time()
        old_keys = [
            key for key, (cached_time, _) in self.verification_cache.items()
            if current_time - cached_time > 3600  # 1 hour
        ]
        
        for key in old_keys:
            del self.verification_cache[key]
    
    def check_enhanced_flood(self, user_id: int) -> Tuple[bool, str]:
        """Check if user is flooding with enhanced detection"""
        return db.check_enhanced_flood(user_id)
    
    def check_maintenance(self, user_id: int) -> bool:
        """Check if maintenance mode is active for user"""
        if user_id in Config.ADMIN_IDS:
            return False
        
        return db.get_config('maint_mode') == 'ON'
    
    def check_access(self, user_id: int, required_level: int = 1) -> bool:
        """Check user access level with enhanced permissions"""
        if user_id in Config.ADMIN_IDS:
            return True
        
        if required_level == 1:
            return True
        
        if required_level == 2:
            return db.is_vip(user_id)
        
        # Check for custom permission levels
        user_data = db.get_user(user_id)
        if user_data:
            user_level = user_data.get('user_level', 1)
            return user_level >= required_level
        
        return False
    
    def detect_suspicious_activity(self, user_id: int, action: str) -> bool:
        """Detect suspicious activity patterns"""
        current_time = time.time()
        
        # Record activity
        self.suspicious_activity[user_id].append((current_time, action))
        
        # Keep only last 5 minutes of activity
        self.suspicious_activity[user_id] = [
            (t, a) for t, a in self.suspicious_activity[user_id]
            if current_time - t < 300
        ]
        
        # Check for suspicious patterns
        activities = [a for _, a in self.suspicious_activity[user_id]]
        
        # Pattern 1: Too many different actions in short time
        if len(set(activities)) > 10:
            logger.warning(f"Suspicious activity detected for user {user_id}: too many different actions")
            return True
        
        # Pattern 2: Same action repeated too many times
        from collections import Counter
        action_counts = Counter(activities)
        for action, count in action_counts.items():
            if count > 20:  # Same action 20+ times in 5 minutes
                logger.warning(f"Suspicious activity detected for user {user_id}: {action} repeated {count} times")
                return True
        
        return False
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate secure token"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def validate_input(self, text: str, max_length: int = 4000) -> bool:
        """Validate user input for security"""
        if len(text) > max_length:
            return False
        
        # Check for potentially dangerous patterns
        dangerous_patterns = [
            "<script", "javascript:", "onload=", "onerror=",
            "onclick=", "eval(", "exec(", "system("
        ]
        
        for pattern in dangerous_patterns:
            if pattern in text.lower():
                return False
        
        return True

# Initialize enhanced security manager
security = EnhancedSecurityManager()

# ==============================================================================
# 🔄 ENHANCED BACKGROUND TASK MANAGER
# ==============================================================================

class EnhancedBackgroundTaskManager:
    """Manage enhanced background tasks with scheduling"""
    
    def __init__(self):
        self.tasks = []
        self.scheduled_tasks = []
        self.running = True
        self.task_queue = asyncio.Queue()
        
    def add_recurring_task(self, func, interval: int, *args, **kwargs):
        """Add a recurring background task"""
        task = threading.Thread(
            target=self._run_recurring_task,
            args=(func, interval, args, kwargs),
            daemon=True
        )
        self.tasks.append(task)
        task.start()
    
    def add_scheduled_task(self, func, scheduled_time: datetime.datetime, *args, **kwargs):
        """Add a scheduled task for specific time"""
        task_data = {
            'func': func,
            'scheduled_time': scheduled_time,
            'args': args,
            'kwargs': kwargs,
            'executed': False
        }
        self.scheduled_tasks.append(task_data)
    
    def _run_recurring_task(self, func, interval, args, kwargs):
        """Run recurring task at intervals"""
        while self.running:
            try:
                start_time = time.time()
                func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Log slow tasks
                if execution_time > 1.0:
                    logger.warning(f"Slow background task: {func.__name__} took {execution_time:.2f}s")
                
            except Exception as e:
                logger.error(f"Background task error in {func.__name__}: {e}")
                # Add exponential backoff for failing tasks
                interval = min(interval * 2, 3600)  # Max 1 hour
            
            time.sleep(interval)
    
    def _check_scheduled_tasks(self):
        """Check and execute scheduled tasks"""
        current_time = datetime.datetime.now()
        
        for task in self.scheduled_tasks:
            if not task['executed'] and current_time >= task['scheduled_time']:
                try:
                    task['func'](*task['args'], **task['kwargs'])
                    task['executed'] = True
                    logger.info(f"Executed scheduled task: {task['func'].__name__}")
                except Exception as e:
                    logger.error(f"Failed to execute scheduled task: {e}")
        
        # Remove executed tasks
        self.scheduled_tasks = [t for t in self.scheduled_tasks if not t['executed']]
    
    def monitor_system_resources(self):
        """Monitor system resources and adjust accordingly"""
        stats = system_monitor.get_detailed_system_stats()
        
        # Log resource usage
        if stats['memory_percent'] > 80:
            logger.warning(f"High memory usage: {stats['memory_percent']}%")
        
        if stats['cpu_percent'] > 80:
            logger.warning(f"High CPU usage: {stats['cpu_percent']}%")
        
        # Adjust task intervals based on load
        if stats['cpu_percent'] > 90 or stats['memory_percent'] > 90:
            # Slow down non-critical tasks when system is under heavy load
            pass
    
    def cleanup(self):
        """Cleanup all tasks"""
        self.running = False
        for task in self.tasks:
            task.join(timeout=1)

# Create enhanced background task manager
task_manager = EnhancedBackgroundTaskManager()

# Define enhanced background tasks
def enhanced_cleanup_expired_sessions():
    """Enhanced cleanup of expired sessions"""
    db.cleanup_sessions()
    logger.debug("Cleaned up expired sessions")

def enhanced_create_automatic_backup():
    """Create enhanced automatic backup"""
    backup_file = db.create_smart_backup()
    if backup_file:
        logger.info(f"Enhanced automatic backup created: {backup_file}")
        
        # Check backup size
        backup_size = os.path.getsize(backup_file) / (1024 * 1024)  # MB
        if backup_size > 100:  # 100 MB
            logger.warning(f"Large backup file: {backup_size:.2f} MB")

def enhanced_monitor_system_health():
    """Enhanced system health monitoring"""
    stats = system_monitor.get_detailed_system_stats()
    
    # Check system health
    if stats['memory_percent'] > 90:
        logger.critical(f"CRITICAL: Memory usage at {stats['memory_percent']}%")
    
    if stats['cpu_percent'] > 90:
        logger.critical(f"CRITICAL: CPU usage at {stats['cpu_percent']}%")
    
    # Check disk space
    if stats['disk_percent'] > 90:
        logger.critical(f"CRITICAL: Disk usage at {stats['disk_percent']}%")
    
    # Update task manager monitoring
    task_manager.monitor_system_resources()
    task_manager._check_scheduled_tasks()

def update_analytics():
    """Update analytics data"""
    try:
        # Get today's date in Bangladesh timezone
        today = db.get_bangladesh_time().date()
        
        # Update or create analytics entry for today
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR IGNORE INTO analytics (date) VALUES (?)
        ''', (today,))
        
        # Update peak concurrent users
        stats = system_monitor.get_detailed_system_stats()
        cursor.execute('''
            UPDATE analytics 
            SET peak_concurrent_users = ?
            WHERE date = ?
        ''', (stats['peak_concurrent'], today))
        
        conn.commit()
    except Exception as e:
        logger.error(f"Error updating analytics: {e}")

def cleanup_old_logs():
    """Cleanup old log files"""
    try:
        log_files = [f for f in os.listdir('.') if f.endswith('.log')]
        current_time = time.time()
        
        for log_file in log_files:
            # Keep logs for 7 days
            file_age = current_time - os.path.getmtime(log_file)
            if file_age > 7 * 24 * 3600:  # 7 days
                os.remove(log_file)
                logger.info(f"Removed old log file: {log_file}")
    except Exception as e:
        logger.error(f"Error cleaning up logs: {e}")

# Schedule enhanced background tasks
task_manager.add_recurring_task(enhanced_cleanup_expired_sessions, 300)  # Every 5 minutes
task_manager.add_recurring_task(enhanced_create_automatic_backup, 3600)  # Every hour
task_manager.add_recurring_task(enhanced_monitor_system_health, 60)      # Every minute
task_manager.add_recurring_task(update_analytics, 300)                   # Every 5 minutes
task_manager.add_recurring_task(cleanup_old_logs, 86400)                 # Every day

# ==============================================================================
# 🎮 ENHANCED COMMAND HANDLERS WITH NEW FEATURES
# ==============================================================================

async def enhanced_start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced /start command with Bangladesh time"""
    user = update.effective_user
    start_time = time.time()
    
    system_monitor.update_user_activity(user.id)
    system_monitor.increment_message()
    system_monitor.record_command('start')
    
    # Check for suspicious activity
    if security.detect_suspicious_activity(user.id, 'start_command'):
        await update.message.reply_text(
            "⚠️ Suspicious activity detected. Please try again later.",
            parse_mode=ParseMode.HTML
        )
        return
    
    # Add user to database with enhanced tracking
    db.add_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name or "",
        language_code=user.language_code
    )
    
    # Check enhanced flood control
    is_blocked, reason = security.check_enhanced_flood(user.id)
    if is_blocked:
        await update.message.reply_text(
            f"⚠️ {reason}",
            parse_mode=ParseMode.HTML
        )
        return
    
    # Check maintenance mode
    if security.check_maintenance(user.id):
        await update.message.reply_text(
            ui.format_text_with_time(
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
    missing_channels = await security.check_membership(user.id, context.bot)
    
    if missing_channels:
        # Show lock message with Bangladesh time
        lock_msg = db.get_config('lock_msg')
        enhanced_lock_msg = ui.format_text_with_time(lock_msg, user)
        
        # Create channel join buttons
        buttons = []
        for channel in missing_channels:
            buttons.append([
                {
                    "text": f"📢 Join {channel['name']}",
                    "url": channel['link']
                }
            ])
        
        buttons.append([
            {
                "text": "✅ Verify Membership",
                "callback": "verify_membership"
            }
        ])
        
        keyboard = ui.create_enhanced_keyboard(buttons, add_back=False, add_close=False)
        
        try:
            await update.message.reply_photo(
                photo=db.get_config('welcome_photo'),
                caption=enhanced_lock_msg,
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Failed to send photo: {e}")
            await update.message.reply_text(
                enhanced_lock_msg,
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
    else:
        # Show enhanced welcome message with Bangladesh time
        welcome_msg, keyboard = ui.get_welcome_ui(user)
        
        try:
            message = await update.message.reply_photo(
                photo=db.get_config('welcome_photo'),
                caption=ui.format_text_with_time(welcome_msg, user),
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
            
            # Auto-delete after configured time
            auto_delete = int(db.get_config('auto_delete', Config.DEFAULT_AUTO_DELETE))
            if auto_delete > 0:
                await asyncio.sleep(auto_delete)
                try:
                    await update.message.delete()
                    await message.delete()
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Failed to send welcome: {e}")
            await update.message.reply_text(
                ui.format_text_with_time(welcome_msg, user),
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
    
    # Record response time
    response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
    system_monitor.record_response_time(response_time)
    db.update_user_activity(user.id, 'start')

async def enhanced_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced /admin command with more features"""
    user = update.effective_user
    
    if user.id not in Config.ADMIN_IDS:
        await update.message.reply_text("🚫 Access denied!")
        return
    
    system_monitor.update_user_activity(user.id)
    system_monitor.record_command('admin')
    
    stats = db.get_stats()
    sys_stats = system_monitor.get_detailed_system_stats()
    bangla_time = ui.get_bangladesh_time_display()
    
    text = f"""
{Config.EMOJIS['admin']} <b>🚀 ENHANCED ADMIN PANEL</b>
{Config.EMOJIS['time']} <i>{bangla_time}</i>

{Config.EMOJIS['chart']} <b>📊 Bot Statistics:</b>
├─ Users: <code>{stats['total_users']:,}</code>
├─ Today: <code>{stats['today_users']:,}</code>
├─ VIP: <code>{stats['vip_users']:,}</code>
└─ Active: <code>{stats['active_today']:,}</code>

{Config.EMOJIS['gear']} <b>⚙️ System Status:</b>
├─ Uptime: {sys_stats['uptime']}
├─ CPU: {sys_stats['cpu_percent']}%
├─ Memory: {sys_stats['memory_percent']}%
├─ Messages: <code>{sys_stats['message_count']:,}</code>
└─ Response: <code>{sys_stats['avg_response_time']:.2f}ms</code>

👇 <b>Select an option:</b>
"""
    
    await update.message.reply_text(
        text,
        reply_markup=ui.get_admin_menu(),
        parse_mode=ParseMode.HTML
    )
    
    db.update_user_activity(user.id, 'admin')

async def enhanced_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced /stats command with detailed analytics"""
    user = update.effective_user
    
    if user.id not in Config.ADMIN_IDS:
        await update.message.reply_text("🚫 Admin only command!")
        return
    
    system_monitor.update_user_activity(user.id)
    system_monitor.record_command('stats')
    
    stats = db.get_detailed_stats(7)  # Get 7 days of stats
    sys_stats = system_monitor.get_detailed_system_stats()
    bangla_time = ui.get_bangladesh_time_display()
    
    text = f"""
{Config.EMOJIS['chart']} <b>📈 ENHANCED ANALYTICS DASHBOARD</b>
{Config.EMOJIS['time']} <i>{bangla_time}</i>

{Config.EMOJIS['users']} <b>👥 User Analytics (Last 7 Days):</b>
"""
    
    # Add daily stats summary
    if stats.get('daily_stats'):
        text += f"\n📅 <b>Daily Summary:</b>"
        for day in stats['daily_stats'][:3]:  # Show last 3 days
            text += f"\n• {day['date']}: {day['new_users']} new, {day['active_users']} active"
    
    text += f"""

{Config.EMOJIS['camera']} <b>📸 Performance Metrics:</b>
├─ Total Posts: <code>{stats['performance_stats']['total_posts']:,}</code>
├─ Avg Engagement: <code>{stats['performance_stats']['avg_engagement']}%</code>
├─ Total Views: <code>{stats['performance_stats']['total_views']:,}</code>
└─ Total Likes: <code>{stats['performance_stats']['total_likes']:,}</code>

{Config.EMOJIS['gear']} <b>⚙️ System Performance:</b>
├─ CPU Usage: {ui.create_progress_bar(sys_stats['cpu_percent'])}
├─ Memory Usage: {ui.create_progress_bar(sys_stats['memory_percent'])}
├─ Disk Usage: {ui.create_progress_bar(sys_stats['disk_percent'])}
└─ Peak Concurrent: <code>{sys_stats['peak_concurrent']}</code>
"""
    
    buttons = [
        [
            {"text": "📊 Detailed Report", "callback": "detailed_report"},
            {"text": "📈 Export Data", "callback": "export_analytics"}
        ],
        [
            {"text": "🔄 Refresh", "callback": "refresh_stats"},
            {"text": "📋 User Stats", "callback": "user_statistics"}
        ]
    ]
    
    await update.message.reply_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=ui.create_enhanced_keyboard(buttons, add_back=True, add_close=True)
    )
    
    db.update_user_activity(user.id, 'stats')

async def enhanced_help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced /help command with feature list"""
    user = update.effective_user
    bangla_time = ui.get_bangladesh_time_display()
    
    text = f"""
{Config.EMOJIS['info']} <b>🤖 {Config.BOT_NAME} - Help Center</b>
{Config.EMOJIS['time']} <i>{bangla_time}</i>

<b>🎯 Core Features:</b>
• Auto-delete messages (configurable timer)
• Channel verification system
• VIP access management
• Post scheduling and templates
• Enhanced analytics dashboard

<b>🛡️ Security Features:</b>
• Intelligent flood control
• Suspicious activity detection
• Maintenance mode
• Enhanced user blocking

<b>⚙️ System Features:</b>
• Bangladesh timezone support
• Smart backup system
• Performance monitoring
• Health check server

<b>📊 Admin Features:</b>
• Enhanced admin panel
• Detailed statistics
• Channel management
• Post wizard (6-step)

<b>🔧 User Commands:</b>
/start - Start the bot
/help - Show this help message

<b>👑 Admin Commands:</b>
/admin - Open admin panel
/stats - Show detailed statistics
/backup - Create backup
/broadcast - Broadcast message

<b>🚀 Total Features: 100+</b>
"""
    
    await update.message.reply_text(
        ui.format_text_with_time(text, user),
        parse_mode=ParseMode.HTML
    )
    
    system_monitor.update_user_activity(user.id)
    system_monitor.record_command('help')
    db.update_user_activity(user.id, 'help')

async def enhanced_backup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced /backup command with progress"""
    user = update.effective_user
    
    if user.id not in Config.ADMIN_IDS:
        await update.message.reply_text("🚫 Admin only command!")
        return
    
    system_monitor.update_user_activity(user.id)
    system_monitor.record_command('backup')
    
    message = await update.message.reply_text("💾 Creating smart backup...")
    
    backup_file = db.create_smart_backup()
    
    if backup_file:
        backup_size = os.path.getsize(backup_file) / 1024  # KB
        backup_time = db.format_bangladesh_time()
        
        await message.edit_text(
            f"✅ <b>Smart Backup Created Successfully!</b>\n\n"
            f"📁 File: <code>{os.path.basename(backup_file)}</code>\n"
            f"📦 Size: {backup_size:.2f} KB\n"
            f"🕒 Time: {backup_time}\n"
            f"📍 Location: <code>{backup_file}</code>",
            parse_mode=ParseMode.HTML
        )
    else:
        await message.edit_text("❌ Failed to create backup!")
    
    db.update_user_activity(user.id, 'backup')

async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show Bangladesh time"""
    user = update.effective_user
    bangla_time = ui.get_bangladesh_time_display()
    
    text = f"""
🇧🇩 <b>Bangladesh Time</b>

🕒 <b>Current Time:</b> {bangla_time}

<b>Timezone:</b> {Config.TIMEZONE}
<b>Date Format:</b> DD Month, YYYY - HH:MM AM/PM

<i>All times in the bot are displayed in Bangladesh timezone.</i>
"""
    
    await update.message.reply_text(
        ui.format_text_with_time(text, user),
        parse_mode=ParseMode.HTML
    )
    
    system_monitor.update_user_activity(user.id)
    system_monitor.record_command('time')
    db.update_user_activity(user.id, 'time')

# ==============================================================================
# 🔄 ENHANCED CALLBACK QUERY HANDLER WITH NEW FEATURES
# ==============================================================================

async def enhanced_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced callback query handler with new features"""
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    data = query.data
    
    system_monitor.update_user_activity(user.id)
    
    # Record callback for analytics
    system_monitor.record_command(f"callback_{data}")
    db.update_user_activity(user.id, f"callback_{data}")
    
    # Admin check for admin functions
    admin_functions = {
        'main_menu', 'menu_', 'edit_', 'toggle_', 'remove_', 'add_',
        'broadcast', 'create_post', 'block_user', 'unblock_user',
        'add_vip', 'remove_vip', 'backup_', 'restore_', 'export_',
        'import_', 'bulk_', 'template_', 'schedule_', 'report_',
        'analytics_', 'channel_', 'post_', 'task_'
    }
    
    if any(data.startswith(func) for func in admin_functions) and user.id not in Config.ADMIN_IDS:
        await query.message.reply_text("🚫 Admin access required!")
        return
    
    # Route callbacks to appropriate handlers
    if data == "main_menu":
        await enhanced_show_admin_panel(query.message, user)
    
    elif data == "close_panel":
        try:
            await query.delete_message()
        except:
            pass
    
    elif data == "verify_membership":
        await handle_verify_membership(query, context)
    
    elif data.startswith("menu_"):
        await handle_menu_commands(query, context, data)
    
    elif data.startswith("edit_"):
        await handle_edit_commands(query, context, data)
    
    elif data.startswith("toggle_"):
        await handle_toggle_commands(query, context, data)
    
    elif data.startswith("channel_"):
        await handle_channel_commands(query, context, data)
    
    elif data.startswith("post_"):
        await handle_post_commands(query, context, data)
    
    elif data.startswith("template_"):
        await handle_template_commands(query, context, data)
    
    elif data.startswith("export_"):
        await handle_export_commands(query, context, data)
    
    elif data.startswith("import_"):
        await handle_import_commands(query, context, data)
    
    elif data.startswith("bulk_"):
        await handle_bulk_commands(query, context, data)
    
    elif data in ["backup_now", "restart_bot", "cleanup_db", "view_logs"]:
        await handle_system_commands(query, context, data)
    
    elif data in ["detailed_report", "refresh_stats", "user_statistics"]:
        await handle_analytics_commands(query, context, data)
    
    else:
        await query.message.reply_text("❌ Unknown action!")

async def enhanced_show_admin_panel(message, user):
    """Show enhanced admin panel"""
    stats = db.get_stats()
    sys_stats = system_monitor.get_detailed_system_stats()
    bangla_time = ui.get_bangladesh_time_display()
    
    text = f"""
{Config.EMOJIS['admin']} <b>🚀 ENHANCED ADMIN PANEL</b>
{Config.EMOJIS['time']} <i>{bangla_time}</i>

{Config.EMOJIS['chart']} <b>📊 Bot Statistics:</b>
├─ Users: <code>{stats['total_users']:,}</code>
├─ Today: <code>{stats['today_users']:,}</code>
├─ VIP: <code>{stats['vip_users']:,}</code>
└─ Active: <code>{stats['active_today']:,}</code>

{Config.EMOJIS['gear']} <b>⚙️ System Status:</b>
├─ Uptime: {sys_stats['uptime']}
├─ CPU: {sys_stats['cpu_percent']}%
├─ Memory: {sys_stats['memory_percent']}%
├─ Messages: <code>{sys_stats['message_count']:,}</code>
└─ Response: <code>{sys_stats['avg_response_time']:.2f}ms</code>

👇 <b>Select an option:</b>
"""
    
    if hasattr(message, 'edit_text'):
        await message.edit_text(text, reply_markup=ui.get_admin_menu(), parse_mode=ParseMode.HTML)
    else:
        await message.reply_text(text, reply_markup=ui.get_admin_menu(), parse_mode=ParseMode.HTML)

# ==============================================================================
# 🎯 HANDLER FUNCTIONS FOR NEW FEATURES
# ==============================================================================

async def handle_verify_membership(query, context):
    """Handle membership verification"""
    missing_channels = await security.check_membership(query.from_user.id, context.bot)
    
    if not missing_channels:
        await query.answer("✅ Verified successfully!", show_alert=True)
        
        # Show welcome message with Bangladesh time
        welcome_msg, keyboard = ui.get_welcome_ui(query.from_user)
        
        try:
            await query.message.edit_caption(
                caption=ui.format_text_with_time(welcome_msg, query.from_user),
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
        except:
            await query.message.reply_text(
                ui.format_text_with_time(welcome_msg, query.from_user),
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
    else:
        await query.answer("❌ Still missing channels!", show_alert=True)

async def handle_menu_commands(query, context, data):
    """Handle menu commands"""
    if data == "menu_messages":
        buttons = [
            [
                {"text": "✏️ Welcome Message", "callback": "edit_welcome_msg"},
                {"text": "✏️ Lock Message", "callback": "edit_lock_msg"}
            ],
            [
                {"text": "🖼️ Welcome Photo", "callback": "edit_welcome_photo"},
                {"text": "📝 Button Text", "callback": "edit_btn_text"}
            ]
        ]
        
        await query.edit_message_text(
            ui.format_text_with_time("📝 <b>Message Editor</b>\nSelect message to edit:", query.from_user),
            reply_markup=ui.create_enhanced_keyboard(buttons, add_back=True, add_close=True),
            parse_mode=ParseMode.HTML
        )
    
    elif data == "menu_links":
        buttons = [
            [
                {"text": "🔗 Watch URL", "callback": "edit_watch_url"},
                {"text": "🔘 Button URL", "callback": "edit_button_url"}
            ],
            [
                {"text": "⏱️ Auto Delete", "callback": "edit_auto_delete"},
                {"text": "🌐 Timezone", "callback": "edit_timezone"}
            ]
        ]
        
        await query.edit_message_text(
            ui.format_text_with_time("🔗 <b>Link Settings</b>\nSelect setting to edit:", query.from_user),
            reply_markup=ui.create_enhanced_keyboard(buttons, add_back=True, add_close=True),
            parse_mode=ParseMode.HTML
        )
    
    elif data == "menu_channels":
        channels = db.get_channels()
        text, buttons = ui.get_channel_management_ui(channels)
        
        await query.edit_message_text(
            ui.format_text_with_time(text, query.from_user),
            reply_markup=ui.create_enhanced_keyboard(buttons, add_back=True, add_close=True),
            parse_mode=ParseMode.HTML
        )
    
    elif data == "menu_security":
        maint_status = db.get_config('maint_mode')
        force_status = db.get_config('force_join')
        flood_status = db.get_config('flood_threshold')
        
        text = f"""
🛡️ <b>Security Settings</b>

<b>Current Status:</b>
├─ Maintenance Mode: {maint_status}
├─ Force Join: {force_status}
├─ Flood Threshold: {flood_status} msgs/min
└─ Session Timeout: {db.get_config('session_timeout')}s

<b>Actions:</b>
"""
        
        buttons = [
            [
                {"text": f"🔄 Maintenance: {maint_status}", "callback": "toggle_maint"},
                {"text": f"🔄 Force Join: {force_status}", "callback": "toggle_force"}
            ],
            [
                {"text": "🚫 Block User", "callback": "block_user_start"},
                {"text": "✅ Unblock User", "callback": "unblock_user_start"}
            ],
            [
                {"text": "📊 Security Logs", "callback": "security_logs"},
                {"text": "🔍 Activity Monitor", "callback": "activity_monitor"}
            ]
        ]
        
        await query.edit_message_text(
            ui.format_text_with_time(text, query.from_user),
            reply_markup=ui.create_enhanced_keyboard(buttons, add_back=True, add_close=True),
            parse_mode=ParseMode.HTML
        )
    
    elif data == "menu_marketing":
        text = """
📡 <b>Marketing Tools</b>

<b>Available Tools:</b>
• Create and schedule posts (6-step wizard)
• Broadcast messages to all users
• Target specific user groups
• Analyze engagement metrics
• Post templates library
• Scheduled campaigns
"""
        
        buttons = [
            [
                {"text": "📝 Create Post", "callback": "create_post_start"},
                {"text": "📢 Broadcast", "callback": "broadcast_start"}
            ],
            [
                {"text": "🎯 Target Users", "callback": "target_users"},
                {"text": "📊 Analytics", "callback": "analytics"}
            ],
            [
                {"text": "🎨 Templates", "callback": "menu_templates"},
                {"text": "⏰ Schedule", "callback": "menu_schedule"}
            ]
        ]
        
        await query.edit_message_text(
            ui.format_text_with_time(text, query.from_user),
            reply_markup=ui.create_enhanced_keyboard(buttons, add_back=True, add_close=True),
            parse_mode=ParseMode.HTML
        )
    
    elif data == "menu_stats":
        stats = db.get_stats()
        text = ui.get_stats_display(stats)
        
        await query.edit_message_text(
            ui.format_text_with_time(text, query.from_user),
            reply_markup=ui.create_enhanced_keyboard([], add_back=True, add_close=True),
            parse_mode=ParseMode.HTML
        )
    
    elif data == "menu_vip":
        vip_users = [uid for uid in db.get_all_users() if db.is_vip(uid)]
        
        text = f"""
👑 <b>VIP Management</b>

<b>Current VIP Users:</b>
{len(vip_users)} VIP users

<b>Actions:</b>
"""
        
        buttons = [
            [
                {"text": "➕ Add VIP", "callback": "add_vip_start"},
                {"text": "➖ Remove VIP", "callback": "remove_vip_start"}
            ],
            [
                {"text": "📋 VIP List", "callback": "vip_list"},
                {"text": "📊 VIP Stats", "callback": "vip_stats"}
            ],
            [
                {"text": "⏰ Set Expiry", "callback": "vip_expiry"},
                {"text": "🎁 VIP Perks", "callback": "vip_perks"}
            ]
        ]
        
        await query.edit_message_text(
            ui.format_text_with_time(text, query.from_user),
            reply_markup=ui.create_enhanced_keyboard(buttons, add_back=True, add_close=True),
            parse_mode=ParseMode.HTML
        )
    
    elif data == "menu_system":
        sys_stats = system_monitor.get_detailed_system_stats()
        bangla_time = ui.get_bangladesh_time_display()
        
        text = f"""
⚙️ <b>System Settings</b>
🕒 <i>{bangla_time}</i>

<b>System Status:</b>
├─ Uptime: {sys_stats['uptime']}
├─ CPU: {sys_stats['cpu_percent']}%
├─ Memory: {sys_stats['memory_percent']}%
├─ Disk: {sys_stats['disk_percent']}%
└─ Messages: <code>{sys_stats['message_count']:,}</code>

<b>Actions:</b>
"""
        
        buttons = [
            [
                {"text": "💾 Backup Now", "callback": "backup_now"},
                {"text": "🔄 Restart Bot", "callback": "restart_bot"}
            ],
            [
                {"text": "🧹 Cleanup DB", "callback": "cleanup_db"},
                {"text": "📜 View Logs", "callback": "view_logs"}
            ],
            [
                {"text": "⚡ Performance", "callback": "performance_tuning"},
                {"text": "🔧 Maintenance", "callback": "system_maintenance"}
            ]
        ]
        
        await query.edit_message_text(
            ui.format_text_with_time(text, query.from_user),
            reply_markup=ui.create_enhanced_keyboard(buttons, add_back=True, add_close=True),
            parse_mode=ParseMode.HTML
        )
    
    elif data == "menu_templates":
        templates = db.get_templates()
        
        text = f"""
🎨 <b>Post Templates</b>

<b>Available Templates:</b>
{len(templates)} templates available
"""
        
        buttons = []
        for template in templates[:5]:  # Show first 5 templates
            buttons.append([
                {"text": f"📝 {template['name'][:15]}", "callback": f"template_use_{template['template_id']}"},
                {"text": f"✏️ Edit", "callback": f"template_edit_{template['template_id']}"}
            ])
        
        buttons.append([
            {"text": "➕ New Template", "callback": "template_create"},
            {"text": "📋 All Templates", "callback": "template_list"}
        ])
        
        await query.edit_message_text(
            ui.format_text_with_time(text, query.from_user),
            reply_markup=ui.create_enhanced_keyboard(buttons, add_back=True, add_close=True),
            parse_mode=ParseMode.HTML
        )
    
    elif data == "menu_schedule":
        pending_tasks = db.get_pending_tasks()
        
        text = f"""
⏰ <b>Scheduled Tasks</b>

<b>Pending Tasks:</b>
{len(pending_tasks)} tasks pending
"""
        
        buttons = [
            [
                {"text": "➕ Schedule Post", "callback": "schedule_post"},
                {"text": "📋 Task List", "callback": "task_list"}
            ],
            [
                {"text": "🔄 Run Now", "callback": "run_scheduled"},
                {"text": "🗑️ Clear All", "callback": "clear_scheduled"}
            ]
        ]
        
        await query.edit_message_text(
            ui.format_text_with_time(text, query.from_user),
            reply_markup=ui.create_enhanced_keyboard(buttons, add_back=True, add_close=True),
            parse_mode=ParseMode.HTML
        )

async def handle_edit_commands(query, context, data):
    """Handle edit commands"""
    if data.startswith("edit_"):
        key = data.replace("edit_", "")
        context.user_data['edit_key'] = key
        current_value = db.get_config(key)
        
        await query.message.reply_text(
            f"✏️ <b>Editing:</b> <code>{key}</code>\n"
            f"<b>Current Value:</b>\n<code>{current_value[:200]}</code>\n\n"
            f"Please send the new value:",
            parse_mode=ParseMode.HTML
        )
        return Config.STATE_EDIT_CONFIG

async def handle_toggle_commands(query, context, data):
    """Handle toggle commands"""
    if data.startswith("toggle_"):
        key = data.replace("toggle_", "")
        current = db.get_config(key)
        new_value = "ON" if current == "OFF" else "OFF"
        db.set_config(key, new_value)
        
        await query.answer(f"✅ {key} set to {new_value}", show_alert=True)
        # Refresh menu
        query.data = "menu_security"
        await enhanced_callback_handler(update, context)

async def handle_channel_commands(query, context, data):
    """Handle channel commands"""
    if data.startswith("edit_channel_"):
        channel_id = data.replace("edit_channel_", "")
        context.user_data['edit_channel_id'] = channel_id
        
        # Get channel details
        channels = db.get_channels()
        channel = next((c for c in channels if c['id'] == channel_id), None)
        
        if channel:
            buttons = [
                [
                    {"text": "✏️ Edit Name", "callback": f"channel_edit_name_{channel_id}"},
                    {"text": "🔗 Edit Link", "callback": f"channel_edit_link_{channel_id}"}
                ],
                [
                    {"text": "🔄 Toggle Private", "callback": f"channel_toggle_private_{channel_id}"},
                    {"text": "🔄 Toggle Force Join", "callback": f"channel_toggle_force_{channel_id}"}
                ],
                [
                    {"text": "📊 Stats", "callback": f"channel_stats_{channel_id}"},
                    {"text": "🗑️ Delete", "callback": f"channel_delete_{channel_id}"}
                ]
            ]
            
            text = f"""
📢 <b>Edit Channel</b>

<b>Current Details:</b>
├─ Name: {channel['name']}
├─ Link: {channel['link'][:50]}...
├─ Private: {'Yes' if channel.get('is_private') else 'No'}
└─ Force Join: {'Yes' if channel.get('force_join', True) else 'No'}

<b>Select what to edit:</b>
"""
            
            await query.edit_message_text(
                ui.format_text_with_time(text, query.from_user),
                reply_markup=ui.create_enhanced_keyboard(buttons, add_back=True, add_close=True),
                parse_mode=ParseMode.HTML
            )
    
    elif data.startswith("remove_channel_"):
        channel_id = data.replace("remove_channel_", "")
        if db.remove_channel(channel_id):
            await query.answer("✅ Channel removed!", show_alert=True)
        else:
            await query.answer("❌ Failed to remove!", show_alert=True)
        # Refresh
        query.data = "menu_channels"
        await enhanced_callback_handler(update, context)
    
    elif data == "add_channel_start":
        await query.message.reply_text(
            "➕ <b>Add New Channel</b>\n\n"
            "Please send the Channel ID (e.g., @channelname or -1001234567890):",
            parse_mode=ParseMode.HTML
        )
        return Config.STATE_CHANNEL_ADD_ID

async def handle_post_commands(query, context, data):
    """Handle post commands"""
    if data == "create_post_start":
        await query.message.reply_text(
            "📝 <b>Post Wizard - Step 1/6</b>\n\n"
            "Please send the post caption/text (HTML formatting supported):",
            parse_mode=ParseMode.HTML
        )
        context.user_data['post_wizard'] = {'step': 1}
        return Config.STATE_POST_CAPTION
    
    elif data == "broadcast_start":
        await query.message.reply_text(
            "📢 <b>Broadcast Message</b>\n\n"
            "Please send the message to broadcast (text, photo, or video):",
            parse_mode=ParseMode.HTML
        )
        return Config.STATE_BROADCAST

async def handle_template_commands(query, context, data):
    """Handle template commands"""
    if data == "template_create":
        await query.message.reply_text(
            "🎨 <b>Create New Template</b>\n\n"
            "Please send the template name:",
            parse_mode=ParseMode.HTML
        )
        context.user_data['template_wizard'] = {'step': 1}
        # This would continue to a conversation handler
    
    elif data.startswith("template_use_"):
        template_id = int(data.replace("template_use_", ""))
        templates = db.get_templates()
        template = next((t for t in templates if t['template_id'] == template_id), None)
        
        if template:
            # Use the template for post creation
            context.user_data['post_wizard'] = {
                'step': 1,
                'caption': template['caption'],
                'media_url': template['media_url'],
                'button_text': template['button_text'],
                'button_url': template['button_url'],
                'using_template': template_id
            }
            
            db.use_template(template_id)
            
            await query.answer(f"✅ Using template: {template['name']}", show_alert=True)
            query.data = "create_post_start"
            await enhanced_callback_handler(update, context)

async def handle_export_commands(query, context, data):
    """Handle export commands"""
    if data == "export_channels":
        csv_content = db.export_channels_csv()
        
        if csv_content:
            # Send as file
            file_obj = io.BytesIO(csv_content.encode())
            file_obj.name = f"channels_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            await query.message.reply_document(
                document=file_obj,
                caption="📤 Channel export completed!"
            )
        else:
            await query.answer("❌ No channels to export!", show_alert=True)
    
    elif data == "export_analytics":
        stats = db.get_detailed_stats(30)  # 30 days
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Date', 'New Users', 'Active Users', 'Messages', 'Posts', 'VIP Added', 'Errors', 'Avg Response'])
        
        # Write data
        for day in stats.get('daily_stats', []):
            writer.writerow([
                day['date'],
                day['new_users'],
                day['active_users'],
                day['messages_sent'],
                day['posts_sent'],
                day['vip_added'],
                day['errors_count'],
                day['avg_response_time']
            ])
        
        file_obj = io.BytesIO(output.getvalue().encode())
        file_obj.name = f"analytics_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        await query.message.reply_document(
            document=file_obj,
            caption="📊 Analytics export completed!"
        )

async def handle_import_commands(query, context, data):
    """Handle import commands"""
    if data == "import_channels_start":
        await query.message.reply_text(
            "📥 <b>Import Channels from CSV</b>\n\n"
            "Please send a CSV file with the following columns:\n"
            "Channel ID, Name, Link, Private (0/1), Force Join (0/1), Status, Category, Priority\n\n"
            "Send /cancel to cancel.",
            parse_mode=ParseMode.HTML
        )
        context.user_data['import_type'] = 'channels'
        # This would continue to a conversation handler

async def handle_bulk_commands(query, context, data):
    """Handle bulk commands"""
    if data == "bulk_edit_channels":
        channels = db.get_channels()
        
        text = "🔄 <b>Bulk Edit Channels</b>\n\n"
        text += f"Total channels: {len(channels)}\n\n"
        text += "Select action:"
        
        buttons = [
            [
                {"text": "✅ Enable All", "callback": "bulk_enable_all"},
                {"text": "❌ Disable All", "callback": "bulk_disable_all"}
            ],
            [
                {"text": "🔒 Make All Private", "callback": "bulk_private_all"},
                {"text": "🔓 Make All Public", "callback": "bulk_public_all"}
            ],
            [
                {"text": "📊 Update Stats", "callback": "bulk_update_stats"},
                {"text": "🧹 Clean Inactive", "callback": "bulk_clean_inactive"}
            ]
        ]
        
        await query.edit_message_text(
            ui.format_text_with_time(text, query.from_user),
            reply_markup=ui.create_enhanced_keyboard(buttons, add_back=True, add_close=True),
            parse_mode=ParseMode.HTML
        )

async def handle_system_commands(query, context, data):
    """Handle system commands"""
    if data == "backup_now":
        await query.answer("💾 Creating backup...", show_alert=True)
        backup_file = db.create_smart_backup()
        if backup_file:
            await query.message.reply_text(f"✅ Backup created: {os.path.basename(backup_file)}")
        else:
            await query.message.reply_text("❌ Backup failed!")
    
    elif data == "cleanup_db":
        # Cleanup old data
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Delete old activity logs (older than 30 days)
        cursor.execute("DELETE FROM activity_logs WHERE timestamp < DATE('now', '-30 days')")
        deleted_logs = cursor.rowcount
        
        # Delete old sessions
        cursor.execute("DELETE FROM sessions WHERE expires_at < CURRENT_TIMESTAMP")
        deleted_sessions = cursor.rowcount
        
        conn.commit()
        
        await query.answer(f"🧹 Cleaned up: {deleted_logs} logs, {deleted_sessions} sessions", show_alert=True)
    
    elif data == "view_logs":
        try:
            with open(Config.LOG_FILE, 'r') as f:
                log_content = f.read()[-4000:]  # Last 4000 characters
            
            await query.message.reply_text(
                f"📜 <b>Recent Logs</b>\n\n"
                f"<code>{log_content}</code>",
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            await query.answer(f"❌ Error reading logs: {e}", show_alert=True)

async def handle_analytics_commands(query, context, data):
    """Handle analytics commands"""
    if data == "detailed_report":
        stats = db.get_detailed_stats(30)
        
        text = "📈 <b>Detailed 30-Day Report</b>\n\n"
        
        if stats.get('daily_stats'):
            text += "<b>Daily Summary:</b>\n"
            for day in stats['daily_stats'][:10]:  # Show last 10 days
                text += f"• {day['date']}: {day['new_users']} new, {day['active_users']} active\n"
        
        text += f"\n<b>User Growth:</b>\n"
        text += f"• Total Users: {stats['user_growth']['total_users']:,}\n"
        text += f"• VIP Users: {stats['user_growth']['vip_users']:,}\n"
        
        text += f"\n<b>Performance:</b>\n"
        text += f"• Total Posts: {stats['performance_stats']['total_posts']:,}\n"
        text += f"• Avg Engagement: {stats['performance_stats']['avg_engagement']}%\n"
        
        await query.edit_message_text(
            ui.format_text_with_time(text, query.from_user),
            parse_mode=ParseMode.HTML
        )
    
    elif data == "refresh_stats":
        await query.answer("🔄 Refreshing statistics...", show_alert=True)
        query.data = "menu_stats"
        await enhanced_callback_handler(update, context)

# ==============================================================================
# ✏️ ENHANCED CONVERSATION HANDLERS
# ==============================================================================

async def enhanced_edit_config_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced configuration editing handler"""
    key = context.user_data.get('edit_key')
    new_value = update.message.text
    
    if key:
        if security.validate_input(new_value):
            if db.set_config(key, new_value):
                # Clear cache for this key
                cache_key = f"config_{key}"
                if cache_key in db.cache:
                    del db.cache[cache_key]
                
                await update.message.reply_text(
                    f"✅ <b>{key}</b> updated successfully!\n\n"
                    f"New value: <code>{new_value[:100]}...</code>",
                    parse_mode=ParseMode.HTML
                )
            else:
                await update.message.reply_text(
                    f"❌ Failed to update {key}!",
                    parse_mode=ParseMode.HTML
                )
        else:
            await update.message.reply_text(
                "❌ Invalid input detected! Please check for dangerous characters.",
                parse_mode=ParseMode.HTML
            )
    else:
        await update.message.reply_text("❌ Error: No key specified!")
    
    context.user_data.clear()
    return ConversationHandler.END

async def enhanced_post_wizard_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced 6-step post wizard handler"""
    if 'post_wizard' not in context.user_data:
        context.user_data['post_wizard'] = {'step': 1}
    
    wizard = context.user_data['post_wizard']
    step = wizard.get('step', 1)
    
    if step == 1:  # Caption
        wizard['caption'] = update.message.text_html
        wizard['step'] = 2
        
        await update.message.reply_text(
            "📸 <b>Post Wizard - Step 2/6</b>\n\n"
            "Send photo or video for the post (or type /skip for text only):\n\n"
            "<i>Tip: You can send multiple media files</i>",
            parse_mode=ParseMode.HTML
        )
        return Config.STATE_POST_MEDIA
    
    elif step == 2:  # Media
        if update.message.photo:
            wizard['media'] = update.message.photo[-1].file_id
            wizard['type'] = 'photo'
        elif update.message.video:
            wizard['media'] = update.message.video.file_id
            wizard['type'] = 'video'
        elif update.message.text and update.message.text.lower() == '/skip':
            wizard['media'] = None
            wizard['type'] = 'text'
        else:
            wizard['media'] = None
            wizard['type'] = 'text'
        
        wizard['step'] = 3
        
        await update.message.reply_text(
            "🔘 <b>Post Wizard - Step 3/6</b>\n\n"
            "Send button text (or /skip to use default):\n\n"
            f"<i>Default: {db.get_config('btn_text')}</i>",
            parse_mode=ParseMode.HTML
        )
        return Config.STATE_POST_BUTTON
    
    elif step == 3:  # Button Text
        if update.message.text and update.message.text.lower() != '/skip':
            wizard['button_text'] = update.message.text
        else:
            wizard['button_text'] = db.get_config('btn_text')
        
        wizard['step'] = 4
        
        await update.message.reply_text(
            "🔗 <b>Post Wizard - Step 4/6</b>\n\n"
            "Send button URL (or /skip to use default):\n\n"
            f"<i>Default: {db.get_config('watch_url')}</i>",
            parse_mode=ParseMode.HTML
        )
        return Config.STATE_POST_BUTTON_URL
    
    elif step == 4:  # Button URL
        if update.message.text and update.message.text.lower() != '/skip':
            wizard['button_url'] = update.message.text
        else:
            wizard['button_url'] = db.get_config('watch_url')
        
        wizard['step'] = 5
        
        # Get channels for selection
        channels = db.get_channels()
        
        if not channels:
            await update.message.reply_text("❌ No channels available!")
            context.user_data.clear()
            return ConversationHandler.END
        
        # Create channel selection
        text = "📢 <b>Post Wizard - Step 5/6</b>\n\n"
        text += "<b>Select channels for force join:</b>\n"
        
        buttons = []
        for channel in channels:
            channel_name = channel['name'][:20]
            buttons.append([
                {
                    "text": f"✅ {channel_name}",
                    "callback": f"wizard_select_{channel['id']}"
                }
            ])
        
        buttons.append([
            {"text": "✅ Select All", "callback": "wizard_select_all"},
            {"text": "❌ Select None", "callback": "wizard_select_none"}
        ])
        buttons.append([
            {"text": "➡️ Next", "callback": "wizard_step_6"}
        ])
        
        wizard['force_join_channels'] = []
        
        await update.message.reply_text(
            text,
            reply_markup=ui.create_enhanced_keyboard(buttons, add_back=False, add_close=False),
            parse_mode=ParseMode.HTML
        )
        return Config.STATE_POST_CONFIRM
    
    elif step == 5:  # Force Join Selection (handled by callback)
        pass
    
    elif step == 6:  # Target Channels
        # Get channels for posting
        channels = db.get_channels()
        
        text = "🎯 <b>Post Wizard - Step 6/6</b>\n\n"
        text += "<b>Select target channels for posting:</b>\n"
        
        buttons = []
        for channel in channels:
            channel_name = channel['name'][:20]
            buttons.append([
                {
                    "text": f"📤 {channel_name}",
                    "callback": f"wizard_target_{channel['id']}"
                }
            ])
        
        buttons.append([
            {"text": "📤 Post to ALL", "callback": "wizard_target_all"}
        ])
        buttons.append([
            {"text": "✅ Finish & Post", "callback": "wizard_finish"}
        ])
        
        wizard['target_channels'] = []
        
        await update.message.reply_text(
            text,
            reply_markup=ui.create_enhanced_keyboard(buttons, add_back=True, add_close=True),
            parse_mode=ParseMode.HTML
        )
        return Config.STATE_POST_CONFIRM

async def enhanced_broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced broadcast handler with progress tracking"""
    message = update.message
    users = db.get_all_users(active_only=True)
    
    if not users:
        await message.reply_text("❌ No users to broadcast!")
        return ConversationHandler.END
    
    total_users = len(users)
    
    # Ask for confirmation
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Yes, Broadcast", callback_data="confirm_broadcast"),
        InlineKeyboardButton("❌ Cancel", callback_data="cancel_broadcast")
    ]])
    
    await message.reply_text(
        f"📢 <b>Broadcast Confirmation</b>\n\n"
        f"Are you sure you want to broadcast to {total_users:,} users?\n\n"
        f"<i>This may take several minutes.</i>",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )
    
    # Store broadcast data
    context.user_data['broadcast_data'] = {
        'message': message,
        'users': users,
        'total': total_users
    }
    
    return Config.STATE_BROADCAST

async def enhanced_add_channel_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced add channel flow"""
    if 'channel_step' not in context.user_data:
        context.user_data['channel_step'] = 1
    
    step = context.user_data['channel_step']
    
    if step == 1:  # Channel ID
        channel_id = update.message.text.strip()
        
        # Validate channel ID
        if not (channel_id.startswith('@') or channel_id.startswith('-100')):
            await update.message.reply_text(
                "❌ Invalid channel ID format!\n"
                "Channel ID should start with @ (for public) or -100 (for private).\n"
                "Please send the channel ID again:"
            )
            return Config.STATE_CHANNEL_ADD_ID
        
        context.user_data['channel_id'] = channel_id
        context.user_data['channel_step'] = 2
        
        await update.message.reply_text(
            "📝 <b>Step 2/4</b>\n\n"
            "Please send the channel name:",
            parse_mode=ParseMode.HTML
        )
        return Config.STATE_CHANNEL_ADD_NAME
    
    elif step == 2:  # Channel Name
        context.user_data['channel_name'] = update.message.text
        context.user_data['channel_step'] = 3
        
        await update.message.reply_text(
            "🔗 <b>Step 3/4</b>\n\n"
            "Please send the channel link (t.me/...):",
            parse_mode=ParseMode.HTML
        )
        return Config.STATE_CHANNEL_ADD_LINK
    
    elif step == 3:  # Channel Link
        context.user_data['channel_link'] = update.message.text
        context.user_data['channel_step'] = 4
        
        # Ask for additional settings
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("🔒 Private", callback_data="channel_private_yes"),
            InlineKeyboardButton("🔓 Public", callback_data="channel_private_no")
        ], [
            InlineKeyboardButton("✅ Force Join", callback_data="channel_force_yes"),
            InlineKeyboardButton("❌ No Force", callback_data="channel_force_no")
        ]])
        
        await update.message.reply_text(
            "⚙️ <b>Step 4/4</b>\n\n"
            "Configure channel settings:",
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
        return Config.STATE_CHANNEL_ADD_LINK
    
    elif step == 4:  # Settings (handled by callback)
        pass

async def enhanced_block_user_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced block user handler with reason"""
    try:
        parts = update.message.text.split(' ', 1)
        user_id = int(parts[0])
        reason = parts[1] if len(parts) > 1 else "Manual block by admin"
        
        if db.block_user(user_id, update.effective_user.id, reason):
            await update.message.reply_text(
                f"✅ User {user_id} blocked successfully!\n"
                f"Reason: {reason}"
            )
        else:
            await update.message.reply_text(f"❌ Failed to block user {user_id}!")
    except ValueError:
        await update.message.reply_text("❌ Invalid format! Use: /block <user_id> [reason]")
    
    return ConversationHandler.END

async def enhanced_add_vip_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced add VIP handler with level"""
    try:
        parts = update.message.text.split(' ', 2)
        user_id = int(parts[0])
        level = int(parts[1]) if len(parts) > 1 else 1
        notes = parts[2] if len(parts) > 2 else ""
        
        if db.add_vip(user_id, level):
            # Add notes if provided
            if notes:
                conn = db.get_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE vip_users SET notes = ? WHERE user_id = ?
                ''', (notes, user_id))
                conn.commit()
            
            await update.message.reply_text(
                f"✅ User {user_id} granted VIP access (Level {level})!\n"
                f"Notes: {notes[:50]}..."
            )
        else:
            await update.message.reply_text(f"❌ Failed to add VIP for user {user_id}!")
    except ValueError:
        await update.message.reply_text("❌ Invalid format! Use: /vipadd <user_id> [level] [notes]")
    
    return ConversationHandler.END

async def enhanced_cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced cancel handler with cleanup"""
    await update.message.reply_text("❌ Operation cancelled.")
    
    # Cleanup user data
    if 'post_wizard' in context.user_data:
        del context.user_data['post_wizard']
    if 'edit_key' in context.user_data:
        del context.user_data['edit_key']
    if 'channel_step' in context.user_data:
        del context.user_data['channel_step']
    
    context.user_data.clear()
    return ConversationHandler.END

# ==============================================================================
# 🚀 ENHANCED MAIN APPLICATION SETUP
# ==============================================================================

def setup_enhanced_application():
    """Setup enhanced Telegram application with all handlers"""
    
    # Create enhanced application
    application = ApplicationBuilder() \
        .token(Config.TOKEN) \
        .connection_pool_size(20) \
        .pool_timeout(60) \
        .read_timeout(60) \
        .write_timeout(60) \
        .get_updates_read_timeout(60) \
        .http_version("1.1") \
        .post_init(set_bot_commands) \
        .build()
    
    # ===== ENHANCED CONVERSATION HANDLERS =====
    
    # Edit configuration conversation
    edit_config_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(enhanced_callback_handler, pattern='^edit_')],
        states={
            Config.STATE_EDIT_CONFIG: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, enhanced_edit_config_handler)
            ]
        },
        fallbacks=[CommandHandler('cancel', enhanced_cancel_handler)]
    )
    
    # Enhanced post wizard conversation (6-step)
    post_wizard_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(enhanced_callback_handler, pattern='^create_post_start$'),
            CallbackQueryHandler(enhanced_callback_handler, pattern='^template_use_')
        ],
        states={
            Config.STATE_POST_CAPTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, enhanced_post_wizard_handler)
            ],
            Config.STATE_POST_MEDIA: [
                MessageHandler(filters.PHOTO | filters.VIDEO | filters.TEXT, enhanced_post_wizard_handler)
            ],
            Config.STATE_POST_BUTTON: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, enhanced_post_wizard_handler)
            ],
            Config.STATE_POST_BUTTON_URL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, enhanced_post_wizard_handler)
            ],
            Config.STATE_POST_CONFIRM: [
                CallbackQueryHandler(enhanced_callback_handler, pattern='^wizard_')
            ]
        },
        fallbacks=[CommandHandler('cancel', enhanced_cancel_handler)]
    )
    
    # Enhanced broadcast conversation
    broadcast_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(enhanced_callback_handler, pattern='^broadcast_start$')],
        states={
            Config.STATE_BROADCAST: [
                MessageHandler(filters.ALL & ~filters.COMMAND, enhanced_broadcast_handler),
                CallbackQueryHandler(enhanced_callback_handler, pattern='^confirm_|^cancel_')
            ]
        },
        fallbacks=[CommandHandler('cancel', enhanced_cancel_handler)]
    )
    
    # Enhanced add channel conversation
    add_channel_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(enhanced_callback_handler, pattern='^add_channel_start$')],
        states={
            Config.STATE_CHANNEL_ADD_ID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, enhanced_add_channel_flow)
            ],
            Config.STATE_CHANNEL_ADD_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, enhanced_add_channel_flow)
            ],
            Config.STATE_CHANNEL_ADD_LINK: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, enhanced_add_channel_flow),
                CallbackQueryHandler(enhanced_callback_handler, pattern='^channel_')
            ]
        },
        fallbacks=[CommandHandler('cancel', enhanced_cancel_handler)]
    )
    
    # Enhanced block user conversation
    block_user_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(enhanced_callback_handler, pattern='^block_user_start$')],
        states={
            Config.STATE_USER_BLOCK: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, enhanced_block_user_handler)
            ]
        },
        fallbacks=[CommandHandler('cancel', enhanced_cancel_handler)]
    )
    
    # Enhanced add VIP conversation
    add_vip_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(enhanced_callback_handler, pattern='^add_vip_start$')],
        states={
            Config.STATE_VIP_ADD: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, enhanced_add_vip_handler)
            ]
        },
        fallbacks=[CommandHandler('cancel', enhanced_cancel_handler)]
    )
    
    # ===== ADD ENHANCED HANDLERS =====
    
    # Enhanced command handlers
    application.add_handler(CommandHandler("start", enhanced_start_command))
    application.add_handler(CommandHandler("admin", enhanced_admin_command))
    application.add_handler(CommandHandler("stats", enhanced_stats_command))
    application.add_handler(CommandHandler("help", enhanced_help_command))
    application.add_handler(CommandHandler("backup", enhanced_backup_command))
    application.add_handler(CommandHandler("time", time_command))
    
    # Enhanced conversation handlers
    application.add_handler(edit_config_conv)
    application.add_handler(post_wizard_conv)
    application.add_handler(broadcast_conv)
    application.add_handler(add_channel_conv)
    application.add_handler(block_user_conv)
    application.add_handler(add_vip_conv)
    
    # Enhanced callback query handler (must be last)
    application.add_handler(CallbackQueryHandler(enhanced_callback_handler))
    
    # Enhanced error handler
    application.add_error_handler(enhanced_error_handler)
    
    return application

async def enhanced_error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced error handler with better logging"""
    system_monitor.increment_error()
    
    # Get error details
    error = context.error
    error_type = type(error).__name__
    
    # Log error with more details
    logger.error(f"Exception while handling update: {error}")
    logger.error(f"Error type: {error_type}")
    
    if update:
        logger.error(f"Update that caused error: {update}")
    
    # Get full traceback
    tb_list = traceback.format_exception(None, error, error.__traceback__)
    tb_string = ''.join(tb_list)
    
    # Log traceback to file
    error_log_file = f"error_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    with open(error_log_file, 'w') as f:
        f.write(f"Time: {datetime.datetime.now()}\n")
        f.write(f"Error: {error}\n")
        f.write(f"Type: {error_type}\n")
        if update:
            f.write(f"Update: {update.to_json() if hasattr(update, 'to_json') else str(update)}\n")
        f.write("\nTraceback:\n")
        f.write(tb_string)
    
    logger.error(f"Full traceback saved to: {error_log_file}")
    
    # Send detailed error notification to admin
    error_msg = f"""
⚠️ <b>Bot Error Notification</b>

<b>Error Type:</b> <code>{error_type}</code>
<b>Error Message:</b> <code>{str(error)[:200]}</code>
<b>Time:</b> {db.format_bangladesh_time()}
<b>Log File:</b> <code>{error_log_file}</code>

<i>Check error logs for full details.</i>
"""
    
    try:
        for admin_id in Config.ADMIN_IDS:
            try:
                await context.bot.send_message(
                    admin_id,
                    error_msg,
                    parse_mode=ParseMode.HTML
                )
            except Exception as e:
                logger.error(f"Failed to send error notification to admin {admin_id}: {e}")
    except:
        pass
    
    # Try to send user-friendly error message to user
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ An unexpected error occurred. Our team has been notified.\n"
                "Please try again later or contact support.",
                parse_mode=ParseMode.HTML
            )
    except:
        pass

async def set_bot_commands(application: Application):
    """Set enhanced bot commands for menu"""
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("admin", "Admin panel"),
        BotCommand("stats", "View detailed statistics"),
        BotCommand("help", "Show help with features"),
        BotCommand("backup", "Create smart backup"),
        BotCommand("time", "Show Bangladesh time")
    ]
    
    try:
        await application.bot.set_my_commands(commands)
        await application.bot.set_my_name(Config.BOT_NAME)
        await application.bot.set_my_description(
            f"{Config.BOT_NAME} - Advanced bot with 100+ features including "
            "auto-delete, channel verification, VIP system, and more!"
        )
        
        logger.info("Enhanced bot commands set successfully")
        logger.info(f"Bot name set to: {Config.BOT_NAME}")
    except Exception as e:
        logger.error(f"Failed to set bot commands/name: {e}")

def enhanced_main():
    """Enhanced main entry point"""
    logger.info("=" * 80)
    logger.info("🚀 STARTING SUPREME GOD BOT v10.0 - ULTIMATE EDITION")
    logger.info("=" * 80)
    
    # Display enhanced system info
    stats = system_monitor.get_detailed_system_stats()
    bangla_time = ui.get_bangladesh_time_display()
    
    logger.info(f"🤖 Bot Name: {Config.BOT_NAME}")
    logger.info(f"🇧🇩 Bangladesh Time: {bangla_time}")
    logger.info(f"⏰ System Uptime: {stats['uptime']}")
    logger.info(f"⚡ CPU Usage: {stats['cpu_percent']}% ({stats['cpu_count']} cores)")
    logger.info(f"💾 Memory Usage: {stats['memory_percent']}%")
    logger.info(f"💿 Disk Usage: {stats['disk_percent']}%")
    
    # Display enhanced bot info
    db_stats = db.get_stats()
    logger.info(f"👥 Total Users: {db_stats['total_users']:,}")
    logger.info(f"📢 Active Channels: {db_stats['active_channels']:,}")
    logger.info(f"⭐ VIP Users: {db_stats['vip_users']:,}")
    
    logger.info("=" * 80)
    logger.info("✨ FEATURES ENABLED: 100+")
    logger.info("🎯 Core: Auto-delete, Admin Panel, 11 Master Channels")
    logger.info("🛡️ Security: Flood Control, Verification, Maintenance Mode")
    logger.info("⚡ Performance: Bangladesh Timezone, Smart Backup, Caching")
    logger.info("📊 Analytics: Detailed Stats, User Tracking, Performance")
    logger.info("🎨 UI: Enhanced Menus, Progress Bars, ASCII Art")
    logger.info("=" * 80)
    
    try:
        # Create and setup enhanced application
        application = setup_enhanced_application()
        
        # Run enhanced polling
        logger.info("📡 Starting enhanced polling...")
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
            close_loop=False,
            poll_interval=0.5,
            timeout=30
        )
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user (KeyboardInterrupt)")
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        # Enhanced cleanup
        task_manager.cleanup()
        logger.info("Enhanced bot shutdown complete")
        logger.info("=" * 80)

if __name__ == "__main__":
    # Run enhanced main function
    asyncio.run(enhanced_main())
