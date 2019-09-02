"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import zipfile
import PIL.Image
import os
import json


LOCATION_INFO = {
    "block": ("textures", ".png"),
    "item": ("textures", ".png"),
    "gui": ("textures", ".png")
}


class ResourceLocator:
    def __init__(self, location: str, output=G.local+"/tmp/generator_output", load_as_json=False):
        # block/yellow_wool
        self.data = None
        # print(location)
        if location.startswith(G.local):
            if not location.endswith(".png"):
                if location.endswith(".json") and load_as_json:
                    with open(location) as f:
                        self.data = json.load(f)
                else:
                    with open(location, mode="rb") as f:
                        self.data = f.read()
            else:
                self.data = PIL.Image.open(location)
        elif os.path.exists(os.path.join(G.local, location)):
            if not location.endswith(".png"):
                if location.endswith(".json") and load_as_json:
                    with open(os.path.join(G.local, location)) as f:
                        self.data = json.load(f)
                else:
                    with open(os.path.join(G.local, location), mode="rb") as f:
                        self.data = f.read()
            else:
                self.data = PIL.Image.open(os.path.join(G.local, location))
        else:
            if ":" not in location:
                try:
                    s = location.split("/")
                    info = LOCATION_INFO[s[0]]
                    location = "assets/minecraft/{}/{}/{}{}".format(info[0], s[0], "/".join(s[1:]), info[1])
                    output += info[1]
                    with open(output, mode="wb") as wf:
                        wf.write(G.jar_archive.read(location))
                    self.data = PIL.Image.open(output)
                except:
                    pass
            if self.data is None:
                try:
                    if not location.endswith(".png"):
                        self.data = G.jar_archive.read(location)
                        if load_as_json:
                            self.data = json.loads(self.data.decode("UTF-8"))
                    else:
                        with G.jar_archive.open(location, mode="r") as f, open(output, mode="wb") as t:
                            t.write(f.read())
                        self.data = PIL.Image.open(output)
                except:
                    raise


