import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import random

print("Initialization...")

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id='4de4fac2c19b4553b53aafb15cea0d69',
    client_secret='cb4b9b7a91eb4f4789300defc0e50a1e',
    redirect_uri='http://127.0.0.1:8000/callback',
    scope='user-read-private playlist-read-private user-modify-playback-state user-read-playback-state streaming',
    open_browser=False,
    cache_path='/home/pi/spotipy_cache/cache'
))

print("Authentication completed")

user = sp.current_user()
print(f"Logged user: {user['display_name']}")

playlist_uri = 'spotify:playlist:02hdeJ4xNLqi0ek760Znxh'
device_name = 'rpi3'

def set_volume(device_id, volume_percent=0):
    try:
        sp.volume(volume_percent, device_id=device_id)
        print(f"Volume set to {volume_percent}%")
    except Exception as e:
        print(f"Error setting volume: {e}")

def activate_device(device_id):
    print("Activating device...")
    silence_uri = 'spotify:track:0EZMXJMWf0tLKRWwCiA6Sx'
    try:
        sp.start_playback(device_id=device_id, uris=[silence_uri])
        time.sleep(1)
        sp.pause_playback(device_id=device_id)
    except Exception as e:
        print(f"Activating device failed: {e}")

def start_playlist(device_id):
    playlist = sp.playlist_tracks(playlist_uri)
    tracks = playlist['items']
    while playlist['next']:
        playlist = sp.next(playlist)
        tracks.extend(playlist['items'])

    random_track = random.choice(tracks)
    track_uri = random_track['track']['uri']
    print(f"Starting playlist from random track: {random_track['track']['name']}")

    sp.shuffle(True, device_id=device_id)
#    sp.repeat('context', device_id=device_id)

    sp.start_playback(
        device_id=device_id,
        context_uri=playlist_uri,
        offset={'uri': track_uri}
    )

def get_target_device():
    devices = sp.devices()['devices']
    for d in devices:
        if d['name'].lower() == device_name.lower():
            return d
    return None

def monitor_playback(device_id):
    last_track_uri = None
    while True:
        try:
            playback = sp.current_playback()
            if not playback or not playback['is_playing']:
                time.sleep(2)
                continue

            current_track = playback['item']
            if not current_track:
                time.sleep(2)
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
                sp.next_track(device_id=device_id)

        except Exception as e:
            print(f"Playback error: {e}")

        time.sleep(2)

target_device = get_target_device()
if not target_device:
    print(f"Device not found: {device_name}")
    exit()

activate_device(target_device['id'])
set_volume(target_device['id'])
start_playlist(target_device['id'])
monitor_playback(target_device['id'])
