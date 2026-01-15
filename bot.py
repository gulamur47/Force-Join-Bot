import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

# আপনার বট টোকেন
TOKEN = '8510787985:AAGZ9KA-16hl8Tc3H1_GM-D3qCMIGygOUkw' 

# আপনার ৫টি চ্যানেলের ইউজারনেম
CHANNELS = ['@virallink259', '@viralfb24', '@fbviral24', '@viralfacebook9', '@viralexpress1']

# বাটনগুলোতে যে নাম দেখাতে চান
CHANNEL_DISPLAY_NAMES = ["Viral Link 🎬", "Viral FB 🚀", "FB Viral 🔥", "Facebook Viral 📽️", "Viral Express ⚡"]

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def check_all_joined(user_id, context):
    not_joined_indices = []
    for i, channel in enumerate(CHANNELS):
        try:
            member = await context.bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                not_joined_indices.append(i)
        except Exception:
            not_joined_indices.append(i)
    return not_joined_indices

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    # ইউজারের নাম স্টাইলিশ ভাবে নেওয়া (HTML Format)
    # এখানে 👤 প্রতীক এবং Bold স্টাইল ব্যবহার করা হয়েছে
    stylish_name = f"👤 <b>{user.first_name}</b>"
    
    not_joined_indices = await check_all_joined(user_id, context)

    if not not_joined_indices:
        await update.message.reply_text(f"✅ স্বাগতম {stylish_name}!\nআপনি সব চ্যানেলে জয়েন করেছেন। এখন ভিডিও দেখতে পারেন।", parse_mode=ParseMode.HTML)
    else:
        buttons = []
        for index in not_joined_indices:
            name = CHANNEL_DISPLAY_NAMES[index]
            link = CHANNELS[index][1:]
            buttons.append([InlineKeyboardButton(f"Join {name}", url=f"https://t.me/{link}")])
        
        buttons.append([InlineKeyboardButton("Check Joined ✅", callback_data="check_status")])
        
        # আপনার কাঙ্ক্ষিত মেসেজ স্টাইলিশ নামের সাথে
        caption = (
            f"Hello {stylish_name},\n\n"
            "🚨 <b>Attention Please!</b>\n\n"
            "Viral ভিডিও দেখার আগে আমাদের Channel Join করা বাধ্যতামূলক।\n"
            "চ্যানেল Join না করলে ভিডিও অ্যাক্সেস পাওয়া যাবে না ❌\n\n"
            "Join করে <b>Check Joined</b> ক্লিক করুন ✅"
        )
        
        await update.message.reply_text(
            caption, 
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.HTML # এটি স্টাইলিশ নাম এবং বোল্ড টেক্সট দেখানোর জন্য জরুরি
        )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    stylish_name = f"<b>{user.first_name}</b>"
    
    not_joined_indices = await check_all_joined(user.id, context)
    
    if not not_joined_indices:
        await query.answer(f"ধন্যবাদ {user.first_name}! জয়েন হয়েছে।", show_alert=True)
        await query.edit_message_text(f"✅ অভিনন্দন {stylish_name}!\nআপনি সফলভাবে সব চ্যানেলে জয়েন করেছেন।", parse_mode=ParseMode.HTML)
    else:
        await query.answer("❌ আপনি এখনও সব চ্যানেলে জয়েন করেননি!", show_alert=True)

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    print("বটটি এখন নাম মেনশন ফিচারের সাথে চালু হয়েছে...")
    app.run_polling()
