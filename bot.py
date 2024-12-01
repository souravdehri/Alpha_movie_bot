import os
from dotenv import load_dotenv
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
from connector import initialize_pool, get_connection, release_connection, close_pool

# Load environment variables
load_dotenv()

# Telegram bot token
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Initialize the database connection pool
initialize_pool()

# Function to fetch drama details from the database
def fetch_drama_details(drama_name):
    conn = None
    try:
        # Get a connection from the pool
        conn = get_connection()
        cursor = conn.cursor()

        # Fetch drama details
        cursor.execute("""
            SELECT title, year, rating, rating_count, description, country, 
                   episodes, airing_start, airing_end, network, duration, 
                   content_rating, genre, trailer_url, image_url
            FROM dramas 
            WHERE title ILIKE %s 
            LIMIT 1
        """, (f"%{drama_name}%",))
        result = cursor.fetchone()
        return result
    except Exception as e:
        print(f"Database error: {e}")
        return None
    finally:
        # Release the connection back to the pool
        if conn:
            release_connection(conn)

# Format drama details for display
def format_drama_details(drama, user_name):
    if not drama:
        return f"Sorry, {user_name}, no details found for the requested drama."
    
    # Unpack drama details
    title, year, rating, rating_count, description, country, episodes, airing_start, airing_end, network, duration, content_rating, genre, trailer_url, image_url = drama

    # Format airing dates
    formatted_start = airing_start.strftime("%b %d, %Y")
    formatted_end = airing_end.strftime("%b %d, %Y")
    formatted_airing = f"{formatted_start} - {formatted_end}"

    # Replace commas in genre with hashtags
    formatted_genre = " ".join([f"#{g.strip()}" for g in genre.split(",")])

    return f"""
**{user_name} via @MoviesGamabot**
**{title} ({year})**
⭐️ Rating: {rating}/10 from {rating_count} users [MyDramaList]({image_url})

        `{description}`

**Country**: `{country}`
**Episodes**: `{episodes}`
**Aired**: `{formatted_airing}`
**Network**: `{network}`
**Duration**: `{duration}`
**Content Rating**: `{content_rating}`

**Genre**: {formatted_genre}

[▶️ Watch Trailer]({trailer_url})
    """

# Handle user messages
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    user_name = update.effective_user.first_name  # Get user's first name
    print(f"User '{user_name}' searched for: {user_input}")

    # Fetch and format drama details
    drama_details = fetch_drama_details(user_input)
    response = format_drama_details(drama_details, user_name)

    # Reply with drama details
    await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

# Define the start command handler
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Bot started by user: {update.effective_user.first_name}")
    await update.message.reply_text("Hello! Send me a drama name to search.")

# Main function to run the bot
if __name__ == "__main__":
    # Create the bot application
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    # Close the database pool on exit
    import atexit
    atexit.register(close_pool)

    print("Bot is running...")
    application.run_polling()
