#!/usr/bin/env python
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import asyncio
import sys

import config

async def ainput(prompt: str) -> str:
    return await asyncio.to_thread(input, f'{prompt}')

async def meow() -> str:
    while True:
        print("meow")
        await asyncio.sleep(10)

async def get_input(prompt: str) -> None:

    commands = {
        "help" : "Displays this message",
        "play": "Start/resume playback",
        "pause": "Pause playback",
        "next": "Skip to next track",
        "previous": "Skip to previous track",
        "current": "Show currently playing track",
        "volume": "[0-100] | Set volume to a given percentage",
        "shuffle": "[on/off] | Turn shuffle mode on or off",
        "repeat": "[off|track|context] | Set repeat mode",
        "devices": "List available devices",
        "transfer": "[device_name] | Transfer playback to another device",
        "search": "[query] | Search for a track",
        "playuri": "[spotify:track:URI] | Play a specific track by URI",
        "queue": "Show playback queue",
        "addqueue": "[spotify:track:URI] | Add track to queue",
        "change-ini": "Changes config.ini file",
        "exit": "Exit the program"
    }
    while True:
        line = await ainput(prompt) # Get input from user, and do some shit when user is not inputting

        args = line.strip().split()

        if not args:
            continue

        cmd = args[0]
        argstr = " ".join(args[1:])

        if cmd in commands:
            pass

        else:
            print(f"{cmd}")
            cmd = None
        
        try:
            
            match cmd:
                case "help":
                    for c, d in commands.items():
                        print(f"{c:25} - {d}")
                
                case "play":
                    sp.start_playback()

                case "pause":
                    sp.pause_playback()
                
                case "next":
                    sp.next_track()

                case "previous":
                    sp.previous_track()

                case "current":
                    current = sp.current_playback()

                    if current and current["is_playing"]:
                        name = current["item"]["name"]
                        artist = current["item"]["artists"][0]["name"]
                        print(f"Currently playing: {name} by {artist}")

                    else:
                        print("Nothing is playing.")

                case "volume":
                    if len(args) > 1:
                        volume = int(args[1])
                        await sp.volume(volume)
                    else:
                        raise IndexError
                    

                case "shuffle":
                    if len(args) > 1:
                        mode = args[1].lower() == "on"
                        await sp.shuffle(mode)
                    else:
                        raise IndexError

                case "repeat":
                    if len(args) > 1:
                        await sp.repeat(args[1].lower())
                    else:
                        raise IndexError

                case "devices":
                    if len(args) > 1:
                        devices = await sp.devices()["devices"]
                        for d in devices:
                            print(f"{d['name']} (ID: {d['id']}) - {'ACTIVE' if d['is_active'] else 'inactive'}")
                    else:
                        raise IndexError

                case "transfer":
                    if len(args) > 1:
                        name = " ".join(args[1:])
                        devices = await sp.devices()["devices"]
                        device = next((d for d in devices if d["name"].lower() == name.lower()), None)
                        if device:
                            await sp.transfer_playback(device["id"], force_play=False)
                            print(f"Transferred to {device['name']}")
                        else:
                            print("Device not found.")
                    else:
                        raise IndexError
                
                case "search":
                    if len(args) > 1:
                        results = await sp.search(argstr, type="track", limit=5) # must be awaited -- fetching data, could lag or sum idk
                        for i, item in enumerate(results["tracks"]["items"], 1):
                            print(f"{i}. {item['name']} by {item['artists'][0]['name']} - URI: {item['uri']}")
                    else:
                        raise IndexError

                case "playuri":
                    if len(args) > 1:
                        await sp.start_playback(uris=[args[1]])
                    else:
                        raise IndexError

                case "addqueue":
                    if len(args) > 1:
                        await sp.add_to_queue(args[1])
                        print("Added to queue.")
                    else:
                        raise IndexError

                case "queue":
                    print("Spotify Web API does not support retrieving the queue. Use your client.")
            
                case "change-ini":
                    print(config.return_config())
                    await config.change_input()

                case "exit":
                    print("Exiting...")
                    sys.exit(0)

                case None:
                    print(f"There is no command such as '{line}'. Type 'help' for more info.")

        except IndexError:
            for Left, Right in commands.items():
                if cmd in Left:
                    print(f"Usage: {Left} - {Right}")
        except Exception as e:
            print(f"Error executing command '{cmd}': {e}")

async def main():
    task_ = asyncio.create_task(get_input("? "))
    meow_ = asyncio.create_task(meow()) # < simulates traffic, delete this when spotify functions will be finished

    await task_
    await meow_
    
asyncio.run(main())



""" ignore this, if something will break i will uncomment this, ------ kubus :3


            if cmd == "help":
                for c, d in commands.items():
                    print(f"{c:25} - {d}")

            elif cmd == "play":
                sp.start_playback()

            elif cmd == "pause":
                sp.pause_playback()

            elif cmd == "next":
                sp.next_track()

            elif cmd == "previous":
                sp.previous_track()

            elif cmd == "current":
                current = sp.current_playback()

                if current and current["is_playing"]:
                    name = current["item"]["name"]
                    artist = current["item"]["artists"][0]["name"]
                    print(f"Currently playing: {name} by {artist}")

                else:
                    print("Nothing is playing.")

            elif cmd == "volume":
                if args[:1]:
                    volume = int(args[1])
                    sp.volume(volume)
                else:
                    raise IndexError

            elif cmd == "shuffle":
                if args[:1]:
                    mode = args[1].lower() == "on"
                    sp.shuffle(mode)
                else:
                    raise IndexError

            elif cmd == "repeat" and args[1:]:
                sp.repeat(args[1].lower())

            elif cmd == "devices":
                devices = sp.devices()["devices"]

                for d in devices:
                    print(f"{d['name']} (ID: {d['id']}) - {'ACTIVE' if d['is_active'] else 'inactive'}")

            elif cmd == "transfer":
                if args[:1]:
                    name = " ".join(args[1:])
                    devices = sp.devices()["devices"]
                    device = next((d for d in devices if d["name"].lower() == name.lower()), None)

                    if device:
                        sp.transfer_playback(device["id"], force_play=False)
                        print(f"Transferred to {device['name']}")

                    else:
                        print("Device not found.")
                else:
                    raise IndexError

            elif cmd == "search":
                if args[:1]:
                    results = sp.search(argstr, type="track", limit=5)

                    for i, item in enumerate(results["tracks"]["items"], 1):
                        print(f"{i}. {item['name']} by {item['artists'][0]['name']} - URI: {item['uri']}")

                else:
                    raise IndexError
                
            elif cmd == "playuri":
                if args[:1]:
                    sp.start_playback(uris=[args[1]])

                else:
                    raise IndexError
                
            elif cmd == "addqueue":
                if args[:1]:
                    sp.add_to_queue(args[1])
                    print("Added to queue.")

                else:
                    raise IndexError
        
            elif cmd == "queue": # kinda pointless??
                print("Spotify Web API does not support retrieving the queue. Use your client.")

            elif cmd == "exit":
                print("Exiting...")

                sys.exit(0)

            elif cmd == None:
                print(f"There is no command such as '{line}'. Type 'help' for more info.")

            """