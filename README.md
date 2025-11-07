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

## License

This project is open source and available under the MIT License.
