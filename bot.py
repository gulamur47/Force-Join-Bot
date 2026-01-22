import telebot
from telebot import types
import sqlite3
import json

# --- কনফিগুরেশন ---
API_TOKEN = '8216066342:AAHLCoA0F0HGpdLRykTGcomTY7jN4sQwRwU'
ADMIN_ID = 6406804999
bot = telebot.TeleBot(API_TOKEN)

# --- ডাটাবেস সেটআপ ---
def init_db():
    conn = sqlite3.connect('hot_love_bot.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, verified INTEGER DEFAULT 0)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS channels (id INTEGER PRIMARY KEY AUTOINCREMENT, channel_id TEXT, username TEXT, title TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)''')
    # ডিফল্ট সেটিংস
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('welcome_text', '💖 Hey {name}! \n\nUfff! Tumi ki amar sathe thakte cao? Tahole age nicher channel gulo join koro baby! 💋')")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('welcome_photo', 'https://telegra.ph/file/example_image.jpg')")
    conn.commit()
    return conn, cursor

conn, cursor = init_db()

# এডমিন স্টেট ট্র্যাকিং
admin_states = {}

# --- হেল্পার ফাংশন (২-রো বাটন গ্রিড) ---
def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu

def check_join(user_id):
    cursor.execute("SELECT channel_id FROM channels")
    chans = cursor.fetchall()
    for (cid,) in chans:
        try:
            status = bot.get_chat_member(cid, user_id).status
            if status in ['left', 'kicked']:
                return False
        except:
            continue
    return True

# --- ইউজার ফ্লো ---

@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.from_user.id
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()

    cursor.execute("SELECT value FROM settings WHERE key='welcome_text'")
    w_text = cursor.fetchone()[0]
    cursor.execute("SELECT value FROM settings WHERE key='welcome_photo'")
    w_photo = cursor.fetchone()[0]

    # বাটন তৈরি (২-রো ফরম্যাট)
    cursor.execute("SELECT title, username FROM channels")
    all_chans = cursor.fetchall()
    
    btn_list = []
    for title, user in all_chans:
        btn_list.append(types.InlineKeyboardButton(text=f"📢 {title}", url=f"https://t.me/{user.replace('@','')}"))
    
    markup = types.InlineKeyboardMarkup(build_menu(btn_list, n_cols=2))
    markup.add(types.InlineKeyboardButton(text="✅ Verified ❤️", callback_data="verify_me"))

    try:
        bot.send_photo(message.chat.id, w_photo, caption=w_text.format(name=message.from_user.first_name), reply_markup=markup)
    except:
        bot.send_message(message.chat.id, w_text.format(name=message.from_user.first_name), reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "verify_me")
def verify_logic(call):
    if check_join(call.from_user.id):
        bot.answer_callback_query(call.id, "Uffff 😍 Tumi verified ❤️ Next surprise unlock 🔥", show_alert=True)
        # Watch Now বাটন দেখানো
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text="🔥 Watch Now 🔥", callback_data="open_content"))
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
    else:
        bot.answer_callback_query(call.id, "Awww 😘 Age sob channel join koro baby 💔", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == "open_content")
def open_content(call):
    if check_join(call.from_user.id):
        bot.send_message(call.message.chat.id, "😘 Here is your special content baby! 🔥✨")
    else:
        bot.answer_callback_query(call.id, "Awww 😘 Age sob channel join koro baby 💔", show_alert=True)

# --- এডমিন প্যানেল ---

@bot.message_handler(commands=['admin'])
def admin_menu(message):
    if message.from_user.id != ADMIN_ID:
        return
    
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("📝 Add Post", callback_data="adm_add_post"), 
               types.InlineKeyboardButton("📢 Channels", callback_data="adm_chans"))
    markup.row(types.InlineKeyboardButton("🖼 Welcome Msg/Photo", callback_data="adm_set_welcome"))
    
    bot.send_message(message.chat.id, "🔥 **Admin Panel**\nSelect an option below:", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("adm_"))
def admin_callbacks(call):
    if call.from_user.id != ADMIN_ID: return

    if call.data == "adm_chans":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("➕ Add New Channel", callback_data="adm_new_chan"))
        markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="adm_back"))
        bot.edit_message_text("Channel Management:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == "adm_new_chan":
        msg = bot.send_message(call.message.chat.id, "চ্যানেলের তথ্য দিন এই ফরম্যাটে:\n`ID,Username,Title` \n(Example: `-1001234,@mychan,Hot Content`)")
        bot.register_next_step_handler(msg, save_new_chan)

    elif call.data == "adm_add_post":
        admin_states[call.from_user.id] = {'buttons': []}
        msg = bot.send_message(call.message.chat.id, "পোস্টের জন্য একটি Title/Caption লিখুন:")
        bot.register_next_step_handler(msg, post_step_media)

def save_new_chan(message):
    try:
        cid, user, title = message.text.split(',')
        cursor.execute("INSERT INTO channels (channel_id, username, title) VALUES (?, ?, ?)", (cid.strip(), user.strip(), title.strip()))
        conn.commit()
        bot.send_message(message.chat.id, "✅ Channel successfully added!")
    except:
        bot.send_message(message.chat.id, "❌ Format Error! /admin এ গিয়ে আবার চেষ্টা করুন।")

# --- মাল্টিপল বাটন পোস্ট ক্রিয়েশন ফ্লো ---

def post_step_media(message):
    admin_states[message.from_user.id]['title'] = message.text
    msg = bot.send_message(message.chat.id, "এখন একটি ফটো বা ভিডিওর URL দিন (অথবা /skip):")
    bot.register_next_step_handler(msg, post_step_btn_ask)

def post_step_btn_ask(message):
    admin_states[message.from_user.id]['media'] = message.text
    msg = bot.send_message(message.chat.id, "বাটন এড করতে চাইলে নাম এবং লিঙ্ক দিন:\n`ButtonName | URL` \n\n(বাটন এড করা শেষ হলে `/done` লিখুন)")
    bot.register_next_step_handler(msg, post_step_btn_loop)

def post_step_btn_loop(message):
    if message.text == '/done':
        # প্রিভিউ দেখানো
        data = admin_states[message.from_user.id]
        btn_objs = []
        for b in data['buttons']:
            btn_objs.append(types.InlineKeyboardButton(text=b['name'], url=b['link']))
        
        markup = types.InlineKeyboardMarkup(build_menu(btn_objs, n_cols=2))
        markup.add(types.InlineKeyboardButton(text="✅ Verified ❤️", callback_data="verify_me"))

        bot.send_message(message.chat.id, "👀 **Post Preview:**", parse_mode="Markdown")
        if data['media'] != '/skip' and data['media'].startswith('http'):
            bot.send_photo(message.chat.id, data['media'], caption=data['title'], reply_markup=markup)
        else:
            bot.send_message(message.chat.id, data['title'], reply_markup=markup)
        
        bot.send_message(message.chat.id, "সব ঠিক থাকলে কনফার্ম করুন!", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("Confirm & Publish"))
    else:
        try:
            name, link = message.text.split('|')
            admin_states[message.from_user.id]['buttons'].append({'name': name.strip(), 'link': link.strip()})
            msg = bot.send_message(message.chat.id, "বাটন এড হয়েছে! আরও এড করতে চাইলে একইভাবে দিন অথবা `/done` লিখুন।")
            bot.register_next_step_handler(msg, post_step_btn_loop)
        except:
            msg = bot.send_message(message.chat.id, "❌ ভুল ফরম্যাট! আবার চেষ্টা করুন: `Name | Link` অথবা `/done` দিন।")
            bot.register_next_step_handler(msg, post_step_btn_loop)

@bot.message_handler(func=lambda m: m.text == "Confirm & Publish")
def publish_post(message):
    if message.from_user.id != ADMIN_ID: return
    bot.send_message(message.chat.id, "🚀 Post Published to all users! (Logic implementation pending for mass blast)", reply_markup=types.ReplyKeyboardRemove())

# --- সেটিংস ---
@bot.callback_query_handler(func=lambda call: call.data == "adm_set_welcome")
def set_welcome(call):
    msg = bot.send_message(call.message.chat.id, "নতুন Welcome টেক্সট দিন (ইউজার নাম দেখাতে `{name}` ব্যবহার করুন):")
    bot.register_next_step_handler(msg, update_w_text)

def update_w_text(message):
    cursor.execute("UPDATE settings SET value=? WHERE key='welcome_text'", (message.text,))
    conn.commit()
    bot.send_message(message.chat.id, "✅ Welcome text updated!")

# --- বট স্টার্ট ---
if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling()
