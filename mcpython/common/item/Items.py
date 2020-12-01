"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

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
    template("bowl").setFuelLevel(5)
    template("bread").setFoodValue(5)
    template("brick")
    template("broken_elytra")
    template("bucket")
    template("carrot").setFoodValue(3)
    template("charcoal").setFuelLevel(80)
    template("chicken").setFoodValue(2)
    template("chorus_fruit")
    template("clay_ball")
    template("coal").setFuelLevel(80)
    template("cod").setFoodValue(2)
    template("cod_bucket")
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
    template("dragon_breath")
    template("egg")
    template("elytra")
    template("emerald")
    template("ender_pearl")
    template("ender_eye")

    def lambda_add_random_xp():
        G.world.get_active_player().add_xp(random.randint(3, 11))
        return True

    template("experience_bottle").setEatCallback(lambda_add_random_xp).setFoodValue(0)
    template("feather")
    template("fermented_spider_eye")
    template("filled_map")
    template("fire_charge")
    template("firework_rocket")
    template("firework_star")
    template("flint")
    template("flint_and_steel")
    template("ghast_tear")
    template("glass_bottle")
    template("glistering_melon_slice")
    template("glowstone_dust")
    template("gold_ingot")
    template("gold_nugget")
    template("golden_apple").setFoodValue(4)
    template("golden_carrot").setFoodValue(6)
    template("gunpowder")
    template("honey_bottle")
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
    template("milk_bucket")
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
    template("saddle")
    template("salmon")
    template("salmon_bucket")
    template("scute")
    template("shulker_shell")
    template("slime_ball")
    template("stick").setFuelLevel(5)
    template("string")
    template("sugar")
    template("spider_eye").setFoodValue(2)
    template("totem_of_undying")
    template("tropical_fish").setFoodValue(1)
    template("water_bucket")
    template("wheat")

    # tools

    template("shears").setToolType([ToolType.SHEAR]).setToolBrakeMutli(5)
    for tooltype, toolname in [
        (ToolType.PICKAXE, "pickaxe"),
        (ToolType.AXE, "axe"),
        (ToolType.SWORD, "sword"),
        (ToolType.HOE, "hoe"),
        (ToolType.SHOVEL, "shovel"),
    ]:
        template("wooden_{}".format(toolname)).setToolType(
            [tooltype]
        ).setToolBrakeMutli(2).setToolLevel(1).setFuelLevel(10)
        template("stone_{}".format(toolname)).setToolType([tooltype]).setToolBrakeMutli(
            4
        ).setToolLevel(2)
        template("iron_{}".format(toolname)).setToolType([tooltype]).setToolBrakeMutli(
            6
        ).setToolLevel(3)
        template("golden_{}".format(toolname)).setToolType(
            [tooltype]
        ).setToolBrakeMutli(8).setToolLevel(4)
        template("diamond_{}".format(toolname)).setToolType(
            [tooltype]
        ).setToolBrakeMutli(12).setToolLevel(5)
        template("netherite_{}".format(toolname)).setToolType(
            [tooltype]
        ).setToolBrakeMutli(14).setToolLevel(6)

    for color in mcpython.util.enums.COLORS:
        template("{}_dye".format(color))

    # armor

    template("golden_helmet").setArmorPoints(2)
    template("golden_chestplate").setArmorPoints(5)
    template("golden_leggings").setArmorPoints(3)
    template("golden_boots").setArmorPoints(1)

    template("chainmail_helmet").setArmorPoints(2)
    template("chainmail_chestplate").setArmorPoints(5)
    template("chainmail_leggings").setArmorPoints(4)
    template("chainmail_boots").setArmorPoints(1)

    template("iron_helmet").setArmorPoints(2)
    template("iron_chestplate").setArmorPoints(6)
    template("iron_leggings").setArmorPoints(5)
    template("iron_boots").setArmorPoints(2)

    template("diamond_helmet").setArmorPoints(3)
    template("diamond_chestplate").setArmorPoints(8)
    template("diamond_leggings").setArmorPoints(6)
    template("diamond_boots").setArmorPoints(3)

    template("netherite_boots").setArmorPoints(3)
    template("netherite_chestplate").setArmorPoints(8)
    template("netherite_helmet").setArmorPoints(6)
    template("netherite_leggings").setArmorPoints(3)

    template("arrow")

    template("barrier").setHasBlockFlag(True).setToolTipRenderer(
        mcpython.client.gui.HoveringItemBox.DEFAULT_BLOCK_ITEM_TOOLTIP
    )

    template.finish()


mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
    "stage:item:factory_usage", load_item, info="generating items"
)
