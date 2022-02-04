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


class FluidCombinationEnvironment:
    def __init__(self):
        self.temperature = 293.15  # 20°C
        self.pressure = 1  # 1 atmosphere
        self.rmp = 0  # rotations per minute by some mixer
        self.rotation_force = 10  # Newton, how much force the mixer uses
        self.rotation_direction = 0  # 0 clockwise, 1 anti-clockwise (viewed from "above")
        self.container_type = "quartz_glass"
        self.container_volume = 1  # in Liter

        self.is_broken = False
        self.is_overflown = False
        self.is_vacuumed = False

    def copy(self):
        env = type(self)()
        env.temperature = self.temperature
        env.pressure = self.pressure
        env.rmp = self.rmp
        env.rotation_force = self.rotation_force
        env.rotation_direction = self.rotation_direction
        env.container_type = self.container_type
        env.container_volume = self.container_volume

        env.is_broken = self.is_broken
        env.is_overflown = self.is_overflown
        env.is_vacuumed = self.is_vacuumed

        return env

