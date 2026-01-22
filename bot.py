# -*- coding: utf-8 -*-
"""
Romantic/Hot Love Telegram Bot
Features: Force Join, Verified Popup, Multi-Button Posts, Admin Panel
Platform: Render Free Web Service (with Flask stay-alive)
"""

import telebot
from telebot import types
import sqlite3
import logging
import os
import threading
import time
from flask import Flask

# --- CONFIGURATION ---
API_TOKEN = '8216066342:AAHLCoA0F0HGpdLRykTGcomTY7jN4sQwRwU'
ADMIN_ID = 6406804999

# Bot initialization
bot = telebot.TeleBot(API_TOKEN, parse_mode='HTML')
logging.basicConfig(level=logging.INFO)

# Flask server to keep Render Web Service alive
app = Flask('')

@app.route('/')
def home():
    return "Bot is running and alive!"

def run_web():
    # Render uses port 8080 or 10000 usually
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# --- DATABASE MANAGEMENT ---
DB_NAME = 'bot_database.db'

def init_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    cursor = conn.cursor()
    # Users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY, 
        name TEXT, 
        verified INTEGER DEFAULT 0)''')
    # Channels table
    cursor.execute('''CREATE TABLE IF NOT EXISTS channels (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        channel_id TEXT UNIQUE, 
        username TEXT, 
        title TEXT)''')
    # Settings table
    cursor.execute('''CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY, 
        value TEXT)''')
    # Posts table
    cursor.execute('''CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        title TEXT, 
        media TEXT, 
        buttons TEXT)''')
    
    # Default values
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('w_text', '💖 <b>Hey {name}!</b>\n\nUffff 😍 Tumi amar kache ashte cao? Age nicher sob channel join koro tarpor verified button-e click koro baby! 🔥')")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('w_photo', 'https://telegra.ph/file/0c93a0b36873c3328e83b.jpg')")
    
    conn.commit()
    return conn

db_conn = init_db()

# --- ADMIN STATES ---
admin_states = {}

# --- HELPER FUNCTIONS ---

def get_db_cursor():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    return conn, conn.cursor()

def check_force_join(user_id):
    _, cursor = get_db_cursor()
    cursor.execute("SELECT channel_id FROM channels")
    rows = cursor.fetchall()
    if not rows:
        return True
    
    for (cid,) in rows:
        try:
            member = bot.get_chat_member(cid, user_id)
            if member.status in ['left', 'kicked', 'None']:
                return False
        except Exception as e:
            logging.error(f"Join Check Error for {cid}: {e}")
            continue
    return True

def build_2_row_markup(btn_list, verify=False, watch=False):
    markup = types.InlineKeyboardMarkup()
    # Group buttons in 2 per row
    for i in range(0, len(btn_list), 2):
        row = btn_list[i:i+2]
        markup.row(*row)
    
    if verify:
        markup.add(types.InlineKeyboardButton(text="✅ Verified ❤️", callback_data="btn_verify"))
    if watch:
        markup.add(types.InlineKeyboardButton(text="🎬 Watch Now 🔥", callback_data="btn_watch"))
    
    return markup

# --- USER SIDE LOGIC ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    
    conn, cursor = get_db_cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, name) VALUES (?, ?)", (user_id, name))
    conn.commit()
    
    cursor.execute("SELECT value FROM settings WHERE key='w_text'")
    w_text = cursor.fetchone()[0]
    cursor.execute("SELECT value FROM settings WHERE key='w_photo'")
    w_photo = cursor.fetchone()[0]
    
    cursor.execute("SELECT title, username FROM channels")
    chans = cursor.fetchall()
    
    btn_list = []
    for title, user in chans:
        url = f"https://t.me/{user.replace('@','')}"
        btn_list.append(types.InlineKeyboardButton(text=f"🔞 {title}", url=url))
    
    markup = build_2_row_markup(btn_list, verify=True)
    
    try:
        bot.send_photo(message.chat.id, w_photo, caption=w_text.format(name=name), reply_markup=markup)
    except:
        bot.send_message(message.chat.id, w_text.format(name=name), reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "btn_verify")
def handle_verification(call):
    user_id = call.from_user.id
    if check_force_join(user_id):
        bot.answer_callback_query(call.id, "Uffff 😍 Tumi verified ❤️ Next surprise unlock 🔥", show_alert=True)
        # Unlock Watch Now button
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text="🎬 Watch Now 🔥", callback_data="btn_watch"))
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
    else:
        bot.answer_callback_query(call.id, "Awww 😘 Age sob channel join koro baby 💔", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == "btn_watch")
def handle_watch(call):
    user_id = call.from_user.id
    if check_force_join(user_id):
        bot.send_message(call.message.chat.id, "🎬 <b>Surprise Baby!</b>\n\nHere is your content: 🔥\nhttps://t.me/your_link_here")
    else:
        bot.answer_callback_query(call.id, "Awww 😘 Age sob channel join koro baby 💔", show_alert=True)

# --- ADMIN PANEL LOGIC ---

@bot.message_handler(commands=['admin'])
def admin_main(message):
    if message.from_user.id != ADMIN_ID:
        return
    
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("➕ Add Post", callback_data="adm_add_post"),
               types.InlineKeyboardButton("📢 Channel Mgmt", callback_data="adm_chans"))
    markup.row(types.InlineKeyboardButton("🖼 Welcome Settings", callback_data="adm_welcome"),
               types.InlineKeyboardButton("📊 Statistics", callback_data="adm_stats"))
    
    bot.send_message(message.chat.id, "🛠 <b>Admin Panel</b>\nManage your bot activities:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "adm_stats")
def admin_stats(call):
    _, cursor = get_db_cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    total = cursor.fetchone()[0]
    bot.answer_callback_query(call.id, f"Total Users: {total}", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == "adm_chans")
def admin_channels(call):
    markup = types.InlineKeyboardMarkup()
    _, cursor = get_db_cursor()
    cursor.execute("SELECT id, title FROM channels")
    rows = cursor.fetchall()
    
    for db_id, title in rows:
        markup.add(types.InlineKeyboardButton(f"❌ Remove {title}", callback_data=f"del_chan_{db_id}"))
    
    markup.add(types.InlineKeyboardButton("➕ Add New Channel", callback_data="adm_new_chan"))
    markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="adm_back"))
    bot.edit_message_text("<b>Manage Channels:</b>", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "adm_new_chan")
def add_chan_step1(call):
    msg = bot.send_message(call.message.chat.id, "চ্যানেল তথ্য পাঠান (ID, Username, Title):\n<code>-100123, @user, Title</code>")
    bot.register_next_step_handler(msg, add_chan_save)

def add_chan_save(message):
    try:
        parts = message.text.split(',')
        cid, user, title = parts[0].strip(), parts[1].strip(), parts[2].strip()
        conn, cursor = get_db_cursor()
        cursor.execute("INSERT INTO channels (channel_id, username, title) VALUES (?, ?, ?)", (cid, user, title))
        conn.commit()
        bot.send_message(message.chat.id, "✅ Channel Added!")
    except:
        bot.send_message(message.chat.id, "❌ Format error! Example: -1001, @user, MyChan")

@bot.callback_query_handler(func=lambda call: call.data.startswith("del_chan_"))
def delete_channel(call):
    db_id = call.data.split('_')[2]
    conn, cursor = get_db_cursor()
    cursor.execute("DELETE FROM channels WHERE id=?", (db_id,))
    conn.commit()
    bot.answer_callback_query(call.id, "Deleted!")
    admin_channels(call)

# --- STEP BY STEP POST CREATION ---

@bot.callback_query_handler(func=lambda call: call.data == "adm_add_post")
def post_init(call):
    admin_states[call.from_user.id] = {'buttons': []}
    msg = bot.send_message(call.message.chat.id, "📤 <b>Post Creation:</b>\nপোস্টের ক্যাপশন/টেক্সট পাঠান:")
    bot.register_next_step_handler(msg, post_media)

def post_media(message):
    admin_states[message.from_user.id]['title'] = message.text
    msg = bot.send_message(message.chat.id, "🖼 ফটো লিঙ্ক পাঠান (অথবা /skip দিন):")
    bot.register_next_step_handler(msg, post_buttons)

def post_buttons(message):
    admin_states[message.from_user.id]['media'] = message.text
    msg = bot.send_message(message.chat.id, "🔘 বাটন যোগ করুন। ফরম্যাট: <code>Name | Link</code>\nএকাধিক বাটন যোগ করতে বারবার পাঠান। শেষ হলে <b>/done</b> লিখুন।")
    bot.register_next_step_handler(msg, post_button_loop)

def post_button_loop(message):
    uid = message.from_user.id
    if message.text.lower() == '/done':
        # Preview
        data = admin_states[uid]
        btn_objs = [types.InlineKeyboardButton(text=b['name'], url=b['url']) for b in data['buttons']]
        markup = build_2_row_markup(btn_objs, verify=True)
        
        bot.send_message(message.chat.id, "👀 <b>Preview:</b>")
        if data['media'] != '/skip':
            bot.send_photo(message.chat.id, data['media'], caption=data['title'], reply_markup=markup)
        else:
            bot.send_message(message.chat.id, data['title'], reply_markup=markup)
        
        conf_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        conf_markup.add("✅ Confirm & Publish", "❌ Cancel")
        bot.send_message(message.chat.id, "পাবলিশ করতে চান?", reply_markup=conf_markup)
        bot.register_next_step_handler(message, post_finalize)
    else:
        try:
            n, l = message.text.split('|')
            admin_states[uid]['buttons'].append({'name': n.strip(), 'url': l.strip()})
            msg = bot.send_message(message.chat.id, f"✅ Added: {n.strip()}\nSend more or /done")
            bot.register_next_step_handler(msg, post_button_loop)
        except:
            msg = bot.send_message(message.chat.id, "❌ Error! Format: <code>Name | Link</code>")
            bot.register_next_step_handler(msg, post_button_loop)

def post_finalize(message):
    if message.text == "✅ Confirm & Publish":
        bot.send_message(message.chat.id, "🚀 <b>Post Published!</b>", reply_markup=types.ReplyKeyboardRemove())
    else:
        bot.send_message(message.chat.id, "❌ Cancelled.", reply_markup=types.ReplyKeyboardRemove())

@bot.callback_query_handler(func=lambda call: call.data == "adm_back")
def back_admin(call):
    admin_main(call.message)
    bot.delete_message(call.message.chat.id, call.message.message_id)

# --- START BOT ---
if __name__ == "__main__":
    # Start the keep-alive web server in a separate thread
    t = threading.Thread(target=run_web)
    t.start()
    
    print("Bot is starting...")
    while True:
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            logging.error(f"Main Loop Error: {e}")
            time.sleep(5)
