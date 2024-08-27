import random

from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

GUESSING = 0

def generate_1a2b_number() -> str:
    return "".join(random.sample("0123456789", 4))

async def start_1a2b(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask the user to input 1a2b guess."""
    text = update.message.text
    context.user_data["secret"] = generate_1a2b_number()
    await update.message.reply_text(f"1A2B started. Type your guess, or use /cancel to exit:")

    return GUESSING


async def bad_1a2b_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle bad input."""
    await update.message.reply_text("Invaild input! Your guess must be four unique digits. Use /cancel to exit:")
    return GUESSING


async def resolve_1a2b_guess(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process user's guess."""
    user_data = context.user_data
    guess = update.message.text
    secret = user_data["secret"]

    if len(set(guess)) < 4:
        await update.message.reply_text("Invaild input! Your guess must be four unique digits. Use /cancel to exit:")
        return GUESSING

    a_count = 0
    b_count = 0

    for i in range(4):
        if guess[i] == secret[i]:
            a_count += 1
        else:
            if guess[i] in secret:
                b_count += 1

    if a_count == 4:
        await update.message.reply_text(f"Congratulations! The answer is {secret}!",)
        user_data.clear()
        return ConversationHandler.END

    await update.message.reply_text(f"{a_count}A{b_count}B")
    return GUESSING


async def cancel_1a2b(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle user cancel game."""
    user_data = context.user_data
    secret = user_data["secret"]

    await update.message.reply_text(f"The answer is {secret}. Better luck next time!",)
    user_data.clear()
    return ConversationHandler.END

handlers = [ConversationHandler(
    entry_points=[CommandHandler("1a2b", start_1a2b)],
    states={
        GUESSING: [
            MessageHandler(filters.Regex("^\d{4}$"), resolve_1a2b_guess),
            CommandHandler("cancel", cancel_1a2b),
            MessageHandler(
                ~(filters.Regex("^\d{4}$") | filters.Regex("^/cancel$")), bad_1a2b_input),
        ]
    },
    fallbacks=[CommandHandler("cancel", cancel_1a2b), cancel_1a2b],
)]
