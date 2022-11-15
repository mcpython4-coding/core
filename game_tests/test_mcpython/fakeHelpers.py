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


class FakeInventoryHandler:
    SHOWN = False

    @classmethod
    async def add(cls, inventory):
        return

    @classmethod
    async def show(cls, inventory):
        cls.SHOWN = True


class FakeCraftingHandler:
    def __call__(self, *args, **kwargs):
        return args[0]


class FakeWorld:
    entities = set()
    dimension = None
    position = (0, 0)

    @classmethod
    def get_dimension_by_name(cls, name: str):
        return cls

    @classmethod
    def get_chunk_for_position(cls, position):
        return cls

    @classmethod
    def exposed_faces(cls, position):
        return {}

    @classmethod
    def exposed_faces_list(cls, position):
        return [False] * 6

    @classmethod
    def exposed_faces_flag(cls, block):
        return 0

    @classmethod
    def mark_position_dirty(cls, position):
        pass

    @classmethod
    def get_active_dimension(cls):
        return cls

    @classmethod
    def get_name(cls):
        return "overworld"

    @classmethod
    def get_dimension(cls):
        return cls

    @classmethod
    def get_dimension_id(cls):
        return 0


FakeWorld.dimension = FakeWorld