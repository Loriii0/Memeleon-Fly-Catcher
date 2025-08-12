import telebot
from telebot import types
import time

# YOUR BOT TOKEN
TOKEN = '8131872814:AAHlwTQyyVkYYsCJlRPVJebyeDAUifRlTbA'

bot = telebot.TeleBot(TOKEN)

# ... rest of your bot code ...

# At the VERY BOTTOM, before bot.polling():
if __name__ == '__main__':
    print("🦎 MemeLeon Game Bot Started!")
    bot.polling(none_stop=True)
    

# Store user scores
user_scores = {}
high_scores = []

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

@bot.message_handler(func=lambda message: message.text == '🎮 Play Game')
def play_game(message):
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

    bot.send_message(
        message.chat.id,
        "🦎 *MemeLeon Tech™ Fly Catcher* 🦎\n\n"
        "🎯 Click to shoot your tongue!\n"
        "🪰 Catch regular flies = 10 pts\n"
        "✨ Catch golden flies = 50 pts\n"
        "❤️ Don't let flies escape - 3 lives!\n"
        "🔥 Build combos for mega scores!\n\n"
        "Can you beat the high score? 🏆\n\n"
        "Join us: @MemeLeonSol",
        parse_mode='Markdown',
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text == '🏆 High Scores')
def show_high_scores(message):  # RENAMED FUNCTION
    bot.send_message(
        message.chat.id,
        "🏆 *TOP HUNTERS* 🏆\n\n"
        "1. 🥇 @Player1 - 1,500 pts\n"
        "2. 🥈 @Player2 - 1,200 pts\n"
        "3. 🥉 @Player3 - 900 pts\n\n"
        "Submit your score!",
        parse_mode='Markdown'
    )

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

@bot.message_handler(func=lambda message: True)
def echo(message):
    bot.reply_to(message, "Type /start to begin!")

# RUN THE BOT
if __name__ == '__main__':
    print("🦎 Bot starting...")
    print("Game URL: https://memeleon.world/flycatcher.html")
    print("Community: @MemeLeonSol")
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Error: {e}")