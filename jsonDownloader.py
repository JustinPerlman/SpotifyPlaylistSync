import json
import subprocess
import os

# --- Configuration ---
JSON_FILE = "EDM.json"
DOWNLOAD_DIR = "downloads"

# The command uses ytsearch1: to search YouTube and grab the first result only.
# -x: extract audio
# --audio-format m4a: CONVERTED FROM MP3 TO M4A TO AVOID libmp3lame ENCODER ERROR
# --audio-quality 0: highest quality available
# -o: output template. We use the artist/track names from the JSON for naming.
YT_DLP_BASE_COMMAND = [
    "yt-dlp",
    "-x",
    "--audio-format",
    "m4a",  # <-- CHANGED from 'mp3' to 'm4a'
    "--audio-quality",
    "0",
    "--quiet",  # Suppress standard output for cleaner terminal
]
# ---------------------


def main():
    """Reads track data and downloads the corresponding audio from YouTube."""

    current_base_command = list(YT_DLP_BASE_COMMAND)

    # 1. Setup download directory
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)
        print(f"Created output directory: {DOWNLOAD_DIR}")

    # 2. Load tracks from JSON file
    try:
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(
            f"Error: The input file '{JSON_FILE}' was not found. Please ensure it's in the same directory."
        )
        return
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from '{JSON_FILE}'. Check file format.")
        return

    # Extract the list of tracks, assuming the nested structure: data[0]['tracks']
    try:
        tracks = data[0]["tracks"]
    except (IndexError, KeyError):
        print(
            "Error: JSON structure is unexpected. Expected a list of playlists with a 'tracks' key."
        )
        return

    total_tracks = len(tracks)
    print(f"Found {total_tracks} tracks to process across all playlists.")

    successful_downloads = 0
    failed_downloads = 0

    # 3. Loop through all tracks and download
    for i, track_info in enumerate(tracks):
        artist = track_info.get("artist", "Unknown Artist")
        track_name = track_info.get("track", "Unknown Track")

        # Construct the most accurate search query
        search_query = f"{artist} - {track_name}"

        # Define the exact output filename path, using a template for yt-dlp
        # This ensures the filename is based on the JSON data, not the YouTube video title.
        output_filename_template = os.path.join(
            DOWNLOAD_DIR, f"{artist} - {track_name}.%(ext)s"
        )

        print(f"\n--- [{i+1}/{total_tracks}] Searching for: {search_query} ---")

        # Construct the full command for this track
        command = current_base_command + [
            "-o",
            output_filename_template,
            f"ytsearch1:{search_query}",
        ]

        try:
            # Execute the download command
            subprocess.run(command, check=True, capture_output=True, text=True)
            print(f"✅ Success: Downloaded {track_name}")
            successful_downloads += 1

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to download/convert for: {search_query}")
            # --- EDITED SECTION: Print the full stderr output for debugging ---
            print("   --- YT-DLP ERROR OUTPUT ---")
            print(e.stderr)
            print("   ---------------------------")
            # -----------------------------------------------------------------
            failed_downloads += 1
        except FileNotFoundError:
            # This FileNotFoundError likely means 'yt-dlp' itself is not found, or possibly ffmpeg
            # if yt-dlp is trying to execute it directly (less common with --ffmpeg-location).
            print(
                "\nFATAL ERROR: 'yt-dlp' command not found, or external tool not accessible."
            )
            print(
                "Please ensure yt-dlp is installed and accessible in your system's PATH."
            )
            return

    # 4. Print summary
    print("\n==================================")
    print("Download Process Complete.")
    print(f"Total Tracks Processed: {total_tracks}")
    print(f"Successful Downloads: {successful_downloads}")
    print(f"Failed Downloads: {failed_downloads}")
    print(f"Files are saved in the '{DOWNLOAD_DIR}' directory.")
    print("==================================")


if __name__ == "__main__":
    main()
