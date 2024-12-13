from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import random

# Telegram Bot API Token
TOKEN = "7992521280:AAEnSyYaWu57nTklnvxYny2UfrrZSYtYQqM"

# Your channel username
CHANNEL_USERNAME = "@destitans"

# Data structure to keep track of anonymous users and their pairings
waiting_users = []
chat_pairs = {}

def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    # Check if user is a member of the required channel
    if not is_member(user.id):
        update.message.reply_text(
            "You must join our channel first: https://t.me/destitans"
        )
        return
    update.message.reply_text(
        "Welcome! Use /find to start chatting anonymously with another user."
    )

def is_member(user_id):
    bot = Bot(TOKEN)
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

def find(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id in chat_pairs:
        update.message.reply_text("You are already in a chat! Use /leave to exit.")
        return

    if waiting_users:
        partner_id = waiting_users.pop(0)
        chat_pairs[user_id] = partner_id
        chat_pairs[partner_id] = user_id
        context.bot.send_message(chat_id=partner_id, text="You are now connected! Say hi.")
        update.message.reply_text("You are now connected! Say hi.")
    else:
        waiting_users.append(user_id)
        update.message.reply_text("Waiting for a partner to connect...")

def leave(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in chat_pairs:
        update.message.reply_text("You are not in a chat!")
        return

    partner_id = chat_pairs.pop(user_id)
    del chat_pairs[partner_id]
    context.bot.send_message(chat_id=partner_id, text="Your partner has left the chat.")
    update.message.reply_text("You have left the chat.")

def message_handler(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id in chat_pairs:
        partner_id = chat_pairs[user_id]
        context.bot.send_message(chat_id=partner_id, text=update.message.text)
    else:
        update.message.reply_text("You are not in a chat! Use /find to connect with someone.")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("find", find))
    dp.add_handler(CommandHandler("leave", leave))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, message_handler))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
