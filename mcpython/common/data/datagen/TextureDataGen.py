"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from mcpython import logger
import mcpython.common.data.datagen.Configuration
import PIL.Image
import mcpython.ResourceLocator
import mcpython.util.texture


class TextureConstructor(mcpython.common.data.datagen.Configuration.IDataGenerator):
    """
    generator system for generating textures
    """

    def __init__(self, config, name: str, image_size: tuple):
        """
        will create an new TextureConstructor-instance
        :param config: the config to use
        :param name: the name of the texture address as "{group}/{path without .png}"
        :param image_size: the size of the image to create
        """
        super().__init__(config)
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
            self.actions.append((0, location_or_image if type(location_or_image) == PIL.Image.Image else
                                 mcpython.ResourceLocator.read(location_or_image, "pil"), position, rescale))
        except:
            logger.print_exception("[ERROR] failed to add image layer from file {}".format(location_or_image))
        return self

    def add_coloring_layer(self, location_or_image, color: tuple, position=(0, 0), rescale=(1, 1)):
        """
        will alpha-composite an image (which is colored before) ontop of all previous actions
        :param location_or_image: the image to add
        :param color: the color to colorize with
        :param position: the position to add on
        :param rescale: rescale of the image
        """
        try:
            self.actions.append((1, location_or_image if type(location_or_image) == PIL.Image.Image else
                                 mcpython.ResourceLocator.read(location_or_image, "pil"), color, position, rescale))
        except:
            logger.print_exception("[ERROR] failed to add colorized layer from file {} with color {}".format(
                location_or_image, color))
        return self

    def add_alpha_composite_layer(self, location_or_image, position=(0, 0)):
        try:
            self.actions.append((2, location_or_image if type(location_or_image) == PIL.Image.Image else
                                 mcpython.ResourceLocator.read(location_or_image, "pil"), position))
        except:
            logger.print_exception("failed to add alpha composite layer")
        return self

    def generate(self):
        image = PIL.Image.new("RGBA", self.image_size, (0, 0, 0, 0))
        for action, *data in self.actions:
            if action == 0:
                sx, sy = data[0].size
                px, py = data[2]
                image.alpha_composite(data[0].resize((sx*px, sy*py), PIL.Image.NEAREST).convert("RGBA"), data[1])
            elif action == 1:
                i = mcpython.util.texture.colorize(data[0], data[1])
                sx, sy = i.size
                px, py = data[3]
                image.alpha_composite(i.resize((sx * px, sy * py), PIL.Image.NEAREST).convert("RGBA"), data[2])
            elif action == 2:
                image.alpha_composite(data[0], data[1])
        self.config.write(image, "assets", "textures", self.name+".png")

