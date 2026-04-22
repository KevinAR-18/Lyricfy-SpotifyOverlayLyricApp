from __future__ import annotations

import threading
from dataclasses import dataclass

from PySide6.QtCore import QObject, Signal

from .config import AppConfig
from .lyrics import LyricsRepository
from .models import LyricsData, TrackInfo
from .overlay import OverlayWindow
from .spotify_client import SpotifyClient
from .sync_engine import SyncEngine


@dataclass(slots=True)
class PlaybackSnapshot:
    track: TrackInfo | None = None
    lyrics: LyricsData | None = None


class PlaybackWorker(QObject):
    refreshed = Signal(object)
    failed = Signal(str)

    def __init__(self, spotify_client: SpotifyClient, poll_interval_ms: int) -> None:
        super().__init__()
        self.spotify_client = spotify_client
        self.poll_interval_ms = poll_interval_ms
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()

    def _run(self) -> None:
        while not self._stop_event.is_set():
            try:
                self.refreshed.emit(self.spotify_client.get_current_track())
            except Exception as exc:  # noqa: BLE001
                self.failed.emit(str(exc))
            self._stop_event.wait(self.poll_interval_ms / 1000)


class AppController(QObject):
    def __init__(
        self,
        spotify_client: SpotifyClient | None,
        lyrics_repository: LyricsRepository,
        overlay: OverlayWindow,
        config: AppConfig,
    ) -> None:
        super().__init__()
        self.spotify_client = spotify_client
        self.lyrics_repository = lyrics_repository
        self.overlay = overlay
        self.config = config
        self.sync_engine = SyncEngine()
        self.snapshot = PlaybackSnapshot()
        self.worker: PlaybackWorker | None = None

    def start(self) -> None:
        if self.spotify_client is None:
            self.overlay.set_track(None)
            self.overlay.set_lines("Open Settings to add Spotify credentials", "")
            return

        try:
            self.refresh(self.spotify_client.get_current_track())
        except Exception as exc:  # noqa: BLE001
            self.snapshot = PlaybackSnapshot(track=None, lyrics=LyricsData(source="none", lines=[]))
            self.sync_engine.set_lyrics(self.snapshot.lyrics)
            self.overlay.set_track(None)
            self.overlay.set_lines("", "")
            self.show_error(str(exc))
        self._start_worker()

    def stop(self) -> None:
        if self.worker is not None:
            self.worker.stop()
            self.worker = None

    def reconnect(self, spotify_client: SpotifyClient | None, config: AppConfig) -> None:
        self.stop()
        self.spotify_client = spotify_client
        self.config = config
        self.snapshot = PlaybackSnapshot()
        self.sync_engine.set_lyrics(LyricsData(source="none", lines=[]))
        self.overlay.load_config_values(config)
        if self.spotify_client is None:
            self.overlay.set_track(None)
            self.overlay.set_lines("Spotify credentials are invalid", "")
            return

        self.overlay.show_status("Spotify reconnected")
        self.start()

    def refresh(self, track: TrackInfo | None) -> None:
        if track is None:
            self.snapshot = PlaybackSnapshot(track=None, lyrics=LyricsData(source="none", lines=[]))
            self.sync_engine.set_lyrics(self.snapshot.lyrics)
            self.overlay.set_track(None)
            self.overlay.set_lines("", "")
            self.overlay.show_status("")
            return

        track_changed = self.snapshot.track is None or self.snapshot.track.track_id != track.track_id

        if track_changed:
            lyrics = self.lyrics_repository.get_lyrics(
                artist=track.artist,
                title=track.title,
                duration_ms=track.duration_ms,
            )
            self.snapshot = PlaybackSnapshot(track=track, lyrics=lyrics)
            self.sync_engine.set_lyrics(lyrics)
        else:
            self.snapshot.track = track

        lyrics_source = self.snapshot.lyrics.source if self.snapshot.lyrics else ""
        self.overlay.set_track(track, lyrics_source=lyrics_source)

        if not track.is_playing:
            self.overlay.set_paused()
        else:
            self.overlay.show_status("")

        adjusted_progress_ms = max(0, track.progress_ms + self.config.lyric_offset_ms)
        active_index, active_line = self.sync_engine.current_line(adjusted_progress_ms)
        next_line = self.sync_engine.next_line(active_index)
        self.overlay.set_lines(
            active_line.text if active_line else "",
            next_line.text if next_line else "",
        )

    def show_error(self, message: str) -> None:
        self.overlay.show_status(self._format_error_message(message))

    def _start_worker(self) -> None:
        if self.spotify_client is None:
            return
        if self.worker is not None:
            return

        self.worker = PlaybackWorker(
            spotify_client=self.spotify_client,
            poll_interval_ms=self.config.poll_interval_ms,
        )
        self.worker.refreshed.connect(self.refresh)
        self.worker.failed.connect(self.show_error)
        self.worker.start()

    def _format_error_message(self, message: str) -> str:
        normalized = message.strip()
        lowered = normalized.lower()

        if "cooldown aktif" in lowered or "cooldown " in lowered:
            return normalized
        if "429" in lowered or "rate limit" in lowered or "too many requests" in lowered:
            return "Spotify API kena rate limit. Tunggu sebentar lalu coba lagi."
        if "connectionerror" in lowered or "failed to establish a new connection" in lowered:
            return "Gagal terhubung ke Spotify API."
        if normalized:
            return normalized
        return "Terjadi error saat mengambil data Spotify."
