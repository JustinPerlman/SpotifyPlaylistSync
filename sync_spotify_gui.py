#!/usr/bin/env python3
"""
sync_spotify_gui.py
-------------------
Tkinter-based GUI wrapper around syncSpotify.py.

Features:
- Accepts a Spotify playlist URL/URI and a destination folder
- Optional Dry Run mode that lists new tracks without downloading
- Streams syncSpotify.py stdout live into the GUI log (per-song status)
"""
import os
import sys
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
SYNC_SCRIPT = SCRIPT_DIR / "syncSpotifyLogon.py"


class SyncSpotifyGUI:
    """Main GUI class encapsulating the layout and subprocess orchestration."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Spotify Sync Downloader")
        self.root.geometry("900x600")
        self.proc = None

        main = ttk.Frame(root, padding=12)
        main.grid(row=0, column=0, sticky="nsew")
        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        # Playlist URL
        ttk.Label(main, text="Spotify Playlist URL/URI:").grid(
            row=0, column=0, sticky="w"
        )
        self.playlist_var = tk.StringVar()
        ttk.Entry(main, textvariable=self.playlist_var, width=70).grid(
            row=1, column=0, columnspan=3, sticky="ew", pady=(2, 8)
        )

        # Download folder
        ttk.Label(main, text="Download Folder:").grid(row=2, column=0, sticky="w")
        self.folder_var = tk.StringVar(value=str(SCRIPT_DIR / "downloads"))
        ttk.Entry(main, textvariable=self.folder_var, width=55).grid(
            row=3, column=0, sticky="ew", pady=(2, 8)
        )
        ttk.Button(main, text="Browse", command=self._browse_folder).grid(
            row=3, column=1, padx=(6, 0)
        )

        # Options
        self.dry_run_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            main, text="Dry run (list new only)", variable=self.dry_run_var
        ).grid(row=4, column=0, sticky="w", pady=(0, 10))

        # Buttons
        btns = ttk.Frame(main)
        btns.grid(row=5, column=0, columnspan=3, pady=(0, 10))
        self.run_btn = ttk.Button(btns, text="Run", command=self._on_run)
        self.run_btn.pack(side=tk.LEFT, padx=5)
        self.stop_btn = ttk.Button(
            btns, text="Stop", command=self._on_stop, state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        # Log
        ttk.Label(main, text="Log:").grid(row=6, column=0, sticky="w")
        self.log = scrolledtext.ScrolledText(
            main, width=100, height=24, state=tk.DISABLED
        )
        self.log.grid(row=7, column=0, columnspan=3, sticky="nsew")

        for i in (7,):
            main.rowconfigure(i, weight=1)
        main.columnconfigure(0, weight=1)

    def _browse_folder(self):
        """Open a folder picker and update the download folder field."""
        folder = filedialog.askdirectory(title="Select Download Folder")
        if folder:
            self.folder_var.set(folder)

    def _append_log(self, text: str):
        """Append text to the scrolled log widget and keep it scrolled to end."""
        self.log.config(state=tk.NORMAL)
        self.log.insert(tk.END, text)
        self.log.see(tk.END)
        self.log.config(state=tk.DISABLED)

    def _on_run(self):
        """Validate inputs, spawn syncSpotify.py, and stream its output."""
        playlist = self.playlist_var.get().strip()
        folder = self.folder_var.get().strip()
        dry = self.dry_run_var.get()

        if not playlist:
            messagebox.showerror(
                "Missing input", "Please enter a Spotify playlist link or URI."
            )
            return
        if not SYNC_SCRIPT.exists():
            messagebox.showerror(
                "Missing script", f"syncSpotify.py not found at {SYNC_SCRIPT}"
            )
            return
        if not folder:
            folder = str(SCRIPT_DIR / "downloads")
        os.makedirs(folder, exist_ok=True)

        # Clear log
        self.log.config(state=tk.NORMAL)
        self.log.delete(1.0, tk.END)
        self.log.config(state=tk.DISABLED)

        # Disable run during execution
        self.run_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)

        # Build command
        # Use -u to force unbuffered stdout from Python child process
        cmd = [sys.executable, "-u", str(SYNC_SCRIPT), playlist, folder]
        if dry:
            cmd.append("--dry-run")

        def worker():
            """Background thread: run the subprocess and stream stdout to the GUI."""
            try:
                self._append_log(f"Running: {' '.join(cmd)}\n\n")
                # Ensure subprocess uses UTF-8 to avoid encoding issues
                env = os.environ.copy()
                env.setdefault("PYTHONIOENCODING", "utf-8")
                env.setdefault("PYTHONUNBUFFERED", "1")
                self.proc = subprocess.Popen(
                    cmd,
                    cwd=str(SCRIPT_DIR),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    env=env,
                    text=True,
                    bufsize=1,
                )
                # Stream output line by line
                assert self.proc.stdout is not None
                for line in self.proc.stdout:
                    self._append_log(line)
                rc = self.proc.wait()
                self._append_log(f"\nProcess finished with exit code {rc}.\n")
            except Exception as e:
                self._append_log(f"\nERROR: {e}\n")
            finally:
                self.proc = None
                self.run_btn.config(state=tk.NORMAL)
                self.stop_btn.config(state=tk.DISABLED)

        threading.Thread(target=worker, daemon=True).start()

    def _on_stop(self):
        """Attempt to gracefully terminate the running sync process."""
        if self.proc and self.proc.poll() is None:
            try:
                self.proc.terminate()
                self._append_log("\nTerminating process...\n")
            except Exception:
                pass


def main():
    """Launch the Tkinter app."""
    root = tk.Tk()
    app = SyncSpotifyGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
