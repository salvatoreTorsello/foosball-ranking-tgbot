import os
import logging
import asyncio
import nest_asyncio
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from tg_bot import start, add_score, button_handler, add_player, handle_add_player, handle_confirmation, handle_cancel, list_players
from database import create_players_table

# Apply nest_asyncio to allow nested event loops if necessary
nest_asyncio.apply()

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    # Get the Telegram bot token from environment variables
    telegram_token = os.getenv('TELEGRAM_TOKEN')

    # Create the Application and pass it your bot's token
    application = ApplicationBuilder().token(telegram_token).build()

    # Initialize the SQLite database and create the necessary tables
    create_players_table()

    # Set commands that will show up in the "Menu" button
    await application.bot.set_my_commands([
        ("start", "Start the bot and view options"),
        ("ranking", "Request the ranking"),
        ("addscore", "Add a match score"),
        ("addplayer", "Add a player (admin only)"),
        ("listplayers", "List all players"),
    ])

    # Register command handlers
    application.add_handler(CommandHandler('start', start))

    # Handle Add Score command
    application.add_handler(CommandHandler('addscore', add_score))
    application.add_handler(CallbackQueryHandler(button_handler))

    # Handle Add Player command
    application.add_handler(CommandHandler('addplayer', add_player))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_add_player))
    application.add_handler(CallbackQueryHandler(handle_confirmation))  # Handles inline button presses for confirmation
    application.add_handler(CallbackQueryHandler(handle_cancel, pattern='cancel'))  # Handles inline button presses for cancellation

    # List players command
    application.add_handler(CommandHandler('listplayers', list_players))

    # Start the bot and keep polling for messages
    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())

