#!/usr/bin/env python
import configparser as cp
from pathlib import Path
import asyncio

config = cp.ConfigParser()
default_config_ini = "./config.ini"
async def ainput(prompt: str) -> str:
    return await asyncio.to_thread(input, f'{prompt}')

def return_config(file_path: str = default_config_ini) -> list:
    if not Path(file_path).exists():
        print("ini file does not exist. Creating a new one")
        first_time()
    else:
        config.read(file_path)

        # parser
        user_config_id = config.get("spotify.user", "config_id")
        user_client_secret = config.get("spotify.user", "client_secret")
        user_cache_path = config.get("spotify.user", "cache_path")
        user_device_name = config.get("spotify.user", "device_name")

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
        "device_name" : "None"
    }

    with open(file_path, 'w') as configfile:
        config.write(configfile)
        configfile.close()

def change_ini(config_id, client_secret, cache_path, device_name, file_path: str = default_config_ini) -> None:
    config['spotify.user'] = {
        "config_id" : config_id,
        "client_secret" : client_secret,
        "redirect_uri" : "http://127.0.0.1:8000/callback",
        "scope" : "user-modify-playback-state user-read-playback-state",
        "open_browser" : "False",
        "cache_path" : cache_path,
        "device_name" : device_name
    }

    with open(file_path, 'w') as configfile:
        config.write(configfile)
        configfile.close()

async def change_input(file_path: str = default_config_ini) -> None:
    ini_file = Path(file_path)

    if not ini_file.exists():
        print("ini file does not exist. Creating new one.")
        first_time()
    else:
        while True:
            config_id = await ainput("Input config_id: ")
            client_secret = await ainput("Input client_secret: ")
            cache_path = await ainput("Input cache_path: ")
            device_name = await ainput("Input device_name: ")

            print(
                f"\nconfig_id = {config_id}\n" \
                f"client_secret = {client_secret}\n" \
                f"cache_path = {cache_path}\n" \
                f"device_name = {device_name}\n"
                )
            choice = await ainput("Are those informations correct? [Y/N]: ")

            if choice.lower() == 'y' or choice.lower() == 't':
                change_ini(config_id, client_secret, cache_path, device_name)
                print(f"Successfully saved to {file_path}")
                break
            elif choice.lower() == 'n':
                pass
            else:
                print("No input given, breaking")
                break
    
async def main():
    change_input_ = asyncio.create_task(change_input())

    await change_input_

if __name__ == "__main__":
    asyncio.run(main())