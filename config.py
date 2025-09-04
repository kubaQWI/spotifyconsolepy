#!/usr/bin/env python
import configparser as cp
from pathlib import Path
import asyncio
import os

config = cp.ConfigParser()
default_config_ini = "./config.ini"

async def ainput(prompt: str) -> str:
    return await asyncio.to_thread(input, f'{prompt}')

def return_config(file_path: str = default_config_ini) -> list: 
    if not Path(file_path).exists():
        print("The config file doesn't exist. Creating new one...")
        first_time()
        return []
    else:
        config.read(file_path)

        # parser
        try:
            user_config_id = config.get("spotify.user", "config_id")
            user_client_secret = config.get("spotify.user", "client_secret")
            user_cache_path = config.get("spotify.user", "cache_path")
            user_device_name = config.get("spotify.user", "device_name")

        except cp.NoOptionError:
            print(f"One of the portions of {file_path} data is broken. Run 'change-ini' to change it.")
            return []

        except cp.NoSectionError:
            print(f"There are no spotify user variables in {file_path}. Please provide them in 'change-ini' command.")
            return []
        
        data = [user_config_id, user_client_secret, user_cache_path, user_device_name]

        return data
            
def first_time(file_path: str = default_config_ini) -> None:
    config['spotify.default'] = {
        "config_id" : "None",
        "client_secret" : "None",
        "redirect_uri" : "http://127.0.0.1:8000/callback",
        "scope" : "user-modify-playback-state user-read-playback-state",
        "open_browser" : "False",
        "cache_path" : "None",
        "device_name" : "None",
        "os" : f"{os.name}"
    }

    with open(file_path, 'w') as configfile:
        config.write(configfile)
        configfile.close()

def change_ini(config_id, client_secret, cache_path, device_name, file_path: str = default_config_ini, osname: str = os.name) -> None:
    ini_path = Path(file_path)

    if ini_path.exists():
        config['spotify.user'] = {
        "config_id" : config_id,
        "client_secret" : client_secret,
        "redirect_uri" : "http://127.0.0.1:8000/callback",
        "scope" : "user-modify-playback-state user-read-playback-state",
        "open_browser" : "False",
        "cache_path" : cache_path,
        "device_name" : device_name,
        "os" : f"{osname}"
        }

        with open(file_path, 'w') as configfile:
            config.write(configfile)
            configfile.close()

    else:
        print("The config file doesn't exist. Creating new one...")
        first_time()

    return

async def change_input(file_path: str = default_config_ini) -> None:
    
    while True:
        config_id = await ainput("Input client_id: ") # i know that is different but i'm too lazy to change every variable name xd
        client_secret = await ainput("Input client_secret: ")
        cache_path = await ainput("Input cache_path: ")
        device_name = await ainput("Input device_name: ")

        print(
            f"\nconfig_id = {config_id}\n" \
            f"client_secret = {client_secret}\n" \
            f"cache_path = {cache_path}\n" \
            f"device_name = {device_name}\n"
            )
        choice = await ainput("Are those informations correct? [Y/N/Q]: ")

        if choice.lower() == 'y' or choice.lower() == 't':
            change_ini(config_id, client_secret, cache_path, device_name)
            print(f"Successfully saved to {file_path}")
            break
        elif choice.lower() == 'n':
            pass
        elif choice.lower() == 'q':
            print("Quitting without saving...")
            break
        else:
            print(f"'{choice}' is not an option. Type again")
            continue
    
async def main() -> None:
    change_input_ = asyncio.create_task(change_input())

    await change_input_

if __name__ == "__main__":
    asyncio.run(main())