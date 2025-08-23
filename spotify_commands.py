import spotipy
from spotipy.oauth2 import SpotifyOAuth
import asyncio

import config

# init
data = config.return_config()

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

async def set_volume(device_id, volume_percent=0):
    try:
        await sp.volume(volume_percent, device_id=device_id)
        print(f"Volume set to {volume_percent}%")
    except Exception as e:
        print(f"Error setting volume: {e}")

async def activate_device(device_id):
    print("Activating device...")
    silence_uri = 'spotify:track:0EZMXJMWf0tLKRWwCiA6Sx'
    try:
        await sp.start_playback(device_id=device_id, uris=[silence_uri])
        await asyncio.wait(1)
        await sp.pause_playback(device_id=device_id)
    except Exception as e:
        print(f"Activating device failed: {e}")

async def start_playlist(device_id):
    playlist = await sp.playlist_tracks(playlist_uri)
    tracks = playlist['items']
    while playlist['next']:
        playlist = await sp.next(playlist)
        tracks.extend(playlist['items'])

    random_track = random.choice(tracks)
    track_uri = random_track['track']['uri']
    print(f"Starting playlist from random track: {random_track['track']['name']}")

    await sp.shuffle(True, device_id=device_id)
#    sp.repeat('context', device_id=device_id)

    await sp.start_playback(
        device_id=device_id,
        context_uri=playlist_uri,
        offset={'uri': track_uri}
    )

async def get_target_device():
    devices = await sp.devices()['devices']
    for d in devices:
        if d['name'].lower() == device_name.lower():
            return d
    return None

async def monitor_playback(device_id):
    last_track_uri = None
    while True:
        try:
            playback = await sp.current_playback()
            if not playback or not playback['is_playing']:
                await asyncio.wait(2)
                continue

            current_track = playback['item']
            if not current_track:
                await asyncio.wait(2)
                continue

            uri = current_track['uri']
            name = current_track['name']

            if uri != last_track_uri:
                print(f"\nNow playing: {name}")
                last_track_uri = uri

            progress = playback['progress_ms'] / 1000
            total = current_track['duration_ms'] / 1000
            remaining = total - progress

            if remaining <= 1:
                print("Track ending, ensuring playback continues...")
                await sp.next_track(device_id=device_id)

        except Exception as e:
            print(f"Playback error: {e}")

        time.sleep(2)

async def fade_in(device_id, fade_duration: int = 5) -> None:
    try:
        devices_response = await sp.devices()

        if 'devices' not in devices_response:
            print("Error: no control devices.")
            return

        current_volume = devices_response['devices'][0].get('volume_percent', None)

        if current_volume == None:
            print("Failed to get device volume.")

        print(f"Current volume: {current_volume}")

        for volume in range(current_volume, 96, int(fade_duration)):
            await sp.volume(volume, device_id) # << assume that it works (i dont have premium xd) decomment this when you will test it out
            print(f"Vol: {volume}")
            time.sleep(fade_duration / 10)

    except Exception as e:
        print(f"Something went wrong: {e}")

async def fade_out(device_id, fade_duration=5):
    try:
        devices_response = await sp.devices()
        
        if 'devices' not in devices_response:
            print("Error: no control devices.")
            return
        
        current_volume = devices_response['devices'][0].get('volume_percent', None)
        
        if current_volume is None:
            print("Error: failed to get device volume.")
            return

        for vol in range(current_volume, -5, -5): 
            await sp.volume(vol, device_id=device_id)
            print(vol)
            time.sleep(fade_duration / 15)  
    except Exception as e:
        print(f"An error occurred during fade-out: {e}")

async def pause(device_id: str|int) -> None:
    await sp.pause_playback(device_id)
    print("Paused.")


