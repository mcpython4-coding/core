"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""


class DamageSource:
    """
    Class direct representing an mc DamageSource
    """

    def __init__(self, name: str = None):
        self.attributes = {}
        self.__attributes = set()
        self.type = name
        self.bypasses_armor = None
        self.bypasses_invulnerability = None
        self.bypasses_magic = None
        self.target_entity = None
        self.source_entity = None
        self.is_explosion = None
        self.is_fire = None
        self.is_magic = None
        self.is_projectile = None
        self.is_lighting = None

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
