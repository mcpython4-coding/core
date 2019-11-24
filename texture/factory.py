"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import util.texture
import PIL.Image
import ResourceLocator
import os
import event.Registry


class ITextureChange:
    @staticmethod
    def get_name() -> str: raise NotImplementedError()

    @staticmethod
    def convert(images: list, image: PIL.Image.Image, *args, **kwargs) -> PIL.Image.Image: raise NotImplementedError()


class TextureFactory:
    def __init__(self):
        self.changer = {}

    @staticmethod
    def add_transform(registry, obj: ITextureChange):
        G.texturefactoryhandler.changer[obj.get_name()] = obj

    def transform(self, images: list, image, mode, *args, **kwargs):
        if mode not in self.changer:
            raise ValueError("unknown task named '{}'. please use only registered tasks".format(mode))
        texturechange: ITextureChange = self.changer[mode]
        return texturechange.convert(images, image, *args, **kwargs)

    def apply_from_file(self, file):
        self.apply_from_data(ResourceLocator.read(file, "json"))

    def apply_from_data(self, data: dict):
        images = [ResourceLocator.read(x, "pil") for x in data["images"]]
        if "space" in data: images += [None] * data["space"]
        for entry in data["transforms"]:
            image = entry["image"]
            out = entry["store"]
            mode = entry["mode"]
            entry.pop("image")
            entry.pop("store")
            entry.pop("mode")
            if type(image) == list:
                if type(out) != list: raise ValueError("can't cast data {} to valid results".format(data))
                for i, e in enumerate(image):
                    images[out[i]] = self.transform(images, images[e], mode, **entry)
            else:
                images[out] = self.transform(images, images[image], mode, **entry)
        for store in data["store"]:
            f = G.local+"/build/texture/"+store["location"]
            d = os.path.dirname(f)
            if not os.path.exists(d): os.makedirs(d)
            images[store["id"]].save(f)

    def load(self):
        entries = ResourceLocator.get_all_entries_special("assets/factory/texture")
        for entry in entries:
            self.apply_from_file(entry)


G.texturefactoryhandler = TextureFactory()
texturechanges = event.Registry.Registry("texturechanges", [ITextureChange], 
                                         injection_function=TextureFactory.add_transform)


@G.registry
class TextureResize(ITextureChange):
    @staticmethod
    def get_name() -> str: return "resize"

    @staticmethod
    def convert(images: list, image: PIL.Image.Image, size=None) -> PIL.Image.Image:
        return image.resize(size)


@G.registry
class TextureColorize(ITextureChange):
    @staticmethod
    def get_name() -> str: return "colorize"

    @staticmethod
    def convert(images: list, image: PIL.Image.Image, color=None) -> PIL.Image.Image:
        return util.texture.colorize(image, color)


@G.registry
class TextureCut(ITextureChange):
    @staticmethod
    def get_name() -> str: return "cut"

    @staticmethod
    def convert(images: list, image: PIL.Image.Image, area=None) -> PIL.Image.Image:
        return image.crop(area)


@G.registry
class TextureRebase(ITextureChange):
    @staticmethod
    def get_name() -> str: return "rebase"

    @staticmethod
    def convert(images: list, image: PIL.Image.Image, size=None, position=(0, 0)) -> PIL.Image.Image:
        base = PIL.Image.new("RGBA", size)
        base.paste(image, position)
        return base


@G.registry
class TextureCombine(ITextureChange):
    @staticmethod
    def get_name() -> str: return "combine"

    @staticmethod
    def convert(images: list, image: PIL.Image.Image, base=None, position=(0, 0)) -> PIL.Image.Image:
        imageb: PIL.Image.Image = images[base].copy()
        imageb.paste(image, position)
        return imageb

