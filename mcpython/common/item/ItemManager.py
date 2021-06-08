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
import json
import os

import mcpython.client.gui.HoveringItemBox
import mcpython.common.data.tags.TagTargetHolder
import mcpython.common.event.Registry
import mcpython.common.factory.ItemFactory
import mcpython.ResourceLoader
from mcpython import logger, shared

COLLECTED_ITEMS = []
tag_holder = mcpython.common.data.tags.TagTargetHolder.TagTargetHolder("items")


if shared.IS_CLIENT and not shared.IS_TEST_ENV:
    import mcpython.common.item.ItemTextureAtlas

    ITEM_ATLAS = mcpython.common.item.ItemTextureAtlas.ItemAtlasHandler()
else:
    ITEM_ATLAS = None


def build():
    ITEM_ATLAS.build()
    ITEM_ATLAS.dump()
    for cls in COLLECTED_ITEMS:
        for i, file in enumerate(cls.get_used_texture_files()):
            items.item_index_table[cls.NAME][file] = ITEM_ATLAS.get_texture_info_or_add(
                cls.NAME + "#?" + str(i), file
            )


def load_data():
    if not shared.invalidate_cache and os.path.exists(
        shared.build + "/item_block_factory.json"
    ):
        with open(shared.build + "/item_block_factory.json") as f:
            data = json.load(f)
        builder = logger.TableBuilder(
            header=[
                "MCPYTHON REGISTRY CHANGE - Following BlockItemTextures",
                "are obsolete as this blocks are missing.",
                "They are removed from the system",
            ]
        )
        for entry in data[:]:
            name = entry[0]
            table = shared.registry.get_by_name("minecraft:block").entries
            if name in table:
                obj = (
                    mcpython.common.factory.ItemFactory.ItemFactory()
                    .set_name(name)
                    .set_has_block_flag(True)
                    .set_default_item_file(entry[1])
                    .set_tool_tip_renderer(
                        mcpython.client.gui.HoveringItemBox.DEFAULT_BLOCK_ITEM_TOOLTIP
                    )
                )
                block = shared.registry.get_by_name("minecraft:block")[name]
                block.modify_block_item(obj)
                obj.finish()

                if shared.IS_CLIENT:
                    import mcpython.client.rendering.model.ItemModel as ItemModel

                    model = ItemModel.ItemModel(name)
                    model.addTextureLayer(0, entry[1])
                    ItemModel.handler.models[name] = model
            else:
                builder.println("-'{}'".format(entry))
                data.remove(entry)
        builder.finish()
        with open(shared.build + "/item_block_factory.json", mode="w") as f:
            json.dump(data, f)


def register_item(registry, cls):
    tag_holder.register_class(cls)
    if cls.NAME in items.item_index_table:
        return
    items.item_index_table.setdefault(cls.NAME, {})

    if shared.IS_CLIENT:
        for i, file in enumerate(cls.get_used_texture_files()):
            ITEM_ATLAS.add_file("{}#{}".format(cls.NAME, i), file)

    COLLECTED_ITEMS.append(cls)


items = mcpython.common.event.Registry.Registry(
    "minecraft:item",
    ["minecraft:item"],
    "stage:item:load",
    injection_function=register_item,
)
items.item_index_table = {}


def load_items():
    pass


if not shared.IS_TEST_ENV:
    import mcpython.common.mod.ModMcpython

    mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
        "stage:block:overwrite", load_data, info="loading prepared item data"
    )
    mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
        "stage:item:load", load_items, info="loading items"
    )

    import mcpython.common.item.Items
