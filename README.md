# Lyricfy

Lyricfy is a Windows desktop Spotify lyric overlay built with Python and PySide6.  
It displays synced lyrics in a compact top overlay inspired by Dynamic Island behavior.

## Features

- Reads the currently playing track from Spotify
- Syncs lyrics using Spotify playback progress
- Uses local `.lrc` files first, then falls back to LRCLIB
- Compact always-on-top overlay
- Draggable overlay with light snap behavior
- Tray icon with `Show Overlay`, `Hide Overlay`, `Open Settings`, and `Exit`
- Settings panel for Spotify credentials
- Adjustable lyric offset in milliseconds
- Custom overlay, text, lyric, and glow colors
- Auto-hide track header after the first 10 seconds of a new song
- First-run `.env` generation with default theme values

## Project Structure

```text
.
├─ assets/
│  └─ lrc/
├─ src/
│  ├─ main.py
│  └─ lyric_overlay/
│     ├─ app_controller.py
│     ├─ config.py
│     ├─ lyrics.py
│     ├─ main.py
│     ├─ models.py
│     ├─ overlay.py
│     ├─ spotify_client.py
│     └─ sync_engine.py
├─ .env
├─ .env.example
├─ build.bat
├─ icon.ico
├─ requirements.txt
└─ README.md
```

## Requirements

- Windows
- Python 3.11+
- A Spotify Developer app
- Spotify playback available on your account/device

## Spotify App Setup

1. Open the Spotify Developer Dashboard.
2. Create a new app.
3. Add this redirect URI:

```text
http://127.0.0.1:8888/callback
```

4. Copy the `Client ID` and `Client Secret`.

## Installation

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

## First Run and .env

Lyricfy supports automatic `.env` creation on first run.

Behavior:

- In development mode, it uses the project folder `.env`
- In bundled `.exe` mode, it uses:

```text
%APPDATA%\Lyricfy\.env
```

If no `.env` exists yet, Lyricfy creates one automatically with these defaults:

```env
SPOTIFY_CLIENT_ID=
SPOTIFY_CLIENT_SECRET=
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
POLL_INTERVAL_MS=2500
LRCLIB_ENABLED=true
LYRIC_OFFSET_MS=0
OVERLAY_BG_COLOR=#0A0A0AEB
OVERLAY_TEXT_COLOR=#F4F4F4
LYRIC_TEXT_COLOR=#F4F4F4
LYRIC_GLOW_COLOR=#66CCFFFF
```

## Run

Use the project entry point:

```powershell
python src\main.py
```

Do not run internal module files such as `src\lyric_overlay\sync_engine.py` directly.

## Settings Panel

The in-app settings panel supports:

- Spotify Client ID
- Spotify Client Secret
- Redirect URI
- Lyric Offset (ms)
- Overlay Color
- Text Color
- Lyric Color
- Lyric Glow Color

## Lyric Offset

Use `Lyric Offset (ms)` to adjust sync timing:

- Negative value: lyrics appear earlier
- Positive value: lyrics appear later

Examples:

- `-250` makes lyrics appear 250 ms earlier
- `300` makes lyrics appear 300 ms later

## Local LRC Files

Place local lyric files inside `assets/lrc/` using this format:

```text
Artist - Title.lrc
```

Example:

```text
Coldplay - Yellow.lrc
```

Example file content:

```text
[00:10.00]Look at the stars
[00:13.50]Look how they shine for you
[00:18.20]And everything you do
```

## Build

To build the executable:

```powershell
build.bat
```

Output:

```text
dist\Lyricfy.exe
```

Bundled runtime data is stored in:

```text
%APPDATA%\Lyricfy\
```

That location is used for:

- `.env`
- `.spotify_cache`
- `assets\lrc\`

## Sync Notes

- Sync is based on Spotify `progress_ms`
- External synced lyrics may not match the exact Spotify track version
- The most stable setup is still a local `.lrc` file with known timestamps

## Sources

- Spotify Web API for current playback
- LRCLIB for synced lyric fallback

## Current UI Behavior

- The overlay opens at the top-center of the screen
- The overlay does not appear as a normal taskbar window
- The tray icon remains available for control and exit
- The track header shows for about 10 seconds when a new track starts
- Long lyrics can wrap to a second line
- The `-` button hides the overlay
- The settings button expands the configuration panel
