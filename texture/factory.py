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
    def convert(image: PIL.Image.Image, *args, **kwargs) -> PIL.Image.Image: raise NotImplementedError()


class TextureFactory:
    def __init__(self):
        self.changer = {}

    @staticmethod
    def add_transform(registry, obj: ITextureChange):
        G.texturefactoryhandler.changer[obj.get_name()] = obj

    def transform(self, image, mode, *args, **kwargs):
        if mode not in self.changer:
            raise ValueError("unknown task named '{}'. please use only registered tasks".format(mode))
        texturechange: ITextureChange = self.changer[mode]
        return texturechange.convert(image, *args, **kwargs)

    def apply_from_file(self, file):
        data = ResourceLocator.read(file, "json")
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
                if type(out) != list: raise ValueError("can't cast file {} to valid results".format(file))
                for i, e in enumerate(image):
                    images[out[i]] = self.transform(images[e], mode, **entry)
            else:
                images[out] = self.transform(images[image], mode, **entry)
        for store in data["store"]:
            f = G.local+"/tmp/"+store["location"]
            d = os.path.dirname(f)
            if not os.path.exists(d): os.makedirs(d)
            images[store["id"]].save(f)

    def load(self):
        entrys = ResourceLocator.get_all_entrys("assets/factory/texture")
        for entry in entrys:
            self.apply_from_file(entry)


G.texturefactoryhandler = TextureFactory()
texturechanges = event.Registry.Registry("texturechanges", [ITextureChange], 
                                         injection_function=TextureFactory.add_transform)


@G.registry
class TextureResize(ITextureChange):
    @staticmethod
    def get_name() -> str: return "resize"

    @staticmethod
    def convert(image: PIL.Image.Image, size=None) -> PIL.Image.Image:
        return image.resize(size)


@G.registry
class TextureColorize(ITextureChange):
    @staticmethod
    def get_name() -> str: return "colorize"

    @staticmethod
    def convert(image: PIL.Image.Image, color=None) -> PIL.Image.Image:
        return util.texture.colorize(image, color)


@G.registry
class TextureCut(ITextureChange):
    @staticmethod
    def get_name() -> str: return "cut"

    @staticmethod
    def convert(image: PIL.Image.Image, area=None) -> PIL.Image.Image:
        return image.crop(area)

