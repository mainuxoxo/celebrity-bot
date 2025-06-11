from flask import Flask, request, render_template_string
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import re

app = Flask(__name__)

# HTML Template
HTML_TEMPLATE = """
<!doctype html>
<title>CelebrityBot Web</title>
<h2>Find Social Usernames</h2>
<form method="post">
  <input name="name" placeholder="Enter full name" required>
  <input type="submit" value="Search">
</form>
{% if usernames %}
  <h3>Possible Usernames:</h3>
  <ul>{% for u in usernames %}<li>{{ u }}</li>{% endfor %}</ul>
{% endif %}
"""

# Extract usernames from URLs
def extract_usernames(query):
    results = []
    usernames = set()

    with DDGS() as ddgs:
        for r in ddgs.text(query + " site:twitter.com OR site:instagram.com OR site:tiktok.com", max_results=15):
            url = r.get("href") or r.get("url")
            if url:
                match = re.search(r"(?:twitter|instagram|tiktok)\.com/([A-Za-z0-9_.]+)", url)
                if match:
                    usernames.add(f"{match.group(1)} ({url})")
    return sorted(usernames)

# --- Web route ---
@app.route('/', methods=['GET', 'POST'])
def home():
    usernames = []
    if request.method == 'POST':
        name = request.form['name']
        usernames = extract_usernames(name)
    return render_template_string(HTML_TEMPLATE, usernames=usernames)

# --- Telegram Bot ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! Send me a name and I'll look for social usernames.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    usernames = extract_usernames(name)
    if usernames:
        await update.message.reply_text("Found:\n" + "\n".join(usernames))
    else:
        await update.message.reply_text("No usernames found.")

# Start Telegram bot
def start_bot():
    import os
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if token:
        app_bot = ApplicationBuilder().token(token).build()
        app_bot.add_handler(CommandHandler("start", start))
        app_bot.add_handler(CommandHandler("help", start))
        app_bot.add_handler(CommandHandler("find", handle_message))
        app_bot.add_handler(CommandHandler("", handle_message))
        app_bot.run_polling()

# Run both web + bot
if __name__ == "__main__":
    import threading
    threading.Thread(target=start_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=8080)
