import spotify_commands as scmd
import warnings
import argparse
import asyncio
import config

parser = argparse.ArgumentParser(
    prog="arguments.py",
    description="Argument parser for commands in spotify_commands.py",
    epilog="Made with <3 by kubaQWI and cement / https://github.com/kubaQWI/spotifyconsolepy")

warnings.filterwarnings("ignore")

parser.add_argument('-P', '--play', help="Start/resume playback", action="store_true")
parser.add_argument('-p', '--pause', help="Pause playback", action="store_true")
parser.add_argument('-n', '--next', help="Skip to next track", action="store_true")
parser.add_argument('-r', '--previous', help="Skip to previous track", action="store_true")
parser.add_argument('-c', '--current', help="Show currently playing track", action="store_true")
parser.add_argument('-v', '--volume', help="Set volume to a given percentage", type=int)
parser.add_argument('-s', '--shuffle', help="Turn shuffle mode on or off", type=str)
parser.add_argument('-R', '--repeat', help="Set repeat mode", type=str)
parser.add_argument('-d', '--devices', help="List available devices", action="store_true")
parser.add_argument('-t', '--transfer', help="Transfer playback to another device", type=str) # not done
parser.add_argument('-S', '--search', help="Search for a track", type=str)                    # not done
parser.add_argument('-Pu', '--playuri', help="Play a specific track by URI", type=str)
parser.add_argument('-q', '--queue', help="Show playback queue", action="store_true")
parser.add_argument('-a', '--addqueue', help="Add track to queue", type=str)
parser.add_argument('-fi', '--fadein', help="Initializes fade in action", action="store_true")
parser.add_argument('-fo', '--fadeout', help="Initializes fade out action", action="store_true")

args = parser.parse_args()

async def main() -> None:
    actions = {
        "play": lambda: scmd.start_playback(),
        "pause": lambda: scmd.pause_playback(),
        "next": lambda: scmd.next_track(),
        "previous": lambda: scmd.previous_track(),
        "current": lambda: scmd.current_playback(),
        "volume": lambda: scmd.set_volume(args.volume) if args.volume else None,
        "shuffle": lambda: scmd.shuffle(args.shuffle) if args.shuffle else None,
        "repeat": lambda: scmd.repeat(args.repeat) if args.repeat else None,
        "devices": lambda: scmd.api_get_device_data(),
        "queue": lambda: scmd.queue(),
        "playuri": lambda: scmd.start_playback(uris = args.playuri if args.playuri else None), 
        "fadein": lambda: scmd.fade_in(),
        "fadeout": lambda: scmd.fade_out()
    }

    for arg, action in actions.items():
        try:
            value = getattr(args, arg)
            if value:
                coro = action()
                if coro:
                    await coro
                    print("Done '%s' task." %(arg))

        except scmd.spotipy.exceptions.SpotifyException as e:
            print(f"There was a problem with spotify api: {e}")

if __name__ == "__main__":
    asyncio.run(main())