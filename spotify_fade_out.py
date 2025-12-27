#!/usr/bin/env python
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import spotify_commands as scmd
import asyncio
import time

import config
# init
data = config.return_config()

if not data:
    print("ini file is broken")
    exit(1)

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
def fade_out(device_id=None, fade_duration=5):
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
            print("Error: failed to find device.")
            return

        if device_id is None:
            device_id = current_device['id']

        current_volume = current_device.get('volume_percent', None)

        if current_volume is None:
            print("Error: failed to get device volume.")
            return

        steps = max(1, int(current_volume / 5))
        step_delay = fade_duration / (steps if steps > 0 else 1)
        step_size = 5

        for vol in range(current_volume, -5, -step_size):
            sp.volume(volume_percent=vol, device_id=device_id)
#            print(vol)
            time.sleep(step_delay)
    except Exception as e:
        print(f"An error occurred during fade-out: {e}")

if __name__ == "__main__":
    fade_out()

"""
async def main() -> None:
    fade_out_ = asyncio.create_task(scmd.fade_out())

    await fade_out_

if __name__ == "__main__":
    asyncio.run(main())
"""
