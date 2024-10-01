import os
import logging
import asyncio
import nest_asyncio
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from tg_bot import start, addplayer, add_score, message_handler, cancel
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

    # Register command handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('addplayer', addplayer))
    application.add_handler(CommandHandler('addscore', add_score))  # Handler for Add Score button
    application.add_handler(CommandHandler('cancel', cancel))  # Handler for canceling operations
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))  # Handles text input like player names and scores

    # Start the bot and keep polling for messages
    await application.run_polling()

    # Ensure to close the database connection when the bot is stopped
    if db_connection:
        await db_connection.close()
        logger.info("Database connection closed")

if __name__ == '__main__':
    asyncio.run(main())

