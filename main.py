import os
import logging
import asyncio
import nest_asyncio
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from tg_bot import start, add_score, button_handler
from database import connect_db

# Apply nest_asyncio to allow nested event loops if necessary
nest_asyncio.apply()

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    # Get the Telegram bot token from environment variables
    telegram_token = os.getenv('TELEGRAM_TOKEN')

    # Connect to the database
    db_connection = await connect_db()
    if db_connection:
        logger.info("Connected to the database")

    # Create the Application and pass it your bot's token
    application = ApplicationBuilder().token(telegram_token).build()

    # Set commands that will show up in the "Menu" button
    await application.bot.set_my_commands([
        ("start", "Start the bot and view options"),
        ("addplayer", "Add a player (admin only)"),
        ("addscore", "Add a match score"),
        ("ranking", "Request the raking"),
    ])

    # Register command handlers
    application.add_handler(CommandHandler('start', start))
    # application.add_handler(CommandHandler('addplayer', add_player))
    application.add_handler(CommandHandler('addscore', add_score))
    # application.add_handler(CommandHandler('ranking', ranking))
    # Handles inline button presses
    application.add_handler(CallbackQueryHandler(button_handler))

    # Start the bot and keep polling for messages
    await application.run_polling()

    # Ensure to close the database connection when the bot is stopped
    if db_connection:
        await db_connection.close()
        logger.info("Database connection closed")

if __name__ == '__main__':
    asyncio.run(main())

