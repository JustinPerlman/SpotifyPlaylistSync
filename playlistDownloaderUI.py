import os
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import threading
import queue
from dotenv import load_dotenv
import csv
import re
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error, TIT2, TPE1, TALB, TCON
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from songDownloader import download_song

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)

# Configuration
SPOTIFY_CLIENT_ID = os.environ.get("SPOTIPY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIPY_CLIENT_SECRET")

if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
    print("Error: SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET must be set in .env file")

# Initialize Spotify client
sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET
    )
)

csv_lock = Lock()


def extract_playlist_id(playlist_input):
    """Extract playlist ID from URL, URI, or ID string"""
    if len(playlist_input) == 22 and not ('/' in playlist_input or ':' in playlist_input):
        return playlist_input
    
    if 'open.spotify.com/playlist/' in playlist_input:
        match = re.search(r'playlist/([a-zA-Z0-9]+)', playlist_input)
        if match:
            return match.group(1)
    
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
                track_id = f"{row['artist']}|{row['title']}"
                downloaded.add(track_id)
    except Exception as e:
        print(f"Error reading history CSV: {e}")
    
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
            print(f"Error saving to history CSV: {e}")


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


def download_from_youtube(song, download_dir):
    """Download song from YouTube using songDownloader utility"""
    success = download_song(song['title'], song['artist'], download_dir)
    
    if success:
        return os.path.join(download_dir, f"{song['title']}.mp3")
    return None


def apply_metadata(mp3_path, song):
    """Apply Spotify metadata and cover art to mp3 file"""
    try:
        audio = MP3(mp3_path, ID3=ID3)
        try:
            audio.add_tags()
        except error:
            pass

        audio["TIT2"] = TIT2(encoding=3, text=song['title'])
        audio["TPE1"] = TPE1(encoding=3, text=song['artist'])
        audio["TALB"] = TALB(encoding=3, text=song['album'])
        if song['genre']:
            audio["TCON"] = TCON(encoding=3, text=song['genre'])

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
    except Exception as e:
        print(f"Metadata error for {song['title']}: {e}")


def process_song(song, download_dir, csv_path, log_queue):
    """Download and apply metadata to a single song"""
    try:
        log_queue.put(f"🎧 Downloading: {song['artist']} - {song['title']}")
        mp3_path = download_from_youtube(song, download_dir)
        if mp3_path:
            apply_metadata(mp3_path, song)
            save_downloaded_track(csv_path, song)
            log_queue.put(f"✅ Completed: {song['title']}\n")
            return True, song['title']
        else:
            log_queue.put(f"❌ Failed: {song['title']}\n")
            return False, song['title']
    except Exception as e:
        log_queue.put(f"⚠️ Error: {song['title']} - {e}\n")
        return False, song['title']


class PlaylistDownloaderUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Spotify Playlist Downloader")
        self.root.geometry("800x600")
        
        self.download_thread = None
        self.log_queue = queue.Queue()
        
        self.create_widgets()
        self.check_log_queue()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        # Playlist URL
        ttk.Label(main_frame, text="Playlist URL:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.playlist_entry = ttk.Entry(main_frame, width=50)
        self.playlist_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # Output Directory
        ttk.Label(main_frame, text="Output Directory:").grid(row=1, column=0, sticky=tk.W, pady=5)
        dir_frame = ttk.Frame(main_frame)
        dir_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        dir_frame.columnconfigure(0, weight=1)
        
        self.output_dir_entry = ttk.Entry(dir_frame)
        self.output_dir_entry.insert(0, "./newThingDownloads")
        self.output_dir_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(dir_frame, text="Browse", command=self.browse_directory).grid(row=0, column=1)
        
        # Thread Count
        ttk.Label(main_frame, text="Concurrent Downloads:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.threads_spinbox = ttk.Spinbox(main_frame, from_=1, to=20, width=10)
        self.threads_spinbox.set(4)
        self.threads_spinbox.grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Progress Bar
        ttk.Label(main_frame, text="Progress:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # Status Label
        self.status_label = ttk.Label(main_frame, text="Ready", foreground="blue")
        self.status_label.grid(row=4, column=0, columnspan=2, pady=5)
        
        # Log Area
        ttk.Label(main_frame, text="Log:").grid(row=5, column=0, sticky=(tk.W, tk.N), pady=5)
        self.log_text = scrolledtext.ScrolledText(main_frame, width=70, height=20, state='disabled')
        self.log_text.grid(row=5, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=10)
        
        self.download_button = ttk.Button(button_frame, text="Start Download", command=self.start_download)
        self.download_button.grid(row=0, column=0, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_download, state='disabled')
        self.stop_button.grid(row=0, column=1, padx=5)
        
        ttk.Button(button_frame, text="Clear Log", command=self.clear_log).grid(row=0, column=2, padx=5)
        
    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir_entry.delete(0, tk.END)
            self.output_dir_entry.insert(0, directory)
    
    def log_message(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
    
    def clear_log(self):
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')
    
    def check_log_queue(self):
        """Check for new log messages from the download thread"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_message(message)
        except queue.Empty:
            pass
        self.root.after(100, self.check_log_queue)
    
    def start_download(self):
        playlist_url = self.playlist_entry.get().strip()
        output_dir = self.output_dir_entry.get().strip()
        
        if not playlist_url:
            self.log_message("❌ Error: Please enter a playlist URL")
            return
        
        if not output_dir:
            self.log_message("❌ Error: Please enter an output directory")
            return
        
        try:
            threads = int(self.threads_spinbox.get())
        except ValueError:
            self.log_message("❌ Error: Invalid thread count")
            return
        
        # Disable buttons
        self.download_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.status_label.config(text="Downloading...", foreground="orange")
        
        # Start download in separate thread
        self.download_thread = threading.Thread(
            target=self.download_playlist,
            args=(playlist_url, output_dir, threads),
            daemon=True
        )
        self.download_thread.start()
    
    def stop_download(self):
        self.status_label.config(text="Stopping...", foreground="red")
        self.log_message("\n⚠️ Stop requested (current downloads will complete)...\n")
        # Note: Graceful stopping would require more complex thread management
    
    def download_playlist(self, playlist_url, output_dir, num_threads):
        try:
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            # Setup history CSV
            playlist_id = extract_playlist_id(playlist_url)
            playlists_dir = os.path.join(os.path.dirname(__file__), 'playlists')
            os.makedirs(playlists_dir, exist_ok=True)
            csv_path = os.path.join(playlists_dir, f"{playlist_id}.csv")
            
            # Load previously downloaded tracks
            downloaded_tracks = load_downloaded_tracks(csv_path)
            self.log_queue.put(f"📋 Previously downloaded: {len(downloaded_tracks)} tracks\n")
            
            # Fetch playlist
            self.log_queue.put("🔍 Fetching playlist tracks...")
            songs = get_playlist_tracks(playlist_url)
            self.log_queue.put(f"Found {len(songs)} tracks in playlist.\n")
            
            # Filter new songs
            new_songs = []
            for song in songs:
                track_id = f"{song['artist']}|{song['title']}"
                if track_id not in downloaded_tracks:
                    new_songs.append(song)
            
            if not new_songs:
                self.log_queue.put("✅ No new tracks to download!\n")
                self.download_complete(0, 0, 0)
                return
            
            self.log_queue.put(f"🆕 New tracks to download: {len(new_songs)}\n")
            self.log_queue.put(f"Using {num_threads} concurrent threads...\n")
            self.log_queue.put("="*50 + "\n")
            
            # Update progress bar
            self.progress['maximum'] = len(new_songs)
            self.progress['value'] = 0
            
            successful = 0
            failed = 0
            
            # Download with thread pool
            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                futures = {
                    executor.submit(process_song, song, output_dir, csv_path, self.log_queue): song 
                    for song in new_songs
                }
                
                for future in as_completed(futures):
                    success, title = future.result()
                    if success:
                        successful += 1
                    else:
                        failed += 1
                    
                    # Update progress
                    self.progress['value'] = successful + failed
                    self.root.update_idletasks()
            
            self.download_complete(successful, failed, len(new_songs))
            
        except Exception as e:
            self.log_queue.put(f"\n❌ Error: {str(e)}\n")
            self.download_complete(0, 0, 0, error=True)
    
    def download_complete(self, successful, failed, total, error=False):
        """Called when download is complete"""
        self.log_queue.put("\n" + "="*50)
        if not error:
            self.log_queue.put(f"Download Complete!")
            self.log_queue.put(f"Successful: {successful}/{total}")
            self.log_queue.put(f"Failed: {failed}/{total}")
        self.log_queue.put("="*50 + "\n")
        
        # Re-enable buttons
        self.download_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.status_label.config(text="Complete" if not error else "Error", 
                                foreground="green" if not error else "red")


def main():
    root = tk.Tk()
    app = PlaylistDownloaderUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
