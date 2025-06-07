from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from utils import normalize_query, search_links

TOKEN = "8190665855:AAEeqLfymMfbITw6ggYFPfoEG5adt6gHf68"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Use /find <name>, [nationality], [occupation]")

async def find(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = " ".join(context.args)
    if not args:
        await update.message.reply_text("Usage: /find <name>, [nationality], [occupation]")
        return

    parts = [part.strip() for part in args.split(",")]
    name = parts[0]
    nationality = parts[1] if len(parts) > 1 else None
    occupation = parts[2] if len(parts) > 2 else None

    query = normalize_query(name, nationality, occupation)
    await update.message.reply_text(f"Searching for: {query} 🔍")

    links = search_links(query)
    if not links:
        await update.message.reply_text("No social media found 😔")
        return

    buttons = [[InlineKeyboardButton(text=link.split("//")[-1], url=link)] for link in links]
    reply_markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text("Found social media profiles:", reply_markup=reply_markup)

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("find", find))
    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
