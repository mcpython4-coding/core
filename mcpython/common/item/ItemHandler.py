"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft, representing snapshot 20w51a
(https://www.minecraft.net/en-us/article/minecraft-snapshot-20w51a)

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared, logger
import mcpython.ResourceLoader
import mcpython.common.event.Registry
import mcpython.client.texture.TextureAtlas
import mcpython.common.item.ItemAtlas
import json
import os
import mcpython.common.factory.ItemFactory
import mcpython.common.mod.ModMcpython
import mcpython.client.gui.HoveringItemBox
import mcpython.client.rendering.model.ItemModel
import mcpython.common.data.tags.TagGroup


COLLECTED_ITEMS = []
tag_holder = mcpython.common.data.tags.TagGroup.TagTargetHolder("items")

ITEM_ATLAS = mcpython.common.item.ItemAtlas.ItemAtlasHandler()


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
                    .setName(name)
                    .setHasBlockFlag(True)
                    .setDefaultItemFile(entry[1])
                    .setToolTipRenderer(
                        mcpython.client.gui.HoveringItemBox.DEFAULT_BLOCK_ITEM_TOOLTIP
                    )
                )
                # block = blocktable[name]
                # block.modify_block_item(obj)
                obj.finish()
                model = mcpython.client.rendering.model.ItemModel.ItemModel(name)
                model.addTextureLayer(0, entry[1])
                mcpython.client.rendering.model.ItemModel.handler.models[name] = model
            else:
                builder.println("-'{}'".format(entry))
                data.remove(entry)
        builder.finish()
        with open(shared.build + "/item_block_factory.json", mode="w") as f:
            json.dump(data, f)


def register_item(registry, cls):
    tag_holder.register_class(cls)
    items.entries[cls.NAME.split(":")[-1]] = cls
    if cls.NAME in items.item_index_table:
        return
    items.item_index_table.setdefault(cls.NAME, {})
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


mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
    "stage:block:overwrite", load_data, info="loading prepared item data"
)
mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
    "stage:item:load", load_items, info="loading items"
)

import mcpython.common.item.Items
