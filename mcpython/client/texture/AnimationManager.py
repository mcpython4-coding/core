"""
mcpython - a minecraft clone written in python licenced under the MIT-licence 
(https://github.com/mcpython4-coding/core)

Contributors: uuk, xkcdjerry (inactive)

Based on the game of fogleman (https://github.com/fogleman/Minecraft), licenced under the MIT-licence
Original game "minecraft" by Mojang Studios (www.minecraft.net), licenced under the EULA
(https://account.mojang.com/documents/minecraft_eula)
Mod loader inspired by "Minecraft Forge" (https://github.com/MinecraftForge/MinecraftForge) and similar

This project is not official by mojang and does not relate to it.
"""
import typing

import mcpython.engine.ResourceLoader
import PIL.Image
import pyglet
from mcpython import shared
from mcpython.engine import logger
from mcpython.util.annotation import onlyInClient
from mcpython.util.texture import to_pyglet_image
from pyglet.graphics import TextureGroup


@onlyInClient()
class AnimatedTexture(TextureGroup):
    def __init__(self, hash_texture, texture, parent=None):
        super().__init__(texture, parent)
        self.hash_texture = hash_texture

    def __hash__(self):
        return hash((self.hash_texture.target, self.hash_texture.id, self.parent))

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__
            and self.hash_texture.target == other.hash_texture.target
            and self.hash_texture.id == other.hash_texture.id
            and self.parent == other.parent
        )


@onlyInClient()
class AnimationController:
    """
    Manager class for the animation group, identified by frame count and ticks needed for one frame.
    Animation controllers are shared by AnimationManager when possible.

    WARNING: This system is highly unstable currently, and may never be fully stable
    """

    def __init__(self, frames: int, timing: int):
        self.frames = frames
        self.timing = timing
        from .TextureAtlas import MISSING_TEXTURE, TextureAtlas

        self.group: typing.Optional[
            pyglet.graphics.TextureGroup
        ] = pyglet.graphics.TextureGroup(to_pyglet_image(MISSING_TEXTURE).get_texture())
        self.ticks_since_change = 0
        self.atlas_index = 0

        self.textures = [None] * frames
        self.atlases = [TextureAtlas(size=(2, 2)) for _ in range(frames)]

        self.remaining_ticks = 0

    def add_texture(self, image: PIL.Image, lookup: typing.List[int]):
        if len(lookup) != self.frames:
            raise ValueError(lookup, len(lookup), self.frames)

        if not all(isinstance(e, int) for e in lookup):
            raise ValueError(lookup, len(lookup))

        atlas = self.atlases[0]
        width = image.width

        # todo: split textures beforehand!

        pos = atlas.add_image(
            image.crop((0, lookup[0] * width, width, (lookup[0] + 1) * width))
        )

        for atlas, index in zip(self.atlases[1:], lookup[1:]):
            atlas.add_image(image.crop((0, index * width, width, (index + 1) * width)))

        return pos

    def add_textures(self, textures: typing.List[PIL.Image.Image]):
        if len(textures) != self.frames:
            raise ValueError(textures, len(textures), self.frames)

        atlas = self.atlases[0]
        pos = atlas.add_image(textures[0])

        for atlas, image in zip(self.atlases[1:], textures):
            atlas.add_image(image, pos)

        return pos

    def bake(self):
        for i, atlas in enumerate(self.atlases):
            self.textures[i] = atlas.get_pyglet_texture()
            # atlas.texture.save(shared.build+f"/atlas_{self.frames}_{self.timing}_{i}.png")

        self.group = AnimatedTexture(self.textures[0], self.textures[0])

    def tick(self, ticks: float):
        self.ticks_since_change += ticks
        swaps = int(self.ticks_since_change // self.timing)
        self.ticks_since_change %= self.timing

        self.atlas_index = int((self.atlas_index + swaps) % self.frames)
        self.group.texture = self.textures[self.atlas_index]


@onlyInClient()
class AnimationManager:
    """
    Manager for any block animations

    Handles all AnimationController's, use get_atlas_for_spec() when needing your own one.
    Use prepare_animated_texture() when wanting stuff from a texture on resources.
    Use the get_...() methods to get the needed data for animations
    """

    def __init__(self):
        self.controllers: typing.Dict[typing.Tuple[int, int], AnimationController] = {}
        self.positions: typing.List[typing.Tuple[int, int]] = []
        self.texture2controller: typing.List[AnimationController] = []
        self.texture_lookup: typing.Dict[str, int] = {}

    def prepare_animated_texture(self, location: str) -> int:
        """
        Prepares a texture for later animation; Internally loads the .mcmeta file for the image,
        and does some parsing for knowing how the animation should play
        :param location: a location to look at
        :return: the texture id, for later lookup operations
        """

        if location in self.texture_lookup:
            return self.texture_lookup[location]

        texture = mcpython.engine.ResourceLoader.read_image(location)

        if ":" in location:
            t_location = "assets/{}/textures/{}.png".format(*location.split(":"))
        elif not location.endswith(".png"):
            t_location = "assets/minecraft/textures/{}.png".format(location)
        else:
            t_location = location

        if not mcpython.engine.ResourceLoader.exists(t_location + ".mcmeta"):
            logger.println(
                "skipping animated texture @" + location + " / " + t_location
            )
            return -1

        meta: dict = mcpython.engine.ResourceLoader.read_json(t_location + ".mcmeta")[
            "animation"
        ]

        if "frames" not in meta:
            meta["frames"] = list(range(texture.height // texture.width))

        atlas = self.get_atlas_for_spec(
            len(meta["frames"]), meta.setdefault("frametime", 1)
        )
        self.positions.append(atlas.add_texture(texture, meta["frames"]))
        self.texture2controller.append(atlas)

        self.texture_lookup[location] = len(self.positions) - 1

        return len(self.positions) - 1

    def prepare_texture_series_as_animation(
        self, textures: typing.List[PIL.Image.Image], timing_per_frame: int = 1
    ) -> int:
        """
        Prepares a set of textures with some ticks in between for rendering as an animation
        :param textures: the textures to use
        :param timing_per_frame: how many ticks per frame to use
        :return: the animation id
        """
        controller = self.get_atlas_for_spec(len(textures), timing_per_frame)
        self.positions.append(controller.add_textures(textures))
        self.texture2controller.append(controller)
        return len(self.positions) - 1

    def get_atlas_for_spec(self, frames: int, timing: int) -> AnimationController:
        """
        Returns or creates the AnimationController for the given configuration
        Use prepare_texture_series_as_animation for fully registering it into the system
        """

        if (frames, timing) in self.controllers:
            return self.controllers[(frames, timing)]

        controller = AnimationController(frames, timing)
        self.controllers[(frames, timing)] = controller
        return controller

    def get_group_for_texture(self, texture: int):
        return self.texture2controller[texture].group

    def get_position_for_texture(self, texture: int):
        return self.positions[texture] if texture != -1 else (0, 0)

    def get_atlas_size_for_texture(self, texture: int):
        return self.texture2controller[texture].atlases[0].size

    def tick(self, ticks: float):
        if not shared.ENABLE_ANIMATED_TEXTURES:
            return

        for controller in self.controllers.values():
            controller.tick(ticks)

    def bake(self):
        for controller in self.controllers.values():
            controller.bake()


if shared.IS_CLIENT or typing.TYPE_CHECKING:
    animation_manager = AnimationManager()
