import os
import logging
import yt_dlp
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio

# Replace with your actual bot token
BOT_TOKEN = "7790682238:AAFT_BlrNjtj97FoK9i0zIIC5WG6fgY8FEo"

# Setup logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Ensure the downloads directory exists
os.makedirs("downloads", exist_ok=True)

async def download_mp3_youtube(query: str) -> str:
    """Searches and downloads an MP3 from YouTube."""
    ydl_opts = {
        'format': 'bestaudio/best',
        'extract_audio': True,
        'audio_format': 'mp3',
        'outtmpl': f"downloads/{query}.mp3",
        'noplaylist': True,
        'quiet': True,
    }
    
    loop = asyncio.get_running_loop()
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            await loop.run_in_executor(None, ydl.extract_info, f"ytsearch:{query}", True)
    except Exception as e:
        logging.error(f"Error downloading from YouTube: {e}")
        return None
    
    file_path = f"downloads/{query}.mp3"
    return file_path if os.path.exists(file_path) else None

async def download_mp3_tubidy(query: str) -> str:
    """Downloads an MP3 from Tubidy."""
    search_url = f"https://api.tubidy.ws/search?query={query}"
    try:
        response = requests.get(search_url)
        response.raise_for_status()  # Raise an error for bad responses
    except requests.RequestException as e:
        logging.error(f"Error fetching from Tubidy: {e}")
        return None

    results = response.json()
    if results and 'items' in results and len(results['items']) > 0:
        mp3_url = results['items'][0]['download_url']
        file_path = f"downloads/{query}.mp3"

        try:
            with open(file_path, 'wb') as f:
                f.write(requests.get(mp3_url).content)
            return file_path if os.path.exists(file_path) else None
        except Exception as e:
            logging.error(f"Error saving file from Tubidy: {e}")
            return None
    return None

async def download_mp3(query: str) -> str:
    """Tries downloading from YouTube first, then Tubidy."""
    file_path = await download_mp3_youtube(query)
    if not file_path:
        file_path = await download_mp3_tubidy(query)
    return file_path

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Babe❤️ please Send me a list of song names separated by commas, and I'll get the MP3s for you okay👌💕!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    queries = [q.strip() for q in update.message.text.split(',')]
    await update.message.reply_text(f"Searching for {len(queries)} songs...")

    all_success = True  # Track if all downloads were successful

    for query in queries:
        file_path = await download_mp3(query)

        if file_path:
            try:
                with open(file_path, 'rb') as audio_file:
                    await update.message.reply_audio(audio=audio_file)
                os.remove(file_path)  # Clean up after sending
            except Exception as e:
                logging.error(f"Error sending audio file: {e}")
                await update.message.reply_text(f"Couldn't send the audio for: {query}. Please try again!")
                all_success = False
        else:
            await update.message.reply_text("Oh baby 😘 sorry, let's try another one please😢👍")
            all_success = False

    if all_success:
        await update.message.reply_text("You're Welcome My Darling😊❤️")

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logging.info("Bot is running...")
    app.run_polling()

if __name__ == "__main__": 
    main()
