"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
import json
import io
import requests
import globals as G


class SimulatedResponse:
    """
    Simulated response
    """

    def __init__(self, content, is_json, raw=None):
        self.content = content
        self.is_json = is_json
        self.status_code = 200
        self.raw = raw

    def json(self):
        if self.is_json:
            return json.loads(self.content)
        return None


SIMULATE = False


def get_url(url, **kwargs):
    """
    gets the content of an URL as an requests.get() or an an SimulatedResponse-instance
    :param url: the url to download from
    :param kwargs: kwargs to requests.get() with
    :return: the content
    """
    if SIMULATE:
        raw = None
        # These files are not provided in the git repo because I consider them
        # kind of sensitive.  Feel free to provide your own in their place.
        if url.startswith('https://api.mojang.com/users/profiles/minecraft/'):
            with open(G.build+'/simulated_userid_response.json', 'r') as f:
                content = f.read()
            is_json = True
        elif url.startswith('https://sessionserver.mojang.com/session/minecraft/profile/'):
            with open(G.build+'/simulated_userinfo_response.json', 'r') as f:
                content = f.read()
            is_json = True
        else:
            with open(G.build+'/simulated_skin_response.png', 'rb') as f:
                content = f.read()
            is_json = False
            raw = io.BytesIO(content)
        return SimulatedResponse(content, is_json, raw)
    else:
        return requests.get(url, **kwargs)
