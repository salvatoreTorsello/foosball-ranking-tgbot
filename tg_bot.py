import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from database import add_player_to_db  # Import the function to add players to the database

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

start_message = ('Welcome to the Foosball Bot!\n'
    'Use the /addplayer command to add a player (admin only).\n'
    'Use the /addscore command to add a match score.\n'
    'Use the /ranking command to request the foosball ranking.')

# Sample list of players for demonstration
players_all = ["Player 1", "Player 2", "Player 3", "Player 4", "Player 5", "Player 6"]

def create_keyboard_with_two_columns(players, callback_prefix):
    keyboard = []
    row = []

    # Iterate over players, placing two buttons per row
    for i, player in enumerate(players):
        # Prepare callback data for each player using the provided prefix
        callback_data = f"{callback_prefix}:{player}"

        # Add the player button to the row
        row.append(InlineKeyboardButton(player, callback_data=callback_data))

        # Check if the row has two buttons or if it's the last player in case of an odd number of players
        if len(row) == 2 or i == len(players) - 1:
            keyboard.append(row)
            row = []  # Start a new row

    # Add the "Cancel" button in its own row
    keyboard.append([InlineKeyboardButton("Cancel", callback_data="cancel")])

    return InlineKeyboardMarkup(keyboard)

# Start command handler that shows the available options
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(start_message)

# Function to handle adding a score
async def add_score(update: Update, context: CallbackContext):
    # Create the inline keyboard with players distributed in two columns
    reply_markup = create_keyboard_with_two_columns(players_all, "select_player_1")

    # Send or update message for Player 1 selection
    await update.message.reply_text(
        "Select Player 1:",
        reply_markup=reply_markup
    )

    # Set the context flag for awaiting the score input
    context.user_data['awaiting_score'] = True
    context.user_data['selected_players'] = {}  # Initialize a dictionary to store selected players and scores

# Handle button callbacks for player and score selection
async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()  # Acknowledge the button press

    # Cancel the operation if the user presses the cancel button
    if query.data == "cancel":
        context.user_data['awaiting_score'] = False
        context.user_data['selected_players'] = {}
        await query.edit_message_text("Operation canceled.")
        return

    # Handle Player 1 selection
    elif query.data.startswith("select_player_1"):
        player1 = query.data.split(":")[1]
        context.user_data['selected_players']['player1'] = player1

        players_rem = [player for player in players_all if player != player1]
        # Create new inline buttons for selecting Player 2
        reply_markup = create_keyboard_with_two_columns(players_rem, "select_player_2")

        # Update the message for Player 2 selection
        await query.edit_message_text(
            f"Player 1: {player1}\nSelect Player 2:",
            reply_markup=reply_markup
        )

    # Handle Player 2 selection
    elif query.data.startswith("select_player_2"):
        player2 = query.data.split(":")[1]
        context.user_data['selected_players']['player2'] = player2

        players_rem = [player for player in players_all if player not in [
            context.user_data['selected_players']['player1'],
            player2
        ]]
        # Create new inline buttons for selecting Player 3 (excluding Player 1 and Player 2)
        reply_markup = create_keyboard_with_two_columns(players_rem, "select_player_3")

        # Update the message for Player 3 selection
        await query.edit_message_text(
            f"Player 1: {context.user_data['selected_players']['player1']}\n"
            f"Player 2: {player2}\nSelect Player 3:",
            reply_markup=reply_markup
        )

    # Handle Player 3 selection
    elif query.data.startswith("select_player_3"):
        player3 = query.data.split(":")[1]
        context.user_data['selected_players']['player3'] = player3

        players_rem = [player for player in players_all if player not in [
            context.user_data['selected_players']['player1'],
            context.user_data['selected_players']['player2'],
            player3
        ]]
        # Create new inline buttons for selecting Player 4 (excluding Player 1, Player 2, and Player 3)
        reply_markup = create_keyboard_with_two_columns(players_rem, "select_player_4")

        # Update the message for Player 4 selection
        await query.edit_message_text(
            f"Player 1: {context.user_data['selected_players']['player1']}\n"
            f"Player 2: {context.user_data['selected_players']['player2']}\n"
            f"Player 3: {player3}\nSelect Player 4:",
            reply_markup=reply_markup
        )

    # Handle Player 4 selection
    elif query.data.startswith("select_player_4"):
        player4 = query.data.split(":")[1]
        context.user_data['selected_players']['player4'] = player4

        # Present score options for Team 1
        score_buttons = [[InlineKeyboardButton(f"{i}", callback_data=f"team1_score:{i}") for i in range(0, 10)]]
        score_buttons.append([InlineKeyboardButton("Cancel", callback_data="cancel")])  # Add cancel button
        reply_markup = InlineKeyboardMarkup(score_buttons)

        # Update the message for Team 1 score selection
        await query.edit_message_text(
            f"Team 1: {context.user_data['selected_players']['player1']} and "
            f"{context.user_data['selected_players']['player2']}\n"
            "\tvs\n"
            f"Team 2: {context.user_data['selected_players']['player3']} and "
            f"{player4}\n\n"
            "Select Team 1's score:",
            reply_markup=reply_markup
        )

    # Handle Team 1 score selection
    elif query.data.startswith("team1_score"):
        score1 = query.data.split(":")[1]
        context.user_data['selected_players']['team1_score'] = score1

        # Present score options for Team 2
        score_buttons = [[InlineKeyboardButton(f"{i}", callback_data=f"team2_score:{i}") for i in range(0, 10)]]
        score_buttons.append([InlineKeyboardButton("Cancel", callback_data="cancel")])  # Add cancel button
        reply_markup = InlineKeyboardMarkup(score_buttons)

        # Update the message for Team 2 score selection
        await query.edit_message_text(
            f"Team 1: {context.user_data['selected_players']['player1']} and "
            f"{context.user_data['selected_players']['player2']}\n"
            "\tvs\n"
            f"Team 2: {context.user_data['selected_players']['player3']} and "
            f"{context.user_data['selected_players']['player4']}\n\n"
            f"Team 1 score: {score1}\n\n"
            "Select Team 2's score:",
            reply_markup=reply_markup
        )

    # Handle Team 2 score selection and finalize the match
    elif query.data.startswith("team2_score"):
        score2 = query.data.split(":")[1]

        # Check if Team 2's score is the same as Team 1's score
        if score2 == context.user_data['selected_players']['team1_score']:

            # Send an alert popup that the same score can't be selected for both teams
            await update.callback_query.answer(
                text="Team 2's score cannot be the same as Team 1's score. Please select a different score.",
                show_alert=True  # This enables the pop-up dialog
            )

        else:
            context.user_data['selected_players']['team2_score'] = score2

            # Display the final match summary
            summary_text = (
                f"Match Summary:\n"
                f"{context.user_data['selected_players']['player1']} and "
                f"{context.user_data['selected_players']['player2']}\n"
                "\tvs\n"
                f"{context.user_data['selected_players']['player3']} and "
                f"{context.user_data['selected_players']['player4']}\n\n"
                f"Result: {context.user_data['selected_players']['team1_score']} - "
                f"{score2}\n\n"
                "Do you confirm this match result?"
            )

            # Create confirmation buttons (Confirm and Cancel side by side)
            reply_markup = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("Confirm", callback_data="confirm_match"),
                    InlineKeyboardButton("Cancel", callback_data="cancel")
                ]
            ])

            # Ask for confirmation by updating the message
            await query.edit_message_text(
                text=summary_text,
                reply_markup=reply_markup
            )

    # Handle match confirmation
    elif query.data == "confirm_match":
        # Here you would insert the match result into the database or perform the desired action
        await query.edit_message_text("Match has been added successfully!")

        # Reset the context after adding the match
        context.user_data['awaiting_score'] = False
        context.user_data['selected_players'] = {}
