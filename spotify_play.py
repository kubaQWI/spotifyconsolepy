import time
import random
import json
import os
import config
import spotify_commands as scmd

print("Initialization...")

config_data = config.return_config()
print(config_data)

# Get Spotify instance and device name from module
sp = scmd.get_spotify()
device_name = scmd.get_device_name()

if sp is None or device_name is None:
    print("! Spotify initialization failed. Check your config.")
    exit()

try:
    user = sp.current_user()
    print("Authentication completed")
    print(f"Logged user: {user['display_name']}")
except Exception as e:
    print(f"! Failed to get current user: {e}")
    exit()

playlist_uri = 'spotify:playlist:02hdeJ4xNLqi0ek760Znxh'
cache_file = '/home/pi/cache_tracks.json' if os.name != 'nt' else './cache_tracks.json'
max_cache_tracks = 180

def set_volume(volume_percent=0):
    try:
        sp.volume(volume_percent, device_id=scmd.get_device_name())
        print(f"Volume set to {volume_percent}%")
    except Exception as e:
        print(f"Error setting volume: {e}")

def load_played_tracks():
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            return set(json.load(f))
    return set()

def save_played_track(track_uri):
    played = load_played_tracks()
    played.add(track_uri)
    if len(played) >= max_cache_tracks:
        print(f"Cache cleared: {max_cache_tracks}")
        played = set()
    with open(cache_file, 'w') as f:
        json.dump(list(played), f)

def get_target_device():
    devices = sp.devices().get('devices', [])
    for d in devices:
        if d['name'].lower() == device_name.lower():
            return d
    return None

def fetch_playlist_tracks():
    playlist = sp.playlist_tracks(playlist_uri)
    tracks = playlist['items']
    while playlist['next']:
        playlist = sp.next(playlist)
        tracks.extend(playlist['items'])
    return tracks

def get_unplayed_tracks(tracks):
    played_tracks = load_played_tracks()
    return [t for t in tracks if t['track']['uri'] not in played_tracks]

def start_playback(device_id):
    tracks = fetch_playlist_tracks()
    unplayed_tracks = get_unplayed_tracks(tracks)
    if not unplayed_tracks:
        with open(cache_file, 'w') as f:
            json.dump([], f)
        unplayed_tracks = tracks
    random_track = random.choice(unplayed_tracks)
    track_uri = random_track['track']['uri']
    print(f"Starting playback from random track: {random_track['track']['name']}")
    sp.start_playback(
        device_id=device_id,
        context_uri=playlist_uri,
        offset={'uri': track_uri}
    )
    save_played_track(track_uri)
    time.sleep(2)

def add_next_to_queue(device_id):
    tracks = fetch_playlist_tracks()
    unplayed_tracks = get_unplayed_tracks(tracks)
    if not unplayed_tracks:
        with open(cache_file, 'w') as f:
            json.dump([], f)
        unplayed_tracks = tracks
    random_track = random.choice(unplayed_tracks)
    track_uri = random_track['track']['uri']
    sp.add_to_queue(track_uri, device_id=device_id)
    save_played_track(track_uri)
    print(f"Added to queue: {random_track['track']['name']}")

def fetch_playlist_tracks():
    playlist = sp.playlist_tracks(playlist_uri)
    tracks = playlist['items']
    while playlist['next']:
        playlist = sp.next(playlist)
        tracks.extend(playlist['items'])
    return tracks

def get_unplayed_tracks(tracks):
    played_tracks = load_played_tracks()
    return [t for t in tracks if t['track']['uri'] not in played_tracks]

def start_playback(device_id):
    tracks = fetch_playlist_tracks()
    unplayed_tracks = get_unplayed_tracks(tracks)
    if not unplayed_tracks:
        with open(cache_file, 'w') as f:
            json.dump([], f)
        unplayed_tracks = tracks
    random_track = random.choice(unplayed_tracks)
    track_uri = random_track['track']['uri']
    print(f"Starting playback from random track: {random_track['track']['name']}")
    sp.start_playback(
        device_id=device_id,
        context_uri=playlist_uri,
        offset={'uri': track_uri}
    )
    save_played_track(track_uri)
    time.sleep(2)

def add_next_to_queue(device_id):
    tracks = fetch_playlist_tracks()
    unplayed_tracks = get_unplayed_tracks(tracks)
    if not unplayed_tracks:
        with open(cache_file, 'w') as f:
            json.dump([], f)
        unplayed_tracks = tracks
    random_track = random.choice(unplayed_tracks)
    track_uri = random_track['track']['uri']
    sp.add_to_queue(track_uri, device_id=device_id)
    save_played_track(track_uri)
    print(f"Added to queue: {random_track['track']['name']}")

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
            if remaining <= 5:
                add_next_to_queue(device_id)
        except Exception as e:
            print(f"Playback error: {e}")
        time.sleep(2)

target_device = get_target_device()
if not target_device:
    print(f"Device not found: {device_name}")
    exit()

set_volume(0)
start_playback(target_device['id'])
monitor_playback(target_device['id'])

"""
"   Made with <3 by kubaQWI and cement for ZSTiO Radiowęzeł Automated Music System using Spotify API
"   https://github.com/kubaQWI/spotifyconsolepy
"""
