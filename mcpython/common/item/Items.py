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
import mcpython.common.factory.ItemFactory
from mcpython import shared
import random
from mcpython.util.enums import ToolType
import mcpython.common.mod.ModMcpython
import mcpython.client.gui.HoveringItemBox


def load_item():
    template = (
        mcpython.common.factory.ItemFactory.ItemFactory()
        .set_global_mod_name("minecraft")
        .set_template()
    )

    template.set_name("apple").set_food_value(4).finish()
    template.set_name("baked_potato").set_food_value(5).finish()
    template.set_name("beef").set_food_value(3).finish()
    template.set_name("beetroot").set_food_value(1).finish()
    template.set_name("beetroot_soup").set_food_value(6).set_max_stack_size(1).finish()
    template.set_name("blaze_powder").finish()
    template.set_name("blaze_rod").set_fuel_level(120).finish()
    template.set_name("bone").finish()
    template.set_name("bone_meal").finish()
    template.set_name("book").finish()
    template.set_name("bow").finish()
    template.set_name("bowl").set_fuel_level(5).set_max_stack_size(8).finish()
    template.set_name("bread").set_food_value(5).finish()
    template.set_name("brick").finish()
    template.set_name("broken_elytra").set_max_stack_size(1).finish()
    template.set_name("bucket").set_max_stack_size(16).finish()
    template.set_name("carrot").set_food_value(3).finish()
    template.set_name("charcoal").set_fuel_level(80).finish()
    template.set_name("chicken").set_food_value(2).finish()
    template.set_name("chorus_fruit").finish()
    template.set_name("clay_ball").finish()
    template.set_name("coal").set_fuel_level(80).finish()
    template.set_name("cod").set_food_value(2).finish()
    template.set_name("cod_bucket").set_max_stack_size(1).finish()
    template.set_name("cooked_beef").set_food_value(8).finish()
    template.set_name("cooked_chicken").set_food_value(6).finish()
    template.set_name("cooked_cod").set_food_value(5).finish()
    template.set_name("cooked_mutton").set_food_value(6).finish()
    template.set_name("cooked_porkchop").set_food_value(8).finish()
    template.set_name("cooked_rabbit").set_food_value(5).finish()
    template.set_name("cooked_salmon").set_food_value(6).finish()
    template.set_name("cookie").set_food_value(2).finish()
    template.set_name("diamond").finish()
    template.set_name("dried_kelp").set_food_value(1).finish()
    template.set_name("dragon_breath").set_max_stack_size(1).finish()
    template.set_name("egg").set_max_stack_size(16).finish()
    template.set_name("elytra").set_max_stack_size(1).finish()
    template.set_name("emerald").finish()
    template.set_name("ender_pearl").set_max_stack_size(16).finish()
    template.set_name("ender_eye").set_max_stack_size(16).finish()

    def lambda_add_random_xp():
        shared.world.get_active_player().add_xp(random.randint(3, 11))
        return True

    template.set_name("experience_bottle").set_eat_callback(lambda_add_random_xp).set_food_value(0).finish()
    template.set_name("feather").finish()
    template.set_name("fermented_spider_eye").finish()
    template.set_name("filled_map").set_max_stack_size(1).finish()
    template.set_name("fire_charge").finish()
    template.set_name("firework_rocket").finish()
    template.set_name("firework_star").finish()
    template.set_name("flint").finish()
    template.set_name("flint_and_steel").set_max_stack_size(1).set_durability(64).finish()
    template.set_name("ghast_tear").finish()
    template.set_name("glass_bottle").set_max_stack_size(16).finish()
    template.set_name("glistering_melon_slice").finish()
    template.set_name("glowstone_dust").finish()
    template.set_name("gold_ingot").finish()
    template.set_name("gold_nugget").finish()
    template.set_name("golden_apple").set_food_value(4).finish()
    template.set_name("golden_carrot").set_food_value(6).finish()
    template.set_name("gunpowder").finish()
    template.set_name("honey_bottle").set_max_stack_size(16).finish()
    template.set_name("honeycomb").finish()
    template.set_name("ink_sac").finish()
    template.set_name("iron_ingot").finish()
    template.set_name("iron_nugget").finish()
    template.set_name("lapis_lazuli").finish()
    template.set_name("lead").finish()
    template.set_name("leather").finish()
    template.set_name("lingering_potion").finish()
    template.set_name("magma_cream").finish()
    template.set_name("map").finish()
    template.set_name("melon_slice").set_food_value(2).finish()
    template.set_name("milk_bucket").set_max_stack_size(1).finish()
    template.set_name("mushroom_stew").set_food_value(6).set_max_stack_size(1).finish()
    template.set_name("mutton").set_food_value(2).finish()
    template.set_name("name_tag").finish()
    template.set_name("nautilus_shell").finish()
    template.set_name("nether_brick").finish()
    template.set_name("nether_star").finish()
    template.set_name("nether_wart").finish()
    template.set_name("netherite_ingot").finish()
    template.set_name("netherite_scrap").finish()
    template.set_name("painting").finish()
    template.set_name("paper").finish()
    template.set_name("phantom_membrane").finish()
    template.set_name("poisonous_potato").set_food_value(2).finish()
    template.set_name("porkchop").set_food_value(3).finish()
    template.set_name("potato").set_food_value(1).finish()
    template.set_name("prismarine_shard").finish()
    template.set_name("pufferfish").set_food_value(1).finish()
    template.set_name("pufferfish_bucket").finish()
    template.set_name("pumpkin_pie").set_food_value(8).finish()
    template.set_name("quartz").finish()
    template.set_name("rabbit").set_food_value(3).finish()
    template.set_name("rabbit_foot").finish()
    template.set_name("rabbit_hide").finish()
    template.set_name("rabbit_stew").set_food_value(10).set_max_stack_size(1).finish()
    template.set_name("redstone").finish()  # todo: binding to block
    template.set_name("rotten_flesh").set_food_value(4).finish()
    template.set_name("saddle").set_max_stack_size(1).finish()
    template.set_name("salmon").finish()
    template.set_name("salmon_bucket").set_max_stack_size(1).finish()
    template.set_name("scute").finish()
    template.set_name("shulker_shell").finish()
    template.set_name("slime_ball").finish()
    template.set_name("stick").set_fuel_level(5).finish()
    template.set_name("string").finish()
    template.set_name("sugar").finish()
    template.set_name("spider_eye").set_food_value(2).finish()
    template.set_name("totem_of_undying").set_max_stack_size(1).finish()
    template.set_name("tropical_fish").set_food_value(1).finish()
    template.set_name("water_bucket").set_max_stack_size(1).finish()
    template.set_name("wheat").finish()

    # tools

    template.set_name("shears").set_tool_type([ToolType.SHEAR]).set_tool_break_multi(5)
    for tool_type, tool_name in [
        (ToolType.PICKAXE, "pickaxe"),
        (ToolType.AXE, "axe"),
        (ToolType.SWORD, "sword"),
        (ToolType.HOE, "hoe"),
        (ToolType.SHOVEL, "shovel"),
    ]:
        template.set_name("wooden_{}".format(tool_name)).set_tool_type(
            [tool_type]
        ).set_tool_break_multi(2).set_tool_level(1).set_fuel_level(10).set_durability(
            59
        ).set_max_stack_size(
            1
        ).finish()
        template.set_name("stone_{}".format(tool_name)).set_tool_type(
            [tool_type]
        ).set_tool_break_multi(4).set_tool_level(2).set_durability(131).set_max_stack_size(1).finish()
        template.set_name("iron_{}".format(tool_name)).set_tool_type(
            [tool_type]
        ).set_tool_break_multi(6).set_tool_level(3).set_durability(250).set_max_stack_size(1).finish()
        template.set_name("golden_{}".format(tool_name)).set_tool_type(
            [tool_type]
        ).set_tool_break_multi(8).set_tool_level(4).set_durability(32).set_max_stack_size(1).finish()
        template.set_name("diamond_{}".format(tool_name)).set_tool_type(
            [tool_type]
        ).set_tool_break_multi(12).set_tool_level(5).set_durability(1561).set_max_stack_size(1).finish()
        template.set_name("netherite_{}".format(tool_name)).set_tool_type(
            [tool_type]
        ).set_tool_break_multi(14).set_tool_level(6).set_durability(2031).set_max_stack_size(1).finish()

    for color in mcpython.util.enums.COLORS:
        template.set_name("{}_dye".format(color)).finish()

    # armor

    template.set_name("golden_helmet").set_armor_points(2).set_durability(77).set_max_stack_size(1).finish()
    template.set_name("golden_chestplate").set_armor_points(5).set_durability(112).set_max_stack_size(
        1
    ).finish()
    template.set_name("golden_leggings").set_armor_points(3).set_durability(105).set_max_stack_size(1).finish()
    template.set_name("golden_boots").set_armor_points(1).set_durability(91).set_max_stack_size(1).finish()

    template.set_name("chainmail_helmet").set_armor_points(2).set_durability(165).set_max_stack_size(
        1
    ).finish()
    template.set_name("chainmail_chestplate").set_armor_points(5).set_durability(
        240
    ).set_max_stack_size(1).finish()
    template.set_name("chainmail_leggings").set_armor_points(4).set_durability(
        225
    ).set_max_stack_size(1).finish()
    template.set_name("chainmail_boots").set_armor_points(1).set_durability(195).set_max_stack_size(1).finish()

    template.set_name("iron_helmet").set_armor_points(2).set_durability(165).set_max_stack_size(1).finish()
    template.set_name("iron_chestplate").set_armor_points(6).set_durability(240).set_max_stack_size(1).finish()
    template.set_name("iron_leggings").set_armor_points(5).set_durability(225).set_max_stack_size(1).finish()
    template.set_name("iron_boots").set_armor_points(2).set_durability(195).set_max_stack_size(1).finish()

    template.set_name("diamond_helmet").set_armor_points(3).set_durability(363).set_max_stack_size(1).finish()
    template.set_name("diamond_chestplate").set_armor_points(8).set_durability(
        528
    ).set_max_stack_size(1).finish()
    template.set_name("diamond_leggings").set_armor_points(6).set_durability(495).set_max_stack_size(
        1
    ).finish()
    template.set_name("diamond_boots").set_armor_points(3).set_durability(429).set_max_stack_size(1).finish()

    template.set_name("netherite_boots").set_armor_points(3).set_durability(407).set_max_stack_size(1).finish()
    template.set_name("netherite_chestplate").set_armor_points(8).set_durability(
        592
    ).set_max_stack_size(1).finish()
    template.set_name("netherite_helmet").set_armor_points(6).set_durability(555).set_max_stack_size(
        1
    ).finish()
    template.set_name("netherite_leggings").set_armor_points(3).set_durability(
        481
    ).set_max_stack_size(1).finish()

    template.set_name("arrow").finish()

    template.set_name("barrier").set_has_block_flag(True).set_tool_tip_renderer(
        mcpython.client.gui.HoveringItemBox.DEFAULT_BLOCK_ITEM_TOOLTIP
    ).finish()


mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
    "stage:item:factory_usage", load_item, info="generating items"
)
