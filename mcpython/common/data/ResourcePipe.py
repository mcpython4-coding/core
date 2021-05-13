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
import gc
import typing

import mcpython.client.rendering.entities.EntityRenderer
import mcpython.client.rendering.util
import mcpython.common.config
import mcpython.common.DataPacks
from mcpython import shared


def recipe_mapper(modname, pathname):
    import mcpython.common.container.crafting.CraftingManager

    shared.mod_loader.mods[modname].eventbus.subscribe(
        "stage:recipes",
        shared.crafting_handler.load,
        pathname,
        info="loading crafting recipes for mod {}".format(modname),
    )


def model_mapper(modname, pathname):
    from mcpython.client.rendering.model.BlockState import BlockStateDefinition

    shared.mod_loader.mods[modname].eventbus.subscribe(
        "stage:model:model_search",
        shared.model_handler.add_from_mod,
        pathname,
        info="searching for block models for mod {}".format(modname),
    )

    shared.mod_loader.mods[modname].eventbus.subscribe(
        "stage:model:blockstate_search",
        BlockStateDefinition.from_directory,
        "assets/{}/blockstates".format(pathname),
        modname,
        info="searching for block states for mod {}".format(modname),
    )


def model_bake():
    shared.model_handler.build(immediate=True)


def tag_mapper(modname, pathname):
    import mcpython.common.data.tags.TagHandler

    shared.mod_loader.mods[modname].eventbus.subscribe(
        "stage:tag:group",
        lambda: mcpython.common.data.tags.TagHandler.add_from_location(pathname),
        info="adding tag groups for mod {}".format(modname),
    )


def language_mapper(modname, pathname):
    import mcpython.common.Language

    mcpython.common.Language.from_mod_name(modname)


def loot_table_mapper(modname, pathname):
    from mcpython.common.data.loot import (LootTable, LootTableCondition,
                                           LootTableFunction)

    shared.mod_loader.mods[modname].eventbus.subscribe(
        "stage:loottables:load",
        lambda: LootTable.handler.for_mod_name(modname, pathname),
        info="adding loot tables for mod {}".format(modname),
    )


class ResourcePipeHandler:
    def __init__(self):
        self.namespaces: typing.List[typing.Tuple[str, str]] = []
        self.mappers: typing.List[typing.Callable[[str, str], None]] = []
        self.reload_handlers = []
        self.bake_handlers = []
        self.data_processors = []

    def register_for_mod(self, providing_mod: str, namespace: str = None):
        """
        Used internally to add new namespaces to the loading system
        """
        if namespace is None:
            namespace = providing_mod
        self.namespaces.append((providing_mod, namespace))
        for mapper in self.mappers:
            mapper(providing_mod, namespace)

    def register_mapper(
        self, mapper: typing.Callable[[str, str], None], on_dedicated_server=True
    ):
        """
        To use in "stage:resources:pipe:add_mapper"
        """
        if not on_dedicated_server and not shared.IS_CLIENT:
            return

        self.mappers.append(mapper)

        for name, pathname in self.namespaces:
            mapper(name, pathname)

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

    def reload_content(self):
        shared.window.print_profiler()  # print the profilers

        if not shared.event_handler.call_cancelable("data:reload:cancel"):
            return

        mcpython.common.DataPacks.datapack_handler.reload()  # reloads all data packs
        shared.tag_handler.reload()  # reloads all tags
        shared.crafting_handler.reload_crafting_recipes()  # reloads all recipes

        import mcpython.common.data.loot.LootTable as LootTable

        LootTable.handler.reload()

        # as we are reloading, this may get mixed up...
        shared.crafting_handler.recipe_relink_table.clear()
        shared.loot_table_handler.relink_table.clear()
        shared.event_handler.call("data:shuffle:clear")

        if mcpython.common.config.SHUFFLE_DATA:  # .. and we need to re-do if needed
            shared.event_handler.call("data:shuffle:all")

        shared.inventory_handler.reload_config()  # reloads inventory configuration
        shared.model_handler.reload_models()
        mcpython.client.rendering.util.setup()
        # todo: regenerate block item images, regenerate item atlases

        # reload entity model files
        [
            e.reload()
            for e in mcpython.client.rendering.entities.EntityRenderer.RENDERERS
        ]

        for function in self.reload_handlers:
            function()

        for function in self.bake_handlers:
            function()

        shared.event_handler.call("data:reload:work")

        gc.collect()  # make sure that memory was cleaned up
        shared.window.print_profiler()  # and now print the profile's (if needed)

        for function in self.data_processors:
            function()


handler = ResourcePipeHandler()
handler.register_mapper(recipe_mapper)
handler.register_mapper(model_mapper, on_dedicated_server=False)
handler.register_mapper(tag_mapper)
handler.register_mapper(language_mapper)
handler.register_mapper(loot_table_mapper)

if shared.IS_CLIENT:
    handler.bake_handlers += [model_bake]


def load():
    from mcpython.common.data.worldgen import (Biome, WorldGenerationMode,
                                               WorldGenerationModeModifier)
