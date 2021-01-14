"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft, representing snapshot 20w51a
(https://www.minecraft.net/en-us/article/minecraft-snapshot-20w51a)

This project is not official by mojang and does not relate to it.
"""
import zipfile
import subprocess
import os
import urllib.request
import json
import sys


def download_file(url, dest):
    urllib.request.urlretrieve(url, dest)


local = os.path.dirname(__file__)


def create_or_leave(directory: str):
    if not os.path.exists(directory):
        os.makedirs(directory)


a = str(
    input("MDK configurator: (1) update target version, (2) update API information: ")
).lower()


if a == "1":
    v = int(
        input(
            "newest dev: (1), newest release (2), launcher profile (3), dev environment (4): "
        )
    )

    print("getting newest version...")
    url = None
    d = None

    if v == 1:
        url = "https://github.com/mcpython4-coding/core/archive/dev.zip"
    elif v == 2:
        url = "https://github.com/mcpython4-coding/core/archive/release.zip"
    elif v == 3:
        directory = input("please select the launcher directory: ")
        sys.path.append(directory)
        import launcher.Launcher

        import launcher.globalstorage as G

        G.local = directory  # re-direct this!

        launcher.Launcher.setup()
        instance = launcher.Launcher.Launcher()
        instance.load_index()

        version = launcher.Launcher.Version.user_selects()
        version.download()

        d = {
            "url": None,
            "path": version.path,
            "home": local + "/cache/home",
            "build": local + "/cache/build",
        }
    elif v == 4:
        directory = input("please select the dev directory: ")
        d = {
            "url": None,
            "path": directory,
            "home": directory + "/home",
            "build": directory + "/home/build",
        }
    else:
        raise ValueError("unsupported operation: " + str(v))

    with open(local + "/config.json", mode="w") as f:
        json.dump(d, f)

    print("installing libraries...")
    subprocess.call(
        [sys.executable, local + "/cache/core/installer.py"],
        stdin=sys.stdin,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
elif a == "2":
    if os.path.exists(local + "/api.json"):
        with open(local + "/api.json") as f:
            data = json.load(f)
    else:
        data = {}
    b = input(
        "Would you like to (1) create an new API package, (2) remove an existing api package, (3) get the status of the API system"
    ).lower()
    if b == "1":
        name = input("Please enter the name of the api folder: ")
        data[name] = {
            "path": local + "/api/{}".format(name),
            "source": input("Is part of your mod (y/n)? ").lower() == "y",
        }
        if not os.path.exists(local + "/api/{}".format(name)):
            os.makedirs(local + "/api/{}".format(name))
    elif b == "2":
        name = input("Please enter the name of the api folder: ")
        if name not in data:
            raise ValueError("name not found!")
        del data[name]
    elif b == "3":
        if len(data) == 0:
            sys.exit(-1)
        print("the following api's are registered")
        for name in data:
            print(
                " - '{}' under '{}' (source: )".format(
                    name, data[name]["path"], str(data[name]["source"]).lower()
                )
            )
    else:
        raise ValueError("invalid answer!")
    with open(local + "/api.json", mode="w") as f:
        json.dump(data, f)
else:
    raise ValueError("invalid answer")
