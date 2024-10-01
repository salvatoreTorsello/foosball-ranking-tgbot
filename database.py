import os
import asyncpg
import logging

logger = logging.getLogger(__name__)

# Get the database url from environment variables
databse_url = os.getenv('DATABASE_URL')

# Database connection
async def connect_db():
    # Replace with your actual database URL or connection parameters
    return await asyncpg.connect(databse_url)

# Function to add a player to the database
async def add_player_to_db(player_name):
    conn = None
    try:
        # Connect to the database
        conn = await connect_db()

        # Insert the player's name into the players table
        query = "INSERT INTO players (name) VALUES ($1)"
        await conn.execute(query, player_name)

        logger.info(f"Player '{player_name}' added to the database.")
    except Exception as e:
        logger.error(f"Error adding player to the database: {e}")
    finally:
        if conn:
            await conn.close()

