#!/usr/bin/env python
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import asyncio

import config
import spotify_commands as scmd

async def ainput(prompt: str) -> str:
    return await asyncio.to_thread(input, f'{prompt}')

async def get_input(prompt: str = "? ") -> None:

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
        "fade-in": "Initializes fade in action",
        "fade-out": "Initializes fade out action",
        "change-ini": "Changes config.ini file",
        "clear": "Clears history of a terminal",
        "exit": "Exit the program"
    }

    while True:
        
        line = await ainput(prompt)

        args = line.strip().split()

        if not args:
            continue

        cmd = args[0]
        #argstr = " ".join(args[1:]) < don't know where is used xd, gotta leave that...

        if cmd in commands:
            pass

        else:
            cmd = None
        
        """
        "   I have to set every case to await in case of some action to not hold traffic
        "   This portion of code is such spaghetti ikr?
        "   Plz don't judge on how I do things
        "   I'm looking at you wojtek.
        """

        try:
            
            match cmd:
                case "help":
                    for c, d in commands.items():
                        print(f"{c:25} - {d}")
                
                case "play":
                    await scmd.start_playback()

                case "pause":
                    await scmd.pause_playback()
                
                case "next":
                    await scmd.next_track()

                case "previous":
                    await scmd.previous_track()

                case "current":
                    await scmd.current_playback()
                    
                case "volume":
                    if len(args) > 1:
                        volume = int(args[1])
                        await scmd.set_volume(volume=volume)
                    else:
                        raise IndexError
                    
                case "shuffle":
                    if len(args) > 1 and len(args) < 3:
                        mode = args[1]
                        await scmd.shuffle(mode.lower())
                    else:
                        raise IndexError

                case "repeat": # TODO
                    if len(args) > 1 and len(args) < 3:
                        await scmd.repeat(args[1].lower())
                    else:
                        raise IndexError
                        
                case "devices":
                    if len(args) == 1:
                        devices = (await scmd.api_get_device_data(print_all_devices=True))
                    else:
                        raise IndexError

                case "transfer": # TODO
                    """
                    if len(args) > 1 and len(args) < 3:
                        name = " ".join(args[1:])
                        devices = await scmd.api_get_device_data()
                        device = next((d for d in devices if d["name"].lower() == name.lower()), None)
                        if device:
                            await sp.transfer_playback(device["id"], force_play=False)
                            print(f"Transferred to {device['name']}")
                        else:
                            print("Device not found.")
                    else:
                        raise IndexError
                    """
                
                case "search": # TODO
                    """
                    if len(args) > 1:
                        results = await sp.search(argstr, type="track", limit=5)
                        for i, item in enumerate(results["tracks"]["items"], 1):
                            print(f"{i}. {item['name']} by {item['artists'][0]['name']} - URI: {item['uri']}")
                    else:
                        raise IndexError
                    """

                case "playuri":
                    if len(args) > 1:
                        await scmd.start_playback(uris=args)
                    else:
                        raise IndexError
                    
                case "queue":
                    #print("Spotify Web API does not support retrieving the queue. Use your client.")
                    
                    

                case "addqueue": # TODO
                    """
                    if len(args) > 1 and len(args) < 3:
                        await scmd.add_to_queue(args[1])
                        print("Added to queue.")
                    else:
                        raise IndexError
                    """
                
                case "fade-in":
                    await scmd.fade_in()
            
                case "fade-out":
                    await scmd.fade_out()
                
                case "change-ini":
                    await config.change_input()

                case "clear":
                    print("\033c")

                case "exit":
                    tasks = asyncio.all_tasks()
                    for task in tasks:
                        task.cancel()

                    print("Exiting...")
                    return

                case None:
                    print(f"There is no command such as '{line}'. Type 'help' for more info.")

        except IndexError:
            for Left, Right in commands.items():
                if cmd in Left: # type: ignore
                    print(f"Usage: {Left} - {Right}")

        except NameError:
            print("All spotify related functions are disabled.")
            
        except Exception as e:
            print(f"Error executing command '{cmd}': {e}")

async def main():
    task_ = asyncio.create_task(get_input())

    try:
        await asyncio.gather(task_, return_exceptions=True)
    except asyncio.exceptions.CancelledError:
        pass
        

asyncio.run(main())