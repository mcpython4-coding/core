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
import typing
from mcpython import shared


class ICapabilityContainer:
    CAPABILITY_CONTAINER_NAME = None

    def __init__(self):
        self.capability_data: typing.Dict[str, typing.Any] = {}

    def get_capability_content(self, name: str):
        capability = shared.capability_manager.get_by_name(name)

        if name not in self.capability_data:
            self.write_raw_capability_data(name, capability.attach(self))

        return capability.prepareData(self, self.capability_data[name])

    def copy_capabilities(self, target: "ICapabilityContainer"):
        for name in self.capability_data.keys():
            self.copy_capability(target, name)

    def copy_capability(self, target: "ICapabilityContainer", name: str):
        capability = shared.capability_manager.get_by_name(name)
        data = self.capability_data[name]

        new_data = capability.copyOver(self, target, data)
        if new_data is None: return

        target.write_raw_capability_data(name, new_data)

    def write_raw_capability_data(self, key: str, data):
        self.capability_data[key] = data

    def read_raw_capability_data(self, key: str):
        return self.capability_data[key]

