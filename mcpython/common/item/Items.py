"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import mcpython.common.factory.ItemFactory
from mcpython import shared as G
import random
from mcpython.util.enums import ToolType
import mcpython.common.mod.ModMcpython
import mcpython.client.gui.HoveringItemBox


def load_item():
    template = (
        mcpython.common.factory.ItemFactory.ItemFactory()
        .setGlobalModName("minecraft")
        .setTemplate(True)
    )

    template("apple").setFoodValue(4)
    template("baked_potato").setFoodValue(5)
    template("beef").setFoodValue(3)
    template("beetroot").setFoodValue(1)
    template("beetroot_soup").setFoodValue(6).setMaxStackSize(1)
    template("blaze_powder")
    template("blaze_rod").setFuelLevel(120)
    template("bone")
    template("bone_meal")
    template("book")
    template("bow")
    template("bowl").setFuelLevel(5).setMaxStackSize(8)
    template("bread").setFoodValue(5)
    template("brick")
    template("broken_elytra").setMaxStackSize(1)
    template("bucket").setMaxStackSize(16)
    template("carrot").setFoodValue(3)
    template("charcoal").setFuelLevel(80)
    template("chicken").setFoodValue(2)
    template("chorus_fruit")
    template("clay_ball")
    template("coal").setFuelLevel(80)
    template("cod").setFoodValue(2)
    template("cod_bucket").setMaxStackSize(1)
    template("cooked_beef").setFoodValue(8)
    template("cooked_chicken").setFoodValue(6)
    template("cooked_cod").setFoodValue(5)
    template("cooked_mutton").setFoodValue(6)
    template("cooked_porkchop").setFoodValue(8)
    template("cooked_rabbit").setFoodValue(5)
    template("cooked_salmon").setFoodValue(6)
    template("cookie").setFoodValue(2)
    template("diamond")
    template("dried_kelp").setFoodValue(1)
    template("dragon_breath").setMaxStackSize(1)
    template("egg").setMaxStackSize(16)
    template("elytra").setMaxStackSize(1)
    template("emerald")
    template("ender_pearl").setMaxStackSize(16)
    template("ender_eye").setMaxStackSize(16)

    def lambda_add_random_xp():
        G.world.get_active_player().add_xp(random.randint(3, 11))
        return True

    template("experience_bottle").setEatCallback(lambda_add_random_xp).setFoodValue(0)
    template("feather")
    template("fermented_spider_eye")
    template("filled_map").setMaxStackSize(1)
    template("fire_charge")
    template("firework_rocket")
    template("firework_star")
    template("flint")
    template("flint_and_steel").setMaxStackSize(1).set_durability(64)
    template("ghast_tear")
    template("glass_bottle").setMaxStackSize(16)
    template("glistering_melon_slice")
    template("glowstone_dust")
    template("gold_ingot")
    template("gold_nugget")
    template("golden_apple").setFoodValue(4)
    template("golden_carrot").setFoodValue(6)
    template("gunpowder")
    template("honey_bottle").setMaxStackSize(16)
    template("honeycomb")
    template("ink_sac")
    template("iron_ingot")
    template("iron_nugget")
    template("lapis_lazuli")
    template("lead")
    template("leather")
    template("lingering_potion")
    template("magma_cream")
    template("map")
    template("melon_slice").setFoodValue(2)
    template("milk_bucket").setMaxStackSize(1)
    template("mushroom_stew").setFoodValue(6).setMaxStackSize(1)
    template("mutton").setFoodValue(2)
    template("name_tag")
    template("nautilus_shell")
    template("nether_brick")
    template("nether_star")
    template("nether_wart")
    template("netherite_ingot")
    template("netherite_scrap")
    template("painting")
    template("paper")
    template("phantom_membrane")
    template("poisonous_potato").setFoodValue(2)
    template("porkchop").setFoodValue(3)
    template("potato").setFoodValue(1)
    template("prismarine_shard")
    template("pufferfish").setFoodValue(1)
    template("pufferfish_bucket")
    template("pumpkin_pie").setFoodValue(8)
    template("quartz")
    template("rabbit").setFoodValue(3)
    template("rabbit_foot")
    template("rabbit_hide")
    template("rabbit_stew").setFoodValue(10).setMaxStackSize(1)
    template("redstone")  # todo: binding to block
    template("rotten_flesh").setFoodValue(4)
    template("saddle").setMaxStackSize(1)
    template("salmon")
    template("salmon_bucket").setMaxStackSize(1)
    template("scute")
    template("shulker_shell")
    template("slime_ball")
    template("stick").setFuelLevel(5)
    template("string")
    template("sugar")
    template("spider_eye").setFoodValue(2)
    template("totem_of_undying").setMaxStackSize(1)
    template("tropical_fish").setFoodValue(1)
    template("water_bucket").setMaxStackSize(1)
    template("wheat")

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
        )
        template("stone_{}".format(tool_name)).setToolType(
            [tool_type]
        ).setToolBrakeMulti(4).setToolLevel(2).set_durability(131).setMaxStackSize(1)
        template("iron_{}".format(tool_name)).setToolType(
            [tool_type]
        ).setToolBrakeMulti(6).setToolLevel(3).set_durability(250).setMaxStackSize(1)
        template("golden_{}".format(tool_name)).setToolType(
            [tool_type]
        ).setToolBrakeMulti(8).setToolLevel(4).set_durability(32).setMaxStackSize(1)
        template("diamond_{}".format(tool_name)).setToolType(
            [tool_type]
        ).setToolBrakeMulti(12).setToolLevel(5).set_durability(1561).setMaxStackSize(1)
        template("netherite_{}".format(tool_name)).setToolType(
            [tool_type]
        ).setToolBrakeMulti(14).setToolLevel(6).set_durability(2031).setMaxStackSize(1)

    for color in mcpython.util.enums.COLORS:
        template("{}_dye".format(color))

    # armor

    template("golden_helmet").setArmorPoints(2).set_durability(77).setMaxStackSize(1)
    template("golden_chestplate").setArmorPoints(5).set_durability(112).setMaxStackSize(
        1
    )
    template("golden_leggings").setArmorPoints(3).set_durability(105).setMaxStackSize(1)
    template("golden_boots").setArmorPoints(1).set_durability(91).setMaxStackSize(1)

    template("chainmail_helmet").setArmorPoints(2).set_durability(165).setMaxStackSize(
        1
    )
    template("chainmail_chestplate").setArmorPoints(5).set_durability(
        240
    ).setMaxStackSize(1)
    template("chainmail_leggings").setArmorPoints(4).set_durability(
        225
    ).setMaxStackSize(1)
    template("chainmail_boots").setArmorPoints(1).set_durability(195).setMaxStackSize(1)

    template("iron_helmet").setArmorPoints(2).set_durability(165).setMaxStackSize(1)
    template("iron_chestplate").setArmorPoints(6).set_durability(240).setMaxStackSize(1)
    template("iron_leggings").setArmorPoints(5).set_durability(225).setMaxStackSize(1)
    template("iron_boots").setArmorPoints(2).set_durability(195).setMaxStackSize(1)

    template("diamond_helmet").setArmorPoints(3).set_durability(363).setMaxStackSize(1)
    template("diamond_chestplate").setArmorPoints(8).set_durability(
        528
    ).setMaxStackSize(1)
    template("diamond_leggings").setArmorPoints(6).set_durability(495).setMaxStackSize(
        1
    )
    template("diamond_boots").setArmorPoints(3).set_durability(429).setMaxStackSize(1)

    template("netherite_boots").setArmorPoints(3).set_durability(407).setMaxStackSize(1)
    template("netherite_chestplate").setArmorPoints(8).set_durability(
        592
    ).setMaxStackSize(1)
    template("netherite_helmet").setArmorPoints(6).set_durability(555).setMaxStackSize(
        1
    )
    template("netherite_leggings").setArmorPoints(3).set_durability(
        481
    ).setMaxStackSize(1)

    template("arrow")

    template("barrier").setHasBlockFlag(True).setToolTipRenderer(
        mcpython.client.gui.HoveringItemBox.DEFAULT_BLOCK_ITEM_TOOLTIP
    )

    template.finish()


mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
    "stage:item:factory_usage", load_item, info="generating items"
)
