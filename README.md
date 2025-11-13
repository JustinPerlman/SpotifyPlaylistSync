# Spotify Playlist Syncer

A powerful Spotify playlist downloader with GUI and CLI interfaces. Downloads tracks from Spotify playlists as high-quality MP3s with full metadata (title, artist, album, genre, and album artwork). Automatically tracks download history per-playlist to avoid re-downloading songs you already have.

**✨ Key Features:**
- 🎨 **Modern GUI** - Easy-to-use Tkinter interface with real-time progress tracking
- 🚀 **Fast Downloads** - Concurrent multi-threaded downloads (configurable)
- 🎵 **Full Metadata** - Automatic ID3 tagging with album art
- 📋 **Smart History** - Per-playlist CSV tracking to skip previously downloaded songs
- ⚡ **CLI & GUI** - Use whichever interface you prefer

---

## What you can do

- Download entire Spotify playlists with metadata and album art
- Skip tracks you've already downloaded (automatic per-playlist history)
- Download with concurrent threads for faster processing
- Use the modern GUI or command-line interface
- Track multiple playlists independently

History files are stored in `playlists/<playlist_id>.csv` with artist, title, and album information. Downloads are saved as MP3 files with complete metadata.

---

## Requirements

- **Python 3.9+** (tested on macOS and Windows)
- **Spotify Developer Application** (free - see setup below)
- **ffmpeg (for audio conversion)

All Python dependencies are in `requirements.txt`:
- `spotipy` - Spotify Web API client
- `yt-dlp` - YouTube download utility
- `mutagen` - Audio metadata tagging
- `python-dotenv` - Environment variable management
- `requests` - HTTP library for album art

---

## Complete Setup Guide

### Step 1: Install Python

Make sure you have Python 3.9 or higher installed:

```bash
python --version
# Should show Python 3.9.0 or higher
```

If not installed, download from [python.org](https://www.python.org/downloads/)

### Step 2: Install ffmpeg

**macOS (using Homebrew):**
```bash
brew install ffmpeg
```

**Windows:**
- Download from [ffmpeg.org](https://ffmpeg.org/download.html)
- Add ffmpeg to your PATH environment variable
- Or use: `choco install ffmpeg` (if you have Chocolatey)

**Linux:**
```bash
sudo apt install ffmpeg  # Debian/Ubuntu
sudo yum install ffmpeg  # RedHat/CentOS
```

Verify installation:
```bash
ffmpeg -version
```

### Step 3: Clone and Setup Project

```bash
# Clone the repository
git clone https://github.com/JustinPerlman/YoutubeAudioDownloader.git
cd YoutubeAudioDownloader

# Create a virtual environment (recommended)
python -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Create Spotify Developer Application

1. Go to https://developer.spotify.com/dashboard
2. Log in with your Spotify account (create one if needed)
3. Click **"Create app"**
4. Fill in the form:
   - **App name**: "Playlist Downloader" (or any name)
   - **App description**: "Personal playlist downloader"
   - **Redirect URI**: `http://127.0.0.1:8888/callback`
   - Check the Terms of Service box
5. Click **"Save"**
6. On your app's dashboard, click **"Settings"**
7. Copy your **Client ID** and **Client Secret**

### Step 5: Configure Environment Variables

Create a `.env` file in the project root directory:

```bash
# On macOS/Linux:
touch .env

# On Windows:
type nul > .env
```

Edit the `.env` file and add your Spotify credentials:

```ini
SPOTIPY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
SPOTIPY_REDIRECT_URI=http://127.0.0.1:8888/callback
```

**Important:** Replace `your_client_id_here` and `your_client_secret_here` with the actual values from Step 4.

### Step 6: Run the Application

**Option A: GUI (Recommended for beginners)**

```bash
python playlistDownloaderUI.py
```

The GUI window will open with:
- **Playlist URL field**: Paste your Spotify playlist URL
- **Output Directory**: Choose where to save MP3 files
- **Concurrent Downloads**: Set number of simultaneous downloads (4-12 recommended)
- **Start Download**: Begin downloading!

**Option B: Command Line**

```bash
python playlistDownloader.py \
  --playlist "https://open.spotify.com/playlist/YOUR_PLAYLIST_ID" \
  --output-dir ./my_music \
  --threads 8
```

### First Run

The first time you run the application, it will:
1. Fetch the playlist from Spotify
2. Check `playlists/` directory for download history
3. Download only new songs (or all songs if first time)
4. Save history to `playlists/<playlist_id>.csv`

Subsequent runs will automatically skip songs you've already downloaded!

---

## Usage Guide

### GUI Interface (Recommended)

```bash
python playlistDownloaderUI.py
```

**Using the GUI:**

1. **Paste Playlist URL**
   - Go to your Spotify playlist
   - Click "Share" → "Copy link to playlist"
   - Paste into the "Playlist URL" field
   
2. **Choose Output Directory**
   - Click "Browse" to select where MP3s will be saved
   - Or manually type the path (default: `./newThingDownloads`)

3. **Set Concurrent Downloads** (optional)
   - Adjust the number (1-20) based on your system
   - Recommended: 4-8 for most systems, 8-12 for faster machines
   - Higher numbers = faster but more CPU/network usage

4. **Click "Start Download"**
   - Watch real-time progress in the log window
   - Progress bar shows completion percentage
   - Each song shows: 🎧 Downloading → ✅ Completed

5. **Subsequent Downloads**
   - Run the same playlist again anytime
   - Only new songs added since last run will download
   - History is tracked automatically per-playlist

**GUI Features:**
- ✅ Real-time log updates
- ✅ Progress bar with completion tracking
- ✅ Status indicator (Ready/Downloading/Complete)
- ✅ Stop button (gracefully stops after current downloads)
- ✅ Clear log button

---

### Command Line Interface

```bash
# Basic usage
python playlistDownloader.py \
  --playlist "https://open.spotify.com/playlist/3lQT9JB3MettQcTTrmtxRR" \
  --output-dir ./my_music \
  --threads 8

# Using Spotify URI
python playlistDownloader.py \
  --playlist "spotify:playlist:3lQT9JB3MettQcTTrmtxRR" \
  --output-dir ./edm_collection

# Using just the playlist ID
python playlistDownloader.py \
  --playlist "3lQT9JB3MettQcTTrmtxRR" \
  --output-dir ./music
```

**CLI Arguments:**
- `--playlist` (required): Spotify playlist URL, URI, or ID
- `--output-dir` (optional): Download directory (default: `./newThingDownloads`)
- `--threads` (optional): Number of concurrent downloads (default: 4)

**Accepted Playlist Formats:**
- Full URL: `https://open.spotify.com/playlist/3lQT9JB3MettQcTTrmtxRR`
- Spotify URI: `spotify:playlist:3lQT9JB3MettQcTTrmtxRR`
- Playlist ID: `3lQT9JB3MettQcTTrmtxRR`

---

### How It Works

1. **Extracts Playlist ID** from URL/URI/ID
2. **Fetches All Tracks** from Spotify API (handles pagination automatically)
3. **Loads History** from `playlists/<playlist_id>.csv`
4. **Filters New Songs** by comparing with history
5. **Downloads in Parallel** using thread pool
6. **Applies Metadata** (title, artist, album, genre, album art)
7. **Saves to History** only on successful download

**Smart History Tracking:**
- Each playlist has its own CSV: `playlists/<playlist_id>.csv`
- Tracks are identified by `artist|title` combination
- Only successful downloads are added to history
- Failed downloads are retried on next run

---

## File Organization

**Downloaded Music:**
- Location: Your chosen output directory (e.g., `./newThingDownloads`)
- Format: MP3 with full metadata
- Naming: `{Track Title}.mp3`

**Download History:**
- Location: `playlists/<playlist_id>.csv`
- Format: CSV with columns: `artist`, `title`, `album`
- Purpose: Tracks which songs have been downloaded
- One CSV per playlist for independent tracking

**Cache Files:**
- `.cache_spotify` - Spotify authentication token (auto-refreshed)
- `.env` - Your Spotify credentials (never commit to git!)

**Tips:**
- Delete a playlist's CSV to force re-downloading all songs
- `.gitignore` already excludes `.env`, cache files, and download folders
- History CSVs are safe to commit (just track artist/title, no personal data)

---

## Troubleshooting

### Installation Issues

**"Python not found" or "pip not found"**
- Install Python 3.9+ from [python.org](https://www.python.org/)
- Make sure to check "Add Python to PATH" during installation

**"ffmpeg not found"**
- Install ffmpeg using the instructions in Step 2 of setup
- Verify with: `ffmpeg -version`
- Restart terminal after installation

**"Module not found" errors**
- Activate your virtual environment: `source venv/bin/activate` (macOS/Linux) or `venv\Scripts\activate` (Windows)
- Reinstall dependencies: `pip install -r requirements.txt`

### Spotify API Issues

**"Error: SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET must be set"**
- Create a `.env` file in the project root directory
- Add your Spotify credentials (see Step 5 in setup)
- Make sure the file is named exactly `.env` (with the dot)

**"Redirect URI mismatch"**
- Ensure `SPOTIPY_REDIRECT_URI` in `.env` is exactly: `http://127.0.0.1:8888/callback`
- In Spotify Developer Dashboard, add this exact URI to your app's Redirect URIs
- Save the settings in the Spotify Dashboard

**"Playlist not found" or "403 Forbidden"**
- Make sure the playlist is public or you have access
- Private playlists require user authentication (not yet supported)
- Try a different playlist to test

### Download Issues

**"No new tracks to download"**
- Check `playlists/<playlist_id>.csv` - songs listed there are skipped
- Delete the CSV file to force re-downloading all songs
- Make sure you're using the correct playlist URL

**Some songs fail to download**
- This is normal - some songs may not be found on YouTube
- The script continues with other songs
- Failed songs are NOT added to history, so they'll retry next run
- Check the log for specific error messages

**Downloads are very slow**
- Increase thread count: `--threads 12` or adjust in GUI
- Check your internet connection
- Note: Quality setting is "best available" which may be slower

**GUI doesn't open**
- Make sure tkinter is installed: `python -m tkinter` (should open a test window)
- On Linux: `sudo apt install python3-tk`
- Try the CLI version instead: `python playlistDownloader.py --help`

### File Issues

**"Permission denied" when saving files**
- Choose a different output directory you have write access to
- On macOS/Linux: check folder permissions with `ls -la`
- Avoid system directories like `/usr` or `C:\Windows`

**Files don't have metadata or album art**
- This is rare - check the log for "Metadata error" messages
- Try re-downloading (delete from history CSV first)
- Ensure mutagen is properly installed: `pip install --upgrade mutagen`

**Filename issues with special characters**
- Some track names have characters that aren't valid in filenames
- The script should handle this, but you may see truncated names
- Files are saved as `{Track Title}.mp3`

---

## Project Structure

```
YoutubeAudioDownloader/
├── playlistDownloaderUI.py    # GUI application (main entry point)
├── playlistDownloader.py       # CLI application
├── songDownloader.py           # Core download logic module
├── checkPlaylist_Spotify.py    # Playlist checker for Apple Music integration
├── requirements.txt            # Python dependencies
├── .env                        # Your Spotify credentials (create this)
├── .gitignore                  # Excludes sensitive/generated files
├── README.md                   # This file
├── playlists/                  # Download history (auto-created)
│   └── {playlist_id}.csv       # Per-playlist tracking
└── newThingDownloads/          # Default download location (auto-created)
    └── {Track Title}.mp3       # Downloaded songs with metadata
```

**Key Files:**
- `playlistDownloaderUI.py` - Tkinter GUI with progress tracking
- `playlistDownloader.py` - Command-line interface
- `songDownloader.py` - Reusable download function (used by other scripts)
- `.env` - Your Spotify API credentials (you create this)
- `playlists/*.csv` - Download history per playlist

---

## Technical Details

**Download Process:**
1. Parses Spotify playlist URL/URI/ID
2. Authenticates with Spotify API using Client Credentials
3. Fetches all tracks (handles pagination for large playlists)
4. Extracts metadata: artist, title, album, genre, album art URL
5. Compares with history CSV using `artist|title` as unique key
6. Downloads new tracks via yt-dlp from YouTube (searches: "artist - title")
7. Converts to MP3 (best quality available)
8. Applies ID3 tags using mutagen:
   - TIT2: Title
   - TPE1: Artist
   - TALB: Album
   - TCON: Genre
   - APIC: Album artwork (embedded JPEG)
9. Saves successful downloads to history CSV

**Concurrency:**
- Uses `ThreadPoolExecutor` for parallel downloads
- Thread-safe CSV writing with `threading.Lock`
- Downloads are CPU-bound (re-encoding) so 4-12 threads is optimal
- GUI uses separate thread to keep interface responsive

**Authentication:**
- Client Credentials flow (app-only, no user login required)
- Works with public playlists
- Token cached and auto-refreshed by spotipy

---

## Frequently Asked Questions

**Q: Why are some songs not found?**
A: The app searches YouTube for "Artist - Title". If the video isn't available or has a different name, it may fail. The script continues with other songs.

**Q: Can I change the audio quality?**
A: Yes, edit `songDownloader.py` and modify the `--audio-quality` parameter (0 = best, 9 = worst).

**Q: How do I reset a playlist and re-download everything?**
A: Delete `playlists/<playlist_id>.csv` and run the downloader again.

**Q: Can I run multiple playlists simultaneously?**
A: Yes! Each playlist is tracked independently. Run multiple instances or queue them in the GUI.

**Q: Does this work on Windows/macOS/Linux?**
A: Yes, it's cross-platform Python. Just make sure ffmpeg is installed on your system.

**Q: How much disk space do I need?**
A: Approximately 3-5 MB per song (varies by length and quality). A 100-song playlist ≈ 300-500 MB.

**Q: Can I use this commercially?**
A: This tool is for personal use only. Respect Spotify's Terms of Service and copyright laws.

**Q: The GUI shows "Complete" but some downloads failed. Why?**
A: Failed downloads are logged in the output. They're NOT added to history, so they'll retry on your next run.

**Q: Can I change the filename format?**
A: Yes, edit the `download_from_youtube()` function in `playlistDownloader.py` or `playlistDownloaderUI.py`.

---

## Additional Features

### Playlist Checkers (Apple Music & Spotify)

The repository includes `checkPlaylist_Spotify.py` which integrates with the Apple Music checker workflow. See the script for details on automated playlist monitoring.

### Command-Line Only Mode

If you prefer no GUI dependencies:
```bash
pip install spotipy yt-dlp mutagen python-dotenv requests
python playlistDownloader.py --playlist "URL" --output-dir ./music
```

### Extending the Downloader

`songDownloader.py` is a reusable module. Import it in your own scripts:

```python
from songDownloader import download_song

success = download_song("Track Name", "Artist Name", "./output_folder")
if success:
    print("Downloaded successfully!")
```

---

## Contributing

Contributions are welcome! Areas for improvement:
- Better error handling for edge cases
- Playlist update notifications
- Support for other streaming services
- Custom metadata templates

---

## License

This project is provided as-is for personal use. Respect the terms of service of Spotify, YouTube, and other platforms. The authors are not responsible for misuse.

---

## Credits

Built with:
- [spotipy](https://github.com/plamere/spotipy) - Spotify Web API client
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube downloader
- [mutagen](https://github.com/quodlibet/mutagen) - Audio metadata library
- [tkinter](https://docs.python.org/3/library/tkinter.html) - Python GUI framework

---

## Support

If you encounter issues:
1. Check the [Troubleshooting](#troubleshooting) section
2. Verify your `.env` file is configured correctly
3. Make sure ffmpeg is installed and in your PATH
4. Check the log output for specific error messages
5. Open an issue on GitHub with details about your problem

**Happy downloading! 🎵**
