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
from mcpython.server.command.Builder import (
    Command,
    CommandNode,
    IntPosition,
    DefinedString,
)
from mcpython import shared, logger


def block_info(env, position):
    if position is None:
        return

    block = env.get_dimension().get_block(position)

    if block is None:
        env.chat.print_ln("block is None")
        return

    if type(block) == str:
        env.chat.print_ln(f"invalid target; not generated at {position}")
    else:
        env.chat.print_ln(repr(block))
        env.chat.print_ln(", ".join(block.TAGS))


def print_item_info(itemstack, text: str):
    logger.println(text)

    logger.println("- amount: {}".format(itemstack.amount))
    logger.println("- item name: '{}'".format(itemstack.get_item_name()))
    if itemstack.item:
        logger.println("- has block: {}".format(itemstack.item.HAS_BLOCK))
        if itemstack.item.HAS_BLOCK:
            logger.println("- blockname: {}".format(itemstack.item.get_block()))
        logger.println(
            "- item file: '{}'".format(itemstack.item.get_default_item_image_location())
        )
        logger.println("- max stack size: {}".format(itemstack.item.STACK_SIZE))
        tags = []
        for tag in shared.tag_handler.taggroups["items"].tags.values():
            if itemstack.item.NAME in tag.entries:
                tags.append(tag.name)
        logger.println("- tags: {}".format(tags))


info = (
    Command("info").than(
        CommandNode(DefinedString("block"))
        .of_name("block")
        .than(
            CommandNode(IntPosition())
            .of_name("position")
            .on_execution(lambda env, data: block_info(env, data[2]))
            .info("Gives information about the given block")
        )
        .on_execution(
            lambda env, data: block_info(
                env,
                env.get_dimension()
                .get_world()
                .hit_test(
                    env.get_this().get_position(), shared.window.get_sight_vector()
                )[0],
            )
        )
        .info("Gives information about the block looking at")
    )
    # todo: block inventory
    .than(
        CommandNode(DefinedString("item"))
        .of_name("item")
        .than(
            CommandNode(DefinedString("hand"))
            .of_name("hand")
            .info("gets information about the held item")
            .on_execution(
                lambda env, data: print_item_info(
                    env.get_this().get_active_inventory_slot().get_itemstack(),
                    "held item",
                )
            )
        )
        .than(
            CommandNode(DefinedString("inventory"))
            .of_name("inventory")
            .info("prints information about each slot of the inventory")
            .on_execution(
                lambda env, data: [
                    [
                        print_item_info(slot.get_itemstack(), f"slot {ii}:{i}")
                        for i, slot in enumerate(inventory.slots)
                    ]
                    for ii, inventory in enumerate(env.get_this().get_inventories())
                ]
            )
        )
    )
)
