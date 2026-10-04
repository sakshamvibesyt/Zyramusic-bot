from __future__ import annotations

import logging

from pyrogram import Client

from config import settings


logger = logging.getLogger(__name__)


assistant = Client(
    name="assistant",
    api_id=settings.api_id,
    api_hash=settings.api_hash,
    session_string=settings.session_string,
    in_memory=True,
)


async def start_assistant() -> None:
    logger.info(
        "Starting assistant Telegram account..."
    )

    await assistant.start()

    me = await assistant.get_me()

    logger.info(
        "Assistant connected as @%s",
        me.username or me.id,
    )


async def stop_assistant() -> None:
    if assistant.is_connected:
        logger.info(
            "Stopping assistant Telegram account..."
        )

        await assistant.stop()
