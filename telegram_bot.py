import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from PIL import Image
from io import BytesIO
import cv2
import numpy as np

# Import DCT-based functions
from stegan import encode_image_dct, decode_image_dct

# Set up logging
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# Replace with your BotFather token
TOKEN = "7096958130:AAF5gDrvnx5dYH8BIWSd_vR5withupNmHaM"

# Function to show the main menu
async def show_menu(update, context):
    keyboard = [
        [InlineKeyboardButton("🔒 Encode a Message", callback_data="encode")],
        [InlineKeyboardButton("🔓 Decode an Image", callback_data="decode")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.message.reply_text("✅ Task completed! Choose your next action:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("✅ Task completed! Choose your next action:", reply_markup=reply_markup)

# Start command
async def start(update: Update, context):
    await update.message.reply_text(
        "Welcome to the DCT Image Steganography Bot! 🖼️🔐\n"
        "Send an image with a caption to encode a message or just send an image to decode."
    )
    await show_menu(update, context)

# Handle menu button clicks
async def button_click(update: Update, context):
    query = update.callback_query
    await query.answer()

    if query.data == "encode":
        await query.message.reply_text("📷 Send an image with a caption to encode your message.")
    elif query.data == "decode":
        await query.message.reply_text("📷 Send an image to decode the hidden message.")
    elif query.data == "help":
        await query.message.reply_text("ℹ️ **How to use this bot?**\n\n"
                                       "1️⃣ Send an image with a **caption** to encode a message.\n"
                                       "2️⃣ Send an image **without a caption** to decode.")

# Encoding function
async def encode(update: Update, context):
    if not update.message.photo:
        await update.message.reply_text("⚠️ Please send an image with a caption containing the secret message.")
        return

    photo = await update.message.photo[-1].get_file()
    image_bytes = await photo.download_as_bytearray()
    img = Image.open(BytesIO(image_bytes))

    if not update.message.caption:
        await update.message.reply_text("⚠️ Please provide a secret message in the caption.")
        return

    secret_message = update.message.caption
    temp_path = "temp.png"
    encoded_path = "encoded_dct_image.png"

    try:
        img.save(temp_path)
        encode_image_dct(temp_path, secret_message)
        
        with open(encoded_path, "rb") as f:
            await update.message.reply_photo(f, caption="✅ Message encoded successfully! 📷🔒")

        os.remove(temp_path)
        os.remove(encoded_path)
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

    await show_menu(update, context)

# Decoding function
async def decode(update: Update, context):
    if not update.message.photo:
        await update.message.reply_text("⚠️ Please send an image to decode.")
        return

    photo = await update.message.photo[-1].get_file()
    image_bytes = await photo.download_as_bytearray()
    img = Image.open(BytesIO(image_bytes))

    temp_path = "decoded.png"
    img.save(temp_path)
    
    try:
        secret_message = decode_image_dct(temp_path)
        await update.message.reply_text(f"✅ Decoded Message: `{secret_message}`", parse_mode="Markdown")
        os.remove(temp_path)
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

    await show_menu(update, context)

# Set up the bot
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.PHOTO & filters.Caption(), encode))
    app.add_handler(MessageHandler(filters.PHOTO, decode))

    logging.info("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
