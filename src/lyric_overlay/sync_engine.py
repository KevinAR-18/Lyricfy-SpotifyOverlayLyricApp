from __future__ import annotations

from .models import LyricLine, LyricsData


class SyncEngine:
    def __init__(self) -> None:
        self._lyrics = LyricsData(source="none", lines=[])

    def set_lyrics(self, lyrics: LyricsData) -> None:
        self._lyrics = lyrics

    def current_line(self, progress_ms: int) -> tuple[int, LyricLine | None]:
        lines = self._lyrics.lines
        if not lines:
            return -1, None

        active_index = -1
        for index, line in enumerate(lines):
            if line.timestamp_ms <= progress_ms:
                active_index = index
            else:
                break

        if active_index == -1:
            return -1, None

        return active_index, lines[active_index]

    def next_line(self, active_index: int) -> LyricLine | None:
        if active_index < 0:
            return self._lyrics.lines[0] if self._lyrics.lines else None

        next_index = active_index + 1
        if next_index >= len(self._lyrics.lines):
            return None

        return self._lyrics.lines[next_index]
