from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from config import settings
from database import Database


logging.basicConfig(
    level=getattr(
        logging,
        settings.log_level,
        logging.INFO,
    ),
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    ),
)

logger = logging.getLogger(__name__)

database = Database(
    settings.database_path
)


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if update.effective_chat is None:
        return

    chat = update.effective_chat

    database.ensure_group(
        chat_id=chat.id,
        title=chat.title or chat.full_name,
    )

    welcome = database.get_group(
        chat.id
    )

    welcome_message = (
        welcome["welcome_message"]
        if welcome and welcome["welcome_message"]
        else (
            f"🎧 <b>{settings.bot_name}</b>\n\n"
            "Welcome!\n\n"
            "Music system is being initialized.\n"
            "Use /help to see available commands."
        )
    )

    await update.message.reply_text(
        welcome_message,
        parse_mode="HTML",
    )


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    message = (
        f"🎧 <b>{settings.bot_name} Help</b>\n\n"
        "🎵 <b>Music</b>\n"
        "/play &lt;song&gt;\n"
        "/queue\n"
        "/song\n"
        "/skip\n\n"
        "🎛 <b>Controls</b>\n"
        "/pause\n"
        "/resume\n"
        "/stop\n"
        "/end\n"
        "/volume &lt;1-200&gt;\n\n"
        "⚙️ More features are coming in the next modules."
    )

    await update.message.reply_text(
        message,
        parse_mode="HTML",
    )


async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    logger.exception(
        "Unhandled Telegram error",
        exc_info=context.error,
    )


def create_application() -> Application:
    application = (
        Application.builder()
        .token(settings.bot_token)
        .build()
    )

    application.add_handler(
        CommandHandler(
            "start",
            start,
        )
    )

    application.add_handler(
        CommandHandler(
            "help",
            help_command,
        )
    )

    application.add_error_handler(
        error_handler
    )

    return application


def main() -> None:
    logger.info(
        "Initializing database..."
    )

    database.initialize()

    logger.info(
        "Starting %s...",
        settings.bot_name,
    )

    application = create_application()

    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()
