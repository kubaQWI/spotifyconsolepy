import spotipy
from spotipy.oauth2 import SpotifyOAuth
import asyncio
import time
import json
from typing import Optional
import config
import os

_sp: Optional[spotipy.Spotify] = None
_device_name: Optional[str] = None

def init_oauth(conf: Optional[list[Optional[str]]] = None) -> Optional[spotipy.Spotify]:
    global _sp, _device_name

    if _sp is not None:
        return _sp

    if conf is None:
        conf = config.return_config()

    if not conf:
        print("! Check if config data is correct. All Spotify functions are disabled.")
        return None

    allowed = True
    for i, key in enumerate(conf):
        if not key or " " in key:
            conf[i] = None
            allowed = False

    if not allowed:
        print("! Invalid config data. Spotify functions are disabled.")
        return None

    _sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=conf[0],
        client_secret=conf[1],
        redirect_uri='http://127.0.0.1:8000/callback',
        scope='user-modify-playback-state user-read-currently-playing user-read-playback-state playlist-read-private playlist-modify-private playlist-modify-public',
        open_browser=False,
        cache_path=conf[2]
    ))

    _device_name = conf[3]

    return _sp

def get_spotify() -> Optional[spotipy.Spotify]:
    global _sp
    if _sp is None:
        return init_oauth()
    return _sp

def get_device_name() -> Optional[str]:
    global _device_name
    if _device_name is None:
        init_oauth()
    return _device_name

def int_to_time(value: int | float, is_ms: bool = True) -> str:
    if is_ms:
        value = value // 1000
    if value >= 3600:
        timestamp = time.strftime("%H:%M:%S", time.gmtime(value))
    elif value >= 86400:
        timestamp = time.strftime("%d:%H:%M:%S", time.gmtime(value))
    else:
        timestamp = time.strftime("%M:%S", time.gmtime(value))
    return timestamp

async def api_get_device_data(device: str | None = None, print_all_devices: bool = False) -> dict | None:
    sp = get_spotify()
    if sp is None:
        return {}
    
    if device is None:
        device = get_device_name()
        if device is None:
            print("! Your config file is damaged. Use 'change-ini' to fix it.")
            return {}

    api_get_devices = (sp.devices() or {}).get("devices", {})

    if not api_get_devices:
        print("! No active devices")
        return {}

    if print_all_devices:
        for index, key in enumerate(api_get_devices):
            print(f"{index + 1}: Name: {key['name']}, ID: {key['id']}, Is active: {key['is_active']}, Is restricted: {key['is_restricted']}, Type: {key['type']}")
        return

    data = {}
    try:
        for key in api_get_devices:
            if device.lower() in key.get("name", "").lower():
                data.update(key)
            elif "Web Player" in key.get("name", ""):
                print("! Please do not use open.spotify.com as a player.")
    except Exception as e:
        print(f"! There was a problem: {e}")

    return data

async def check_cache_permissions(cache_path: str | None = None) -> None:
    #if os.name == "nt": # the issue occurs only on linux systems
    #    return
    if cache_path is None:
        device_data = await api_get_device_data()

        if device_data is None:
            return

        cache_path = device_data.get("cache_path")

        print(cache_path)

async def set_volume(volume: int, device_data: dict | None = None) -> None:
    sp = get_spotify()
    if sp is None:
        return
    
    if device_data is None:
        device_data = await api_get_device_data()
    if not device_data:
        return

    device_id = device_data.get("id")
    try:
        sp.volume(volume, device_id)
    except Exception as e:
        print(f"! There was an error: {e}")

async def fade_out(device_data: dict | None = None, fade_duration: int | float = 5):
    sp = get_spotify()
    if sp is None:
        return

    if device_data is None:
        device_data = await api_get_device_data()
    if not device_data:
        return

    current_volume = device_data.get("volume_percent")
    device_id = device_data.get("id")
    if current_volume is None:
        print("! Error: failed to get device volume.")
        return

    for vol in range(current_volume, -5, -5):
        sp.volume(vol, device_id)
        print(vol)
        await asyncio.sleep(fade_duration / 15)

async def fade_in(device_data: dict | None = None, fade_duration: int | float = 5):
    sp = get_spotify()
    if sp is None:
        return

    if device_data is None:
        device_data = await api_get_device_data()
    if not device_data:
        return

    current_volume = device_data.get("volume_percent")
    device_id = device_data.get("id")
    if current_volume is None:
        print("! Error: failed to get device volume.")
        return

    for vol in range(current_volume, 101, int(fade_duration)):
        sp.volume(vol, device_id)
        print(vol)
        await asyncio.sleep(fade_duration / 15)

async def start_playback(device_data: dict | None = None, context_uri: str | None = None, uris: str | list[str] | None = None, offset: None = None, position_ms: None = None) -> None:
    sp = get_spotify()
    if sp is None:
        return

    if device_data is None:
        device_data = await api_get_device_data()
    if not device_data:
        return

    if isinstance(uris, str):
        uris = uris.split(" ")

    if isinstance(uris, list):
        data = uris[:]
        try:
            for u in uris:
                if "spotify:track:" not in u:
                    print("! Wrong uri.")
                    return
        except Exception as e:
            print(f"There was an error {e}")
            return
    else:
        data = None

    device_id = device_data.get("id")
    sp.start_playback(device_id=device_id, context_uri=context_uri, uris=data, offset=offset, position_ms=position_ms)

async def pause_playback(device_data: dict | None = None) -> None:
    sp = get_spotify()
    if sp is None:
        return

    if device_data is None:
        device_data = await api_get_device_data()
    if not device_data:
        return

    device_id = device_data.get("id")
    is_active = device_data.get("is_active")
    if is_active:
        sp.pause_playback(device_id)
    else:
        print("! Device is already paused.")

async def next_track(device_data: dict | None = None) -> None:
    sp = get_spotify()
    if sp is None:
        return

    if device_data is None:
        device_data = await api_get_device_data()
    if not device_data:
        return

    sp.next_track(device_data.get("id"))

async def previous_track(device_data: dict | None = None) -> None:
    sp = get_spotify()
    if sp is None:
        return

    if device_data is None:
        device_data = await api_get_device_data()
    if not device_data:
        return

    sp.previous_track(device_data.get("id"))

async def current_playback() -> None:
    sp = get_spotify()
    if sp is None:
        return

    current = sp.current_playback()
    if not current:
        print("! Nothing playing.")
        return

    audio_track_type = current.get("currently_playing_type")
    if audio_track_type != "track":
        print("! Podcasts are not yet supported by Spotify API.")
        return

    name = current["item"]["name"]
    artists = current["item"]["artists"]
    data = [f'"{a["name"]}"' for a in artists]
    album = current["item"]["album"]["name"]
    album_type = current["item"]["album"]["album_type"]
    isExplicit = current["item"]["explicit"]
    progress = current["progress_ms"]
    duration = current['item']['duration_ms']

    list_to_str = ', '.join(artist for artist in data)
    artist = list_to_str

    if album == name:
        album_type = "single"

    print(f'! Currently playing: "{name}" by {artist} {"from album " + album if album_type != "single" else ""}')
    print(f'! Album type: {album_type}')
    print(f'! Explicit: {"Yes" if isExplicit else "No"}')
    print(f'! Progress: {int_to_time(progress, True)} - {int_to_time(duration, True)}')

async def shuffle(mode: str | bool = "off", device_id: str | None = None) -> None:
    sp = get_spotify()
    if sp is None:
        return

    if device_id is None:
        device_data = await api_get_device_data()
        if not device_data:
            return
        device_id = device_data.get("id")

    if isinstance(mode, str):
        mode = mode.lower()
        if mode == "on" or mode == "true":
            mode = True
        elif mode == "off" or mode == "false":
            mode = False
        else:
            print("! Invalid argument")
            return

    sp.shuffle(bool(mode), device_id)

async def repeat(mode: str = "off", device_id: str | None = None) -> None:
    sp = get_spotify()
    if sp is None:
        return

    if device_id is None:
        device_data = await api_get_device_data()
        if not device_data:
            return
        device_id = device_data.get("id")

    if mode.lower() in ["track", "context", "off"]:
        sp.repeat(mode.lower(), device_id)
        print(f"! Changed repeat mode to {mode.lower()}")
    else:
        print("! Invalid option, (off, context, track)")

async def queue() -> None:
    sp = get_spotify()
    if sp is None:
        return

    sp_data = sp.queue()
    if not sp_data:
        print("! No data")
        return

    def remove_keys(obj, keys_to_remove):
        if isinstance(obj, dict):
            return {k: remove_keys(v, keys_to_remove) for k, v in obj.items() if k not in keys_to_remove}
        elif isinstance(obj, list):
            return [remove_keys(i, keys_to_remove) for i in obj]
        else:
            return obj

    data = remove_keys(sp_data, {
        "available_markets", "images", "currently_playing", "external_ids", "external_urls",
        "disc_number", "track_number", "total_tracks", "popularity", "preview_url",
        "href", "release_date", "release_date_precision"
    })

    with open('queue.json', 'w') as que:
        json.dump(data, que, indent=4)

    sp_queue = data.get("queue") if isinstance(data, dict) else None
    if not sp_queue:
        return

    for index, item in enumerate(sp_queue, start=1):
        if not isinstance(item, dict):
            continue
        artists = item.get("artists", [])
        album = item.get("album", {})
        title = item.get("name")
        is_explicit = item.get("explicit")
        album_type = item.get("album_type")
        duration_ms = item.get("duration_ms")
        duration = int_to_time(duration_ms, True) if isinstance(duration_ms, int) else "No data"
        artists_list = [f'"{a["name"]}"' for a in artists]
        artist_str = ", ".join(artists_list)
        album_str = f' from album "{album.get("name")}"' if album_type != "single" else ""
        print(f'{index} : "{title}" by {artist_str}{album_str}, explicit: {is_explicit}, duration: {duration}\n')

async def add_to_queue(uri: str, device_id: str | None = None) -> None:
    sp = get_spotify()
    if sp is None:
        return

    if device_id is None:
        device_data = await api_get_device_data()
        if not device_data:
            return
        device_id = device_data.get("id")

    if "spotify:track" not in uri:
        print("! Not a URI")
        return

    print("! Added URI to queue")
    sp.add_to_queue(uri, device_id)

async def transfer_playback(device: str | None = None) -> None:
    sp = get_spotify()
    if sp is None:
        return
    
    device_id = await api_get_device_data(device)
    if device_id:
        device_id = device_id['id']

    if not device_id:
        print(f"! Incorrect device: {device} | Use 'devices' command to list all devices.")
        return

    sp.transfer_playback(device_id)

if __name__ == "__main__":
    print("This file is not meant to be executed. Use console.py")
    exit()
    

"""
"   Made with <3 by kubaQWI and cement for ZSTiO Radiowęzeł Automated Music System using Spotify API
"   https://github.com/kubaQWI/spotifyconsolepy
"""