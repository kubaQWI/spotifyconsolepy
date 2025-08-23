import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id='4de4fac2c19b4553b53aafb15cea0d69',
    client_secret='cb4b9b7a91eb4f4789300defc0e50a1e',
    redirect_uri='http://127.0.0.1:8000/callback',
    scope='user-modify-playback-state user-read-playback-state',
    open_browser=False,
    cache_path='/home/pi/spotipy_cache/cache'
))

user = sp.current_user()

device_name = 'rpi3'

def fade_out(device_id, fade_duration=5):
    try:
        devices_response = sp.devices()
        
        if 'devices' not in devices_response:
            print("Error: no control devices.")
            return
        
        current_volume = devices_response['devices'][0].get('volume_percent', None)
        
        if current_volume is None:
            print("Error: failed to get device volume.")
            return

        for vol in range(current_volume, -5, -5): 
            sp.volume(vol, device_id=device_id)
            print(vol)
            time.sleep(fade_duration / 15)  
    except Exception as e:
        print(f"An error occurred during fade-out: {e}")

try:
    devices = sp.devices()['devices']
    target_device = None
    for d in devices:
        if d['name'].lower() == device_name.lower():
            target_device = d
            break

    if target_device:
        fade_out(target_device['id'], fade_duration=5)
    else:
        print(f"Device not found: '{device_name}'")
except Exception as e:
    print(f"An error occurred while obtaining devices: {e}")
