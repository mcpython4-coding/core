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
    """
    Sync init package send during the Server2ClientHandshake-handle
    Send client -> server
    """

    PACKAGE_NAME = "minecraft:registry_sync_init"

    def __init__(self):
        super().__init__()
        self.registries = []

    async def setup(self):
        for registry_name, instance in shared.registry.registries.items():
            if instance.sync_via_network:
                self.registries.append(registry_name)

        await shared.event_handler.call_async("minecraft:network:registry_sync:setup", self)

        return self

    async def read_from_buffer(self, buffer: ReadBuffer):
        self.registries = [e async for e in buffer.read_list(buffer.read_string)]

    async def write_to_buffer(self, buffer: WriteBuffer):
        await buffer.write_list(self.registries, buffer.write_string)

    async def handle_inner(self):
        shared.NETWORK_MANAGER.client_profiles[self.sender_id]["registry_sync"] = {
            e: -1 for e in self.registries
        }

        await shared.event_handler.call_async(
            "minecraft:network:registry_sync:init", self
        )

        for name in self.registries:
            registry = shared.registry.get_by_name(name)

            if registry is None:
                logger.println(
                    f"[REGISTRY][SYNC] skipping registry {name} as it is not arrival on server"
                )
                continue

            package = await (
                registry.registry_sync_package_class or RegistrySyncPackage
            )().setup(name)
            await self.answer(package)


class RegistrySyncPackage(AbstractPackage):
    """
    Package send server -> client as a response on the RegistrySyncInitPackage
    Send for each requested registry
    """

    PACKAGE_NAME = "minecraft:registry_sync_content"

    def __init__(self):
        super().__init__()
        self.content = []
        self.name = None

    async def setup(self, name: str):
        self.name = name

        for entry in shared.registry.get_by_name(name).entries.values():
            self.content.append(
                (entry.NAME, entry.INFO if entry.INFO is not None else "")
            )

        await shared.event_handler.call_async("minecraft:network:registry_sync:setup", self)

        return self

    async def read_from_buffer(self, buffer: ReadBuffer):
        self.name = buffer.read_string()
        self.content = [e async for e in buffer.read_list(
            lambda: (buffer.read_string(), buffer.read_string())
        )]

    async def write_to_buffer(self, buffer: WriteBuffer):
        buffer.write_string(self.name)
        await buffer.write_list(
            self.content, lambda e: buffer.write_string(e[0]).write_string(e[1])
        )

    async def handle_inner(self):
        entries_there = set(self.content)
        entries_here = set(
            (entry.NAME, entry.INFO if entry.INFO is not None else "")
            for entry in shared.registry.get_by_name(self.name).entries.values()
        )

        await shared.event_handler.call_async(
            "minecraft:network:registry_sync:data_recv",
            self,
            entries_here,
            entries_there,
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

            await self.answer(RegistrySyncResultPackage().setup(self.name, False))
            if not shared.event_handler.call_cancelable(
                "minecraft:network:registry_sync:fail",
                self,
                entries_here,
                entries_there,
            ):
                return

        logger.println(
            f"[REGISTRY][SYNC] registry {self.name} seems to be equal in client & server"
        )
        await self.answer(RegistrySyncResultPackage().setup(self.name, True))


class RegistrySyncResultPackage(AbstractPackage):
    PACKAGE_NAME = "minecraft:registry_sync_status"
    CAN_GET_ANSWER = True

    def __init__(self):
        super().__init__()
        self.name = ""
        self.status = False

    def setup(self, name: str, status: bool):
        self.name = name
        self.status = status
        return self

    async def write_to_buffer(self, buffer: WriteBuffer):
        buffer.write_string(self.name)
        buffer.write_bool(self.status)

    async def read_from_buffer(self, buffer: ReadBuffer):
        self.name = buffer.read_string()
        self.status = buffer.read_bool()

    async def handle_inner(self):
        from .DisconnectionPackage import DisconnectionInitPackage

        if shared.IS_CLIENT:
            if self.status:
                logger.println(
                    "[NETWORK][INFO] registry compare results are back from server, everything fine"
                )
                if await shared.event_handler.call_cancelable_async(
                    "minecraft:network:registry_sync:success", self
                ):
                    logger.println("[NETWORK][INFO] requesting world now...")
                    from .WorldDataExchangePackage import DataRequestPackage

                    async def handle(*_):
                        logger.println(
                            "[NETWORK][WORLD] world data received successful, handing over to user..."
                        )
                        await shared.state_handler.change_state("minecraft:game")
                        shared.world.get_active_player().teleport((0, 100, 0))
                        shared.world.get_active_dimension().get_chunk(
                            0, 0
                        ).update_visible()

                    package = (
                        DataRequestPackage().request_player_info().request_world_info()
                    )
                    shared.NETWORK_MANAGER.register_answer_handler(package, handle)
                    await self.answer(package)

                    return

            else:
                logger.println("[NETWORK][WARN] registry sync FAILED on server side")
                await shared.event_handler.call_async(
                    "minecraft:network:registry_sync:fail", self
                )

            await self.answer(
                DisconnectionInitPackage().set_reason("registry sync fatal")
            )
            return

        shared.NETWORK_MANAGER.client_profiles[self.sender_id]["registry_sync"][
            self.name
        ] = int(self.status)

        if (
            -1
            not in shared.NETWORK_MANAGER.client_profiles[self.sender_id][
                "registry_sync"
            ].values()
        ):
            if (
                0
                in shared.NETWORK_MANAGER.client_profiles[self.sender_id][
                    "registry_sync"
                ].values()
            ):
                await self.answer(
                    DisconnectionInitPackage().set_reason("registry miss-matches")
                )
            else:
                await self.answer(RegistrySyncResultPackage().setup("all", True))
