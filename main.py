import os
import telebot
from telebot import types
import time
import sqlite3
import json
from datetime import datetime

# Load token from .env file or environment variable
def load_token():
    # First try environment variable
    token = os.environ.get('BOT_TOKEN')
    if token:
        return token

    # Then try .env file
    try:
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('BOT_TOKEN='):
                    return line.split('=', 1)[1].strip()
    except FileNotFoundError:
        pass

    print("ERROR: No BOT_TOKEN found!")
    print("Please set BOT_TOKEN in .env file or as environment variable")
    exit(1)

TOKEN = load_token()

bot = telebot.TeleBot(TOKEN)

# Main group chat ID (you can get this by forwarding a message from the group to @userinfobot)
MAIN_GROUP = "@MemeleonSol"  # Can use @username or -100123456789 chat ID

# Initialize SQLite Database
def init_db():
    conn = sqlite3.connect('flycatcher_scores.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS scores
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  username TEXT,
                  first_name TEXT,
                  score INTEGER,
                  chat_id INTEGER,
                  chat_type TEXT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

# Database helper functions
def add_score(user_id, username, first_name, score, chat_id, chat_type):
    conn = sqlite3.connect('flycatcher_scores.db')
    c = conn.cursor()
    c.execute('''INSERT INTO scores (user_id, username, first_name, score, chat_id, chat_type)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (user_id, username, first_name, score, chat_id, chat_type))
    conn.commit()
    conn.close()

def get_top_scores(limit=10):
    conn = sqlite3.connect('flycatcher_scores.db')
    c = conn.cursor()
    c.execute('''SELECT user_id, username, first_name, MAX(score) as best_score
                 FROM scores
                 GROUP BY user_id
                 ORDER BY best_score DESC
                 LIMIT ?''', (limit,))
    results = c.fetchall()
    conn.close()
    return results

def get_user_best(user_id):
    conn = sqlite3.connect('flycatcher_scores.db')
    c = conn.cursor()
    c.execute('''SELECT MAX(score) FROM scores WHERE user_id = ?''', (user_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result[0] else 0

def get_user_rank(user_id):
    conn = sqlite3.connect('flycatcher_scores.db')
    c = conn.cursor()
    # Get user's best score
    user_best = get_user_best(user_id)
    if user_best == 0:
        conn.close()
        return 0  # User has no scores
    # Count how many users have a better best score
    c.execute('''SELECT COUNT(DISTINCT user_id)
                 FROM (SELECT user_id, MAX(score) as best_score
                       FROM scores
                       GROUP BY user_id
                       HAVING best_score > ?)''', (user_best,))
    result = c.fetchone()
    conn.close()
    # Rank is count of better users + 1
    return result[0] + 1 if result else 1

# Initialize database on startup
init_db()

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    play_btn = types.KeyboardButton('🎮 Play Game')
    scores_btn = types.KeyboardButton('🏆 High Scores')
    info_btn = types.KeyboardButton('ℹ️ About')
    website_btn = types.KeyboardButton('🌐 Visit Website')
    markup.add(play_btn, scores_btn, info_btn, website_btn)

    bot.send_message(
        message.chat.id,
        "🦎 *MEMELEON FLY CATCHER* 🦎\n\n"
        "Welcome to the official MemeLeon Tech™ game!\n\n"
        "Tap the buttons below to start!",
        parse_mode='Markdown',
        reply_markup=markup
    )

def send_game(chat_id, context="private"):
    """Send the game with appropriate context"""
    game_url = f"https://memeleon.world/flycatcher.html?v={int(time.time())}"

    markup = types.InlineKeyboardMarkup()

    web_app = types.WebAppInfo(game_url)
    play_button = types.InlineKeyboardButton(
        text="🎮 PLAY NOW",
        web_app=web_app
    )

    browser_button = types.InlineKeyboardButton(
        text="🌐 Open in Browser",
        url=game_url
    )

    markup.add(play_button)
    markup.add(browser_button)

    context_msg = "Your score will be posted here!" if context == "group" else "Play and beat the high score!"

    bot.send_message(
        chat_id,
        "🦎 *MemeLeon Tech™ Fly Catcher* 🦎\n\n"
        "🎯 Click to shoot your tongue!\n"
        "🪰 Catch regular flies = 10 pts\n"
        "✨ Catch golden flies = 50 pts\n"
        "❤️ Don't let flies escape - 3 lives!\n"
        "🔥 Build combos for mega scores!\n\n"
        f"Can you beat the high score? 🏆\n\n"
        f"{context_msg}\n\n"
        "Join us: @MemeLeonSol",
        parse_mode='Markdown',
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text == '🎮 Play Game')
def play_game(message):
    send_game(message.chat.id, "private")

@bot.message_handler(commands=['flycatcher', 'launchflycatcher'])
def flycatcher_command(message):
    """Launch game from any chat (private or group)"""
    context = "group" if message.chat.type in ['group', 'supergroup'] else "private"
    send_game(message.chat.id, context)

def display_leaderboard(message):
    """Display the leaderboard - can be used from button or command"""
    top_scores = get_top_scores(10)

    if not top_scores:
        bot.send_message(
            message.chat.id,
            "🏆 *TOP HUNTERS* 🏆\n\n"
            "No scores yet! Be the first to play! 🦎\n\n"
            "Use /flycatcher to start playing!",
            parse_mode='Markdown'
        )
        return

    medals = ['🥇', '🥈', '🥉']
    leaderboard_text = "🏆 *TOP HUNTERS* 🏆\n\n"

    for idx, (user_id, username, first_name, score) in enumerate(top_scores):
        medal = medals[idx] if idx < 3 else f"{idx + 1}."
        display_name = f"@{username}" if username else first_name
        leaderboard_text += f"{medal} {display_name} - {score:,} pts\n"

    # Add user's personal stats if they've played
    user_best = get_user_best(message.from_user.id)
    if user_best > 0:
        user_rank = get_user_rank(message.from_user.id)
        leaderboard_text += f"\n📊 Your Best: {user_best:,} pts (Rank #{user_rank})"

    bot.send_message(
        message.chat.id,
        leaderboard_text,
        parse_mode='Markdown'
    )

@bot.message_handler(func=lambda message: message.text == '🏆 High Scores')
def show_high_scores(message):
    display_leaderboard(message)

@bot.message_handler(commands=['leaderboard', 'highscores', 'scores'])
def leaderboard_command(message):
    """Show leaderboard - works in any chat"""
    display_leaderboard(message)

@bot.message_handler(func=lambda message: message.text == 'ℹ️ About')
def about(message):
    markup = types.InlineKeyboardMarkup()

    web_btn = types.InlineKeyboardButton("🌐 Website", url="https://memeleon.world")
    tg_btn = types.InlineKeyboardButton("💬 Join", url="https://t.me/MemeLeonSol")

    markup.add(web_btn, tg_btn)

    bot.send_message(
        message.chat.id,
        "🦎 *MEMELEON TECH™* 🦎\n\n"
        "We build:\n"
        "• Games & Bots\n"
        "• Smart Contracts\n"
        "• Websites\n\n"
        "Contact: @MemeFreedomFighter",
        parse_mode='Markdown',
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text == '🌐 Visit Website')
def website(message):
    markup = types.InlineKeyboardMarkup()

    btn = types.InlineKeyboardButton("🌐 MemeLeon.World", url="https://memeleon.world")
    markup.add(btn)

    bot.send_message(
        message.chat.id,
        "Visit our website!",
        reply_markup=markup
    )

@bot.message_handler(content_types=['web_app_data'])
def handle_web_app_data(message):
    """Handle score submission from the WebApp game"""
    try:
        # Parse the data sent from the game
        data = json.loads(message.web_app_data.data)
        score = int(data.get('score', 0))

        if score <= 0:
            bot.reply_to(message, "Invalid score! 🤔")
            return

        # Get user info
        user = message.from_user
        user_id = user.id
        username = user.username
        first_name = user.first_name
        chat_id = message.chat.id
        chat_type = message.chat.type

        # Save score to database
        add_score(user_id, username, first_name, score, chat_id, chat_type)

        # Get user's best score and rank
        user_best = get_user_best(user_id)
        is_new_best = score >= user_best

        # Format username for display
        display_name = f"@{username}" if username else first_name

        # Create response message
        if is_new_best:
            response = f"🎉 *NEW PERSONAL BEST!* 🎉\n\n"
        else:
            response = f"🦎 *Score Recorded!* 🦎\n\n"

        response += f"👤 {display_name}\n"
        response += f"🎯 Score: *{score:,}* pts\n"
        response += f"🏆 Your Best: {user_best:,} pts\n"

        # Get rank
        rank = get_user_rank(user_id)
        response += f"📊 Global Rank: #{rank}\n"

        # Check if it's a top score
        top_scores = get_top_scores(10)
        is_top_10 = any(user_id == top_user_id for top_user_id, _, _, _ in top_scores[:10])

        if is_top_10:
            response += f"\n🔥 You're in the TOP 10! 🔥"

        # Handle posting to groups
        if chat_type in ['group', 'supergroup']:
            # Score was submitted from a group - post it there
            bot.send_message(
                chat_id,
                response,
                parse_mode='Markdown'
            )
        else:
            # Score from private chat
            # Send confirmation to user
            markup = types.InlineKeyboardMarkup()
            share_btn = types.InlineKeyboardButton(
                "📢 Share to @MemeleonSol",
                url=f"https://t.me/MemeleonSol"
            )
            markup.add(share_btn)

            bot.send_message(
                chat_id,
                response + "\n\n💬 Share your score with the community!",
                parse_mode='Markdown',
                reply_markup=markup
            )

            # If it's a top score or personal best, also post to main group
            if is_top_10 and is_new_best:
                try:
                    group_msg = f"🔥 *NEW HIGH SCORE!* 🔥\n\n"
                    group_msg += f"👤 {display_name}\n"
                    group_msg += f"🎯 Score: *{score:,}* pts\n"
                    group_msg += f"📊 Rank: #{rank}\n\n"
                    group_msg += f"Can you beat it? Use /flycatcher to play! 🦎"

                    bot.send_message(
                        MAIN_GROUP,
                        group_msg,
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    print(f"Could not post to main group: {e}")

    except json.JSONDecodeError:
        bot.reply_to(message, "Error processing score data! 😕")
    except Exception as e:
        print(f"Error handling web app data: {e}")
        bot.reply_to(message, "An error occurred! Please try again. 🔄")

@bot.message_handler(func=lambda message: True)
def echo(message):
    bot.reply_to(message, "Type /start to begin or /flycatcher to play! 🦎")

# RUN THE BOT
if __name__ == '__main__':
    print("🦎 Bot starting...")
    print("Game URL: https://memeleon.world/flycatcher.html")
    print("Community: @MemeLeonSol")
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Error: {e}")
