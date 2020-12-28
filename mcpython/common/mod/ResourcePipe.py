"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import typing
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
    import mcpython.common.data.loot.LootTable

    shared.mod_loader.mods[modname].eventbus.subscribe(
        "stage:loottables:load",
        lambda: mcpython.common.data.loot.LootTable.handler.for_mod_name(
            modname, pathname
        ),
        info="adding loot tables for mod {}".format(modname),
    )


class ResourcePipeHandler:
    def __init__(self):
        self.mods: typing.List[typing.Tuple[str, str]] = []
        self.mappers: typing.List[typing.Callable[[str, str], None]] = []

    def register_for_mod(self, modname: str, pathname: str = None):
        """
        Used internally to add new namespaces to the loading system
        """
        if pathname is None:
            pathname = modname
        self.mods.append((modname, pathname))
        for mapper in self.mappers:
            mapper(modname, pathname)

    def register_mapper(self, mapper: typing.Callable[[str, str], None]):
        """
        To use in "stage:resources:pipe:add_mapper"
        """
        self.mappers.append(mapper)

        for name, pathname in self.mods:
            mapper(name, pathname)


handler = ResourcePipeHandler()
handler.register_mapper(recipe_mapper)
handler.register_mapper(model_mapper)
handler.register_mapper(tag_mapper)
handler.register_mapper(language_mapper)
handler.register_mapper(loot_table_mapper)


def load():
    from mcpython.common.data.worldgen import (
        WorldGenerationMode, WorldGenerationModeModifier
    )
