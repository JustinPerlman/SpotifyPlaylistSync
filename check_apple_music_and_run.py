#!/usr/bin/env python3
"""
check_apple_music_and_run.py

Checks an Apple Music playlist (macOS Music app) for new songs compared to an existing CSV
(`flumbuses.csv` by default), writes a CSV of the new songs (matching the columns expected by
`csvDownloader.py`) and then runs `csvDownloader.py` on that CSV.

This script uses `osascript` (AppleScript) to query the Music app, so it only runs on macOS.

Usage:
  python check_apple_music_and_run.py --playlist "My Playlist" --output-dir downloads

If no `--csv` is provided the script will read `flumbuses.csv` in the repo root to determine
which tracks were already processed.
"""
import argparse
import csv
import datetime
import os
import subprocess
import sys
import tempfile
from typing import List, Tuple


TRACK_NAME_COLUMN = "Track Name"
ARTIST_NAME_COLUMN = "Artist Name(s)"
HISTORY_CSV = "EDM_Justin.csv"  # Stores all previously processed songs


def read_processed_set(csv_path: str) -> set:
    """Read existing CSV and return a set of (track_lower, first_artist_lower) tuples."""
    processed = set()
    if not os.path.exists(csv_path):
        return processed

    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if TRACK_NAME_COLUMN not in reader.fieldnames or ARTIST_NAME_COLUMN not in reader.fieldnames:
                # If the CSV doesn't contain both columns, treat as empty
                return processed

            for row in reader:
                track = (row.get(TRACK_NAME_COLUMN) or "").strip().lower()
                artist_field = (row.get(ARTIST_NAME_COLUMN) or "").strip()
                # Take first artist when multiple are separated by ';'
                first_artist = artist_field.split(";")[0].strip().lower() if artist_field else ""
                if track and first_artist:
                    processed.add((track, first_artist))
    except Exception:
        # On any read/parsing issue, return empty set to avoid false-negatives
        return set()

    return processed


def query_music_playlist(playlist_name: str) -> List[Tuple[str, str]]:
    """Query the macOS Music app for tracks in a playlist using AppleScript (osascript).

    Returns a list of (track_name, artist) pairs in the playlist order.
    If playlist doesn't exist or another error happens, raises RuntimeError.
    """
    # Build AppleScript that concatenates name and artist with separators we can parse reliably
    sep_item = "|||ITEM|||"
    sep_fields = "|||FIELD|||"

    applescript = f'''
tell application "Music"
  if not (exists playlist "{playlist_name}") then
    return "__PLAYLIST_NOT_FOUND__"
  end if
  set outStr to ""
  set pl to playlist "{playlist_name}"
  repeat with tr in (tracks of pl)
    try
      set tname to name of tr
    on error
      set tname to ""
    end try
    try
      set art to artist of tr
    on error
      set art to ""
    end try
    set outStr to outStr & tname & "{sep_fields}" & art & "{sep_item}"
  end repeat
  return outStr
end tell
'''

    try:
        result = subprocess.run(["osascript", "-e", applescript], capture_output=True, text=True, check=True)
        output = result.stdout
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"osascript failed: {e.stderr or e.stdout}")

    if not output:
        return []
    if "__PLAYLIST_NOT_FOUND__" in output:
        raise RuntimeError(f"Playlist '{playlist_name}' not found in Music app.")

    items = [s for s in output.split(sep_item) if s]
    tracks = []
    for it in items:
        if sep_fields in it:
            tname, art = it.split(sep_fields, 1)
            tracks.append((tname.strip(), art.strip()))
    return tracks


def write_new_csv(new_tracks: List[Tuple[str, str]], out_path: str) -> None:
    """Write a CSV compatible with `csvDownloader.py` containing only Track Name and Artist Name(s)."""
    fieldnames = [TRACK_NAME_COLUMN, ARTIST_NAME_COLUMN]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for track, artist in new_tracks:
            writer.writerow({TRACK_NAME_COLUMN: track, ARTIST_NAME_COLUMN: artist})


def download_single_track(track: str, artist: str, output_dir: str) -> bool:
    """Download a single track and return True if successful."""
    # Create a temporary CSV with just this track
    fd, tmp_csv = tempfile.mkstemp(suffix=".csv")
    os.close(fd)
    try:
        write_new_csv([(track, artist)], tmp_csv)
        csvdownloader_path = os.path.join(os.path.dirname(__file__), "csvDownloader.py")
        if not os.path.exists(csvdownloader_path):
            print(f"Error: csvDownloader.py not found at {csvdownloader_path}")
            return False

        cmd = [sys.executable, csvdownloader_path, tmp_csv, output_dir]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Check if download was actually successful by looking for success message in output
        success = "✅ Success: Downloaded" in result.stdout
        
        if not success:
            print(f"Failed to download: {artist} - {track}")
            if result.stderr:
                print(f"Error output: {result.stderr}")
            if result.stdout:
                print(f"Download output: {result.stdout}")
        return success
    finally:
        # Clean up temp file
        try:
            os.unlink(tmp_csv)
        except OSError:
            pass


def append_to_history(new_tracks: List[Tuple[str, str]], history_path: str) -> None:
    """Append newly processed tracks to the history CSV."""
    fieldnames = [TRACK_NAME_COLUMN, ARTIST_NAME_COLUMN]
    # Create file with header if it doesn't exist
    if not os.path.exists(history_path):
        with open(history_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
    
    # Append new tracks
    with open(history_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        for track, artist in new_tracks:
            writer.writerow({TRACK_NAME_COLUMN: track, ARTIST_NAME_COLUMN: artist})


def main():
    parser = argparse.ArgumentParser(description="Detect new songs in an Apple Music playlist and run csvDownloader on them.")
    parser.add_argument("--playlist", required=True, help="Name of the playlist in the macOS Music app to check")
    parser.add_argument("--out-csv", default=None, help="Path to write the new-songs CSV (default: temporary file)")
    parser.add_argument("--output-dir", default="downloads", help="Directory where downloads will be stored")
    parser.add_argument("--dry-run", action="store_true", help="Only print which songs would be added / downloaded, don't run downloader")
    args = parser.parse_args()

    if sys.platform != "darwin":
        print("This script only runs on macOS using the Music app via AppleScript.")
        sys.exit(1)

    history_path = os.path.join(os.path.dirname(__file__), HISTORY_CSV)
    processed = read_processed_set(history_path)
    try:
        playlist_tracks = query_music_playlist(args.playlist)
    except RuntimeError as e:
        print(f"Error querying Music app: {e}")
        sys.exit(1)

    new_tracks = []
    for track_name, artist in playlist_tracks:
        key = (track_name.strip().lower(), (artist.split(';')[0].strip().lower() if artist else ""))
        if key not in processed:
            # Keep artist string as-is (Music usually gives a single artist string)
            new_tracks.append((track_name.strip(), artist.strip()))

    if not new_tracks:
        print("No new tracks found in playlist. Nothing to do.")
        sys.exit(0)

    print(f"Found {len(new_tracks)} new track(s) in playlist '{args.playlist}':")
    for t, a in new_tracks:
        print(f"  - {a} - {t}")

    # Create csv directory in repo if it doesn't exist
    csv_dir = os.path.join(os.path.dirname(__file__), "csv")
    os.makedirs(csv_dir, exist_ok=True)

    # Determine CSV path
    if args.out_csv:
        out_csv = args.out_csv
    else:
        # Use timestamp for unique filenames
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        out_csv = os.path.join(csv_dir, f"new_songs_{timestamp}.csv")

    write_new_csv(new_tracks, out_csv)
    print(f"Wrote new songs CSV to: {out_csv}")

    if args.dry_run:
        print("Dry run requested; not running csvDownloader.")
        sys.exit(0)

    # Ensure output directory exists
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir, exist_ok=True)

    # Process each track individually
    successful_tracks = []
    failed_tracks = []

    for track, artist in new_tracks:
        print(f"\nProcessing: {artist} - {track}")
        if download_single_track(track, artist, args.output_dir):
            successful_tracks.append((track, artist))
            # Add to history immediately after successful download
            append_to_history([(track, artist)], history_path)
            print(f"✓ Successfully downloaded and added to history: {artist} - {track}")
        else:
            failed_tracks.append((track, artist))

    # Print summary
    print("\n=== Download Summary ===")
    print(f"Total tracks processed: {len(new_tracks)}")
    print(f"Successfully downloaded: {len(successful_tracks)}")
    print(f"Failed to download: {len(failed_tracks)}")
    
    if failed_tracks:
        print("\nFailed tracks (will be retried next time):")
        for track, artist in failed_tracks:
            print(f"  - {artist} - {track}")
    
    # Exit with error if any track failed
    sys.exit(1 if failed_tracks else 0)


if __name__ == "__main__":
    main()
