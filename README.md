# Supreme God Bot - Ultimate Edition

A feature-rich Telegram bot with force channel verification, multiple button posts, and admin management system.

## Features
- Force channel join verification
- Multiple button posts support
- Admin panel with full management
- Romantic/hot love themed popups
- Welcome photo system
- User statistics and tracking

## Deployment

### On Bot.Builder.co
1. Create new project
2. Upload `bot.py` and `requirements.txt`
3. Set environment variables:
   - `BOT_TOKEN`: Your Telegram bot token
   - `ADMIN_IDS`: Your Telegram ID (comma separated)
4. Deploy

### Local Deployment
1. Install Python 3.8+
2. Run: `pip install -r requirements.txt`
3. Set environment variables
4. Run: `python bot.py`

## Environment Variables
- `BOT_TOKEN`: Telegram bot token from @BotFather
- `ADMIN_IDS`: Admin user IDs (comma separated)
- `DB_NAME`: Database filename (optional, default: supreme_bot.db)

## Admin Commands
- `/admin` - Access admin panel
- Button-based management system

## User Commands
- `/start` - Start the bot and begin verification
