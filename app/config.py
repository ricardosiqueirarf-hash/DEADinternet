from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent


def _path_from_env(name: str, default: str) -> Path:
    raw = Path(os.getenv(name, default)).expanduser()
    return raw if raw.is_absolute() else ROOT_DIR / raw


@dataclass(frozen=True)
class Settings:
    host: str = os.getenv("DEADINTERNET_HOST", "127.0.0.1")
    port: int = int(os.getenv("DEADINTERNET_PORT", "4750"))
    db_path: Path = _path_from_env("DEADINTERNET_DB_PATH", "data/deadinternet.db")
    agent_outbox: Path = _path_from_env("DEADINTERNET_AGENT_OUTBOX", "agent_workspace/outbox")
    agent_inbox: Path = _path_from_env("DEADINTERNET_AGENT_INBOX", "agent_workspace/inbox")


settings = Settings()
