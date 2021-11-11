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
import importlib

from mcpython import shared
from mcpython.engine import logger
from mcpython.server.command.Builder import (
    AnyString,
    Command,
    CommandNode,
    DefinedString,
    Item,
)

data = (
    # todo
    Command("data")
    .than(
        CommandNode(DefinedString("shuffle"))
        .of_name("shuffle")
        .info("shuffles the internal data links for fun; only for fun")
        .on_execution(
            lambda env, d: shared.event_handler.call("minecraft:data:shuffle:all")
        )
    )
    .than(
        CommandNode(DefinedString("view"))
        # todo: add tags, loot tables, helper command for /data view recipe resulting <item>
        #  and /data view recipe using <item>
        .than(
            CommandNode(DefinedString("recipe"), execute_on_client=True)
            .of_name("recipe")
            .than(
                CommandNode(DefinedString("output"))
                .of_name("output")
                .than(
                    CommandNode(Item())
                    .of_name("output item type")
                    .info("displays all recipes outputting said item")
                    .on_execution(
                        lambda env, d: shared.crafting_handler.show_to_player_from_output(d[4].NAME)
                    )
                )
            )
            .than(
                CommandNode(DefinedString("using"))
                .of_name("using")
                .than(
                    CommandNode(Item())
                    .of_name("item to use")
                    .info("displays all recipes using the given item")
                    .on_execution(
                        lambda env, d: shared.crafting_handler.show_to_player_from_input(d[4].NAME)
                    )
                )
            )
            .than(
                CommandNode(AnyString.INSTANCE)
                .of_name("recipe name")
                .info("creates a view for the given recipe")
                .on_execution(
                    lambda env, d: shared.crafting_handler.show_to_player(d[3])
                )
            )
        ).than(
            # todo: a real in-game view with scrollbar, and custom injection point for rendering,
            #   e.g. items with item texture, blocks with BlockItem, ...
            CommandNode(DefinedString("registry"), execute_on_client=True)
            .of_name("registry")
            .than(
                CommandNode(DefinedString("list"))
                .of_name("list")
                .info("lists all registry names")
                .on_execution(
                    lambda env, d: logger.println("Arrival registries:")
                    == [
                        logger.println(
                            f"- {name}: {len(registry.entries)} arrival entries"
                        )
                        for name, registry in shared.registry.registries.items()
                    ]
                )
            )
            .than(
                CommandNode(AnyString.INSTANCE)
                .of_name("registry")
                .info("views the content of a registry")
                .on_execution(lambda env, d: shared.registry.print_content(d[3]))
                .than(
                    CommandNode(AnyString.INSTANCE)
                    .of_name("namespace")
                    .info("views the content of a registry filtered by namespace")
                    .on_execution(
                        lambda env, d: shared.registry.print_content(d[3], d[4])
                    )
                )
            )
        )
    )
    .than(
        CommandNode(DefinedString("creative"))
        .of_name("creative")
        .than(
            # client-executed
            CommandNode(DefinedString("missing"), execute_on_client=True)
            .of_name("missing")
            .info("prints all missing items in creative tabs")
            .on_execution(
                lambda env, d: importlib.import_module(
                    "mcpython.client.gui.InventoryCreativeTab"
                ).CT_MANAGER.print_missing()
            )
        )
    )
)
