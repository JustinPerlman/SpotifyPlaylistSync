# YouTube Audio Downloader

A Python tool that automates downloading audio tracks from YouTube based on either a JSON playlist file or a CSV file. The script searches YouTube for each track and downloads the audio in M4A format.

## Features

- Bulk download audio tracks from YouTube
- Two input formats supported:
  - JSON playlist file (exported from services like Spotify via Songshift)
  - CSV file with track and artist information
- Searches YouTube based on artist and track name
- Converts downloads to M4A format (to avoid libmp3lame encoder issues)
- Organizes downloads in dedicated folders
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
cd YoutubeMP3Downloader
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

1. Place your playlist JSON file in the root directory (default name: `EDM.json`)
2. If needed, set the FFmpeg path in either `jsonDownloader.py` or `csvDownloader.py`:

```python
FFMPEG_PATH = 'path/to/ffmpeg'  # Leave empty if FFmpeg is in system PATH
```

## Input Formats

### JSON Format

Use the iOS app [Songshift](https://www.songshift.com/) to export a playlist from Spotify, Apple Music, etc. to JSON format. The JSON file should follow this structure:

```json
[
  {
    "name": "Playlist Name",
    "tracks": [
      {
        "track": "Song Name",
        "artist": "Artist Name",
        "album": "Album Name",
        "isrc": "ISRC Code" // Optional
      }
    ]
  }
]
```

### CSV Format

The CSV file should contain at minimum these columns:

- `Artist Name(s)`: The name of the artist(s)
- `Track Name`: The name of the song

Example CSV format:

```csv
Artist Name(s),Track Name
The Beatles,Hey Jude
Queen,Bohemian Rhapsody
```

## Usage

You can use either the JSON or CSV method to download tracks:

### JSON Method

Run the script:

```bash
python jsonDownloader.py
```

The script will:

1. Create a `downloads` directory if it doesn't exist
2. Read the track list from `EDM.json`
3. Search YouTube for each track
4. Download and convert the audio to M4A format
5. Save files as `Artist - Track.m4a`
6. Provide a summary of successful and failed downloads

### CSV Method

Run the script:

```bash
python csvDownloader.py
```

The script will:

1. Create a `downloads_csv` directory if it doesn't exist
2. Read the track list from your CSV file (default: `flumbuses.csv`)
3. Search YouTube for each track
4. Download and convert the audio to M4A format
5. Save files as `Artist - Track.m4a`
6. Provide a summary of successful and failed downloads

## Output

Files are saved in the respective output directories:

- JSON method: `downloads` directory
- CSV method: `downloads_csv` directory

Files in both directories follow the naming format:

```
Artist - Track.m4a
```

## Error Handling

The script provides detailed error output for:

- Missing JSON file
- Invalid JSON format
- Download failures
- FFmpeg/yt-dlp command errors

## License

This project is open source and available under the MIT License.
