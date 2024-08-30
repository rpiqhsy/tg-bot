from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
import json

INPUT_INITIAL_GUESS = 0
NEXT_GUESS = 1

KEYBOARD = ReplyKeyboardMarkup([
    ["0A0B"],
    ["0A1B", "0A2B", "0A3B", "0A4B"],
    ["1A0B", "1A1B", "1A2B", "1A3B"],
    ["2A0B", "2A1B", "2A2B"],
    ["3A0B", "4A0B"]
], is_persistent=True)

TYPES = ["4A0B", "2A2B", "1A3B",
         "0A4B", "3A0B", "2A1B",
         "2A0B", "1A2B", "0A3B",
         "0A0B", "1A0B", "1A1B",
         "0A2B", "0A1B"]

# 1A2B answers file from https://www.tanaka.ecc.u-tokyo.ac.jp/ktanaka/moo/moo-en.html
with open("plugins/1a2b_answers.json", "r") as f:
    ANSWER_DATA = json.load(f)


def set_map(num: str) -> str:
    """ Generate a mapping by the initial clue. """
    mapping = list("0123456789")
    rest = set(mapping) - set(num)
    mapping = list(num) + sorted(list(rest))
    return "".join(mapping)


def map_num(mapping: str, num: str) -> str:
    """ Map a number to the new mapping. """
    return "".join([mapping[int(i)] for i in num])


async def start_1a2b_solver(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ Show start message for 1A2B solver and ask for initial clue number.  """
    await update.message.reply_text(f"1A2B solver started, please input a initial clue, or use /cancel to exit:")
    return INPUT_INITIAL_GUESS


async def resolve_initial_clue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ Process user's initial clue and show keyboard for the result. """
    user_data = context.user_data
    initial_clue = update.message.text
    user_data["mapping"] = set_map(initial_clue)
    await update.message.reply_text(f"Your initial clue is {initial_clue}. Please choose the result:", reply_markup=KEYBOARD)
    return NEXT_GUESS


async def resolve_next_guess(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ Process user's next guess and show keyboard for the result. """
    user_data = context.user_data
    mapping = user_data["mapping"]
    data = user_data.get("data", ANSWER_DATA)

    input_result = update.message.text
    index = TYPES.index(input_result)

    try:
        fetch = data[index]
        if type(fetch) == str: 
            # Got final result
            user_data.clear()
            await update.message.reply_text(f"The answer is {map_num(mapping, fetch)}.", reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END
        elif not fetch: 
            # Got False
            await update.message.reply_text("Invalid input, please try again.")
            return NEXT_GUESS
        else:
            # Got a dict
            next_guess = next(iter(fetch))
            user_data["data"] = fetch[next_guess]
            await update.message.reply_text(f"Next guess is {map_num(mapping, next_guess)}. Please choose the result:", reply_markup=KEYBOARD)
            return NEXT_GUESS
    except Exception as e:
        await update.message.reply_text("Invalid input, please try again.")
        return NEXT_GUESS


async def cancel_1a2b_solver(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ Cancel the 1A2B solver. """
    context.user_data.clear()
    await update.message.reply_text("1A2B solver canceled.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


handlers = [ConversationHandler(
    entry_points=[CommandHandler("solve_1a2b", start_1a2b_solver)],
    states={
        INPUT_INITIAL_GUESS: [
            MessageHandler(filters.Regex("^\d{4}$"), resolve_initial_clue),
        ],
        NEXT_GUESS: [
            MessageHandler(filters.Regex("^\dA\dB$"), resolve_next_guess),
            CommandHandler("cancel", cancel_1a2b_solver),
        ]
    },
    fallbacks=[CommandHandler("cancel", cancel_1a2b_solver), cancel_1a2b_solver],
)]
