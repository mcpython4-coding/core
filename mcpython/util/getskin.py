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
# code for downloading skin data from the mc server API
# todo: make class-based
# todo: make more fail-save

import json
import os
import shutil
from base64 import b64decode

import PIL.Image
import requests
from mcpython import shared
from mcpython.engine import logger

# file licensed under the licence in licenses/LICENSE_mcskinview
# modified for this project to match the overall system
# modified for newer skin textures
from mcpython.util.url import get_url

DEBUG = False
SIMULATE = False

userid_url = "https://api.mojang.com/users/profiles/minecraft/{username}"
userinfo_url = "https://sessionserver.mojang.com/session/minecraft/profile/{userid}"


def find_texture_info(properties):
    for prop in properties:
        if prop["name"] == "textures":
            return json.loads(b64decode(prop["value"], validate=True).decode("utf-8"))
    return None


async def store_missing_texture(path: str):
    import mcpython.engine.ResourceLoader

    missing_texture = await mcpython.engine.ResourceLoader.read_image(
        "assets/missing_texture.png"
    )

    missing_texture.save(path)


async def download_skin(username: str, store: str):
    """
    Will download skin data for a username
    :param username: the user to download for
    :param store: where to store the data
    :raises ValueError: raised when an error occurred during retrieving the data

    Will also store data in an cache for later usage
    """
    if os.path.isfile(shared.build + "/skins/{}.png".format(username)):
        logger.println("loading skin from cache...")
        shutil.copy(shared.build + "/skins/{}.png".format(username), store)
        return
    logger.println("downloading skin for '{}'".format(username))
    if os.path.exists(store):
        os.remove(store)

    try:
        r = get_url(userid_url.format(username=username))
    except requests.exceptions.ConnectionError:
        await store_missing_texture(store)
        return

    if r.status_code != 200:
        await store_missing_texture(store)
        return

    userid = r.json()["id"]

    r = get_url(userinfo_url.format(userid=userid))
    userinfo = r.json()

    if "error" in userinfo:
        logger.println(
            "[MOJANG/SERVER] {}: {}".format(userinfo["error"], userinfo["errorMessage"])
        )
        await store_missing_texture(store)
        return

    try:
        texture_info = find_texture_info(userinfo["properties"])
    except KeyError:
        logger.println("ParseError in '{}'".format(userinfo))
        raise

    if texture_info is None:
        await store_missing_texture(store)
        return

    skin_url = texture_info["textures"]["SKIN"]["url"]
    r = get_url(skin_url, stream=True)

    if r.status_code != 200:
        await store_missing_texture(store)
        return

    with open(store, "wb") as f:
        f.write(r.content)  # lgtm [py/clear-text-storage-sensitive-data]
    image = PIL.Image.open(store)
    if image.size[0] != image.size[1:]:
        new_image = PIL.Image.new("RGBA", (image.size[0], image.size[0]), (0, 0, 0, 0))
        new_image.alpha_composite(image)
        new_image.alpha_composite(image.crop((0, 16, 15, 32)), (16, 48))
        new_image.alpha_composite(image.crop((40, 16, 55, 32)), (32, 48))
        new_image.save(store)
    if not os.path.exists(shared.build + "/skins"):
        os.makedirs(shared.build + "/skins")
    shutil.copy(store, shared.build + "/skins/{}.png".format(username))
