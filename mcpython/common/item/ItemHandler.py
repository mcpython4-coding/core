"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared as G, logger
import mcpython.ResourceLoader
import mcpython.common.event.Registry
import mcpython.texture.TextureAtlas
import mcpython.common.item.ItemAtlas
import json
import os
import mcpython.common.factory.ItemFactory
import mcpython.common.mod.ModMcpython
import mcpython.client.gui.HoveringItemBox
import mcpython.client.rendering.model.ItemModel


COLLECTED_ITEMS = []

ITEM_ATLAS = mcpython.common.item.ItemAtlas.ItemAtlasHandler()


def build():
    ITEM_ATLAS.build()
    ITEM_ATLAS.dump()
    for itemclass in COLLECTED_ITEMS:
        for file in itemclass.get_used_texture_files():
            items.itemindextable[itemclass.NAME][file] = ITEM_ATLAS.get_texture_info(
                file
            )


def load_data(from_block_item_generator=False):
    if not G.prebuilding and os.path.exists(G.build + "/itemblockfactory.json"):
        collected_overflow = (
            []
        )  # an list of items which we don't need anymore, so we can warn the user
        with open(G.build + "/itemblockfactory.json") as f:
            data = json.load(f)
        for entry in data[:]:
            name = entry[0]
            blocktable = G.registry.get_by_name("block").registered_object_map
            if name in blocktable:
                obj = (
                    mcpython.common.factory.ItemFactory.ItemFactory()
                    .setName(name)
                    .setHasBlockFlag(True)
                    .setDefaultItemFile(entry[1])
                    .setToolTipRenderer(
                        mcpython.client.gui.HoveringItemBox.DEFAULT_BLOCK_ITEM_TOOLTIP
                    )
                )
                block = blocktable[name]
                block.modify_block_item(obj)
                obj.finish()
                model = mcpython.client.rendering.model.ItemModel.ItemModel(name)
                model.addTextureLayer(0, entry[1])
                mcpython.client.rendering.model.ItemModel.handler.models[name] = model
            else:
                collected_overflow.append(entry)
                data.remove(entry)
        if len(collected_overflow) > 0:
            logger.write_into_container(
                ["-'{}'".format(e[0]) for e in collected_overflow],
                header=[
                    "MCPYTHON REGISTRY CHANGE - Following BlockItemTextures",
                    "are obsolete as this blocks are missing.",
                    "They are removed from the system",
                ],
            )
        with open(G.build + "/itemblockfactory.json", mode="w") as f:
            json.dump(data, f)


def add_to_image_atlas(file):
    ITEM_ATLAS.schedule_item_file(file)


def register_item(registry, itemclass):
    items.registered_object_map[itemclass.NAME.split(":")[-1]] = itemclass
    if itemclass.NAME in items.itemindextable:
        return
    items.itemindextable.setdefault(itemclass.NAME, {})
    for file in itemclass.get_used_texture_files():
        add_to_image_atlas(file)
    COLLECTED_ITEMS.append(itemclass)


items = mcpython.common.event.Registry.Registry(
    "item", ["minecraft:item"], injection_function=register_item
)
items.itemindextable = {}


def load_items():
    pass


mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
    "stage:block:overwrite", load_data, info="loading prepared item data"
)
mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
    "stage:item:load", load_items, info="loading items"
)

import mcpython.common.item.Items
