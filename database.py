import sqlite3
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the path to the SQLite database
db_path = os.getenv('DATABASE_PATH')

# Connect to the SQLite database:
def connect_db():
    try:
        conn = sqlite3.connect(db_path)  # Connect to the SQLite database
        logger.info("Database connection established.")
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        return None

# Create a table for storing players if it doesn't exist
def create_players_table():
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS players (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    nickname TEXT NOT NULL
                )
            ''')
            conn.commit()
            logger.info("Players table created successfully.")
        except sqlite3.Error as e:
            logger.error(f"Error creating players table: {e}")
        finally:
            conn.close()

# Function to add a player to the database
def add_player(first_name, last_name, nickname):
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO players (first_name, last_name, nickname) VALUES (?, ?, ?)", (first_name, last_name, nickname))
            conn.commit()
            logger.info(f"Player {first_name} {last_name} (Nickname: {nickname}) added successfully.")
        except sqlite3.Error as e:
            logger.error(f"Error adding player: {e}")
        finally:
            conn.close()

# Function to fetch all players
def fetch_players():
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM players")
            players = cursor.fetchall()
            return players
        except sqlite3.Error as e:
            logger.error(f"Error fetching players: {e}")
            return []
        finally:
            conn.close()

