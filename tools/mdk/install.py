"""
mcpython - a minecraft clone written in python licenced under the MIT-licence 
(https://github.com/mcpython4-coding/core)

Contributors: uuk, xkcdjerry (inactive)

Based on the game of fogleman (https://github.com/fogleman/Minecraft), licenced under the MIT-licence
Original game "minecraft" by Mojang Studios (www.minecraft.net), licenced under the EULA
(https://account.mojang.com/documents/minecraft_eula)
Mod loader inspired by "Minecraft Forge" (https://github.com/MinecraftForge/MinecraftForge) and similar

This project is not official by mojang and does not relate to it.
"""
import json
import os
import shutil
import subprocess
import sys
import urllib.request
import zipfile


def download_file(url, dest):
    urllib.request.urlretrieve(url, dest)


print("\nMDK FOR MCPYTHON VERSION 1.0.0 - INSTALLER\n")
print("please wait until the installer has completed its work...")

local = os.path.dirname(__file__)


def create_or_leave(directory: str):
    if not os.path.exists(directory):
        os.makedirs(directory)


create_or_leave(local + "/source")
create_or_leave(local + "/cache")

mod_name = None

while mod_name is None or " " in mod_name:
    if mod_name is not None:
        print("error: can not contain ' '!")
    mod_name = input("Name of the mod: ")

version = input("Version of the mod: ")

mod_name_camel_case = "".join([e[0].upper() + e[1:] for e in mod_name.split("_")])

create_or_leave(local + "/source/{}".format(mod_name))

print("creating mod.json...")
with open(local + "/source/mod.json", mode="w") as target, open(
    local + "/tools/mod.jsont"
) as template:
    target.write(
        template.read().format(
            CAMEL_NAME=mod_name_camel_case, VERSION=version, NAME=mod_name
        )
    )

print("creating main files...")
with open(
    local + "/source/{}/{}.py".format(mod_name, mod_name_camel_case), mode="w"
) as target, open(local + "/tools/mod.py") as template:
    target.write(
        template.read().format(
            CAMEL_NAME=mod_name_camel_case, VERSION=version, NAME=mod_name
        )
    )

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
    import launcher.globalstorage as G
    import launcher.Launcher

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
        "home": local + "/cache/home",
        "build": local + "/cache/build",
    }
else:
    raise ValueError("unsupported operation: " + str(v))

if v in (1, 2):
    download_file(url, local + "/cache/core.zip")

    print("extracting code...")
    print()

    i = 1
    with zipfile.ZipFile(local + "/cache/core.zip") as f:
        names = f.namelist()
        total = len(names)
        for element in names:
            if element.replace("\\", "/").endswith("/"):
                continue
            print("\rextracting {}/{}: {}".format(i, total, element), end="")
            r = os.path.join(
                local + "/cache/core",
                "/".join(element.replace("\\", "/").split("/")[1:]),
            )
            create_or_leave(os.path.dirname(r))
            with open(r, mode="wb") as fw:
                fw.write(f.read(element))
            i += 1
    print("\nfinished!")

    d = {
        "url": url,
        "path": local + "/cache/core",
        "home": local + "/cache/home",
        "build": local + "/cache/build",
    }

with open(local + "/config.json", mode="w") as f:
    json.dump(d, f)

print("installing libraries...")
subprocess.call(
    [sys.executable, d["path"] + "/tools/installer.py"],
    stdin=sys.stdin,
    stdout=sys.stdout,
    stderr=sys.stderr,
)

if v in (1, 2):
    print("doing data-gen as it is an not-build-ed version...")
    subprocess.call(
        [
            sys.executable,
            d["path"] + "/__main__.py",
            "--data-gen",
            "--enable-all-blocks",
            "--home-folder",
            d["home"],
            "--build-folder",
            d["build"],
            "--exit-after-data-gen",
            "--no-window",
        ]
    )
