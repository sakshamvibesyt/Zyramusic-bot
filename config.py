from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")


def get_required_env(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise RuntimeError(
            f"Required environment variable '{name}' is missing."
        )

    return value.strip()


def get_optional_int(name: str, default: int) -> int:
    value = os.getenv(name)

    if not value:
        return default

    try:
        return int(value)
    except ValueError as exc:
        raise RuntimeError(
            f"Environment variable '{name}' must be an integer."
        ) from exc


@dataclass(frozen=True)
class Settings:
    bot_token: str

    api_id: int
    api_hash: str
    session_string: str

    owner_id: int

    database_path: Path
    download_dir: Path

    max_queue_size: int
    default_volume: int

    bot_name: str
    log_level: str


def load_settings() -> Settings:
    bot_token = get_required_env("BOT_TOKEN")

    api_id = get_optional_int("API_ID", 0)

    if api_id <= 0:
        raise RuntimeError("API_ID must be a valid positive integer.")

    api_hash = get_required_env("API_HASH")
    session_string = get_required_env("SESSION_STRING")

    owner_id = get_optional_int("OWNER_ID", 0)

    if owner_id <= 0:
        raise RuntimeError("OWNER_ID must be a valid positive integer.")

    database_path = Path(
        os.getenv("DATABASE_PATH", "data/bot.db")
    )

    download_dir = Path(
        os.getenv("DOWNLOAD_DIR", "downloads")
    )

    max_queue_size = get_optional_int(
        "MAX_QUEUE_SIZE",
        50,
    )

    default_volume = get_optional_int(
        "DEFAULT_VOLUME",
        100,
    )

    default_volume = max(1, min(default_volume, 200))

    bot_name = os.getenv(
        "BOT_NAME",
        "MusicBot",
    ).strip()

    log_level = os.getenv(
        "LOG_LEVEL",
        "INFO",
    ).upper()

    return Settings(
        bot_token=bot_token,
        api_id=api_id,
        api_hash=api_hash,
        session_string=session_string,
        owner_id=owner_id,
        database_path=database_path,
        download_dir=download_dir,
        max_queue_size=max_queue_size,
        default_volume=default_volume,
        bot_name=bot_name,
        log_level=log_level,
    )


settings = load_settings()


# Make sure runtime directories exist.
settings.database_path.parent.mkdir(
    parents=True,
    exist_ok=True,
)

settings.download_dir.mkdir(
    parents=True,
    exist_ok=True,
)
