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
import itertools
import string

INVOKED = 0


def test_for_invoke():
    global INVOKED
    INVOKED += 1


async def test_for_invoke_async():
    global INVOKED
    INVOKED += 1


def create_big_function():
    chars = "abcdefghijklmnopqrstuvwxyz"

    names = itertools.product(chars, chars)
    func_code = "\n    ".join(f"{''.join(name)}_ = 0" for name in names)

    code = f"""
def test():
    {func_code}"""

    scope = {}

    exec(code, globals(), scope)
    return scope["test"]
