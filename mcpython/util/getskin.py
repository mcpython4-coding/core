"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
# code for downloading skin data from the mc server API
# todo: make class-based
# todo: make more fail-save

# file licensed under the licence in licenses/LICENSE_mcskinview
# modified for this project to match the overall system
# modified for newer skin textures
from mcpython.util.net import get_url
import json
import os
import shutil
from base64 import b64decode

import PIL.Image
import requests

from mcpython import globals as G, logger

DEBUG = False
SIMULATE = False

userid_url = "https://api.mojang.com/users/profiles/minecraft/{username}"
userinfo_url = "https://sessionserver.mojang.com/session/minecraft/profile/{userid}"


def find_texture_info(properties):
    for prop in properties:
        if prop["name"] == "textures":
            return json.loads(b64decode(prop["value"], validate=True).decode("utf-8"))
    return None


def download_skin(username: str, store: str):
    """
    will download skin data for an user name
    :param username: the user to download for
    :param store: where to store the data
    :raises ValueError: raised when an error occurred during retrieving the data

    Will also store data in an cache for later usage
    """
    if os.path.isfile(G.build + "/skins/{}.png".format(username)):
        logger.println("loading skin from cache...")
        shutil.copy(G.build + "/skins/{}.png".format(username), store)
        return
    logger.println("downloading skin for '{}'".format(username))
    if os.path.exists(store):
        os.remove(store)

    try:
        r = get_url(userid_url.format(username=username))
    except requests.exceptions.ConnectionError:
        raise ValueError() from None
    if r.status_code != 200:
        raise ValueError()
    userid = r.json()["id"]

    r = get_url(userinfo_url.format(userid=userid))
    userinfo = r.json()
    if "error" in userinfo:
        logger.println(
            "[SERVER] {}: {}".format(userinfo["error"], userinfo["errorMessage"])
        )
        raise ValueError()
    try:
        texture_info = find_texture_info(userinfo["properties"])
    except KeyError:
        logger.println("ParseError in '{}'".format(userinfo))
        raise
    if texture_info is None:
        raise ValueError()

    skin_url = texture_info["textures"]["SKIN"]["url"]
    r = get_url(skin_url, stream=True)
    if r.status_code != 200:
        raise ValueError()
    with open(store, "wb") as f:
        f.write(r.content)
    image = PIL.Image.open(store)
    if image.size[0] != image.size[1:]:
        new_image = PIL.Image.new("RGBA", (image.size[0], image.size[0]), (0, 0, 0, 0))
        new_image.alpha_composite(image)
        new_image.alpha_composite(image.crop((0, 16, 15, 32)), (16, 48))
        new_image.alpha_composite(image.crop((40, 16, 55, 32)), (32, 48))
        new_image.save(store)
    if not os.path.exists(G.build + "/skins"):
        os.makedirs(G.build + "/skins")
    shutil.copy(store, G.build + "/skins/{}.png".format(username))
