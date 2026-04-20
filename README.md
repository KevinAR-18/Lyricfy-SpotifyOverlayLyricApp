# Lyric Overlay for Spotify

Versi sederhana untuk Windows. Jalankan langsung satu file: `app.py`.

## Struktur

```text
.
├─ app.py
├─ assets/
│  └─ lrc/
├─ .env.example
├─ requirements.txt
└─ README.md
```

## Prasyarat

- Windows
- Python 3.11+
- Spotify Premium disarankan untuk playback state yang lebih konsisten
- Spotify Developer App

## Setup Spotify App

1. Buka Spotify Developer Dashboard.
2. Buat app baru.
3. Tambahkan redirect URI:

```text
http://127.0.0.1:8888/callback
```

4. Salin `Client ID` dan `Client Secret`.

## Instalasi

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Isi `.env`:

```env
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
POLL_INTERVAL_MS=2500
LRCLIB_ENABLED=true
```

## Menjalankan

```powershell
python app.py
```

Pada login pertama, browser akan terbuka untuk OAuth Spotify.

## Format LRC Lokal

Simpan file ke `assets/lrc/` dengan pola nama:

```text
Artist - Title.lrc
```

Contoh:

```text
Coldplay - Yellow.lrc
```

Isi file:

```text
[00:10.00]Look at the stars
[00:13.50]Look how they shine for you
[00:18.20]And everything you do
```

## Catatan Sinkronisasi

- Sinkronisasi bergantung pada `progress_ms` dari Spotify.
- Jika lirik dari provider eksternal tidak persis sama dengan versi track Spotify, offset bisa sedikit meleset.
- Jalur paling stabil adalah file `.lrc` lokal dengan timestamp yang Anda kontrol sendiri.

## Catatan

- Jika ingin stabil, pakai file `.lrc` lokal di `assets/lrc/`
- `LRCLIB` hanya fallback saat file lokal tidak ada
- Source lama di `src/` masih ada, tapi entry point yang dipakai sekarang adalah `app.py`
