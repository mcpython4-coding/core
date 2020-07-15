"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
import zipfile
import subprocess
import os
import urllib.request
import json
import sys
import shutil


def download_file(url, dest):
    urllib.request.urlretrieve(url, dest)


local = os.path.dirname(__file__)


def create_or_leave(directory: str):
    if not os.path.exists(directory):
        os.makedirs(directory)


a = str(input("MDK configurator: (1) update target version: ")).lower()


if a == "1":
    v = int(input("newest dev: (1), newest release (2): "))

    print("getting newest version...")

    if v == 1:
        url = "https://github.com/mcpython4-coding/core/archive/dev.zip"
    else:
        url = "https://github.com/mcpython4-coding/core/archive/release.zip"

    download_file(url, local + "/cache/core.zip")

    print("removing old code...")
    shutil.rmtree(local + "/cache/core")

    print("extracting code...")
    print()

    i = 1
    with zipfile.ZipFile(local + "/cache/core.zip") as f:
        names = f.namelist()
        total = len(names)
        for element in names:
            if element.replace("\\", "/").endswith("/"): continue
            print("\rextracting {}/{}: {}".format(i, total, element), end="")
            r = os.path.join(local + "/cache/core", "/".join(element.replace("\\", "/").split("/")[1:]))
            create_or_leave(os.path.dirname(r))
            with open(r, mode="wb") as fw:
                fw.write(f.read(element))
            i += 1
    print("\nfinished!")

    d = {"url": url, "path": local + "/cache/core", "home": local + "/cache/home", "build": local + "/cache/build"}

    with open(local + "/config.json", mode="w") as f:
        json.dump(d, f)

    print("installing libraries...")
    subprocess.call([sys.executable, local + "/cache/core/installer.py"], stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
else:
    raise ValueError("invalid answer")

