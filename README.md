# YouTube Audio Downloader

A Python tool that automates downloading audio tracks from YouTube based on a CSV file containing track information. The script searches YouTube for each track and downloads the audio in M4A format.

## Features

- Bulk download audio tracks from YouTube
- Simple CSV input format
- Searches YouTube based on artist and track name
- Converts downloads to M4A format (to avoid libmp3lame encoder issues)
- Organizes downloads in a specified output folder
- Provides detailed progress and error reporting
- Supports custom FFmpeg path configuration

## Prerequisites

- Python 3.x
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [FFmpeg](https://ffmpeg.org/download.html)

## Installation

1. Clone this repository:

```bash
git clone https://github.com/JustinPerlman/YoutubeMP3Downloader.git
cd YoutubeAudioDownloader
```

2. Install yt-dlp:

```bash
pip install yt-dlp
```

3. Install FFmpeg:
   - Windows: `choco install ffmpeg`
   - macOS: `brew install ffmpeg`
   - Linux: `sudo apt-get install ffmpeg` or equivalent

## Configuration

If needed, set the FFmpeg path in `csvDownloader.py`:

```python
FFMPEG_PATH = 'path/to/ffmpeg'  # Leave empty if FFmpeg is in system PATH
```

## Usage

Use [Exportify](https://exportify.net/) to export a Spotify playlist to CSV. The CSV file should contain at minimum these columns:

- `Artist Name(s)`: The name of the artist(s)
- `Track Name`: The name of the song

Example CSV format:

```csv
Artist Name(s),Track Name
The Beatles,Hey Jude
Queen,Bohemian Rhapsody
```

## Usage

Run the script by providing the input CSV file and output directory:

```bash
python csvDownloader.py input.csv output_directory
```

For example:

```bash
python csvDownloader.py playlist.csv downloads
```

The script will:

1. Create the specified output directory if it doesn't exist
2. Read the track list from your CSV file
3. Search YouTube for each track
4. Download and convert the audio to M4A format
5. Save files as `Artist - Track.m4a` in the specified output directory
6. Provide a summary of successful and failed downloads

## Output

Files are saved in your specified output directory with the naming format:

```
Artist - Track.m4a
```

## Error Handling

The script provides detailed error output for:

- Missing or invalid CSV file
- Missing required CSV columns
- Download failures
- FFmpeg/yt-dlp command errors



# Playlist Checkers (Apple Music & Spotify)

This repository includes two helper scripts that detect new songs in a playlist and feed them to the downloader:

- `checkPlaylist_AppleMusic.py` — queries the macOS Music app (Apple Music) using AppleScript (`osascript`) and finds tracks that aren't in your history CSV.
- `checkPlaylist_Spotify.py` — queries Spotify via the Web API (uses `spotipy`) and does the same for Spotify playlists.

Purpose
- Automatically detect new tracks in a playlist and download them via `csvDownloader.py`.
- Keep per-playlist history so tracks are not re-downloaded.

How it works (high level)
- The checker fetches the playlist contents, normalizes track and artist names, and compares them against a per-playlist history file in `playlists/` (history file name: `{playlist_id}.csv`).
- A playlist snapshot is also written on each run (`playlists/{playlist_id}_snapshot.csv`) so you can inspect the fetched playlist.
- For each new track the script will either show it (dry-run) or call `csvDownloader.py` with a temporary single-track CSV. Only successfully downloaded tracks are appended to the history file.

Requirements & notes
- Apple Music checker:
   - Must be run on macOS (it uses AppleScript to talk to the Music app).
   - No extra Python dependencies are required beyond what's needed by this repo.

- Spotify checker:
   - Requires Python packages: `spotipy` and `python-dotenv` (install with `pip install spotipy python-dotenv`).
   - You need a Spotify Developer App (https://developer.spotify.com/dashboard/) to obtain `CLIENT_ID` and `CLIENT_SECRET`.
   - Set environment variables (or create a `.env` file next to the scripts):
      - `SPOTIPY_CLIENT_ID`, `SPOTIPY_CLIENT_SECRET`, `SPOTIPY_REDIRECT_URI` (use a loopback address like `http://127.0.0.1:8888/callback`).
   - The script uses a named OAuth cache file (default: `.cache_spotify` in the repo) so you won't have to sign in every run. You can override its location with `SPOTIPY_CACHE_PATH`.

Quick examples
- Dry-run (don't download; just show new songs):
   ```bash
   python3 check_apple_music_and_run.py --playlist "My Playlist" --dry-run
   python3 checkPlaylist_Spotify.py --playlist "<playlist-id-or-uri>" --dry-run
   ```

- Real run (downloads new tracks):
   ```bash
   python3 check_apple_music_and_run.py --playlist "My Playlist" --output-dir downloads
   python3 checkPlaylist_Spotify.py --playlist "<playlist-id-or-uri>" --output-dir downloads
   ```

Security & git
- OAuth tokens are cached in a small JSON cache file. The repo `.gitignore` excludes `.cache` and `.cache_spotify` by default — do not commit these files.

If you want, the Spotify checker can be made to use a home-directory cache (e.g., `~/.spotify_token_cache`) instead of a repo-local file.
