"""Shared configuration for the AQI data pipeline.

All credentials are read from environment variables. For local development
they can be placed in a ``.env`` file next to this module (see
``.env.example``); that file is gitignored and must never be committed.

In CI / deployment, set the same variables using GitHub Secrets (or an
Environment's secrets) rather than a .env file.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.engine import URL

# Loading a local .env is a no-op when the file is absent (e.g. in CI).
load_dotenv(Path(__file__).with_name(".env"))

DEFAULT_URL_ROOT = "https://breathe-london-7x54d7qf.ew.gateway.dev/"


def _required(name: str) -> str:
    """Return a non-empty environment variable or fail with a clear message."""
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(
            f"Missing required setting {name!r}. "
            "Copy .env.example to .env and fill it in, or set it as a "
            "GitHub Secret in CI."
        )
    return value


@dataclass(frozen=True)
class Config:
    breathe_url_root: str
    breathe_api_key: str
    mysql_host: str
    mysql_port: int
    mysql_user: str
    mysql_password: str
    mysql_database: str
    flask_host: str
    flask_debug: bool

    def database_url(self) -> URL:
        """Build a SQLAlchemy URL without putting the password in a log line."""
        return URL.create(
            "mysql+mysqlconnector",
            username=self.mysql_user,
            password=self.mysql_password,
            host=self.mysql_host,
            port=self.mysql_port,
            database=self.mysql_database,
        )

    def safe_summary(self) -> str:
        """Connection description that is safe to log (never includes secrets)."""
        return (
            f"{self.mysql_user}@{self.mysql_host}:{self.mysql_port}/"
            f"{self.mysql_database}"
        )


@lru_cache(maxsize=1)
def get_config() -> Config:
    url_root = os.getenv("BREATHE_URL_ROOT", DEFAULT_URL_ROOT).strip() or DEFAULT_URL_ROOT
    if not url_root.endswith("/"):
        url_root += "/"

    try:
        port = int(os.getenv("MYSQL_PORT", "3306"))
    except ValueError as exc:
        raise RuntimeError("MYSQL_PORT must be an integer") from exc

    return Config(
        breathe_url_root=url_root,
        breathe_api_key=_required("BREATHE_API_KEY"),
        mysql_host=os.getenv("MYSQL_HOST", "localhost").strip() or "localhost",
        mysql_port=port,
        mysql_user=os.getenv("MYSQL_USER", "project").strip() or "project",
        mysql_password=_required("MYSQL_PASSWORD"),
        mysql_database=os.getenv("MYSQL_DATABASE", "airquality").strip() or "airquality",
        flask_host=os.getenv("FLASK_HOST", "127.0.0.1").strip() or "127.0.0.1",
        flask_debug=os.getenv("FLASK_DEBUG", "false").strip().lower()
        in {"1", "true", "yes", "on"},
    )
