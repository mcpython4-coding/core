# file licensed under the licence in licenses/LICENSE_mcskinview
# modified for this project

import io
import sys
import json
import shutil

from base64 import b64decode

import requests
import globals as G
import os
import logger
import PIL.Image

DEBUG = False
SIMULATE = False

userid_url = "https://api.mojang.com/users/profiles/minecraft/{username}"
userinfo_url = "https://sessionserver.mojang.com/session/minecraft/profile/{userid}"


class SimulatedResponse(object):
    def __init__(self, content, is_json, raw=None):
        self.content = content
        self.is_json = is_json
        self.status_code = 200
        self.raw = raw

    def json(self):
        if self.is_json:
            return json.loads(self.content)
        return None


def find_texture_info(properties):
    for prop in properties:
        if prop['name'] == 'textures':
            return json.loads(b64decode(prop['value'], validate=True).decode('utf-8'))
    return None


def get_url(url, **kwargs):
    if SIMULATE:
        content = None
        is_json = False
        raw = None
        # These files are not provided in the git repo because I consider them
        # kind of sensitive.  Feel free to provide your own in their place.
        if url.startswith('https://api.mojang.com/users/profiles/minecraft/'):
            with open('simulated_userid_response.json', 'r') as f:
                content = f.read()
            is_json = True
        elif url.startswith('https://sessionserver.mojang.com/session/minecraft/profile/'):
            with open('simulated_userinfo_response.json', 'r') as f:
                content = f.read()
            is_json = True
        else:
            with open('simulated_skin_response.png', 'rb') as f:
                content = f.read()
            is_json = False
            raw = io.BytesIO(content)
        return SimulatedResponse(content, is_json, raw)
    else:
        return requests.get(url, **kwargs)


def download_skin(username: str, store: str):
    if os.path.isfile(G.local+"/build/skin_{}.png".format(username)):
        print("loading skin from cache...")
        shutil.copy(G.local+"/build/skin_{}.png".format(username), store)
        return
    print("downloading skin for '{}'".format(username))
    if os.path.exists(store):
        os.remove(store)

    r = get_url(userid_url.format(username=username))
    if r.status_code != 200: raise ValueError()
    userid = r.json()['id']

    r = get_url(userinfo_url.format(userid=userid))
    userinfo = r.json()
    if "error" in userinfo:
        logger.println("[SERVER] {}: {}".format(userinfo["error"], userinfo["errorMessage"]))
        raise ValueError()
    try:
        texture_info = find_texture_info(userinfo['properties'])
    except KeyError:
        logger.println("ParseError in '{}'".format(userinfo))
        raise
    if texture_info is None: raise ValueError()

    skin_url = texture_info["textures"]["SKIN"]["url"]
    r = get_url(skin_url, stream=True)
    if r.status_code != 200: raise ValueError()
    with open(store, 'wb') as f:
        f.write(r.content)
    image = PIL.Image.open(store)
    if image.size[0] != image.size[1:]:
        new_image = PIL.Image.new("RGBA", (image.size[0], image.size[0]), (0, 0, 0, 0))
        new_image.alpha_composite(image)
        new_image.alpha_composite(image.crop((0, 16, 15, 32)), (16, 48))
        new_image.alpha_composite(image.crop((40, 16, 55, 32)), (32, 48))
        new_image.save(store)
    shutil.copy(store, G.local+"/build/skin_{}.png".format(username))
