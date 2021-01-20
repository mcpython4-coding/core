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
        .setGlobalModName("minecraft")
        .setTemplate()
    )

    template("apple").setFoodValue(4).finish()
    template("baked_potato").setFoodValue(5).finish()
    template("beef").setFoodValue(3).finish()
    template("beetroot").setFoodValue(1).finish()
    template("beetroot_soup").setFoodValue(6).setMaxStackSize(1).finish()
    template("blaze_powder").finish()
    template("blaze_rod").setFuelLevel(120).finish()
    template("bone").finish()
    template("bone_meal").finish()
    template("book").finish()
    template("bow").finish()
    template("bowl").setFuelLevel(5).setMaxStackSize(8).finish()
    template("bread").setFoodValue(5).finish()
    template("brick").finish()
    template("broken_elytra").setMaxStackSize(1).finish()
    template("bucket").setMaxStackSize(16).finish()
    template("carrot").setFoodValue(3).finish()
    template("charcoal").setFuelLevel(80).finish()
    template("chicken").setFoodValue(2).finish()
    template("chorus_fruit").finish()
    template("clay_ball").finish()
    template("coal").setFuelLevel(80).finish()
    template("cod").setFoodValue(2).finish()
    template("cod_bucket").setMaxStackSize(1).finish()
    template("cooked_beef").setFoodValue(8).finish()
    template("cooked_chicken").setFoodValue(6).finish()
    template("cooked_cod").setFoodValue(5).finish()
    template("cooked_mutton").setFoodValue(6).finish()
    template("cooked_porkchop").setFoodValue(8).finish()
    template("cooked_rabbit").setFoodValue(5).finish()
    template("cooked_salmon").setFoodValue(6).finish()
    template("cookie").setFoodValue(2).finish()
    template("diamond").finish()
    template("dried_kelp").setFoodValue(1).finish()
    template("dragon_breath").setMaxStackSize(1).finish()
    template("egg").setMaxStackSize(16).finish()
    template("elytra").setMaxStackSize(1).finish()
    template("emerald").finish()
    template("ender_pearl").setMaxStackSize(16).finish()
    template("ender_eye").setMaxStackSize(16).finish()

    def lambda_add_random_xp():
        shared.world.get_active_player().add_xp(random.randint(3, 11))
        return True

    template("experience_bottle").setEatCallback(lambda_add_random_xp).setFoodValue(0).finish()
    template("feather").finish()
    template("fermented_spider_eye").finish()
    template("filled_map").setMaxStackSize(1).finish()
    template("fire_charge").finish()
    template("firework_rocket").finish()
    template("firework_star").finish()
    template("flint").finish()
    template("flint_and_steel").setMaxStackSize(1).set_durability(64).finish()
    template("ghast_tear").finish()
    template("glass_bottle").setMaxStackSize(16).finish()
    template("glistering_melon_slice").finish()
    template("glowstone_dust").finish()
    template("gold_ingot").finish()
    template("gold_nugget").finish()
    template("golden_apple").setFoodValue(4).finish()
    template("golden_carrot").setFoodValue(6).finish()
    template("gunpowder").finish()
    template("honey_bottle").setMaxStackSize(16).finish()
    template("honeycomb").finish()
    template("ink_sac").finish()
    template("iron_ingot").finish()
    template("iron_nugget").finish()
    template("lapis_lazuli").finish()
    template("lead").finish()
    template("leather").finish()
    template("lingering_potion").finish()
    template("magma_cream").finish()
    template("map").finish()
    template("melon_slice").setFoodValue(2).finish()
    template("milk_bucket").setMaxStackSize(1).finish()
    template("mushroom_stew").setFoodValue(6).setMaxStackSize(1).finish()
    template("mutton").setFoodValue(2).finish()
    template("name_tag").finish()
    template("nautilus_shell").finish()
    template("nether_brick").finish()
    template("nether_star").finish()
    template("nether_wart").finish()
    template("netherite_ingot").finish()
    template("netherite_scrap").finish()
    template("painting").finish()
    template("paper").finish()
    template("phantom_membrane").finish()
    template("poisonous_potato").setFoodValue(2).finish()
    template("porkchop").setFoodValue(3).finish()
    template("potato").setFoodValue(1).finish()
    template("prismarine_shard").finish()
    template("pufferfish").setFoodValue(1).finish()
    template("pufferfish_bucket").finish()
    template("pumpkin_pie").setFoodValue(8).finish()
    template("quartz").finish()
    template("rabbit").setFoodValue(3).finish()
    template("rabbit_foot").finish()
    template("rabbit_hide").finish()
    template("rabbit_stew").setFoodValue(10).setMaxStackSize(1).finish()
    template("redstone").finish()  # todo: binding to block
    template("rotten_flesh").setFoodValue(4).finish()
    template("saddle").setMaxStackSize(1).finish()
    template("salmon").finish()
    template("salmon_bucket").setMaxStackSize(1).finish()
    template("scute").finish()
    template("shulker_shell").finish()
    template("slime_ball").finish()
    template("stick").setFuelLevel(5).finish()
    template("string").finish()
    template("sugar").finish()
    template("spider_eye").setFoodValue(2).finish()
    template("totem_of_undying").setMaxStackSize(1).finish()
    template("tropical_fish").setFoodValue(1).finish()
    template("water_bucket").setMaxStackSize(1).finish()
    template("wheat").finish()

    # tools

    template("shears").setToolType([ToolType.SHEAR]).setToolBrakeMulti(5)
    for tool_type, tool_name in [
        (ToolType.PICKAXE, "pickaxe"),
        (ToolType.AXE, "axe"),
        (ToolType.SWORD, "sword"),
        (ToolType.HOE, "hoe"),
        (ToolType.SHOVEL, "shovel"),
    ]:
        template("wooden_{}".format(tool_name)).setToolType(
            [tool_type]
        ).setToolBrakeMulti(2).setToolLevel(1).setFuelLevel(10).set_durability(
            59
        ).setMaxStackSize(
            1
        ).finish()
        template("stone_{}".format(tool_name)).setToolType(
            [tool_type]
        ).setToolBrakeMulti(4).setToolLevel(2).set_durability(131).setMaxStackSize(1).finish()
        template("iron_{}".format(tool_name)).setToolType(
            [tool_type]
        ).setToolBrakeMulti(6).setToolLevel(3).set_durability(250).setMaxStackSize(1).finish()
        template("golden_{}".format(tool_name)).setToolType(
            [tool_type]
        ).setToolBrakeMulti(8).setToolLevel(4).set_durability(32).setMaxStackSize(1).finish()
        template("diamond_{}".format(tool_name)).setToolType(
            [tool_type]
        ).setToolBrakeMulti(12).setToolLevel(5).set_durability(1561).setMaxStackSize(1).finish()
        template("netherite_{}".format(tool_name)).setToolType(
            [tool_type]
        ).setToolBrakeMulti(14).setToolLevel(6).set_durability(2031).setMaxStackSize(1).finish()

    for color in mcpython.util.enums.COLORS:
        template("{}_dye".format(color)).finish()

    # armor

    template("golden_helmet").setArmorPoints(2).set_durability(77).setMaxStackSize(1).finish()
    template("golden_chestplate").setArmorPoints(5).set_durability(112).setMaxStackSize(
        1
    ).finish()
    template("golden_leggings").setArmorPoints(3).set_durability(105).setMaxStackSize(1).finish()
    template("golden_boots").setArmorPoints(1).set_durability(91).setMaxStackSize(1).finish()

    template("chainmail_helmet").setArmorPoints(2).set_durability(165).setMaxStackSize(
        1
    ).finish()
    template("chainmail_chestplate").setArmorPoints(5).set_durability(
        240
    ).setMaxStackSize(1).finish()
    template("chainmail_leggings").setArmorPoints(4).set_durability(
        225
    ).setMaxStackSize(1).finish()
    template("chainmail_boots").setArmorPoints(1).set_durability(195).setMaxStackSize(1).finish()

    template("iron_helmet").setArmorPoints(2).set_durability(165).setMaxStackSize(1).finish()
    template("iron_chestplate").setArmorPoints(6).set_durability(240).setMaxStackSize(1).finish()
    template("iron_leggings").setArmorPoints(5).set_durability(225).setMaxStackSize(1).finish()
    template("iron_boots").setArmorPoints(2).set_durability(195).setMaxStackSize(1).finish()

    template("diamond_helmet").setArmorPoints(3).set_durability(363).setMaxStackSize(1).finish()
    template("diamond_chestplate").setArmorPoints(8).set_durability(
        528
    ).setMaxStackSize(1).finish()
    template("diamond_leggings").setArmorPoints(6).set_durability(495).setMaxStackSize(
        1
    ).finish()
    template("diamond_boots").setArmorPoints(3).set_durability(429).setMaxStackSize(1).finish()

    template("netherite_boots").setArmorPoints(3).set_durability(407).setMaxStackSize(1).finish()
    template("netherite_chestplate").setArmorPoints(8).set_durability(
        592
    ).setMaxStackSize(1).finish()
    template("netherite_helmet").setArmorPoints(6).set_durability(555).setMaxStackSize(
        1
    ).finish()
    template("netherite_leggings").setArmorPoints(3).set_durability(
        481
    ).setMaxStackSize(1).finish()

    template("arrow").finish()

    template("barrier").setHasBlockFlag(True).setToolTipRenderer(
        mcpython.client.gui.HoveringItemBox.DEFAULT_BLOCK_ITEM_TOOLTIP
    ).finish()


mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
    "stage:item:factory_usage", load_item, info="generating items"
)
