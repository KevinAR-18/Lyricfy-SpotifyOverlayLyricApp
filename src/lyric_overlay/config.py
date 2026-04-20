from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[2]
ASSETS_DIR = BASE_DIR / "assets"
LRC_DIR = ASSETS_DIR / "lrc"
TOKEN_CACHE = BASE_DIR / ".spotify_cache"
ENV_FILE = BASE_DIR / ".env"


@dataclass(slots=True)
class AppConfig:
    spotify_client_id: str
    spotify_client_secret: str
    spotify_redirect_uri: str
    poll_interval_ms: int = 2500
    lrclib_enabled: bool = True
    lyric_offset_ms: int = 0
    overlay_bg_color: str = "#0A0A0AEB"
    overlay_text_color: str = "#F4F4F4"
    lyric_text_color: str = "#F4F4F4"
    lyric_glow_color: str = "#66CCFFFF"


def load_config() -> AppConfig:
    load_dotenv(ENV_FILE)

    return AppConfig(
        spotify_client_id=os.getenv("SPOTIFY_CLIENT_ID", "").strip(),
        spotify_client_secret=os.getenv("SPOTIFY_CLIENT_SECRET", "").strip(),
        spotify_redirect_uri=os.getenv(
            "SPOTIFY_REDIRECT_URI",
            "http://127.0.0.1:8888/callback",
        ).strip(),
        poll_interval_ms=int(os.getenv("POLL_INTERVAL_MS", "2500")),
        lrclib_enabled=os.getenv("LRCLIB_ENABLED", "true").lower() == "true",
        lyric_offset_ms=int(os.getenv("LYRIC_OFFSET_MS", "0")),
        overlay_bg_color=os.getenv("OVERLAY_BG_COLOR", "#0A0A0AEB").strip() or "#0A0A0AEB",
        overlay_text_color=os.getenv("OVERLAY_TEXT_COLOR", "#F4F4F4").strip() or "#F4F4F4",
        lyric_text_color=os.getenv("LYRIC_TEXT_COLOR", "#F4F4F4").strip() or "#F4F4F4",
        lyric_glow_color=os.getenv("LYRIC_GLOW_COLOR", "#66CCFFFF").strip() or "#66CCFFFF",
    )


def ensure_directories() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    LRC_DIR.mkdir(parents=True, exist_ok=True)


def save_config(config: AppConfig) -> None:
    lines = [
        f"SPOTIFY_CLIENT_ID={config.spotify_client_id}",
        f"SPOTIFY_CLIENT_SECRET={config.spotify_client_secret}",
        f"SPOTIFY_REDIRECT_URI={config.spotify_redirect_uri}",
        f"POLL_INTERVAL_MS={config.poll_interval_ms}",
        f"LRCLIB_ENABLED={'true' if config.lrclib_enabled else 'false'}",
        f"LYRIC_OFFSET_MS={config.lyric_offset_ms}",
        f"OVERLAY_BG_COLOR={config.overlay_bg_color}",
        f"OVERLAY_TEXT_COLOR={config.overlay_text_color}",
        f"LYRIC_TEXT_COLOR={config.lyric_text_color}",
        f"LYRIC_GLOW_COLOR={config.lyric_glow_color}",
    ]
    ENV_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
