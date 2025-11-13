import os
import re
import csv
import argparse
from dotenv import load_dotenv
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error, TIT2, TPE1, TALB, TCON
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from songDownloader import download_song

# Load environment variables from .env file
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    print("Warning: .env file not found. Make sure to set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET environment variables.")

# --- CONFIGURATION ---
SPOTIFY_CLIENT_ID = os.environ.get("SPOTIPY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIPY_CLIENT_SECRET")
DOWNLOAD_DIR = r"./newThingDownloads"

if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
    print("Error: SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET must be set in .env file or environment variables.")
    exit(1)


# --- AUTHENTICATE SPOTIFY ---
sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET
    )
)

# Thread-safe lock for CSV writing
csv_lock = Lock()

def extract_playlist_id(playlist_input):
    """Extract playlist ID from URL, URI, or ID string"""
    # If it's already just an ID
    if len(playlist_input) == 22 and not ('/' in playlist_input or ':' in playlist_input):
        return playlist_input
    
    # Extract from URL
    if 'open.spotify.com/playlist/' in playlist_input:
        match = re.search(r'playlist/([a-zA-Z0-9]+)', playlist_input)
        if match:
            return match.group(1)
    
    # Extract from URI
    if 'spotify:playlist:' in playlist_input:
        return playlist_input.split(':')[-1]
    
    return playlist_input


def load_downloaded_tracks(csv_path):
    """Load previously downloaded tracks from CSV"""
    if not os.path.exists(csv_path):
        return set()
    
    downloaded = set()
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Create unique identifier from artist and title
                track_id = f"{row['artist']}|{row['title']}"
                downloaded.add(track_id)
    except Exception as e:
        print(f"⚠️ Error reading history CSV: {e}")
    
    return downloaded


def save_downloaded_track(csv_path, song):
    """Append a successfully downloaded track to the CSV"""
    file_exists = os.path.exists(csv_path)
    
    with csv_lock:
        try:
            with open(csv_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['artist', 'title', 'album'])
                if not file_exists:
                    writer.writeheader()
                writer.writerow({
                    'artist': song['artist'],
                    'title': song['title'],
                    'album': song['album']
                })
        except Exception as e:
            print(f"⚠️ Error saving to history CSV: {e}")

def get_playlist_tracks(playlist_url):
    """Fetch all track info from a Spotify playlist"""
    results = sp.playlist_tracks(playlist_url)
    tracks = results['items']

    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])

    songs = []
    for item in tracks:
        track = item['track']
        if track is None:
            continue

        artist = track['artists'][0]['name']
        track_name = track['name']
        album = track['album']['name']
        cover_url = track['album']['images'][0]['url'] if track['album']['images'] else None
        track_id = track['artists'][0]['id']

        # Fetch genre (from artist metadata)
        genre = None
        try:
            artist_info = sp.artist(track_id)
            if artist_info['genres']:
                genre = artist_info['genres'][0].title()
        except Exception:
            genre = None

        songs.append({
            "artist": artist,
            "title": track_name,
            "album": album,
            "cover_url": cover_url,
            "genre": genre
        })
    return songs


def download_from_youtube(song):
    """Download song from YouTube using songDownloader utility"""
    print(f"🎧 Downloading: {song['artist']} - {song['title']}")
    success = download_song(song['title'], song['artist'], DOWNLOAD_DIR)
    
    if success:
        # songDownloader outputs as mp3 with format: "Track.mp3"
        return os.path.join(DOWNLOAD_DIR, f"{song['title']}.mp3")
    return None


def apply_metadata(mp3_path, song):
    """Apply Spotify metadata and cover art to mp3 file"""
    try:
        audio = MP3(mp3_path, ID3=ID3)
        try:
            audio.add_tags()
        except error:
            pass

        # Apply text metadata using ID3 tags
        audio["TIT2"] = TIT2(encoding=3, text=song['title'])
        audio["TPE1"] = TPE1(encoding=3, text=song['artist'])
        audio["TALB"] = TALB(encoding=3, text=song['album'])
        if song['genre']:
            audio["TCON"] = TCON(encoding=3, text=song['genre'])

        # Apply album art
        if song['cover_url']:
            img_data = requests.get(song['cover_url']).content
            audio.tags.add(
                APIC(
                    encoding=3,
                    mime="image/jpeg",
                    type=3,
                    desc=u"Cover",
                    data=img_data,
                )
            )
        
        audio.save()
        print(f"✅ Tagged: {song['artist']} - {song['title']}\n")
    except Exception as e:
        print(f"⚠️ Metadata error for {song['title']}: {e}")


def process_song(song, csv_path):
    """Download and apply metadata to a single song (for threading)"""
    try:
        mp3_path = download_from_youtube(song)
        if mp3_path:
            apply_metadata(mp3_path, song)
            save_downloaded_track(csv_path, song)
            return True, song['title']
        else:
            return False, song['title']
    except Exception as e:
        print(f"⚠️ Error processing {song['title']}: {e}")
        return False, song['title']


def main():
    parser = argparse.ArgumentParser(
        description="Download tracks from a Spotify playlist with metadata and album art."
    )
    parser.add_argument(
        "--playlist",
        required=True,
        help="Spotify playlist URL, URI, or ID"
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Download directory (default: from DOWNLOAD_DIR env var or 'downloads')"
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=4,
        help="Number of concurrent downloads (default: 4)"
    )
    args = parser.parse_args()

    # Temporarily override DOWNLOAD_DIR for this run if specified
    global DOWNLOAD_DIR
    if args.output_dir:
        DOWNLOAD_DIR = args.output_dir
    
    # Create the download directory
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    
    # Extract playlist ID and setup history CSV
    playlist_id = extract_playlist_id(args.playlist)
    playlists_dir = os.path.join(os.path.dirname(__file__), 'playlists')
    os.makedirs(playlists_dir, exist_ok=True)
    csv_path = os.path.join(playlists_dir, f"{playlist_id}.csv")
    
    # Load previously downloaded tracks
    downloaded_tracks = load_downloaded_tracks(csv_path)
    print(f"📋 Previously downloaded: {len(downloaded_tracks)} tracks\n")

    songs = get_playlist_tracks(args.playlist)
    print(f"Found {len(songs)} tracks in playlist.\n")
    
    # Filter out already downloaded tracks
    new_songs = []
    for song in songs:
        track_id = f"{song['artist']}|{song['title']}"
        if track_id not in downloaded_tracks:
            new_songs.append(song)
    
    if not new_songs:
        print("✅ No new tracks to download!\n")
        return
    
    print(f"🆕 New tracks to download: {len(new_songs)}\n")
    print(f"Downloading with {args.threads} concurrent threads...\n")

    successful = 0
    failed = 0

    # Use ThreadPoolExecutor for concurrent downloads
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        # Submit all download jobs
        futures = {executor.submit(process_song, song, csv_path): song for song in new_songs}
        
        # Process completed downloads as they finish
        for future in as_completed(futures):
            success, title = future.result()
            if success:
                successful += 1
            else:
                failed += 1

    print(f"\n{'='*50}")
    print(f"Download Complete!")
    print(f"Successful: {successful}/{len(new_songs)}")
    print(f"Failed: {failed}/{len(new_songs)}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()
