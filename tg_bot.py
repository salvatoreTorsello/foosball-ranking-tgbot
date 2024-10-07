import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import database as db

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

players = {"test1", "test2", "test3", "test4"}

# Start command handler that shows the available options
async def start(update: Update, context: CallbackContext):
    start_message = (
        'Welcome to the Foosball Bot!\n'
        'Use the /addplayer command to add a player (admin only).\n'
        'Use the /addscore command to add a match score.\n'
        'Use the /ranking command to request the foosball ranking.\n'
        'Use the /listplayers command to view all players.'
    )
    await update.message.reply_text(start_message)

# States for Player and Score functionality
FIRST_NAME, LAST_NAME, NICKNAME, CONFIRMATION, PLAYER1, PLAYER2, PLAYER3, PLAYER4, TEAM1_SCORE, TEAM2_SCORE = range(10)

# Inline keyboard for cancel button
def get_cancel_button():
    keyboard = [[InlineKeyboardButton("Cancel", callback_data='cancel')]]
    return InlineKeyboardMarkup(keyboard)

# Inline keyboard for confirmation and cancel buttons
def get_confirmation_buttons():
    keyboard = [
        [
            InlineKeyboardButton("Confirm", callback_data='confirm'),
            InlineKeyboardButton("Cancel", callback_data='cancel')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# Start the add_player process
async def add_player(update: Update, context: CallbackContext):
    await update.message.reply_text("Please enter the player's first name:", reply_markup=get_cancel_button())
    context.user_data['state'] = FIRST_NAME  # Set the conversation state to FIRST_NAME

# Handle text input for adding a player
async def handle_add_player(update: Update, context: CallbackContext):
    state = context.user_data.get('state')

    if state == FIRST_NAME:
        context.user_data['first_name'] = update.message.text
        await update.message.reply_text(
            f"First Name: {context.user_data['first_name']}\nPlease enter the player's last name:",
            reply_markup=get_cancel_button()
        )
        context.user_data['state'] = LAST_NAME  # Move to LAST_NAME state

    elif state == LAST_NAME:
        context.user_data['last_name'] = update.message.text
        await update.message.reply_text(
            f"First Name: {context.user_data['first_name']}\n"
            f"Last Name: {context.user_data['last_name']}\n"
            "Please enter the player's nickname (optional, type 'None' if no nickname):",
            reply_markup=get_cancel_button()
        )
        context.user_data['state'] = NICKNAME  # Move to NICKNAME state

    elif state == NICKNAME:
        nickname = update.message.text
        if nickname.lower() == 'none':
            nickname = None
        context.user_data['nickname'] = nickname

        # Show confirmation message with inline buttons
        await update.message.reply_text(
            f"Please confirm the player details:\n"
            f"First Name: {context.user_data['first_name']}\n"
            f"Last Name: {context.user_data['last_name']}\n"
            f"Nickname: {context.user_data['nickname']}\n",
            reply_markup=get_confirmation_buttons()
        )
        context.user_data['state'] = CONFIRMATION  # Move to CONFIRMATION state

# Start the add_score process
async def add_score(update: Update, context: CallbackContext):
    await update.message.reply_text("Select Player 1:", reply_markup=get_cancel_button())
    context.user_data['state'] = PLAYER1  # Set the conversation state to PLAYER1

# Handle button callbacks for player selection
async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()  # Acknowledge the button press

    if query.data == "cancel":
        await handle_cancel(update, context)
        return

    # Player selection logic
    if context.user_data['state'] == PLAYER1:
        context.user_data['player1'] = query.data.split(":")[1]
        context.user_data['state'] = PLAYER2
        await query.edit_message_text(f"Player 1: {context.user_data['player1']}\nSelect Player 2:", reply_markup=get_cancel_button())

    elif context.user_data['state'] == PLAYER2:
        context.user_data['player2'] = query.data.split(":")[1]
        context.user_data['state'] = PLAYER3
        await query.edit_message_text(f"Player 1: {context.user_data['player1']}\nPlayer 2: {context.user_data['player2']}\nSelect Player 3:", reply_markup=get_cancel_button())

    elif context.user_data['state'] == PLAYER3:
        context.user_data['player3'] = query.data.split(":")[1]
        context.user_data['state'] = PLAYER4
        await query.edit_message_text(f"Player 1: {context.user_data['player1']}\nPlayer 2: {context.user_data['player2']}\nPlayer 3: {context.user_data['player3']}\nSelect Player 4:", reply_markup=get_cancel_button())

    elif context.user_data['state'] == PLAYER4:
        context.user_data['player4'] = query.data.split(":")[1]
        context.user_data['state'] = TEAM1_SCORE
        await ask_for_team1_score(query)

# Ask for Team 1's score
async def ask_for_team1_score(query):
    score_buttons = [[InlineKeyboardButton(f"{i}", callback_data=f"team1_score:{i}") for i in range(0, 10)]]
    score_buttons.append([InlineKeyboardButton("Cancel", callback_data="cancel")])  # Add cancel button
    reply_markup = InlineKeyboardMarkup(score_buttons)

    await query.edit_message_text(
        f"Team 1: {query.data['player1']} and {query.data['player2']}\n"
        f"Team 2: {query.data['player3']} and {query.data['player4']}\n\n"
        "Select Team 1's score:",
        reply_markup=reply_markup
    )

# Handle score selection
async def handle_score_selection(query, context):
    if context.user_data['state'] == TEAM1_SCORE:
        context.user_data['team1_score'] = query.data.split(":")[1]
        context.user_data['state'] = TEAM2_SCORE
        await ask_for_team2_score(query)

    elif context.user_data['state'] == TEAM2_SCORE:
        context.user_data['team2_score'] = query.data.split(":")[1]
        await confirm_match_result(query, context)

# Ask for Team 2's score
async def ask_for_team2_score(query):
    score_buttons = [[InlineKeyboardButton(f"{i}", callback_data=f"team2_score:{i}") for i in range(0, 10)]]
    score_buttons.append([InlineKeyboardButton("Cancel", callback_data="cancel")])  # Add cancel button
    reply_markup = InlineKeyboardMarkup(score_buttons)

    await query.edit_message_text(
        f"Team 1 score: {context.user_data['team1_score']}\n\n"
        "Select Team 2's score:",
        reply_markup=reply_markup
    )

# Confirm match result
async def confirm_match_result(query, context):
    summary_text = (
        f"Match Summary:\n"
        f"{context.user_data['player1']} and {context.user_data['player2']}\n"
        f"vs\n"
        f"{context.user_data['player3']} and {context.user_data['player4']}\n\n"
        f"Result: {context.user_data['team1_score']} - {context.user_data['team2_score']}\n\n"
        "Do you confirm this match result?"
    )
    await query.edit_message_text(
        text=summary_text,
        reply_markup=get_confirmation_buttons()
    )

# Handle confirmation or cancellation
async def handle_confirmation(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()  # Acknowledge the callback

    if query.data == 'confirm':
        if context.user_data.get('state') == CONFIRMATION:  # Confirm adding a player
            await add_new_player(context)
        else:  # Confirm match result
            await add_match_result(context)

        await query.edit_message_text("Operation completed successfully!")
        context.user_data.clear()  # Clear user data after operation

    elif query.data == 'cancel':
        await query.edit_message_text("Operation canceled.")
        context.user_data.clear()  # Clear user data

async def add_new_player(context):
    first_name = context.user_data['first_name']
    last_name = context.user_data['last_name']
    nickname = context.user_data['nickname']
    db.add_player(first_name, last_name, nickname)

async def add_match_result(context):
    players = {
        "player1": context.user_data['player1'],
        "player2": context.user_data['player2'],
        "player3": context.user_data['player3'],
        "player4": context.user_data['player4'],
        "team1_score": context.user_data['team1_score'],
        "team2_score": context.user_data['team2_score'],
    }
    # Example: db.add_match_result(players)
    logger.info("Match result added to the database: %s", players)

# Handle cancellation
async def handle_cancel(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()  # Answer the callback query
    await query.edit_message_text("Operation canceled.")
    context.user_data.clear()  # Clear the conversation state


# List all players in the database
async def list_players(update: Update, context: CallbackContext):
    players = db.fetch_players()  # Fetch players from the database

    if not players:
        await update.message.reply_text("No players found in the database.")
    else:
        logger.info(players)
        player_list = "\n".join([f"{p[0]} {p[1]} {p[2]} (Nickname: {p[3] if p[3] else 'None'})" for p in players])
        await update.message.reply_text(f"Current Players:\n{player_list}")
