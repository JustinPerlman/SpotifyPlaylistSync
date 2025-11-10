# YoutubeAudioDownloader

A small utility to keep a local music folder in sync with a Spotify playlist. It fetches all tracks in a playlist, compares them against a per‑playlist download history, and only downloads songs you don’t already have. Under the hood, it resolves each track to an audio source and saves it to your chosen folder. A simple GUI launcher is included.

> Privacy note: This project uses Spotify’s Client Credentials flow (no user login) to read public playlist metadata. Your Spotify Client ID/Secret live in your local `.env`.

---

## What you can do

- Sync a Spotify playlist to your local disk
- Skip tracks you’ve already downloaded (per‑playlist CSV history)
- Dry‑run to see what’s new before downloading
- Use a basic GUI helper or the CLI

History files live in `playlists/<playlist_id>.csv` as `track,artist` rows. Downloads go to any folder you pick (e.g. `./downloads`).

---

## Requirements

- Windows 10/11 (tested). Should also work on macOS/Linux with Python.
- Python 3.9+
- A Spotify Developer application (for Client ID/Secret)

Dependencies are listed in `requirements.txt` (Spotipy, python-dotenv, and the downloader dependencies).

---

## Setup (Windows, PowerShell)

1. Clone or download this repository.

2. (Recommended) Create and activate a virtual environment:

```powershell
# In the repo folder
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install Python dependencies:

```powershell
pip install -r requirements.txt
```

4. Create a Spotify application and get your credentials:

- Go to https://developer.spotify.com/dashboard
- Create an app; copy the Client ID and Client Secret
- No redirect URI is required for this app (client credentials only)

5. Create a `.env` file (or copy `.env.example`):

```ini
SPOTIPY_CLIENT_ID=your_client_id_here
SPOTIPY_CLIENT_SECRET=your_client_secret_here
# SPOTIPY_REDIRECT_URI=http://localhost:8888/callback   # optional, not required here
```

That’s it. You’re ready to run the sync.

---

## Usage

### CLI (recommended)

```powershell
# Basic: sync a playlist to the ./downloads folder
python .\syncSpotify.py "https://open.spotify.com/playlist/<playlist_id>" ".\downloads"

# Dry-run: list what would download without saving files or updating history
python .\syncSpotify.py "https://open.spotify.com/playlist/<playlist_id>" ".\downloads" --dry-run
```

You can pass any of these as the first argument:

- Full URL: `https://open.spotify.com/playlist/<id>`
- Spotify URI: `spotify:playlist:<id>`
- Raw ID: `<id>`

The script will:

1. Resolve the playlist ID
2. Fetch all tracks via Spotify’s API (paginated)
3. Load `playlists/<id>.csv` as history
4. Determine new `(track, artist)` pairs
5. If not `--dry-run`, download each new one and append it to history

Notes:

- A cache file `.cache_spotify` is created in the repo to store the token.
- History uses lowercase normalized comparisons for `(track, artist)`.

### GUI (optional)

A simple helper UI is available:

```powershell
python .\sync_spotify_gui.py
```

Use it to provide the playlist link/ID and pick a download folder, then start the sync. The GUI wraps the same logic as the CLI.

---

## Where files go

- Downloaded audio: wherever you point the script (e.g. `./downloads`)
- Per‑playlist history: `playlists/<playlist_id>.csv`
- Spotify token cache: `.cache_spotify`

You can safely delete a playlist’s CSV to force a full re‑download on the next run.

---

## Troubleshooting

- “Spotify credentials not set in environment variables”
  - Ensure `.env` exists with `SPOTIPY_CLIENT_ID` and `SPOTIPY_CLIENT_SECRET`, then restart your shell or re‑run the script.
- Private or unavailable playlist
  - Client Credentials flow can only read public playlist metadata.
- Nothing downloads
  - Check the `playlists/<id>.csv` file; entries there are considered already downloaded.
- Some tracks fail to download
  - The script continues past failures. Re‑run later or try manually searching the track. Network hiccups or source mismatches can happen.
- Paths with spaces
  - Quote your arguments in PowerShell, e.g. `"C:\\Users\\You\\My Music"`.

---

## Project layout

- `syncSpotify.py` — CLI to sync a Spotify playlist and maintain history
- `sync_spotify_gui.py` — Simple GUI wrapper for the sync
- `songDownloader.py` — Download implementation used by the sync (called as a Python module function)
- `playlists/` — Per‑playlist CSV histories
- `downloads/` — Example output folder (you can choose any folder)
- `checkPlaylist_AppleMusic.py` — Optional Apple Music helper (not required for Spotify sync)
- `requirements.txt` — Python dependencies
- `.cache_spotify` — Spotify access token cache

---

## How it works (under the hood)

- Extracts a canonical playlist ID from URL/URI/raw ID
- Uses Spotipy with Client Credentials auth to page through all tracks
- Normalizes each `(track, artist)` to lowercase for comparison
- Compares against `playlists/<id>.csv` to find new items
- Downloads only the new ones and appends them to the CSV

---

## FAQs

- Can I run this on macOS/Linux?
  - Yes, it’s standard Python. Use your platform’s Python and shell equivalents.
- How do I reset a playlist’s state?
  - Delete `playlists/<id>.csv`. Next run will treat everything as new.
- Can I change where the history lives?
  - By default it’s `playlists/`. You can move it if you also adjust the code.

---

## Legal

This tool is for personal use. Respect the terms of service of the platforms you interact with and your local laws.
