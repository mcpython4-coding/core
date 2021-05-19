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
from abc import ABC


class AbstractExtensionPoint(ABC):
    pass


class ModLoaderExtensionPoint(AbstractExtensionPoint):
    NAME: str = None
    ENABLE_MODS_TOML = False
    ENABLE_MOD_JSON = True

    EXTENSION_POINTS = {}, {}

    @classmethod
    def __init_subclass__(cls, **kwargs):
        if cls.ENABLE_MOD_JSON:
            cls.EXTENSION_POINTS[0][cls.NAME] = cls

        if cls.ENABLE_MODS_TOML:
            cls.EXTENSION_POINTS[1][cls.NAME] = cls

    @classmethod
    def load_mod_from_toml(cls, data):
        pass

    @classmethod
    def load_mod_from_json(cls, data):
        pass
