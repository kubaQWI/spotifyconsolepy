#!/usr/bin/env python
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import asyncio
import spotify_commands as scmd

import config
"""
# init
data = config.return_config()

if not data:
    print("ini file is broken")
    exit(1)
"""

"""
data[0] - config_id
data[1] - client_secret
data[2] - cache_path
data[3] - device_name
"""


""" << temp solution, i may change this
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

        current_volume = devices_response['devices'][0].get('volume_percent', None)

        if current_volume == None:
            print("Failed to get device volume.")
            return

        print(f"Current volume: {current_volume}")

        for volume in range(current_volume, 96, int(fade_duration)):
            sp.volume(volume, device_id)
            print(f"Vol: {volume}")
            time.sleep(fade_duration / 10)

    except Exception as e:
        print(f"Something went wrong: {e}")
"""

async def main() -> None:
    fade_in_ = asyncio.create_task(scmd.fade_in())

    await fade_in_

if __name__ == "__main__":
    asyncio.run(main())


"""
"   Made with <3 by kubaQWI and cement for ZSTiO Radiowęzeł Automated Music System using Spotify API
"   https://github.com/kubaQWI/spotifyconsolepy
"""