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
from mcpython.engine import logger
from mcpython.engine.network.AbstractPackage import AbstractPackage
from mcpython.engine.network.util import ReadBuffer, WriteBuffer


class RegistrySyncInitPackage(AbstractPackage):
    PACKAGE_NAME = "minecraft:registry_sync_init"

    def __init__(self):
        super().__init__()
        self.registries = []

    def setup(self):
        for registry_name, instance in shared.registry.registries.items():
            if instance.sync_via_network:
                self.registries.append(registry_name)
        return self

    def read_from_buffer(self, buffer: ReadBuffer):
        self.registries = buffer.read_list(lambda: buffer.read_string())

    def write_to_buffer(self, buffer: WriteBuffer):
        buffer.write_list(self.registries, lambda e: buffer.write_string(e))

    def handle_inner(self):
        for name in self.registries:
            registry = shared.registry.get_by_name(name)

            if registry is None:
                logger.println(
                    f"[REGISTRY][SYNC] skipping registry {name} as it is not arrival on server"
                )
                continue

            package = (
                registry.registry_sync_package_class or RegistrySyncPackage
            )().setup(name)
            self.answer(package)


class RegistrySyncPackage(AbstractPackage):
    PACKAGE_NAME = "minecraft:registry_sync_content"

    def __init__(self):
        super().__init__()
        self.content = []
        self.name = None

    def setup(self, name: str):
        self.name = name

        for entry in shared.registry.get_by_name(name).entries.values():
            self.content.append(
                (entry.NAME, entry.INFO if entry.INFO is not None else "")
            )

        return self

    def read_from_buffer(self, buffer: ReadBuffer):
        self.name = buffer.read_string()
        self.content = buffer.read_list(
            lambda: (buffer.read_string(), buffer.read_string())
        )

    def write_to_buffer(self, buffer: WriteBuffer):
        buffer.write_string(self.name)
        buffer.write_list(
            self.content, lambda e: buffer.write_string(e[0]).write_string(e[1])
        )

    def handle_inner(self):
        entries_there = set(self.content)
        entries_here = set(
            (entry.NAME, entry.INFO if entry.INFO is not None else "")
            for entry in shared.registry.get_by_name(self.name).entries.values()
        )

        if entries_here.symmetric_difference(entries_there):
            logger.write_into_container(
                [
                    f"{e[0]} ({e[1]})" if e[1] != "" else e[0]
                    for e in entries_there.difference(entries_here)
                ],
                [
                    f"{e[0]} ({e[1]})" if e[1] != "" else e[0]
                    for e in entries_here.difference(entries_there)
                ],
                header=f"registry mismatches in registry {self.name} (first missing on client, second missing on server)",
            )

            from .DisconnectionPackage import DisconnectionInitPackage

            self.answer(DisconnectionInitPackage().set_reason("registry mismatch"))
        else:
            logger.println(
                f"[REGISTRY][SYNC] registry {self.name} seems to be equal in client & server"
            )
