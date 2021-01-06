"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from mcpython import logger
from mcpython.common.data.gen.DataGeneratorManager import (
    IDataGenerator,
    DataGeneratorInstance,
)
import PIL.Image
import mcpython.ResourceLoader as ResourceLoader
import mcpython.util.texture


class TextureConstructor(IDataGenerator):
    """
    generator system for generating textures
    """

    def __init__(self, name: str, image_size: tuple = None):
        """
        will create an new TextureConstructor-instance
        :param name: the name of the texture address as "{group}/{path without .png}"
        :param image_size: the size of the image to create
        """
        self.name = name
        self.image_size = image_size
        self.actions = []

    def add_image_layer_top(self, location_or_image, position=(0, 0), rescale=(1, 1)):
        """
        will alpha-composite an image ontop of all previous actions
        :param location_or_image: the image to add
        :param position: the position to add on
        :param rescale: rescale of the image
        """
        try:
            self.actions.append(
                (
                    0,
                    location_or_image
                    if type(location_or_image) == PIL.Image.Image
                    else ResourceLoader.read_image(location_or_image),
                    position,
                    rescale,
                )
            )
        except:
            logger.print_exception(
                "[ERROR] failed to add image layer from file {}".format(
                    location_or_image
                )
            )
        return self

    def add_coloring_layer(
        self, location_or_image, color: tuple, position=(0, 0), rescale=(1, 1)
    ):
        """
        will alpha-composite an image (which is colored before) ontop of all previous actions
        :param location_or_image: the image to add
        :param color: the color to colorize with
        :param position: the position to add on
        :param rescale: rescale of the image
        """
        try:
            if type(location_or_image) != PIL.Image.Image:
                location_or_image = ResourceLoader.read_image(location_or_image)
            self.actions.append(
                (
                    1,
                    location_or_image,
                    color,
                    position,
                    rescale,
                )
            )
        except:
            logger.print_exception(
                "[ERROR] failed to add colorized layer from file {} with color {}".format(
                    location_or_image, color
                )
            )
        return self

    def scaled(self, scale: tuple):
        self.actions.append((3, scale))
        return self

    def crop(self, region: tuple):
        self.actions.append((4, region))
        return self

    def add_alpha_composite_layer(self, location_or_image, position=(0, 0)):
        try:
            self.actions.append(
                (
                    2,
                    location_or_image
                    if type(location_or_image) == PIL.Image.Image
                    else ResourceLoader.read_image(location_or_image),
                    position,
                )
            )
        except:
            logger.print_exception("failed to add alpha composite layer")
        return self

    def write(self, generator: "DataGeneratorInstance", name: str):
        file = self.get_default_location(generator, name)

        if self.image_size is None:
            for action, *data in self.actions:
                if action == 0:
                    self.image_size = data[0]
                    break
            else:
                logger.println(
                    "[ERROR] failed to texture-gen as image size could not get loaded for"
                    " generator named {} to store at {}!".format(self.name, file)
                )
                return

        image = PIL.Image.new("RGBA", self.image_size, (0, 0, 0, 0))
        for action, *data in self.actions:
            if action == 0:
                sx, sy = data[0].size
                px, py = data[2]
                image.alpha_composite(
                    data[0]
                    .resize((sx * px, sy * py), PIL.Image.NEAREST)
                    .convert("RGBA"),
                    data[1],
                )
            elif action == 1:
                i = mcpython.util.texture.colorize(data[0], data[1])
                sx, sy = i.size
                px, py = data[3]
                image.alpha_composite(
                    i.resize((sx * px, sy * py), PIL.Image.NEAREST).convert("RGBA"),
                    data[2],
                )
            elif action == 2:
                image.alpha_composite(data[0], data[1])
            elif action == 3:
                size = image.size
                scale = data[0]
                image = image.resize(tuple([scale[i] * size[i] for i in range(2)]))
            elif action == 4:
                size = image.size
                region = data[0]
                image = image.crop(tuple([region[i] * size[i % 2] for i in range(4)]))

        image.save(generator.get_full_path(file))
