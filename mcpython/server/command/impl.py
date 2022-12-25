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
from mcpython.engine import ResourceLoader


async def print_block_missing():
    block_registry = shared.registry.get_by_name("minecraft:block")

    print("The following blocks are missing an implementation:")

    for modname in sorted(shared.mod_loader.mods.keys()):
        path = f"assets/{modname}/blockstates/"
        for block in sorted(list(await ResourceLoader.get_all_entries(path))):
            name = modname + ":" + block.removeprefix(path).removesuffix(".json")
            if name not in block_registry:
                print("-", name)

    print("[END OF LIST]")


async def print_item_missing():
    item_registry = shared.registry.get_by_name("minecraft:item")

    print("The following items are missing an implementation:")

    for modname in sorted(shared.mod_loader.mods.keys()):
        path = f"assets/{modname}/models/item/"
        for item in sorted(list(await ResourceLoader.get_all_entries(path))):
            name = modname + ":" + item.removeprefix(path).removesuffix(".json")
            if name not in item_registry:
                print("-", name)

    print("[END OF LIST]")
