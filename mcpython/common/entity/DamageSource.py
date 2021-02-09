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


class DamageSource:
    """
    Class direct representing a mc DamageSource
    Used theoretically everywhere; in mcpython, only in API definitions
    """

    def __init__(self, name: str = None):
        self.attributes = {}
        self.__attributes = set()
        self.type = name

        self.bypasses_armor = False
        self.bypasses_invulnerability = False
        self.bypasses_magic = False
        self.is_explosion = False
        self.is_fire = False
        self.is_magic = False
        self.is_projectile = False
        self.is_lighting = False

        self.target_entity = None
        self.source_entity = None

    def setAttribute(self, key, value):
        self.__attributes.add(key)
        if hasattr(self, key):
            setattr(self, key, value)
            return
        self.attributes[key] = value

    def getAttribute(self, key):
        return getattr(self, key) if hasattr(self, key) else self.attributes[key]

    def __eq__(self, other):
        for attribute in self.__attributes:
            if other.getAttribute(attribute) is None:
                continue
            if other.getAttribute(attribute) != self.getAttribute(attribute):
                return False
        return True
