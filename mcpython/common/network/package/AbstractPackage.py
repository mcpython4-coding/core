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


class AbstractPackage:
    def __init__(self):
        self.package_id = -1  # set during send process
        self.previous_packages = []  # set only during receiving or calling answer()

    def send(self):
        pass

    def answer(self, package: "AbstractPackage"):
        assert self.package_id != -1, "package ID must be set by calling send()!"

        package.previous_packages = self.previous_packages + [self.package_id]
