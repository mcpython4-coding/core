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
import asyncio
import gc
import typing

import mcpython.client.rendering.entities.EntityRenderer
import mcpython.common.config
import mcpython.common.data.DataPacks
import mcpython.engine.rendering.util
from mcpython import shared

from .abstract import AbstractReloadListener


async def recipe_mapper(modname: str, pathname: str):
    import mcpython.common.container.crafting.CraftingManager

    shared.mod_loader.mods[modname].eventbus.subscribe(
        "stage:recipes",
        shared.crafting_handler.load(pathname),
        info="loading crafting recipes for mod {}".format(modname),
    )


async def model_mapper(modname: str, pathname: str):
    from mcpython.client.rendering.model.BlockState import BlockStateContainer

    shared.mod_loader.mods[modname].eventbus.subscribe(
        "stage:model:model_search",
        shared.model_handler.add_from_mod(pathname),
        info="searching for block models for mod {}".format(modname),
    )

    shared.mod_loader.mods[modname].eventbus.subscribe(
        "stage:model:blockstate_search",
        BlockStateContainer.from_directory("assets/{}/blockstates".format(pathname), modname),
        info="searching for block states for mod {}".format(modname),
    )


async def model_bake():
    await shared.model_handler.build(immediate=True)


async def tag_mapper(modname: str, pathname: str):
    import mcpython.common.data.serializer.tags.TagHandler

    shared.mod_loader.mods[modname].eventbus.subscribe(
        "stage:tag:group",
        mcpython.common.data.serializer.tags.TagHandler.add_from_location(
            pathname
        ),
        info="adding tag groups for mod {}".format(modname),
    )


async def language_mapper(modname: str, pathname: str):
    import mcpython.common.data.Language

    mcpython.common.data.Language.from_mod_name(modname)


async def loot_table_mapper(modname: str, pathname: str):
    from mcpython.common.data.serializer.loot import (
        LootTable,
        LootTableCondition,
        LootTableFunction,
    )

    shared.mod_loader.mods[modname].eventbus.subscribe(
        "stage:loottables:load",
        LootTable.handler.for_mod_name(modname, pathname),
        info="adding loot tables for mod {}".format(modname),
    )


class ResourcePipeHandler:
    def __init__(self):
        self.namespaces: typing.List[typing.Tuple[str, str]] = []
        self.mappers: typing.List[typing.Callable[[str, str], None]] = []
        self.reload_handlers = []
        self.bake_handlers = []
        self.data_processors = []

        self.listeners: typing.List[typing.Type[AbstractReloadListener]] = []

        shared.mod_loader("minecraft", "stage:post")(self.reload_content())

    def register_listener(self, listener: typing.Type[AbstractReloadListener]):
        self.listeners.append(listener)

        async def l():
            listener.on_reload(True)

        shared.mod_loader("minecraft", "stage:post")(l())

        return self

    async def register_for_mod(self, providing_mod: str, namespace: str = None):
        """
        Used internally to add new namespaces to the loading system
        """
        if namespace is None:
            namespace = providing_mod

        self.namespaces.append((providing_mod, namespace))

        await asyncio.gather(*filter(lambda e: e is not None, map(lambda e: e(providing_mod, namespace), self.mappers)))

    def register_mapper(
        self, mapper: typing.Callable[[str, str], None | typing.Awaitable], on_dedicated_server=True
    ):
        """
        To use in "stage:resources:pipe:add_mapper"
        """
        if not on_dedicated_server and not shared.IS_CLIENT:
            return

        self.mappers.append(mapper)

        asyncio.get_event_loop().run_until_complete(
            asyncio.gather(
                *filter(lambda e: e is not None, map(lambda e: mapper(*e), self.namespaces)))
        )

        return self

    def register_reload_listener(self, listener):
        self.reload_handlers.append(listener)
        return self

    def register_bake_listener(self, listener):
        self.bake_handlers.append(listener)
        return self

    def register_data_processor(self, listener):
        self.data_processors.append(listener)
        return self

    async def reload_content(self):
        print("starting reload cycle...")

        mcpython.common.data.DataPacks.datapack_handler.reload()  # reloads all data packs
        await shared.tag_handler.reload()  # reloads all tags
        await shared.crafting_handler.reload_crafting_recipes()  # reloads all recipes

        import mcpython.common.data.serializer.loot.LootTable as LootTable

        await LootTable.handler.reload()

        # as we are reloading, this may get mixed up...
        shared.crafting_handler.recipe_relink_table.clear()
        shared.loot_table_handler.relink_table.clear()
        await shared.event_handler.call_async("data:shuffle:clear")

        if mcpython.common.config.SHUFFLE_DATA:  # .. and we need to re-do if needed
            await shared.event_handler.call_async("minecraft:data:shuffle:all")

        if shared.IS_CLIENT:
            await shared.inventory_handler.reload_config()  # reloads inventory configuration
            await shared.model_handler.reload_models()
            mcpython.engine.rendering.util.setup()

            # todo: regenerate block item images, regenerate item atlases

        # reload entity model files
        await asyncio.gather(*[
            e.reload()
            for e in mcpython.client.rendering.entities.EntityRenderer.RENDERERS
        ])

        await asyncio.gather(*filter(lambda e: e is not None, map(lambda e: e(), self.reload_handlers)))
        await asyncio.gather(*filter(lambda e: e is not None, map(lambda e: e.on_unload(), self.listeners)))
        await asyncio.gather(*filter(lambda e: e is not None, map(lambda e: e.on_reload(), self.listeners)))
        await asyncio.gather(*filter(lambda e: e is not None, map(lambda e: e(), self.bake_handlers)))
        await asyncio.gather(*filter(lambda e: e is not None, map(lambda e: e.on_bake(), self.listeners)))

        await shared.inventory_handler.reload_config()

        await shared.event_handler.call_async("data:reload:work")

        gc.collect()  # make sure that memory was cleaned up

        await asyncio.gather(*filter(lambda e: e is not None, map(lambda e: e(), self.data_processors)))


handler = ResourcePipeHandler()
handler.register_mapper(recipe_mapper)
handler.register_mapper(model_mapper, on_dedicated_server=False)
handler.register_mapper(tag_mapper)
handler.register_mapper(language_mapper)
handler.register_mapper(loot_table_mapper)

if shared.IS_CLIENT:
    handler.bake_handlers += [model_bake]


def load():
    from mcpython.common.data.serializer.worldgen import (
        Biome,
        WorldGenerationMode,
        WorldGenerationModeModifier,
    )
