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
from mcpython import shared


class TagTargetHolder:
    def __init__(self, name: str):
        self.name = name
        self.classes = []

        if not shared.IS_TEST_ENV:
            import mcpython.common.data.serializer.tags.TagGroup

            mcpython.common.data.serializer.tags.TagGroup.TagGroup.TAG_HOLDERS.setdefault(
                name, []
            ).append(
                self
            )

    def register_class(self, cls):
        self.classes.append(cls)
        return cls

    def update(self, group):
        # print(self.classes)
        for cls in self.classes:
            cls.TAGS = group.get_tags_for(cls.NAME)
