from __future__ import annotations

from typing import Any

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from .config import TOKEN_CACHE
from .models import TrackInfo


SPOTIFY_SCOPES = "user-read-currently-playing user-read-playback-state"


class SpotifyClient:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
    ) -> None:
        if not client_id or not client_secret or not redirect_uri:
            raise ValueError("Spotify credentials belum lengkap di file .env")

        auth_manager = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=SPOTIFY_SCOPES,
            cache_path=str(TOKEN_CACHE),
            open_browser=True,
        )
        self._spotify = spotipy.Spotify(auth_manager=auth_manager)

    def get_current_track(self) -> TrackInfo | None:
        payload = self._spotify.current_user_playing_track()
        if not payload or not payload.get("item"):
            return None

        item = payload["item"]
        artists = item.get("artists") or []
        images = (item.get("album") or {}).get("images") or []

        return TrackInfo(
            track_id=item["id"],
            title=item["name"],
            artist=", ".join(artist["name"] for artist in artists),
            album=(item.get("album") or {}).get("name", ""),
            duration_ms=item.get("duration_ms", 0),
            progress_ms=payload.get("progress_ms", 0),
            is_playing=payload.get("is_playing", False),
            cover_url=images[0]["url"] if images else None,
        )

    def raw_playback_state(self) -> dict[str, Any] | None:
        return self._spotify.current_playback()
