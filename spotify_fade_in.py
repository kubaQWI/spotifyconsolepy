#!/usr/bin/env python
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import asyncio
import spotify_commands as scmd
import time

import config
# init
data = config.return_config()

if not data:
    print("ini file is broken")
    exit(1)

"""
data[0] - config_id
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

def fade_in(device_id: str | None = None, fade_duration: int = 5) -> None:
    try:
        devices_response = sp.devices()

        if 'devices' not in devices_response:
            print("Error: no control devices.")
            return

        current_device = None
        for dev in devices_response['devices']:
            if device_name == dev['name']:
                current_device = dev
                break

        if current_device is None:
            print("Failed to find device.")
            return

        if device_id is None:
            device_id = current_device['id']

        current_volume = current_device.get('volume_percent', 0)
        if current_volume is None:
            print("Failed to get device volume.")
            return

        for volume in range(current_volume, 101, 5):
            sp.volume(volume_percent=volume, device_id=device_id)
#            print(f"Vol: {volume}")
            time.sleep(fade_duration / 20)

    except Exception as e:
        print(f"Something went wrong: {e}")

if __name__ == "__main__":
    fade_in()

"""
async def main() -> None:
    fade_in_ = asyncio.create_task(scmd.fade_in())

    await fade_in_

if __name__ == "__main__":
    asyncio.run(main())
"""
