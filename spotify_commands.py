import spotipy
from spotipy.oauth2 import SpotifyOAuth
import asyncio
import time
import json

import config

"""
"   config_data[0] - config_id
"   config_data[1] - client_secret
"   config_data[2] - cache_path
"   config_data[3] - device_name
"""

config_data = config.return_config()

def init():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=config_data[0],
    client_secret=config_data[1],
    redirect_uri='http://127.0.0.1:8000/callback',
    scope='user-modify-playback-state user-read-currently-playing user-read-playback-state playlist-read-private playlist-modify-private playlist-modify-public',
    open_browser=False,
    cache_path=config_data[2]
    ))
    
    return sp

if not config_data:
    print("! Check if config data is correct. All spotify related functions are disabled.")
    config_data = [None, None, None, None]
else:
    global allowed
    allowed = True

    for index, key in enumerate(config_data): # check if variables are empty, if true set it as None.
        if not key or " " in key:
            config_data[index] = None
            allowed = False
        else:
            pass
    
    if not allowed:
        print("! Check if config data is correct. All spotify related functions are disabled.")
        config_data = [None, None, None, None]
    else:
        sp = init()

device_name = config_data[3]

def int_to_time(value: int | float, is_ms: bool = True) -> str:
    if is_ms:
        value = value // 1000
    else:
        pass

    if value >= 3600: # value in seconds*
        timestamp = time.strftime("%H:%M:%S", time.gmtime(value))
    elif value >= 86400: # how would you even get that song on spotify???
        timestamp = time.strftime("%d:%H:%M:%S", time.gmtime(value))
    else:
        timestamp = time.strftime("%M:%S", time.gmtime(value))

    return timestamp

async def api_get_device_data(device: str | None = config_data[3], print_all_devices: bool = False) -> dict | None:

    api_get_devices = (sp.devices() or {}).get("devices", {})

    if device is None:
        print(f"! Your config file is damaged. Use 'change-ini' to fix it.")
        return {}

    if not api_get_devices:
        print("! No active devices")
        return {}

    if print_all_devices:
        for index, key in enumerate(api_get_devices):
            print(f"{index + 1}: Name: {key['name']}, ID: {key['id']}, Is active: {key['is_active']}, Is restricted: {key['is_restricted']}, Type: {key['type']}")
        return

    data = {}

    """
    "   returns:
    "       'id'                    - str
    "       'is_active;             - bool
    "       'is_private_session'    - bool
    "       'is_restricted'         - bool
    "       'name'                  - str
    "       'supports_volume'       - bool
    "       'type'                  - str
    "       'volume_percent'        - int
    "
    "   if None found:
    "       returns empty dict
    """

    try:
        for _, key in enumerate(api_get_devices): # searching
            for l, r in key.items():
                if 'name' in l and device.lower() in r.lower():
                    data.update(key)
                elif 'name' in l and "Web Player" in r:
                    print("! Please do not use open.spotify.com as a player.")

    except Exception as e:
        print(f"! There was a problem: {e}")
        
    return data if not None else {}

async def set_volume(volume: int, device_data: dict | None = None) -> None:
    if type(device_data) == dict:
            print("! Custom id is not yet supported.")
            device_id = None
    
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
    try:
        if type(device_data) == dict:
            print("! Custom data is not yet supported.")
            device_id = None

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

    except Exception as e:
        print(f"! An error occurred during fade-out: {e}")

async def fade_in(device_data: dict | None = None, fade_duration: int | float = 5):
    try:
        if type(device_data) == dict:
            print("! Custom data is not yet supported.")
            device_id = None

        if device_data is None:
            device_data = await api_get_device_data()
        
        if not device_data:
            print("! Error: no control devices.")
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

    except Exception as e:
        print(f"! An error occurred during fade-in: {e}")

async def start_playback(device_data: dict | None = None, context_uri: str | None = None, uris: str | list[str] | None = None, offset: None = None, position_ms: None = None) -> None:
    # https://developer.spotify.com/documentation/web-api/reference/start-a-users-playback

    data = []

    if isinstance(device_data, dict):
        print("! Custom id is not yet supported.")
        device_data = None

    if device_data is None:
        device_data = await api_get_device_data()

    if not device_data:
        return

    if isinstance(uris, str):
        uris = uris.split(" ")

    if isinstance(uris, list):
        data = uris[:]
        if data[0] == "playuri":
            data.remove(0) # type: ignore
        try:
            for i, u in enumerate(uris):
                if "spotify:track:" not in u:
                        print("! Wrong uri.")
                        return

        except Exception as e:
            print(f"There was an error {e}")
            return


    device_id = device_data.get("id")

    sp.start_playback(device_id=device_id, context_uri=context_uri, uris=data if data else None, offset=offset, position_ms=position_ms)

async def pause_playback(device_data: dict | None = None) -> None:
    # https://developer.spotify.com/documentation/web-api/reference/pause-a-users-playback

    if isinstance(device_data, dict):
        print("! Custom id is not yet supported.")
        device_data = None

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

    if isinstance(device_data, dict):
        print("! Custom id is not yet supported.")
        device_data = None

    if device_data is None:
        device_data = await api_get_device_data()

    if not device_data:
        return
    
    device_id = device_data.get("id")

    sp.next_track(device_id)

async def previous_track(device_data: dict | None = None) -> None:

    if isinstance(device_data, dict):
        print("! Custom id is not yet supported.")
        device_data = None

    if device_data is None:
        device_data = await api_get_device_data()

    if not device_data:
        return
    
    device_id = device_data.get("id")

    sp.previous_track(device_id)

async def current_playback() -> None:

    current = sp.current_playback() # returns very large dict, every code bellow is formatting

    if not current:
        print("! Nothing playing.")
        return
    
    audio_track_type = current["currently_playing_type"] #type: ignore

    if audio_track_type != "track":
        print("! Podcasts are not yet supported by Spotify API.")
        return
    """
    with open("data.json", "w", encoding="utf-8") as f: # debug
        json.dump(current, f, indent=4)
    """
    if current and current["is_playing"]:
        name = current["item"]["name"]
        artists = current["item"]["artists"]

        data = []

        for nums in range(len(artists)):
            data.append(f'"{artists[nums]["name"]}"')
        
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

    else:
        print("! Nothing is playing.")
    
async def shuffle(mode: str | bool = "off", device_id: str | None = None) -> None:
    if device_id is None:
        device_data = await api_get_device_data()

        if not device_data:
            return
        
        device_id = device_data.get("id")

    if isinstance(mode, str):
        if mode.lower() == "true" or mode.lower() == "false":
            sp.shuffle(bool(mode))    
        
        if mode.lower() == "on":
            mode = True
            print(f"! Changed to {mode}")
        elif mode.lower() == "off":
            mode = False
            print(f"! Changed to {mode}")
        else:
            print("! Invalid argument")
            return

        sp.shuffle(mode)
    else:

        sp.shuffle(bool(mode))

async def repeat(mode: str = "off", device_id: str | None = None) -> None:
    if device_id is None:
        device_data = await api_get_device_data()

        if not device_data:
            return
        
        device_id = device_data.get("id")
    
    if isinstance(mode, str):
        if mode.lower() == "track":
            print(f"! Changed repeat mode to {mode}")
            sp.repeat(mode, device_id)
            return

        elif mode.lower() == "context":
            print(f"! Changed repeat mode to {mode}")
            sp.repeat(mode, device_id)
            return

        elif mode.lower() == "off":
            print(f"! Changed repeat mode to {mode}")
            sp.repeat(mode, device_id)

        else:
            print("! Invalid option, (off, context, track)")
            return
          
    return

async def queue(): # for now only reading queue, later i will add more fun functions :3
    sp_data = sp.queue()

    if not sp_data:
        print("! No data")
        return

    def remove_keys(obj, keys_to_remove): # spooky! (even i don't understand it dw)
        if isinstance(obj, dict):
            return {k: remove_keys(v, keys_to_remove) for k, v in obj.items() if k not in keys_to_remove}
        elif isinstance(obj, list):
            return [remove_keys(i, keys_to_remove) for i in obj]
        else:
            return obj

    data = remove_keys(sp_data, {"available_markets", 
                                "images", 
                                "currently_playing", 
                                "external_ids", 
                                "external_urls", 
                                "disc_number", 
                                "track_number", 
                                "total_tracks", 
                                "popularity",
                                "preview_url",
                                "href",
                                "release_date",
                                "release_date_precision"})
    
    with open('queue.json', 'w') as que:
        json.dump(data, que, indent=4)

    if not data:
        return

    if not isinstance(data, dict):
        return

    sp_queue = data.get("queue")

    if not isinstance(sp_queue, list):
        print(sp_queue)
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
        duration = ""

        if not isinstance(duration_ms, int):
            pass
        else:
            duration = int_to_time(duration_ms, True)

        artists_list = [f'"{a["name"]}"' for a in artists]
        artist_str = ", ".join(artists_list)

        album_str = f' from album "{album.get("name")}"' if album_type != "single" else ""

        print(f'{index} : "{title}" by {artist_str}{album_str}, explicit: {is_explicit}, duration: {"No data" if not duration else duration}\n')

async def add_to_queue(uri: str, device_id: str | None = None) -> None:
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

if __name__ == "__main__":
    print("This file is not meant to be executed. Use console.py")
    exit()


"""
"   Made with <3 by kubaQWI and cement for ZSTiO Radiowęzeł Automated Music System using Spotify API
"   https://github.com/kubaQWI/spotifyconsolepy
"""