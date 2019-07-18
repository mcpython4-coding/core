"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4-pre6.jar"""
import globals as G
import zipfile
import PIL.Image
import os


LOCATION_INFO = {
    "block": ("textures", ".png"),
    "item": ("textures", ".png"),
    "gui": ("textures", ".png")
}


class ResourceLocator:
    def __init__(self, location, output=G.local+"/tmp/generator_output"):
        # block/yellow_wool
        self.data = None
        # print(location)
        if os.path.exists(location):
            if not location.endswith(".png"):
                with open(location, mode="rb") as f:
                    self.data = f.read()
            else:
                self.data = PIL.Image.open(location)
        elif os.path.exists(os.path.join(G.local, location)):
            if not location.endswith(".png"):
                with open(os.path.join(G.local, location), mode="rb") as f:
                    self.data = f.read()
            else:
                self.data = PIL.Image.open(os.path.join(G.local, location))
        else:
            if location.count("/") == 1 and ":" not in location:
                s = location.split("/")
                info = LOCATION_INFO[s[0]]
                location = "assets/minecraft/{}/{}/{}{}".format(info[0], s[0], s[1], info[1])
                output += info[1]
                with open(output, mode="wb") as wf:
                    wf.write(G.jar_archive.read(location))
                self.data = PIL.Image.open(output)
            if self.data is None:
                try:
                    if not location.endswith(".png"):
                        self.data = G.jar_archive.read(location)
                    else:
                        with G.jar_archive.open(location, mode="r") as f, open(output, mode="wb") as t:
                            t.write(f.read())
                        self.data = PIL.Image.open(output)
                except:
                    raise


