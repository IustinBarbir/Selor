"""
config.py — loads DB connection settings from .env file.
"""

import os
import sys


def _app_dir() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


_ENV_FILE = os.path.join(_app_dir(), ".env")


def _load_dotenv(path: str) -> None:
    if not os.path.isfile(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)


_load_dotenv(_ENV_FILE)


class ConfigError(RuntimeError):
    pass


def get_db_config() -> dict:
    required = ["DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME"]
    missing = [key for key in required if not os.environ.get(key)]
    if missing:
        raise ConfigError(
            "Missing environment variables: "
            + ", ".join(missing)
            + ". Set them in the system environment or in a .env file "
              "(see .env.example)."
        )

    return {
        "host": os.environ["DB_HOST"],
        "port": int(os.environ.get("DB_PORT", "3306")),
        "user": os.environ["DB_USER"],
        "password": os.environ["DB_PASSWORD"],
        "database": os.environ["DB_NAME"],
    }
