"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared as G
import mcpython.util.texture
import PIL.Image
import mcpython.ResourceLoader
import os
import mcpython.common.event.Registry

print("someone loaded mcpython.texture.factory... a bad thing !!!! (deprecated :-( )")


class ITextureChange(mcpython.common.event.Registry.IRegistryContent):
    TYPE = "minecraft:texture_change"

    @staticmethod
    def convert(
        images: list, image: PIL.Image.Image, *args, **kwargs
    ) -> PIL.Image.Image:
        raise NotImplementedError()


class TextureFactory:
    def __init__(self):
        self.changer = {}

    @staticmethod
    def add_transform(registry, obj: ITextureChange):
        G.texturefactoryhandler.changer[obj.NAME] = obj

    def transform(self, images: list, image, mode, *args, **kwargs):
        if mode not in self.changer:
            raise ValueError(
                "unknown task named '{}'. please use only registered tasks".format(mode)
            )
        texturechange: ITextureChange = self.changer[mode]
        return texturechange.convert(images, image, *args, **kwargs)

    def apply_from_file(self, file):
        self.apply_from_data(mcpython.ResourceLoader.read_json(file))

    def apply_from_data(self, data: dict):
        images = [mcpython.ResourceLoader.read_image(x) for x in data["images"]]
        if "space" in data:
            images += [None] * data["space"]
        for entry in data["transforms"]:
            image = entry["image"]
            out = entry["store"]
            mode = entry["mode"]
            entry.pop("image")
            entry.pop("store")
            entry.pop("mode")
            if type(image) == list:
                if type(out) != list:
                    raise ValueError("can't cast data {} to valid results".format(data))
                for i, e in enumerate(image):
                    images[out[i]] = self.transform(images, images[e], mode, **entry)
            else:
                images[out] = self.transform(images, images[image], mode, **entry)
        for store in data["store"]:
            f = G.build + "/texture/" + store["location"]
            d = os.path.dirname(f)
            if not os.path.exists(d):
                os.makedirs(d)
            images[store["id"]].save(f)

    def load(self):
        entries = mcpython.ResourceLoader.get_all_entries_special(
            "assets/factory/texture"
        )
        for entry in entries:
            if entry.endswith("/"):
                continue
            self.apply_from_file(entry)


G.texturefactoryhandler = TextureFactory()
texturechanges = mcpython.common.event.Registry.Registry(
    "texturechanges",
    ["minecraft:texture_change"],
    injection_function=TextureFactory.add_transform,
)


@G.registry
class TextureResize(ITextureChange):
    NAME = "resize"

    @staticmethod
    def convert(images: list, image: PIL.Image.Image, size=None) -> PIL.Image.Image:
        return image.resize(
            size, PIL.Image.NEAREST
        )  # todo: implement option to choose mode


@G.registry
class TextureColorize(ITextureChange):
    NAME = "colorize"

    @staticmethod
    def convert(images: list, image: PIL.Image.Image, color=None) -> PIL.Image.Image:
        return mcpython.util.texture.colorize(image, color)


@G.registry
class TextureCut(ITextureChange):
    NAME = "cut"

    @staticmethod
    def convert(images: list, image: PIL.Image.Image, area=None) -> PIL.Image.Image:
        return image.crop(area)


@G.registry
class TextureRebase(ITextureChange):
    NAME = "rebase"

    @staticmethod
    def convert(
        images: list, image: PIL.Image.Image, size=None, position=(0, 0)
    ) -> PIL.Image.Image:
        base = PIL.Image.new("RGBA", size)
        base.paste(image, position)
        return base


@G.registry
class TextureCombine(ITextureChange):
    NAME = "combine"

    @staticmethod
    def convert(
        images: list, image: PIL.Image.Image, base=None, position=(0, 0)
    ) -> PIL.Image.Image:
        imageb: PIL.Image.Image = images[base].copy()
        imageb.paste(image, position)
        return imageb
