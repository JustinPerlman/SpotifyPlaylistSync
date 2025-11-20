"""songDownloader.py
--------------------
Small helper used by higher-level scripts to download a single song
by searching YouTube via yt-dlp. Exposes `download_song` returning
True/False to indicate success without raising.
"""

import subprocess
import os
from typing import List


def _build_command(search_query: str, output_template: str) -> List[str]:
    """Construct the yt-dlp command for a given search query and output path."""
    return [
        "yt-dlp",
        "-x",  # extract audio
        "--audio-format",
        "m4a",  # M4A format
        "--audio-quality",
        "0",  # best available quality
        "--quiet",  # keep stdout clean for callers
        "-o",
        output_template,
        f"ytsearch1:{search_query}",
    ]


def sanitize_filename(filename: str) -> str:
    """Remove or replace characters that are invalid in filenames."""
    # Replace forward slashes with a safe character
    filename = filename.replace('/', '-')
    # Replace other problematic characters
    filename = filename.replace('\\', '-')
    filename = filename.replace(':', '-')
    filename = filename.replace('*', '')
    filename = filename.replace('?', '')
    filename = filename.replace('"', "'")
    filename = filename.replace('<', '')
    filename = filename.replace('>', '')
    filename = filename.replace('|', '-')
    return filename


def download_song(track_name: str, artist: str, download_folder: str) -> bool:
    """Download a song using yt-dlp search of YouTube.

    Args:
        track_name: The track title to search for.
        artist: The primary artist name.
        download_folder: Destination directory for the output audio file.

    Returns:
        True if the yt-dlp command exits successfully; False otherwise.
    """
    if not os.path.exists(download_folder):
        os.makedirs(download_folder, exist_ok=True)
    
    search_query = f"{artist} - {track_name}"
    # Sanitize artist and track name for filesystem - use "Artist - Title" format
    safe_artist = sanitize_filename(artist)
    safe_track_name = sanitize_filename(track_name)
    output_template = os.path.join(download_folder, f"{safe_artist} - {safe_track_name}.%(ext)s")
    command = _build_command(search_query, output_template)

    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        return True
    except Exception:
        return False
