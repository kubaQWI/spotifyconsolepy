import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time

import config

# init
data = config.return_config()

"""
data[0] - client_id
data[1] - client_secret
data[2] - cache_path
data[3] - device_name

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


def fade_in(device_id, fade_duration: int = 5) -> None:
    try:
        devices_response = sp.devices()

        if 'devices' not in devices_response:
            print("Error: no control devices.")
            return

        current_volume = devices_response['devices'][0].get('volume_percent', None)

        if current_volume == None:
            print("Failed to get device volume.")

        print(f"Current volume: {current_volume}")

        for volume in range(current_volume, 96, int(fade_duration)):
            sp.volume(volume, device_id) # << assume that it works (i dont have premium xd) decomment this when you will test it out
            print(f"Vol: {volume}")
            time.sleep(fade_duration / 10)

    except Exception as e:
        print(f"Something went wrong: {e}")

try:
    devices = sp.devices()['devices']
    target_device = None
    for d in devices:
        if d['name'].lower() == device_name.lower():
            target_device = d
            break

    if target_device:
        fade_in(target_device['id'], fade_duration=5)
    else:
        print(f"Device not found: '{device_name}'")
except Exception as e:
    print(f"An error occurred while obtaining devices: {e}")
