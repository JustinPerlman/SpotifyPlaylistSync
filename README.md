# YoutubeAudioDownloader

A small utility to keep a local music folder in sync with a Spotify playlist. It fetches all tracks in a playlist, compares them against a per‑playlist download history, and only downloads songs you don’t already have. Under the hood, it resolves each track to an audio source and saves it to your chosen folder. A simple GUI launcher is included.

> Auth note: This project now supports Spotify user login (Authorization Code / PKCE). First run opens a browser; tokens are cached locally in `.cache_spotify`. You can omit the client secret when using PKCE, but a Spotify Client ID is still required.

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
- A Spotify Developer application (Client ID required; Client Secret optional if using PKCE)

Dependencies are listed in `requirements.txt` (yt-dlp, spotipy, python-dotenv). A recent Spotipy version is recommended for PKCE (login without client secret).

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

4. Create a Spotify application (for user login):

- Go to https://developer.spotify.com/dashboard
- Create an app; copy the Client ID (Client Secret is optional with PKCE)
- Add a redirect URI, e.g. `http://localhost:8888/callback`, in the app settings

5. Create a `.env` file (or copy `.env.example`):

```ini
SPOTIPY_CLIENT_ID=your_client_id_here
# Optional if using PKCE; provide if using OAuth with client secret
SPOTIPY_CLIENT_SECRET=your_client_secret_here
SPOTIPY_REDIRECT_URI=http://localhost:8888/callback
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

- On first run a browser window opens to log in to Spotify; a token is cached in `.cache_spotify` and auto‑refreshed.
- If Spotipy PKCE is available and no secret is set, PKCE is used (no client secret).
- If neither PKCE nor a secret is available, the app falls back to public‑only Client Credentials.
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

- “Missing SPOTIPY_CLIENT_ID”
  - Set `SPOTIPY_CLIENT_ID` in `.env` (you must create an app in the Spotify dashboard).
- Browser didn’t open
  - Copy the auth URL printed in the terminal into your browser manually.
- Redirect URI mismatch
  - Ensure `SPOTIPY_REDIRECT_URI` in `.env` exactly matches one of the redirect URIs configured in the Spotify dashboard.
- Private playlist not found
  - Make sure you logged into the right account in the consent screen; user login with scopes `playlist-read-private`/`playlist-read-collaborative` is required.
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
- Uses Spotipy with user login (PKCE/OAuth) to page through all tracks; can fall back to Client Credentials for public data
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
- Can I avoid creating a Spotify developer app entirely?
  - No. Spotify’s Web API requires an application (Client ID). PKCE lets you omit the secret, but the app registration is still required.

---

## Legal

This tool is for personal use. Respect the terms of service of the platforms you interact with and your local laws.
