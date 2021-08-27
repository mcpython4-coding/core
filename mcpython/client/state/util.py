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
import psutil

from mcpython.client.state.ui import UIPartProgressBar


def update_memory_usage_bar(bar: UIPartProgressBar.UIPartProgressBar):
    # Update memory usage bar progress & text
    process = psutil.Process()
    with process.oneshot():
        bar.progress = process.memory_info().rss

    bar.text = "Memory usage: {}MB/{}MB ({}%)".format(
        bar.progress // 2 ** 20,
        bar.progress_max // 2 ** 20,
        round(bar.progress / bar.progress_max * 10000)
        / 100,
    )