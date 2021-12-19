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
import random

import mcpython.client.gui.HoveringItemBox
import mcpython.common.mod.ModMcpython
from mcpython import shared
from mcpython.common.factory.ItemFactory import ItemFactory
from mcpython.util.enums import ToolType


async def load_item():
    ItemFactory().set_name("minecraft:apple").set_food_value(4).finish()
    ItemFactory().set_name("minecraft:baked_potato").set_food_value(5).finish()
    ItemFactory().set_name("minecraft:beef").set_food_value(3).finish()
    ItemFactory().set_name("minecraft:beetroot").set_food_value(1).finish()
    ItemFactory().set_name("minecraft:beetroot_soup").set_food_value(
        6
    ).set_max_stack_size(1).finish()
    ItemFactory().set_name("minecraft:blaze_powder").finish()
    ItemFactory().set_name("minecraft:blaze_rod").set_fuel_level(120).finish()
    ItemFactory().set_name("minecraft:bone").finish()
    ItemFactory().set_name("minecraft:bone_meal").finish()
    ItemFactory().set_name("minecraft:book").finish()
    ItemFactory().set_name("minecraft:bow").finish()
    ItemFactory().set_name("minecraft:bowl").set_fuel_level(5).set_max_stack_size(
        8
    ).finish()
    ItemFactory().set_name("minecraft:bread").set_food_value(5).finish()
    ItemFactory().set_name("minecraft:brick").finish()
    ItemFactory().set_name("minecraft:broken_elytra").set_max_stack_size(1).finish()
    ItemFactory().set_name("minecraft:carrot").set_food_value(3).finish()
    ItemFactory().set_name("minecraft:charcoal").set_fuel_level(80).finish()
    ItemFactory().set_name("minecraft:chicken").set_food_value(2).finish()
    ItemFactory().set_name("minecraft:chorus_fruit").finish()
    ItemFactory().set_name("minecraft:clay_ball").finish()
    ItemFactory().set_name("minecraft:coal").set_fuel_level(80).finish()
    ItemFactory().set_name("minecraft:cod").set_food_value(2).finish()
    ItemFactory().set_name("minecraft:cod_bucket").set_max_stack_size(1).finish()
    ItemFactory().set_name("minecraft:cooked_beef").set_food_value(8).finish()
    ItemFactory().set_name("minecraft:cooked_chicken").set_food_value(6).finish()
    ItemFactory().set_name("minecraft:cooked_cod").set_food_value(5).finish()
    ItemFactory().set_name("minecraft:cooked_mutton").set_food_value(6).finish()
    ItemFactory().set_name("minecraft:cooked_porkchop").set_food_value(8).finish()
    ItemFactory().set_name("minecraft:cooked_rabbit").set_food_value(5).finish()
    ItemFactory().set_name("minecraft:cooked_salmon").set_food_value(6).finish()
    ItemFactory().set_name("minecraft:cookie").set_food_value(2).finish()
    ItemFactory().set_name("minecraft:diamond").finish()
    ItemFactory().set_name("minecraft:dried_kelp").set_food_value(1).finish()
    ItemFactory().set_name("minecraft:dragon_breath").set_max_stack_size(1).finish()
    ItemFactory().set_name("minecraft:egg").set_max_stack_size(16).finish()
    ItemFactory().set_name("minecraft:elytra").set_max_stack_size(1).finish()
    ItemFactory().set_name("minecraft:emerald").finish()
    ItemFactory().set_name("minecraft:ender_pearl").set_max_stack_size(16).finish()
    ItemFactory().set_name("minecraft:ender_eye").set_max_stack_size(16).finish()

    def lambda_add_random_xp(instance, itemstack):
        asyncio.get_event_loop().run_until_complete(
            shared.world.get_active_player().add_xp(random.randint(3, 11))
        )
        itemstack.add_amount(-1)
        return True

    ItemFactory().set_name("minecraft:experience_bottle").set_eat_callback(
        lambda_add_random_xp
    ).set_food_value(0).finish()
    ItemFactory().set_name("minecraft:feather").finish()
    ItemFactory().set_name("minecraft:fermented_spider_eye").finish()
    ItemFactory().set_name("minecraft:filled_map").set_max_stack_size(1).finish()
    ItemFactory().set_name("minecraft:fire_charge").finish()
    ItemFactory().set_name("minecraft:firework_rocket").finish()
    ItemFactory().set_name("minecraft:firework_star").finish()
    ItemFactory().set_name("minecraft:flint").finish()
    ItemFactory().set_name("minecraft:flint_and_steel").set_max_stack_size(
        1
    ).set_durability(64).finish()
    ItemFactory().set_name("minecraft:ghast_tear").finish()
    ItemFactory().set_name("minecraft:glass_bottle").set_max_stack_size(16).finish()
    ItemFactory().set_name("minecraft:glistering_melon_slice").finish()
    ItemFactory().set_name("minecraft:glowstone_dust").finish()
    ItemFactory().set_name("minecraft:gold_ingot").finish()
    ItemFactory().set_name("minecraft:gold_nugget").finish()
    ItemFactory().set_name("minecraft:golden_apple").set_food_value(4).finish()
    ItemFactory().set_name("minecraft:golden_carrot").set_food_value(6).finish()
    ItemFactory().set_name("minecraft:gunpowder").finish()
    ItemFactory().set_name("minecraft:honey_bottle").set_max_stack_size(16).finish()
    ItemFactory().set_name("minecraft:honeycomb").finish()
    ItemFactory().set_name("minecraft:ink_sac").finish()
    ItemFactory().set_name("minecraft:iron_ingot").finish()
    ItemFactory().set_name("minecraft:iron_nugget").finish()
    ItemFactory().set_name("minecraft:lapis_lazuli").finish()
    ItemFactory().set_name("minecraft:lead").finish()
    ItemFactory().set_name("minecraft:leather").finish()
    ItemFactory().set_name("minecraft:lingering_potion").finish()
    ItemFactory().set_name("minecraft:magma_cream").finish()
    ItemFactory().set_name("minecraft:map").finish()
    ItemFactory().set_name("minecraft:melon_slice").set_food_value(2).finish()
    ItemFactory().set_name("minecraft:milk_bucket").set_max_stack_size(1).finish()
    ItemFactory().set_name("minecraft:mushroom_stew").set_food_value(
        6
    ).set_max_stack_size(1).finish()
    ItemFactory().set_name("minecraft:mutton").set_food_value(2).finish()
    ItemFactory().set_name("minecraft:name_tag").finish()
    ItemFactory().set_name("minecraft:nautilus_shell").finish()
    ItemFactory().set_name("minecraft:nether_brick").finish()
    ItemFactory().set_name("minecraft:nether_star").finish()
    ItemFactory().set_name("minecraft:nether_wart").finish()
    ItemFactory().set_name("minecraft:netherite_ingot").finish()
    ItemFactory().set_name("minecraft:netherite_scrap").finish()
    ItemFactory().set_name("minecraft:painting").finish()
    ItemFactory().set_name("minecraft:paper").finish()
    ItemFactory().set_name("minecraft:phantom_membrane").finish()
    ItemFactory().set_name("minecraft:poisonous_potato").set_food_value(2).finish()
    ItemFactory().set_name("minecraft:porkchop").set_food_value(3).finish()
    ItemFactory().set_name("minecraft:potato").set_food_value(1).finish()
    ItemFactory().set_name("minecraft:prismarine_shard").finish()
    ItemFactory().set_name("minecraft:pufferfish").set_food_value(1).finish()
    ItemFactory().set_name("minecraft:pufferfish_bucket").finish()
    ItemFactory().set_name("minecraft:pumpkin_pie").set_food_value(8).finish()
    ItemFactory().set_name("minecraft:quartz").finish()
    ItemFactory().set_name("minecraft:rabbit").set_food_value(3).finish()
    ItemFactory().set_name("minecraft:rabbit_foot").finish()
    ItemFactory().set_name("minecraft:rabbit_hide").finish()
    ItemFactory().set_name("minecraft:rabbit_stew").set_food_value(
        10
    ).set_max_stack_size(1).finish()
    ItemFactory().set_name("minecraft:redstone").finish()  # todo: binding to block
    ItemFactory().set_name("minecraft:rotten_flesh").set_food_value(4).finish()
    ItemFactory().set_name("minecraft:saddle").set_max_stack_size(1).finish()
    ItemFactory().set_name("minecraft:salmon").finish()
    ItemFactory().set_name("minecraft:salmon_bucket").set_max_stack_size(1).finish()
    ItemFactory().set_name("minecraft:scute").finish()
    ItemFactory().set_name("minecraft:shulker_shell").finish()
    ItemFactory().set_name("minecraft:slime_ball").finish()
    ItemFactory().set_name("minecraft:stick").set_fuel_level(5).finish()
    ItemFactory().set_name("minecraft:string").finish()
    ItemFactory().set_name("minecraft:sugar").finish()
    ItemFactory().set_name("minecraft:spider_eye").set_food_value(2).finish()
    ItemFactory().set_name("minecraft:totem_of_undying").set_max_stack_size(1).finish()
    ItemFactory().set_name("minecraft:tropical_fish").set_food_value(1).finish()
    ItemFactory().set_name("minecraft:wheat").finish()

    # tools

    ItemFactory().set_name("minecraft:shears").set_tool_type(
        [ToolType.SHEAR]
    ).set_tool_break_multi(5)
    for tool_type, tool_name in [
        (ToolType.PICKAXE, "pickaxe"),
        (ToolType.AXE, "axe"),
        (ToolType.SWORD, "sword"),
        (ToolType.HOE, "hoe"),
        (ToolType.SHOVEL, "shovel"),
    ]:
        ItemFactory().set_name("minecraft:wooden_{}".format(tool_name)).set_tool_type(
            [tool_type]
        ).set_tool_break_multi(2).set_tool_level(1).set_fuel_level(10).set_durability(
            59
        ).set_max_stack_size(
            1
        ).finish()
        ItemFactory().set_name("minecraft:stone_{}".format(tool_name)).set_tool_type(
            [tool_type]
        ).set_tool_break_multi(4).set_tool_level(2).set_durability(
            131
        ).set_max_stack_size(
            1
        ).finish()
        ItemFactory().set_name("minecraft:iron_{}".format(tool_name)).set_tool_type(
            [tool_type]
        ).set_tool_break_multi(6).set_tool_level(3).set_durability(
            250
        ).set_max_stack_size(
            1
        ).finish()
        ItemFactory().set_name("minecraft:golden_{}".format(tool_name)).set_tool_type(
            [tool_type]
        ).set_tool_break_multi(8).set_tool_level(4).set_durability(
            32
        ).set_max_stack_size(
            1
        ).finish()
        ItemFactory().set_name("minecraft:diamond_{}".format(tool_name)).set_tool_type(
            [tool_type]
        ).set_tool_break_multi(12).set_tool_level(5).set_durability(
            1561
        ).set_max_stack_size(
            1
        ).finish()
        ItemFactory().set_name(
            "minecraft:netherite_{}".format(tool_name)
        ).set_tool_type([tool_type]).set_tool_break_multi(14).set_tool_level(
            6
        ).set_durability(
            2031
        ).set_max_stack_size(
            1
        ).finish()

    for color in mcpython.util.enums.COLORS:
        ItemFactory().set_name("minecraft:{}_dye".format(color)).finish()

    # armor

    ItemFactory().set_name("minecraft:golden_helmet").set_armor_points(
        2
    ).set_durability(77).set_max_stack_size(1).finish()
    ItemFactory().set_name("minecraft:golden_chestplate").set_armor_points(
        5
    ).set_durability(112).set_max_stack_size(1).finish()
    ItemFactory().set_name("minecraft:golden_leggings").set_armor_points(
        3
    ).set_durability(105).set_max_stack_size(1).finish()
    ItemFactory().set_name("minecraft:golden_boots").set_armor_points(1).set_durability(
        91
    ).set_max_stack_size(1).finish()

    ItemFactory().set_name("minecraft:chainmail_helmet").set_armor_points(
        2
    ).set_durability(165).set_max_stack_size(1).finish()
    ItemFactory().set_name("minecraft:chainmail_chestplate").set_armor_points(
        5
    ).set_durability(240).set_max_stack_size(1).finish()
    ItemFactory().set_name("minecraft:chainmail_leggings").set_armor_points(
        4
    ).set_durability(225).set_max_stack_size(1).finish()
    ItemFactory().set_name("minecraft:chainmail_boots").set_armor_points(
        1
    ).set_durability(195).set_max_stack_size(1).finish()

    ItemFactory().set_name("minecraft:iron_helmet").set_armor_points(2).set_durability(
        165
    ).set_max_stack_size(1).finish()
    ItemFactory().set_name("minecraft:iron_chestplate").set_armor_points(
        6
    ).set_durability(240).set_max_stack_size(1).finish()
    ItemFactory().set_name("minecraft:iron_leggings").set_armor_points(
        5
    ).set_durability(225).set_max_stack_size(1).finish()
    ItemFactory().set_name("minecraft:iron_boots").set_armor_points(2).set_durability(
        195
    ).set_max_stack_size(1).finish()

    ItemFactory().set_name("minecraft:diamond_helmet").set_armor_points(
        3
    ).set_durability(363).set_max_stack_size(1).finish()
    ItemFactory().set_name("minecraft:diamond_chestplate").set_armor_points(
        8
    ).set_durability(528).set_max_stack_size(1).finish()
    ItemFactory().set_name("minecraft:diamond_leggings").set_armor_points(
        6
    ).set_durability(495).set_max_stack_size(1).finish()
    ItemFactory().set_name("minecraft:diamond_boots").set_armor_points(
        3
    ).set_durability(429).set_max_stack_size(1).finish()

    ItemFactory().set_name("minecraft:netherite_boots").set_armor_points(
        3
    ).set_durability(407).set_max_stack_size(1).finish()
    ItemFactory().set_name("minecraft:netherite_chestplate").set_armor_points(
        8
    ).set_durability(592).set_max_stack_size(1).finish()
    ItemFactory().set_name("minecraft:netherite_helmet").set_armor_points(
        6
    ).set_durability(555).set_max_stack_size(1).finish()
    ItemFactory().set_name("minecraft:netherite_leggings").set_armor_points(
        3
    ).set_durability(481).set_max_stack_size(1).finish()

    ItemFactory().set_name("minecraft:arrow").finish()

    ItemFactory().set_name("minecraft:barrier").set_has_block_flag(
        True
    ).set_tool_tip_renderer(
        mcpython.client.gui.HoveringItemBox.DEFAULT_BLOCK_ITEM_TOOLTIP
    ).finish()


mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
    "stage:item:factory_usage", load_item(), info="generating items"
)
