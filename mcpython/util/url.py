"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
import json
import io
import requests
from mcpython import shared


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


def get_url(url, **kwargs):
    """
    Gets the content of an URL as an requests.get() or an an SimulatedResponse-instance
    :param url: the url to download from
    :param kwargs: kwargs to requests.get() with
    :return: the content
    """
    return requests.get(url, **kwargs)


async def get_url_async(url, **kwargs):
    """
    Async variant of above get_url() method
    """
    return requests.get(url, **kwargs)
