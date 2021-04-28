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
import api.annotation


WRAPPER = None


@api.annotation.TestSetting(100).no_result()
def run():
    """
    Test for the LaunchWrapper constructor
    :return:
    """

    global WRAPPER

    import mcpython.LaunchWrapper

    WRAPPER = mcpython.LaunchWrapper.LaunchWrapper()
    assert WRAPPER.is_client is True, "client should be default"


@api.annotation.TestSetting(99).no_result()
def prepare_client():
    WRAPPER.prepare_client()
