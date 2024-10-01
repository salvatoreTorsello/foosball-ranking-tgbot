import os
import logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, CallbackContext
from telegram.constants import ChatMemberStatus
from database import add_player_to_db  # Import the function to add players to the database
import re

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the Telegram bot token from environment variables
telegram_token = os.getenv('TELEGRAM_TOKEN')

# Check if the user is an admin or the group owner
async def is_user_admin(chat, user_id, context):
    member = await chat.get_member(user_id)
    return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]

# Start command handler that shows the keyboard with buttons for "Add Player", "Add Score", and "Ranking"
async def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    chat = update.message.chat

    # Define the basic keyboard buttons for all users
    keyboard = [
        [KeyboardButton("Add Score")],  # Add Score button for everyone
        [KeyboardButton("Ranking")]
    ]

    # Check if the user is an admin or group owner, if so, add the "Add Player" button
    if await is_user_admin(chat, user_id, context):
        keyboard.insert(0, [KeyboardButton("Add Player")])  # Add Player is only for admins

    # Show the appropriate keyboard based on user role
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False, resize_keyboard=True)

    # Send the message with the dynamic keyboard buttons
    await update.message.reply_text(
        'Welcome to the Foosball Bot! Please choose an option.',
        reply_markup=reply_markup
    )

# Admin-only command to add players
async def addplayer(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    chat = update.message.chat

    # Check if the user is an admin or group owner
    if not await is_user_admin(chat, user_id, context):
        await update.message.reply_text("Only group administrators can add players.")
        return

    # Expecting the admin to send the player's full name after this command
    cancel_keyboard = [[KeyboardButton("Cancel")]]
    reply_markup = ReplyKeyboardMarkup(cancel_keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text("Please send the player's full name in the format: Firstname Lastname", reply_markup=reply_markup)

    # Set the context flag for awaiting the player's name
    context.user_data['awaiting_player_name'] = True

# Function to handle adding a score
async def add_score(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    # Expecting the user to send the score in the format "Player1-Player2 vs Player3-Player4: score1-score2"
    cancel_keyboard = [[KeyboardButton("Cancel")]]
    reply_markup = ReplyKeyboardMarkup(cancel_keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(
        "Please enter the score in the format: Player1-Player2 vs Player3-Player4: score1-score2",
        reply_markup=reply_markup
    )

    # Set the context flag for awaiting the score input
    context.user_data['awaiting_score'] = True

# Handle the player's name after the /addplayer command or the "Add Player" button
async def handle_player_name(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    # Check if we are awaiting a player name input
    if context.user_data.get('awaiting_player_name'):
        # Get the player's full name from the message
        player_name = update.message.text.strip()

        # Add the player to the database
        await add_player_to_db(player_name)

        # Confirm the player has been added
        await update.message.reply_text(f"Player '{player_name}' has been added to the database.")

        # Reset the flag and return to the main menu
        context.user_data['awaiting_player_name'] = False
        await start(update, context)
    else:
        await update.message.reply_text("Please use the /addplayer command first.")

# Handle the score input after pressing the "Add Score" button
async def handle_score_input(update: Update, context: CallbackContext):
    user_input = update.message.text
    user_id = update.message.from_user.id

    if context.user_data.get('awaiting_score'):
        # Extract score and players from the input (expecting proper format)
        score_pattern = r"([\w\s]+)-([\w\s]+)\s+vs\s+([\w\s]+)-([\w\s]+):\s*(\d+)-(\d+)"
        match = re.match(score_pattern, user_input)

        if match:
            player1 = match.group(1).strip()
            player2 = match.group(2).strip()
            player3 = match.group(3).strip()
            player4 = match.group(4).strip()
            score1 = match.group(5).strip()
            score2 = match.group(6).strip()

            # For now, just confirm the score
            await update.message.reply_text(
                f"Score confirmed!\n"
                f"Team 1: {player1} and {player2} scored {score1}\n"
                f"Team 2: {player3} and {player4} scored {score2}"
            )

            # Reset the flag
            context.user_data['awaiting_score'] = False

            # Return to the main menu
            await start(update, context)
        else:
            await update.message.reply_text("Invalid format! Please use the correct format or type 'Cancel' to stop.")

# Cancel button handler to stop ongoing operations
async def cancel(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    # Reset any flags for ongoing operations
    context.user_data['awaiting_player_name'] = False
    context.user_data['awaiting_score'] = False

    # Inform the user that the operation has been canceled
    await update.message.reply_text(
        "Operation canceled.",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("Add Player"), KeyboardButton("Add Score"), KeyboardButton("Ranking")]], resize_keyboard=True)
    )
# Message handler for handling user messages (including player name input, score input, and cancel)
async def message_handler(update: Update, context: CallbackContext):
    user_input = update.message.text

    if user_input == "Cancel":
        await cancel(update, context)
    elif user_input == "Add Player":
        await addplayer(update, context)
    elif user_input == "Add Score":
        await add_score(update, context)
    elif user_input == "Ranking":
        await ranking(update, context)
    elif context.user_data.get('awaiting_player_name'):
        await handle_player_name(update, context)
    elif context.user_data.get('awaiting_score'):
        await handle_score_input(update, context)
    else:
        # Handle unrecognized commands or inputs
        await update.message.reply_text("Please use the buttons or valid commands.")
