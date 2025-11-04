# YouTube MP3 Downloader

A Python script that automates downloading audio tracks from YouTube based on a JSON playlist file. The script searches YouTube for each track and downloads the audio in M4A format.

## Features

- Bulk download audio tracks from YouTube
- Searches YouTube based on artist and track name
- Converts downloads to M4A format (to avoid libmp3lame encoder issues)
- Organizes downloads in a dedicated folder
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
2. If needed, set the FFmpeg path in `main.py`:

```python
FFMPEG_PATH = 'path/to/ffmpeg'  # Leave empty if FFmpeg is in system PATH
```

## JSON Format

Use the iOS/Android app [Songshift](https://www.songshift.com/) to export a playlist from Spotify, Apple Music, etc. to JSON format. The JSON file should follow this structure:

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

## Usage

Run the script:

```bash
python main.py
```

The script will:

1. Create a `downloads` directory if it doesn't exist
2. Read the track list from `EDM.json`
3. Search YouTube for each track
4. Download and convert the audio to M4A format
5. Save files as `Artist - Track.m4a`
6. Provide a summary of successful and failed downloads

## Output

Files are saved in the `downloads` directory with the naming format:

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
