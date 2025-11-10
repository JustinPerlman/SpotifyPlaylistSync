"""syncSpotifyLogon.py
------------------
Fetch a Spotify playlist and download only the tracks not yet present in the
local per-playlist history CSV. History lives in `playlists/<playlist_id>.csv`.

Workflow:
1. Resolve playlist ID from URL/URI/raw ID.
2. Fetch all tracks (paginated) via Spotipy user login (PKCE/OAuth).
3. Load previously downloaded (track, artist) pairs from history.
4. If --dry-run: list new tracks and exit.
5. Otherwise: download each new track (via songDownloader), append to history.

Authentication (config file only; no .env used):
    Reads `.spotify_app.json` containing: { "client_id": "...", "redirect_uri": "http://127.0.0.1:8888/callback" }
    Optionally `client_secret` if PKCE unavailable and you want OAuth fallback (NOT recommended to ship secret).

Caching: Uses a dedicated `.cache_spotify` file instead of Spotipy default `.cache`.
"""

import os
import sys
import argparse
import json
from pathlib import Path
from spotipy import Spotify
from spotipy.oauth2 import (
    SpotifyOAuth,
)  # for fallback when PKCE unavailable and secret provided

try:
    # Prefer PKCE (no client secret) when available
    from spotipy.oauth2 import SpotifyPKCE  # type: ignore

    HAS_PKCE = True
except Exception:
    from spotipy.oauth2 import SpotifyOAuth  # fallback to OAuth (needs secret)

    HAS_PKCE = False
from spotipy.cache_handler import CacheFileHandler
from songDownloader import download_song
import csv

TRACKING_DIR = "playlists"


def get_playlist_id(playlist_url):
    """Extract canonical playlist ID from URL/URI/raw ID."""
    # Common URL form: https://open.spotify.com/playlist/<id>?...
    if "playlist/" in playlist_url:
        return playlist_url.split("playlist/")[1].split("?")[0]
    elif ":playlist:" in playlist_url:
        return playlist_url.split(":playlist:")[1]
    return playlist_url


def get_tracks_from_spotify(playlist_id, sp):
    """Return list of (track_name, first_artist_name) for the playlist.

    Handles pagination by following `next` until exhausted.
    """
    results = sp.playlist_tracks(playlist_id)
    tracks = []
    while results:
        for item in results["items"]:
            track = item["track"]
            name = track["name"]
            artist = track["artists"][0]["name"]
            tracks.append((name, artist))
        if results["next"]:
            results = sp.next(results)
        else:
            results = None
    return tracks


def load_downloaded_set(history_path):
    """Load previously downloaded (track, artist) pairs as a normalized set."""
    downloaded = set()
    if os.path.exists(history_path):
        with open(history_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    downloaded.add((row[0].strip().lower(), row[1].strip().lower()))
    return downloaded


def append_to_history(history_path, track, artist):
    """Append one (track, artist) line to the playlist history CSV."""
    with open(history_path, "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([track, artist])


# --- Auth helpers -----------------------------------------------------------
if "HAS_PKCE" in globals() and HAS_PKCE:
    # Some spotipy versions access an internal `_session` attribute in the
    # auth base class destructor, which PKCE may not define. This wrapper
    # ensures the attribute exists and avoids noisy destructor errors.
    class SafeSpotifyPKCE(SpotifyPKCE):  # type: ignore
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            if not hasattr(self, "_session"):
                self._session = None  # type: ignore[attr-defined]

        def __del__(self):  # noqa: D401
            # Suppress destructor errors stemming from missing internals.
            try:
                # Call parent __del__ only if safe
                if hasattr(self, "_session"):
                    super_del = getattr(super(), "__del__", None)
                    if callable(super_del):
                        super_del()
            except Exception:
                pass


def main():
    """CLI entrypoint: orchestrates sync logic and prints progress."""
    # ---- Argument parsing ----
    parser = argparse.ArgumentParser(
        description="Sync Spotify playlist and download new songs."
    )
    parser.add_argument("playlist_url", help="Spotify playlist link or URI")
    parser.add_argument("download_folder", help="Folder to download songs into")
    # No client-id argument; rely exclusively on .spotify_app.json to avoid exposing choices to end user.
    # Provide optional --client-secret only for legacy fallback.
    parser.add_argument(
        "--client-secret",
        help="Optional: Client Secret for OAuth fallback if PKCE unavailable",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List new songs not in history without downloading or recording",
    )
    args = parser.parse_args()

    # ---- Configure Spotify authentication (prefer user login) ----
    # Load client_id / redirect_uri from .spotify_app.json
    config_path = Path(__file__).parent / ".spotify_app.json"
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            app_cfg = json.load(f)
    except FileNotFoundError:
        example = '{ "client_id": "YOUR_ID", "redirect_uri": "http://127.0.0.1:8888/callback" }'
        print(f"ERROR: {config_path.name} not found. Create it with JSON: {example}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to read {config_path.name}: {e}")
        sys.exit(1)

    client_id = app_cfg.get("client_id")
    redirect_uri = app_cfg.get("redirect_uri", "http://127.0.0.1:8888/callback")
    client_secret = args.client_secret  # optional

    if not client_id:
        print(f"ERROR: 'client_id' missing in {config_path.name}. Add it and re-run.")
        sys.exit(1)
    if not redirect_uri:
        print(
            f"ERROR: 'redirect_uri' missing in {config_path.name}. Add it and re-run."
        )
        sys.exit(1)

    # Use a custom cache file instead of default .cache
    cache_path = Path(__file__).parent / ".cache_spotify"
    cache_handler = CacheFileHandler(cache_path=str(cache_path))

    # Scopes for reading public/private and collaborative playlists
    scopes = "playlist-read-private playlist-read-collaborative"

    sp: Spotify
    if HAS_PKCE and not client_secret:
        # User login via PKCE (no client secret). Opens a browser on first run.
        try:
            am = SafeSpotifyPKCE(
                client_id=client_id,
                redirect_uri=redirect_uri,
                scope=scopes,
                cache_handler=cache_handler,
                open_browser=True,
                show_dialog=True,
            )
        except TypeError:
            # Older Spotipy may not support these kwargs on PKCE
            am = SafeSpotifyPKCE(
                client_id=client_id,
                redirect_uri=redirect_uri,
                scope=scopes,
                cache_handler=cache_handler,
            )
        # Workaround for some spotipy versions: ensure _session attribute exists to avoid
        # AttributeError in SpotifyAuthBase.__del__ when cleaning up.
        if not hasattr(am, "_session"):
            am._session = None  # type: ignore[attr-defined]
        sp = Spotify(auth_manager=am)
    else:
        # If PKCE isn't available (older spotipy) but a client secret was provided, use OAuth.
        if not HAS_PKCE and client_secret:
            sp = Spotify(
                auth_manager=SpotifyOAuth(
                    client_id=client_id,
                    client_secret=client_secret,
                    redirect_uri=redirect_uri,
                    scope=scopes,
                    cache_handler=cache_handler,
                    open_browser=True,
                    show_dialog=True,
                )
            )
        else:
            # No PKCE available and no secret provided -> cannot proceed without user login capability.
            print(
                "ERROR: Your spotipy version lacks PKCE and no --client-secret was provided for OAuth. "
                "Upgrade 'spotipy' to a recent version (PKCE) or re-run with --client-secret."
            )
            sys.exit(1)

    # ---- Fetch playlist tracks ----
    playlist_id = get_playlist_id(args.playlist_url)
    tracks = get_tracks_from_spotify(playlist_id, sp)

    # Setup tracking
    # ---- Load / prepare history ----
    os.makedirs(TRACKING_DIR, exist_ok=True)
    history_path = os.path.join(TRACKING_DIR, f"{playlist_id}.csv")
    downloaded = load_downloaded_set(history_path)

    print(f"Found {len(tracks)} tracks in playlist.", flush=True)

    # Determine new tracks not yet in history
    new_tracks = []
    for track, artist in tracks:
        # Normalize to lowercase for consistent comparison
        key = (track.strip().lower(), artist.strip().lower())
        if key not in downloaded:
            new_tracks.append((track, artist))

    if args.dry_run:
        print(f"New tracks not in history ({len(new_tracks)}):", flush=True)
        for track, artist in new_tracks:
            print(f"  - {artist} - {track}", flush=True)
        # Do not download or write history in dry run
        return

    # ---- Download loop ----
    new_downloads = 0
    for track, artist in new_tracks:
        print(f"Downloading: {artist} - {track}", flush=True)
        success = download_song(track, artist, args.download_folder)
        if success:
            append_to_history(history_path, track, artist)
            print(f"[OK] Downloaded and recorded: {artist} - {track}", flush=True)
            new_downloads += 1
        else:
            print(f"[FAIL] Failed to download: {artist} - {track}", flush=True)
    print(f"Sync complete. {new_downloads} new tracks downloaded.", flush=True)


if __name__ == "__main__":
    main()
