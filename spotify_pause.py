import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import signal
import subprocess
import time

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id='4de4fac2c19b4553b53aafb15cea0d69',
    client_secret='cb4b9b7a91eb4f4789300defc0e50a1e',
    redirect_uri='http://127.0.0.1:8000/callback',
    scope='user-modify-playback-state user-read-playback-state',
    open_browser=False,
    cache_path='/home/pi/spotipy_cache/cache'
))

devices = sp.devices()['devices']
active_device = None
for device in devices:
    if device['is_active']:
        active_device = device
        break

if active_device:
    try:
        sp.pause_playback(device_id=active_device['id'])
        print("Music stopped")
    except Exception as e:
        print(f"Pauzing error: {e}")
else:
    print("No active device.")

try:
    result = subprocess.check_output(["pgrep", "-f", "spotify_play.py"]).decode().strip()
    for pid in result.splitlines():
        print(f"Killing process (PID: {pid})")
        os.kill(int(pid), signal.SIGTERM)
except subprocess.CalledProcessError:
    print("Process not found")


