import logging
import yaml

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    TypeHandler
)

import plugins.game_1a2b
import plugins.solve_1a2b

try:
    with open('config.yaml', 'r') as config_file:
        config = yaml.safe_load(config_file)
        TOKEN = config["token"]
        PROXY = config.get("proxy", None)
except (FileNotFoundError, KeyError) as e:
    logging.error("config.yaml not found or invalid!")
    raise e


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display start message."""
    await update.message.reply_text("Hi! I'm Haruka bot. Choose a function in the command menu!")


async def log_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f"{update.effective_user.full_name}({update.effective_user.id}):"
                f"{update.effective_message.text}")


def main() -> None:
    """Run the bot."""
    if PROXY:
        application = Application.builder().token(TOKEN).proxy(
            PROXY).get_updates_proxy(PROXY).build()
    else:
        application = Application.builder().token(TOKEN).build()

    command_handler = CommandHandler("start", start)
    log_handler = TypeHandler(Update, log_message)

    application.add_handler(command_handler)
    application.add_handler(log_handler, -1)

    # Plugins
    application.add_handlers(plugins.game_1a2b.handlers)
    application.add_handlers(plugins.solve_1a2b.handlers)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
