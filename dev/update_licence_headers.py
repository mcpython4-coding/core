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
import os
import sys


def update_licence_headers_in_project(project_home, header):
    for root, _, files in os.walk(project_home, topdown=False):
        for file in files:
            if (
                file.endswith(".py")
                and "mods" not in root
                and not file.replace("\\", "/").endswith("mdk/tools/mod.py")
            ):
                cfile = os.path.join(root, file)
                with open(cfile) as f:
                    data = f.read()
                if not data.startswith(header):
                    if data.startswith("'''"):
                        data = header + data[data.index("'''", 3) + 3 :]
                    elif data.startswith('"""'):
                        data = header + data[data.index('"""', 3) + 3 :]
                    else:
                        data = header + "\n" + data
                with open(cfile, mode="w") as f:
                    f.write(data)


if __name__ == "__main__":
    update_licence_headers_in_project(
        os.path.dirname(os.path.dirname(__file__))
        if len(sys.argv) == 1
        else sys.argv[1],
        '''"""
mcpython - a minecraft clone written in python licenced under the MIT-licence 
(https://github.com/mcpython4-coding/core)

Contributors: uuk, xkcdjerry (inactive)

Based on the game of fogleman (https://github.com/fogleman/Minecraft), licenced under the MIT-licence
Original game "minecraft" by Mojang Studios (www.minecraft.net), licenced under the EULA
(https://account.mojang.com/documents/minecraft_eula)
Mod loader inspired by "Minecraft Forge" (https://github.com/MinecraftForge/MinecraftForge) and similar

This project is not official by mojang and does not relate to it.
"""''',
    )
