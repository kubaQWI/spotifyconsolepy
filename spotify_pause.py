#!/usr/bin/env python
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import signal
import subprocess
import time

import config

# init
data = config.return_config()

"""
"   data[0] - config_id
"   data[1] - client_secret
"   data[2] - cache_path
"   data[3] - device_name
"""


sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=data[0],
    client_secret=data[1],
    redirect_uri='http://127.0.0.1:8000/callback',
    scope='user-modify-playback-state user-read-playback-state',
    open_browser=False,
    cache_path=data[2]
))

user = sp.current_user()
device_name = data[3]

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


"""
"   Made with <3 by kubaQWI and cement for ZSTiO Radiowęzeł Automated Music System using Spotify API
"   https://github.com/kubaQWI/spotifyconsolepy
"""