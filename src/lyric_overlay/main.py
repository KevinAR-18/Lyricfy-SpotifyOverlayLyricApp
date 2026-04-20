from __future__ import annotations

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from lyric_overlay.app_controller import AppController
    from lyric_overlay.config import AppConfig, ensure_directories, load_config, save_config
    from lyric_overlay.lyrics import LyricsRepository
    from lyric_overlay.overlay import OverlayWindow, create_application
    from lyric_overlay.spotify_client import SpotifyClient
else:
    from .app_controller import AppController
    from .config import AppConfig, ensure_directories, load_config, save_config
    from .lyrics import LyricsRepository
    from .overlay import OverlayWindow, create_application
    from .spotify_client import SpotifyClient


def build_spotify_client(config: AppConfig) -> SpotifyClient | None:
    try:
        return SpotifyClient(
            client_id=config.spotify_client_id,
            client_secret=config.spotify_client_secret,
            redirect_uri=config.spotify_redirect_uri,
        )
    except ValueError:
        return None


def main() -> int:
    ensure_directories()
    config = load_config()

    app = create_application()
    overlay = OverlayWindow()
    overlay.load_config_values(config)

    spotify_client = build_spotify_client(config)
    if spotify_client is None:
        overlay.set_track(None)
        overlay.set_lines("Open Settings to add Spotify credentials", "Then click Save and Reload Spotify")

    controller = AppController(
        spotify_client=spotify_client,
        lyrics_repository=LyricsRepository(lrclib_enabled=config.lrclib_enabled),
        overlay=overlay,
        config=config,
    )

    def save_settings(new_config: AppConfig) -> None:
        saved_config = AppConfig(
            spotify_client_id=new_config.spotify_client_id,
            spotify_client_secret=new_config.spotify_client_secret,
            spotify_redirect_uri=new_config.spotify_redirect_uri or "http://127.0.0.1:8888/callback",
            poll_interval_ms=config.poll_interval_ms,
            lrclib_enabled=config.lrclib_enabled,
            lyric_offset_ms=new_config.lyric_offset_ms,
            overlay_bg_color=new_config.overlay_bg_color or config.overlay_bg_color,
            overlay_text_color=new_config.overlay_text_color or config.overlay_text_color,
            lyric_text_color=new_config.lyric_text_color or config.lyric_text_color,
            lyric_glow_color=new_config.lyric_glow_color or config.lyric_glow_color,
        )
        save_config(saved_config)
        overlay.apply_config_theme(saved_config)
        overlay.show_status("Settings saved to .env")
        controller.config = saved_config

    def reconnect_spotify() -> None:
        latest = load_config()
        new_client = build_spotify_client(latest)
        if new_client is None:
            overlay.show_status("Spotify credentials are incomplete")
            controller.reconnect(None, latest)
            return
        controller.reconnect(new_client, latest)

    overlay.save_requested.connect(save_settings)
    overlay.reconnect_requested.connect(reconnect_spotify)
    app.aboutToQuit.connect(controller.stop)
    overlay.show()
    controller.start()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
