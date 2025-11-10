# Spotify Playlist Sync Downloader# Spotify Playlist Sync Downloader

Automatically download new tracks from your Spotify playlists. Remembers what you've already downloaded so you only get new additions.Automatically download new tracks from your Spotify playlists. Remembers what you've already downloaded so you only get new additions.

---

## What It Does##

**syncSpotify** connects to your Spotify playlists and downloads tracks you haven't grabbed yet. It keeps a history file for each playlist, so running it again only downloads newly added songs.**syncSpotify** connects to your Spotify playlists and downloads tracks you haven't grabbed yet. It keeps a history file for each playlist, so running it again only downloads newly added songs.

**Key Features:**

- 🎵 **Auto-sync** - Only downloads new tracks since last run

- 📱 **GUI & CLI** - Desktop app or command-line interface

- 📊 **Smart tracking** - Per-playlist history in CSV files

- 👁️ **Dry run mode** - Preview what's new without downloading

- ⚡ **Real-time feedback** - Live progress for each song

---

## How It Works##

1. Fetches all tracks from your Spotify playlist via the Spotify API1. Fetches all tracks from your Spotify playlist via the Spotify API

2. Compares against your local history file (`playlists/<playlist_id>.csv`)2. Compares against your local history file (`playlists/<playlist_id>.csv`)

3. Downloads new tracks from YouTube as M4A audio files3. Downloads new tracks from YouTube as M4A audio files

4. Records successful downloads so they're skipped next time4. Records successful downloads so they're skipped next time

---

## Installation##

### Prerequisites###

- Python 3.7+- Python 3.7+

- yt-dlp (YouTube downloader)- yt-dlp (YouTube downloader)

- FFmpeg (audio conversion)- FFmpeg (audio conversion)

- Spotify API credentials (free)- Spotify API credentials (free)

### Setup Steps###

**1. Clone the repository:**

`bash`

git clone https://github.com/JustinPerlman/YoutubeAudioDownloader.gitgit clone https://github.com/JustinPerlman/YoutubeAudioDownloader.git

cd YoutubeAudioDownloadercd YoutubeAudioDownloader

````



**2. Create a virtual environment:****2. Create a virtual environment:**



Windows (PowerShell):Windows (PowerShell):

```powershell```powershell

python -m venv venvpython -m venv venv

.\venv\Scripts\Activate.ps1.\venv\Scripts\Activate.ps1

````

macOS/Linux:macOS/Linux:

`bash`bash

python3 -m venv venvpython3 -m venv venv

source venv/bin/activatesource venv/bin/activate

```````



**3. Install Python dependencies:****3. Install Python dependencies:**



```bash```bash

pip install -r requirements.txtpip install -r requirements.txt

```

### Setup Steps```powershell

**4. Install system tools:**

# Windows (PowerShell)

Install FFmpeg via your system package manager:

- **Windows:** `choco install ffmpeg`**1. Clone and navigate to the repo:**python -m venv .venv

- **macOS:** `brew install ffmpeg`

- **Linux:** `sudo apt-get install ffmpeg````bash ..venv\Scripts\Activate.ps1



**5. Get Spotify API credentials:**git clone https://github.com/JustinPerlman/YoutubeAudioDownloader.gitpip install --upgrade pip



1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)cd YoutubeAudioDownloaderpip install -r requirements.txt

2. Create a new app

3. Copy your **Client ID** and **Client Secret**```

4. Add `http://127.0.0.1:8888/callback` to Redirect URIs in app settings

**2. Create a virtual environment:**```cmd

**6. Create a `.env` file in the project root:**

# Windows (cmd.exe)

```env

SPOTIPY_CLIENT_ID=your_client_id_hereWindows (PowerShell):python -m venv .venv

SPOTIPY_CLIENT_SECRET=your_client_secret_here

SPOTIPY_REDIRECT_URI=http://127.0.0.1:8888/callback```powershell.venv\Scripts\activate.bat

```

python -m venv venvpip install --upgrade pip

---

.\venv\Scripts\Activate.ps1pip install -r requirements.txt

## Usage

```

### GUI App (Recommended)

macOS/Linux:```bash

```bash

python sync_spotify_gui.py````bash# macOS / Linux

```

python3 -m venv venvpython3 -m venv .venv

1. Paste your Spotify playlist URL

2. Choose download folder (defaults to `downloads/`)source venv/bin/activatesource .venv/bin/activate

3. Optional: Check "Dry run" to preview without downloading

4. Click **Run** and watch progress in the log```pip install --upgrade pip



### Command Linepip install -r requirements.txt



```bash**3. Install Python dependencies:**```

python syncSpotify.py <playlist_url> <download_folder> [--dry-run]

``````bash



**Examples:**pip install -r requirements.txt3. Install FFmpeg (system package). Some platforms provide FFmpeg via package managers:



Download new tracks:```   - Windows: `choco install ffmpeg`

```bash

python syncSpotify.py "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M" downloads   - macOS: `brew install ffmpeg`

```

**4. Install system tools:**   - Linux: `sudo apt-get install ffmpeg` or equivalent

Preview without downloading:

```bash

python syncSpotify.py "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M" downloads --dry-run

```Install yt-dlp and FFmpeg:## Configuration



---- **Windows:** `choco install ffmpeg`



## Output- **macOS:** `brew install ffmpeg`If needed, set the FFmpeg path in `csvDownloader.py`:



Downloaded files are saved as:- **Linux:** `sudo apt-get install ffmpeg`

```

downloads/Artist - Track.m4a```python

```

**5. Get Spotify API credentials:**FFMPEG_PATH = 'path/to/ffmpeg'  # Leave empty if FFmpeg is in system PATH

History is tracked in:

```````

playlists/<playlist_id>.csv

`````1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)



---2. Create a new app## Usage



## Troubleshooting3. Copy your **Client ID** and **Client Secret**



### "ERROR: Spotify credentials not set"4. Add `http://127.0.0.1:8888/callback` to Redirect URIsUse [Exportify](https://exportify.net/) to export a Spotify playlist to CSV. The CSV file should contain at minimum these columns:

- Check that `.env` exists in the project root

- Verify credentials have no extra spaces**6. Create a `.env` file in the project root:**- `Artist Name(s)`: The name of the artist(s)

- Ensure variable names match exactly

```env- `Track Name`: The name of the song

### "yt-dlp command not found"

- Install: `pip install yt-dlp`SPOTIPY_CLIENT_ID=your_client_id_here

- Verify: `yt-dlp --version`

SPOTIPY_CLIENT_SECRET=your_client_secret_hereExample CSV format:

### "FFmpeg not found"

- Install FFmpeg via your system package managerSPOTIPY_REDIRECT_URI=http://127.0.0.1:8888/callback

- Windows: Ensure FFmpeg is in PATH

````csv

### Playlist access errors

- Ensure playlist is public or you have accessArtist Name(s),Track Name

- Try deleting `.cache_spotify` and run again to re-authenticate

## UsageThe Beatles,Hey Jude

### Unicode/encoding errors

- Already fixed! Scripts use ASCII markers (`[OK]`, `[FAIL]`)Queen,Bohemian Rhapsody

- Subprocess output forced to UTF-8

### GUI App (Easy Mode)```

---



## Tips

```bash## Usage

**Multiple playlists:**

Run the script multiple times with different URLs. Each playlist gets its own history file.python sync_spotify_gui.py



**Automation:**```Run the script by providing the input CSV file and output directory:

Schedule with cron (Linux/macOS) or Task Scheduler (Windows) to sync daily.



**Check what's new:**

Use `--dry-run` to preview new tracks before downloading.1. Paste your Spotify playlist URL```bash



---2. Choose download folder (or use default `downloads/`)python csvDownloader.py input.csv output_directory



## File Structure3. Optional: Check "Dry run" to preview without downloading```



```4. Click **Run** and watch progress in the log

YoutubeAudioDownloader/

├── syncSpotify.py           # Core sync logic (CLI)For example:

├── sync_spotify_gui.py      # Desktop GUI wrapper

├── songDownloader.py        # YouTube download helper### Command Line

├── .env                     # Your Spotify credentials

├── .cache_spotify           # OAuth token (auto-generated)```bash

├── playlists/               # History tracking

│   └── <playlist_id>.csv    # Tracks you've downloaded```bashpython csvDownloader.py playlist.csv downloads

└── downloads/               # Your audio files

```python syncSpotify.py <playlist_url> <download_folder> [--dry-run]```



---```



## LicenseThe script will:



MIT License**Examples:**



## Credits1. Create the specified output directory if it doesn't exist



Built with [yt-dlp](https://github.com/yt-dlp/yt-dlp), [Spotipy](https://github.com/plamere/spotipy), and [FFmpeg](https://ffmpeg.org)Download new tracks:2. Read the track list from your CSV file



---```bash3. Search YouTube for each track



**Happy syncing!** 🎵python syncSpotify.py "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M" downloads4. Download and convert the audio to M4A format


```5. Save files as `Artist - Track.m4a` in the specified output directory

6. Provide a summary of successful and failed downloads

Preview without downloading:

```bash## Output

python syncSpotify.py "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M" downloads --dry-run

```Files are saved in your specified output directory with the naming format:



## Output```

Artist - Track.m4a

Downloaded files are saved as:```

`````

downloads/Artist - Track.m4a## Error Handling

````

The script provides detailed error output for:

History is tracked in:

```- Missing or invalid CSV file

playlists/<playlist_id>.csv- Missing required CSV columns

```- Download failures

- FFmpeg/yt-dlp command errors

## Troubleshooting

# Playlist Checkers (Apple Music & Spotify)

**"ERROR: Spotify credentials not set"**

- Check that `.env` exists in the project rootThis repository includes two helper scripts that detect new songs in a playlist and feed them to the downloader:

- Verify credentials are correct with no extra spaces

- `checkPlaylist_AppleMusic.py` — queries the macOS Music app (Apple Music) using AppleScript (`osascript`) and finds tracks that aren't in your history CSV.

**"yt-dlp command not found"**- `checkPlaylist_Spotify.py` — queries Spotify via the Web API (uses `spotipy`) and does the same for Spotify playlists.

- Install: `pip install yt-dlp`

- Verify: `yt-dlp --version`Purpose



**"FFmpeg not found"**- Automatically detect new tracks in a playlist and download them via `csvDownloader.py`.

- Install FFmpeg via your system package manager- Keep per-playlist history so tracks are not re-downloaded.

- Windows: Add FFmpeg to PATH or set path in `songDownloader.py`

How it works (high level)

**Playlist access errors**

- Ensure playlist is public or you have access- The checker fetches the playlist contents, normalizes track and artist names, and compares them against a per-playlist history file in `playlists/` (history file name: `{playlist_id}.csv`).

- Delete `.cache_spotify` and run again to re-authenticate- A playlist snapshot is also written on each run (`playlists/{playlist_id}_snapshot.csv`) so you can inspect the fetched playlist.

- For each new track the script will either show it (dry-run) or call `csvDownloader.py` with a temporary single-track CSV. Only successfully downloaded tracks are appended to the history file.

**Unicode/encoding errors**

- Already fixed! Scripts use ASCII markers and force UTF-8Requirements & notes



## Tips- Apple Music checker:



**Multiple playlists:**  - Must be run on macOS (it uses AppleScript to talk to the Music app).

Run the script multiple times with different URLs. Each playlist gets its own history file.  - No extra Python dependencies are required beyond what's needed by this repo.



**Automation:**- Spotify checker:

Schedule with cron (Linux/macOS) or Task Scheduler (Windows) to sync daily.  - Requires Python packages: `spotipy` and `python-dotenv` (install with `pip install spotipy python-dotenv`).

  - You need a Spotify Developer App (https://developer.spotify.com/dashboard/) to obtain `CLIENT_ID` and `CLIENT_SECRET`.

**Check what's new:**  - Set environment variables (or create a `.env` file next to the scripts):

Use `--dry-run` to see new tracks before committing to a large download.    - `SPOTIPY_CLIENT_ID`, `SPOTIPY_CLIENT_SECRET`, `SPOTIPY_REDIRECT_URI` (use a loopback address like `http://127.0.0.1:8888/callback`).

  - The script uses a named OAuth cache file (default: `.cache_spotify` in the repo) so you won't have to sign in every run. You can override its location with `SPOTIPY_CACHE_PATH`.

## File Structure

Quick examples

````

YoutubeAudioDownloader/- Dry-run (don't download; just show new songs):

├── syncSpotify.py # Core sync logic (CLI)

├── sync_spotify_gui.py # Desktop GUI wrapper ```bash

├── songDownloader.py # YouTube download helper python3 check_apple_music_and_run.py --playlist "My Playlist" --dry-run

├── .env # Your Spotify credentials python3 checkPlaylist_Spotify.py --playlist "<playlist-id-or-uri>" --dry-run

├── .cache_spotify # OAuth token (auto-generated) ```

├── playlists/ # History tracking

│ └── <playlist_id>.csv # Tracks you've downloaded- Real run (downloads new tracks):

└── downloads/ # Your audio files ```bash

````python3 check_apple_music_and_run.py --playlist "My Playlist" --output-dir downloads

  python3 checkPlaylist_Spotify.py --playlist "<playlist-id-or-uri>" --output-dir downloads

## License  ```



MIT LicenseSecurity & git



## Credits- OAuth tokens are cached in a small JSON cache file. The repo `.gitignore` excludes `.cache` and `.cache_spotify` by default — do not commit these files.



Built with [yt-dlp](https://github.com/yt-dlp/yt-dlp), [Spotipy](https://github.com/plamere/spotipy), and [FFmpeg](https://ffmpeg.org)If you want, the Spotify checker can be made to use a home-directory cache (e.g., `~/.spotify_token_cache`) instead of a repo-local file.


---

**Happy syncing!** 🎵
````
