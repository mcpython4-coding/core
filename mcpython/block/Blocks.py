"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import mcpython.factory.BlockFactory
import globals as G
from mcpython.util.enums import ToolType
import mcpython.mod.ModMcpython
from mcpython.factory import CombinedBlockFactory
import mcpython.datagen.Configuration


def remove_if_downer_block_not_solid(blockinstance):
    """
    Helper function for donwer implementation.
    Will remove THIS block when the block below is air or an not-generated block
    :param blockinstance: the block-instance to check
    """
    x, y, z = blockinstance.position
    other = G.world.get_active_dimension().get_block((x, y - 1, z))
    if other is None or type(other) == str:
        G.world.get_active_dimension().remove_block(blockinstance.position)


# todo: let this generate from java source
def load_blocks():
    full_template = mcpython.factory.BlockFactory.BlockFactory().setGlobalModName("minecraft").setTemplate()
    log_template = full_template.copy().resetTemplate().setLog().setTemplate()
    falling_template = full_template.copy().resetTemplate().setFallable().setTemplate()
    slab_template = full_template.copy().resetTemplate().setSlab().setTemplate()

    colors = mcpython.util.enums.COLORS

    # missing: air, oak, spruce, birch, jungle, acacia and dark oak saplings, water and lava, dispenser
    # note block; white, orange, magenta, light blue, yellow, lime, pink, gray, light gray, cyan, purple, blue,
    # brown, green, red and black bed; powered and detector rail, sticky piston, cobweb, grass, fern, dead bush,
    # seagrass, tall seagrass, piston, dandelion, poppy, blue orchid, allium, azure bluet, red tulip, orange tulip,
    # white tulip, pink tulip, oxeye daisy, cornflower, wither rose, lily of the valley, brown mushroom, tnt

    full_template.setName("podzol").setDefaultModelState({"snowy": "false"}).setStrenght(.5).setBestTools(
        ToolType.SHOVEL).finish()

    log_template.setName("basalt").setStrenght(1.25, 4.2).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(1).finish()
    log_template.setName("polished_basalt").setStrenght(1.25, 4.2).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()

    full_template.setName("gold_ore").setStrenght(3., 3.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(3).finish()
    full_template.setName("iron_ore").setStrenght(3., 3.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(2).finish()
    full_template.setName("coal_ore").setStrenght(3., 3.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(1).finish()
    full_template.setName("lapis_ore").setStrenght(3).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(2).finish()
    log_template.setName("ancient_debris").setBestTools(ToolType.PICKAXE).setMinimumToolLevel(5).finish()

    full_template.setName("lapis_block").setStrenght(3.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(2).finish()
    full_template.setName("gold_block").setStrenght(3., 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        3).finish()
    full_template.setName("iron_block").setStrenght(5., 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        2).finish()
    full_template.setName("netherite_block").setBestTools(ToolType.PICKAXE).setMinimumToolLevel(5).finish()

    log_template.setName("oak_log").setStrenght(2.).setBestTools(ToolType.AXE).finish()
    log_template.setName("spruce_log").setStrenght(2.).setBestTools(ToolType.AXE).finish()
    log_template.setName("birch_log").setStrenght(2.).setBestTools(ToolType.AXE).finish()
    log_template.setName("jungle_log").setStrenght(2.).setBestTools(ToolType.AXE).finish()
    log_template.setName("acacia_log").setStrenght(2.).setBestTools(ToolType.AXE).finish()
    log_template.setName("dark_oak_log").setStrenght(2.).setBestTools(ToolType.AXE).finish()
    log_template.setName("crimson_stem").setStrenght(2.).setBestTools(ToolType.AXE).finish()
    log_template.setName("warped_stem").setStrenght(2.).setBestTools(ToolType.AXE).finish()

    log_template.setName("stripped_oak_log").setStrenght(2.).setBestTools(ToolType.AXE).finish()
    log_template.setName("stripped_spruce_log").setStrenght(2.).setBestTools(ToolType.AXE).finish()
    log_template.setName("stripped_birch_log").setStrenght(2.).setBestTools(ToolType.AXE).finish()
    log_template.setName("stripped_jungle_log").setStrenght(2.).setBestTools(ToolType.AXE).finish()
    log_template.setName("stripped_acacia_log").setStrenght(2.).setBestTools(ToolType.AXE).finish()
    log_template.setName("stripped_dark_oak_log").setStrenght(2.).setBestTools(ToolType.AXE).finish()
    log_template.setName("stripped_crimson_stem").setStrenght(2.).setBestTools(ToolType.AXE).finish()
    log_template.setName("stripped_warped_stem").setStrenght(2.).setBestTools(ToolType.AXE).finish()

    log_template.setName("oak_wood").setStrenght(2.).setBestTools(ToolType.AXE).finish()
    log_template.setName("spruce_wood").setStrenght(2.).setBestTools(ToolType.AXE).finish()
    log_template.setName("birch_wood").setStrenght(2.).setBestTools(ToolType.AXE).finish()
    log_template.setName("jungle_wood").setStrenght(2.).setBestTools(ToolType.AXE).finish()
    log_template.setName("acacia_wood").setStrenght(2.).setBestTools(ToolType.AXE).finish()
    log_template.setName("dark_oak_wood").setStrenght(2.).setBestTools(ToolType.AXE).finish()
    log_template.setName("crimson_hyphae").setStrenght(2.).setBestTools(ToolType.AXE).finish()
    log_template.setName("warped_hyphae").setStrenght(2.).setBestTools(ToolType.AXE).finish()

    log_template.setName("stripped_oak_wood").setStrenght(2.).setBestTools(ToolType.AXE).finish()
    log_template.setName("stripped_spruce_wood").setStrenght(2.).setBestTools(ToolType.AXE).finish()
    log_template.setName("stripped_birch_wood").setStrenght(2.).setBestTools(ToolType.AXE).finish()
    log_template.setName("stripped_jungle_wood").setStrenght(2.).setBestTools(ToolType.AXE).finish()
    log_template.setName("stripped_acacia_wood").setStrenght(2.).setBestTools(ToolType.AXE).finish()
    log_template.setName("stripped_dark_oak_wood").setStrenght(2.).setBestTools(ToolType.AXE).finish()
    log_template.setName("stripped_crimson_hyphae").setStrenght(2.).setBestTools(ToolType.AXE).finish()
    log_template.setName("stripped_warped_hyphae").setStrenght(2.).setBestTools(ToolType.AXE).finish()

    full_template.setName("oak_leaves").setAllSideSolid(False).setStrenght(.2).enableRandomTicks().setBestTools(
        ToolType.SHEAR).finish()
    full_template.setName("spruce_leaves").setAllSideSolid(False).setStrenght(.2).enableRandomTicks().setBestTools(
        ToolType.SHEAR).finish()
    full_template.setName("birch_leaves").setAllSideSolid(False).setStrenght(.2).enableRandomTicks().setBestTools(
        ToolType.SHEAR).finish()
    full_template.setName("jungle_leaves").setAllSideSolid(False).setStrenght(.2).enableRandomTicks().setBestTools(
        ToolType.SHEAR).finish()
    full_template.setName("acacia_leaves").setAllSideSolid(False).setStrenght(.2).enableRandomTicks().setBestTools(
        ToolType.SHEAR).finish()
    full_template.setName("dark_oak_leaves").setAllSideSolid(False).setStrenght(.2).enableRandomTicks().setBestTools(
        ToolType.SHEAR).finish()

    full_template.setName("sponge").setStrenght(.6).finish()
    full_template.setName("wet_sponge").setStrenght(.6).finish()

    full_template.setName("bookshelf").setStrenght(1.5).setBestTools(ToolType.AXE).finish()

    full_template.setName("mossy_cobblestone").setStrenght(2., 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    full_template.setName("obsidian").setStrenght(50., 1200.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()

    # missing: torch, fire, spawner, oak, spruce, birch, jungle, acacia and dark oak stairs, redstone wire

    full_template.setName("diamond_ore").setStrenght(3.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(3).finish()
    full_template.setName("diamond_block").setStrenght(5., 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        3).finish()

    # missing: wheat, farmland; oak, spruce, birch, jungle, acacia and dark oak signs & doors & pressure plates, ladder,
    # rail, lever, stone pressure plate

    full_template.setName("redstone_ore").setStrenght(3.).setBestTools(
        ToolType.PICKAXE).setMinimumToolLevel(3).finish()  # setDefaultModelState({"lit": "false"}).

    # missing: redstone torch, stone button, snow

    full_template.setName("ice").setSpeedMultiplier(1.98).setStrenght(.5).setAllSideSolid(False).setBestTools(
        ToolType.PICKAXE).finish()
    full_template.setName("snow_block").setStrenght(.2).setBestTools(ToolType.SHOVEL).finish()

    # missing: cactus

    # missing: sugar can, jukebox

    full_template.setName("pumpkin").setStrenght(1.).setBestTools(ToolType.AXE).finish()
    full_template.setName("netherrack").setStrenght(.4).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(1).finish()
    full_template.setName("soul_sand").setStrenght(.5).setSpeedMultiplier(.4).setBestTools(ToolType.SHOVEL).finish()
    full_template.setName("glowstone").setStrenght(.3).setBestTools(ToolType.PICKAXE).finish()

    # missing: nether portal

    full_template.setName("carved_pumpkin").setHorizontalOrientable().setStrenght(1.).setBestTools(
        ToolType.AXE).finish()
    full_template.setName("jack_o_lantern").setHorizontalOrientable().setStrenght(1.).setBestTools(
        ToolType.AXE).setBlockItemGeneratorState({"facing": "east"}).finish()

    # missing: cake, repeater

    # missing: oak, spruce, birch, jungle, acacia and dark oak trapdoors

    full_template.setName("stone_bricks").setStrenght(1.5, 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    full_template.setName("mossy_stone_bricks").setStrenght(1.5, 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    full_template.setName("cracked_stone_bricks").setStrenght(1.5, 6.).setBestTools(ToolType.PICKAXE). \
        setMinimumToolLevel(1).finish()
    full_template.setName("chiseled_stone_bricks").setStrenght(1.5, 6.).setBestTools(ToolType.PICKAXE). \
        setMinimumToolLevel(1).finish()

    # missing: infested stone, cobblestone, stone bricks, mossy stone bricks, cracked stone bricks and chiseled stone
    # bricks; brown and red mushroom block, iron bars, glass pane

    full_template.setName("melon").setStrenght(1.).setBestTools(ToolType.AXE).finish()

    # missing: attached pumpkin and melon stem, vine; oak, spruce, birch, jungle, acacia and dark oak fence gates, brick
    # stairs, stone brick stairs

    full_template.setName("mycelium").setDefaultModelState({"snowy": "false"}).setStrenght(.6).setBestTools(
        ToolType.SHOVEL).finish()

    # missing: lily pad

    full_template.setName("nether_bricks").setStrenght(2., 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()

    # missing: nether brick stairs, nether wart, enchanting table, brewing stand, cauldron, end portal, end portal
    # frame

    full_template.setName("end_stone").setStrenght(3., 9.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()

    # missing: draggon egg, redstone lamp, cocoa, sandstone stairs

    full_template.setName("emerald_ore").setStrenght(3.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(3).finish()

    # missing: tripwire hook, tripwire

    full_template.setName("emerald_block").setStrenght(5., 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        3).finish()

    # missing: beacon, flower pot; potted oak, spruce, birch, jungle, acacia and dark oak sapling, fern, dandelion,
    # poppy, blue orchid, allium, azure bluet, red tulip, orange tulip, white tulip, pink tulip, oxeye daisy,
    # cornflower, lily of the valley, wither rose, red mushroom, dead bish, cactus; carrots, potatoes,
    # oak, spruce, birch, jungle, acacia and dark oak buttons, skeleton skull, wither skeleton skull,
    # zombie head, player head, creeper head, dragon head, anvil, chipped anvil, damaged anvil, trapped chest,
    # light & heavy weighted pressure plate, comparator, daylight detector

    full_template.setName("redstone_block").setStrenght(5., 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        3).finish()
    full_template.setName("nether_quartz_ore").setStrenght(3.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        3).finish()

    # missing: hopper

    full_template.setName("quartz_block").setStrenght(.8).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(3).finish()
    full_template.setName("chiseled_quartz_block").setStrenght(.8).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        3).finish()

    # missing: quartz stairs, activator rail, dropper

    # missing colored glass panes, slime block

    full_template.setName("barrier").setAllSideSolid(False).setConductsRedstonePowerFlag(False).setCanMobsSpawnOnFlag(
        False).setSolidFlag(False).setBreakAbleFlag(False).setStrenght(-1, 3600000).finish()

    # missing: iron trapdoor

    full_template.setName("prismarine").setStrenght(1.5, 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    full_template.setName("prismarine_bricks").setStrenght(1.5, 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    full_template.setName("dark_prismarine").setStrenght(1.5, 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    slab_template.setName("prismarine_slab").setStrenght(1.5, 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    slab_template.setName("prismarine_brick_slab").setStrenght(1.5, 6.).setBestTools(
        ToolType.PICKAXE).setMinimumToolLevel(1).finish()
    slab_template.setName("dark_prismarine_slab").setStrenght(1.5, 6.).setBestTools(
        ToolType.PICKAXE).setMinimumToolLevel(1).finish()

    # missing: prismarine stairs, prismarine brick stairs, dark prismarine stairs

    full_template.setName("sea_lantern").setStrenght(.3).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(1).finish()

    log_template.setName("hay_block").setStrenght(.5).finish()

    full_template.setName("terracotta").setStrenght(1.25, 4.2).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()

    full_template.setName("coal_block").setStrenght(5., 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    full_template.setName("packed_ice").setStrenght(.5).setSpeedMultiplier(1.98).setBestTools(ToolType.PICKAXE).finish()

    # missing: sunflower, lilac, rose bush, peony, tall grass, large fern, colored banners

    full_template.setName("red_sandstone").setStrenght(.8).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    full_template.setName("chiseled_red_sandstone").setStrenght(.8).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    full_template.setName("cut_red_sandstone").setStrenght(.8).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()

    # missing: red sandstone stairs

    slab_template.setName("oak_slab").setStrenght(2., 3.).setBestTools(ToolType.AXE).finish()
    slab_template.setName("spruce_slab").setStrenght(2., 3.).setBestTools(ToolType.AXE).finish()
    slab_template.setName("birch_slab").setStrenght(2., 3.).setBestTools(ToolType.AXE).finish()
    slab_template.setName("jungle_slab").setStrenght(2., 3.).setBestTools(ToolType.AXE).finish()
    slab_template.setName("acacia_slab").setStrenght(2., 3.).setBestTools(ToolType.AXE).finish()
    slab_template.setName("dark_oak_slab").setStrenght(2., 3.).setBestTools(ToolType.AXE).finish()
    slab_template.setName("smooth_stone_slab").setStrenght(2., 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    slab_template.setName("sandstone_slab").setStrenght(2., 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    slab_template.setName("cut_sandstone_slab").setStrenght(2., 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    slab_template.setName("petrified_oak_slab").setStrenght(2., 6.).setBestTools(ToolType.AXE).finish()
    slab_template.setName("cobblestone_slab").setStrenght(2., 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    slab_template.setName("brick_slab").setStrenght(2., 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    slab_template.setName("stone_brick_slab").setStrenght(2., 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    slab_template.setName("nether_brick_slab").setStrenght(2., 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    slab_template.setName("quartz_slab").setStrenght(2., 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    slab_template.setName("red_sandstone_slab").setStrenght(2., 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    slab_template.setName("cut_red_sandstone_slab").setStrenght(2., 6.).setBestTools(
        ToolType.PICKAXE).setMinimumToolLevel(1).finish()
    slab_template.setName("purpur_slab").setStrenght(2., 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()

    full_template.setName("smooth_stone").setStrenght(2., 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    full_template.setName("smooth_sandstone").setStrenght(2., 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    full_template.setName("smooth_quartz").setStrenght(2., 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    full_template.setName("smooth_red_sandstone").setStrenght(2., 6.).setBestTools(
        ToolType.PICKAXE).setMinimumToolLevel(1).finish()

    # missing: wooden doors, end rod, chorus plant, chorus flower

    full_template.setName("purpur_block").setStrenght(1.5, 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    log_template.setName("purpur_pillar").setStrenght(1.5, 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()

    # missing: purpur stairs

    full_template.setName("end_stone_bricks").setStrenght(3., 9.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()

    # missing: beetroots, grass path, end gateway, repeating command block, chain command block

    full_template.setName("frosted_ice").setSpeedMultiplier(0.98).setStrenght(.5).setDefaultModelState("age=0"). \
        setBestTools(ToolType.PICKAXE).finish()
    full_template.setName("magma_block").setStrenght(.5).setBestTools(ToolType.PICKAXE).finish()
    full_template.setName("nether_wart_block").setStrenght(1.).setBestTools(ToolType.PICKAXE).finish()
    full_template.setName("red_nether_bricks").setStrenght(2., 6.).setBestTools(ToolType.PICKAXE).finish()
    log_template.setName("bone_block").setStrenght(2.).setBestTools(ToolType.PICKAXE).finish()

    # missing: structure void, observer, colored glazed terracotta

    # missing: kelp, kelp plant

    full_template.setName("dried_kelp_block").setStrenght(.5, 2.5).setBestTools(ToolType.AXE).finish()

    # missing: turtle egg, dead corals, corals, dead coral fans, corals fans, sea pickle

    full_template.setName("blue_ice").setStrenght(2.8).setSpeedMultiplier(1.989).setBestTools(ToolType.PICKAXE).finish()

    # missing: conduit, bamboo sapling, bamboo, potted bamboo, void air, cave air, bubble column; polished andesite,
    # diorite and granite stairs; mossy stone brick stairs, end stone brick stairs, stone stairs, smooth sandstone
    # stairs, smooth quartz stairs; granite, andesite and diorite stairs; red nether brick stairs, smooth red sandstone

    slab_template.setName("smooth_red_sandstone_slab").setBestTools(ToolType.PICKAXE).setMinimumToolLevel(1).finish()
    slab_template.setName("mossy_stone_brick_slab").setBestTools(ToolType.PICKAXE).setMinimumToolLevel(1).finish()
    slab_template.setName("mossy_cobblestone_slab").setBestTools(ToolType.PICKAXE).setMinimumToolLevel(1).finish()
    slab_template.setName("end_stone_brick_slab").setBestTools(ToolType.PICKAXE).setMinimumToolLevel(1).finish()
    slab_template.setName("smooth_sandstone_slab").setBestTools(ToolType.PICKAXE).setMinimumToolLevel(1).finish()
    slab_template.setName("smooth_quartz_slab").setBestTools(ToolType.PICKAXE).setMinimumToolLevel(1).finish()
    slab_template.setName("red_nether_brick_slab").setBestTools(ToolType.PICKAXE).setMinimumToolLevel(1).finish()

    # missing: scaffolding, loom, smoker, blast furnace, cartography table, fletching table, grindstone, lectern,
    # smithing table, stonecutter, bell, lantern, campfire, sweet berry bush, structure block, jigsaw, composter, bee
    # nest, beehive, honey block, honeycomb block


mcpython.mod.ModMcpython.mcpython.eventbus.subscribe("stage:block:factory_usage", load_blocks,
                                                     info="loading block definitions")


@G.modloader("minecraft", "stage:combined_factory:blocks")
def combined_load():
    from mcpython.config import ENABLED_EXTRA_BLOCKS as BLOCKS

    def set_stone_properties(_, factory):
        factory: factory.setStrenght(1.5, 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(1)

    def set_nether_brick(_, factory):
        factory: factory.setStrenght(2, 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(1)

    config = mcpython.datagen.Configuration.DataGeneratorConfig(
        "minecraft", G.local + "/resources/generated").setDefaultNamespace("minecraft")

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:stone", enable=(True, True, BLOCKS["minecraft:stone_wall"]), callback=set_stone_properties)

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:bricks", slab_name="minecraft:brick_slab", wall_name="minecraft:brick_wall",
        callback=lambda _, factory: factory.setStrenght(2., 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(1))

    CombinedBlockFactory.generate_full_block_slab_wall(config, "minecraft:blackstone", callback=set_stone_properties)

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:clay", callback=lambda _, factory: factory.setStrenght(.6).setBestTools(ToolType.SHOVEL),
        enable=(True, BLOCKS["minecraft:clay_slab"], BLOCKS["minecraft:clay_wall"]))

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:cracked_nether_bricks", slab_name="minecraft:cracked_nether_brick_slab",
        wall_name="minecraft:cracked_nether_brick_wall", callback=set_nether_brick,
        enable=(True, BLOCKS["minecraft:cracked_nether_brick_slab"], BLOCKS["minecraft:cracked_nether_brick_wall"]))

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:cracked_polished_blackstone_bricks", callback=set_nether_brick,
        slab_name="minecraft:cracked_polished_blackstone_brick_slab",
        wall_name="minecraft:cracked_polished_blackstone_brick_wall",
        enable=(True, BLOCKS["minecraft:cracked_polished_blackstone_brick_slab"],
                BLOCKS["minecraft:cracked_polished_blackstone_brick_wall"]))

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:cracked_stone_bricks", slab_name="minecraft:cracked_stone_brick_slab",
        wall_name="minecraft:cracked_stone_brick_wall", callback=set_stone_properties)

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:crying_obsidian", enable=(True, BLOCKS["minecraft:crying_obsidian_slab"],
                                                     BLOCKS["minecraft:crying_obsidian_wall"]),
        callback=lambda _, factory: factory.setStrenght(50, 1200).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(5))

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:gilded_blackstone", enable=(True, BLOCKS["minecraft:gilded_blackstone_slab"],
                                                       BLOCKS["minecraft:gilded_blackstone_wall"]),
        callback=set_stone_properties)

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:mossy_cobblestone", callback=set_stone_properties)

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:mossy_stone_bricks", slab_name="minecraft:mossy_cobblestone_brick_slab",
        wall_name="minecraft:mossy_stone_brick_wall", callback=set_stone_properties)

    CombinedBlockFactory.generate_full_block_slab_wall(config, "minecraft:granite", callback=set_stone_properties)

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:polished_granite", callback=set_stone_properties,
        enable=(True, True, BLOCKS["minecraft:polished_granite_wall"]))

    CombinedBlockFactory.generate_full_block_slab_wall(config, "minecraft:diorite", callback=set_stone_properties)

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:polished_diorite", callback=set_stone_properties,
        enable=(True, True, BLOCKS["minecraft:polished_diorite_wall"]))

    CombinedBlockFactory.generate_full_block_slab_wall(config, "minecraft:andesite", callback=set_stone_properties)

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:polished_andesite", callback=set_stone_properties,
        enable=(True, True, BLOCKS["minecraft:polished_andesite_wall"]))

    def dirt_callback(_, factory):
        factory.setStrenght(.5).setBestTools(ToolType.SHOVEL)

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:dirt", callback=dirt_callback,
        enable=(True, BLOCKS["minecraft:dirt_slab"], BLOCKS["minecraft:dirt_wall"]))

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:coarse_dirt", callback=dirt_callback,
        enable=(True, BLOCKS["minecraft:coarse_dirt_slab"], BLOCKS["minecraft:coarse_dirt_wall"]))

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:polished_blackstone", callback=set_stone_properties)
    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:polished_blackstone_bricks", callback=set_stone_properties,
        slab_name="minecraft:polished_blackstone_brick_slab", wall_name="minecraft:polished_blackstone_brick_wall")

    CombinedBlockFactory.generate_full_block_slab_wall(config, "minecraft:cobblestone", callback=set_stone_properties)

    def wood_callback(_, factory):
        factory.setStrenght(2., 3.).setBestTools(ToolType.AXE)

    for wood in ["oak", "spruce", "birch", "jungle", "acacia", "dark_oak", "crimson", "warped"]:
        CombinedBlockFactory.generate_full_block_slab_wall(
            config, "minecraft:{}_planks".format(wood), callback=wood_callback,
            slab_name="minecraft:{}_slab".format(wood),
            enable=(True, True, BLOCKS["minecraft:{}_plank_wall".format(wood)]))

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:bedrock",
        callback=lambda _, factory: factory.setStrenght(-1, 3600000).setBreakAbleFlag(False),
        enable=(True, BLOCKS["minecraft:bedrock_slab"], BLOCKS["minecraft:bedrock_wall"]))

    def fall_able_callback(_, factory):
        factory.setStrenght(.5).setBestTools(ToolType.SHOVEL).setFallable()

    for m in ["sand", "red_sand", "gravel"]:
        CombinedBlockFactory.generate_full_block_slab_wall(
            config, "minecraft:{}".format(m), callback=fall_able_callback,
            enable=(True, BLOCKS["minecraft:{}_slab".format(m)], BLOCKS["minecraft:{}_wall".format(m)]))

    def set_glass(_, factory):
        factory.setAllSideSolid(False).setStrenght(.3).setBestTools(ToolType.PICKAXE)

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:glass", callback=set_glass, enable=(True, BLOCKS["minecraft:grass_slab"], False))

    def set_sandstone(_, factory):
        factory.setBestTools(ToolType.PICKAXE).setStrenght(.8).setMinimumToolLevel(1)

    CombinedBlockFactory.generate_full_block_slab_wall(config, "minecraft:sandstone", callback=set_sandstone)
    CombinedBlockFactory.generate_full_block_slab_wall(config, "minecraft:cut_sandstone", callback=set_sandstone,
                                                       enable=(True, True, BLOCKS["minecraft:cut_sandstone_wall"]))
    CombinedBlockFactory.generate_full_block_slab_wall(config, "minecraft:cut_red_sandstone", callback=set_sandstone,
                                                       enable=(True, True, BLOCKS["minecraft:cut_red_sandstone_wall"]))

    def set_wool(_, factory): factory.setStrenght(.6).setBestTools(ToolType.SHEAR)
    def set_concrete(_, factory): factory.setStrenght(1.8).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(1)
    def set_concrete_powder(_, factory): factory.setStrenght(.5).setBestTools(ToolType.SHOVEL).setFallable()
    def set_terracotta(_, factory): factory.setStrenght(1.25, 4.2).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(1)

    for c in ["white", "orange", "magenta", "light_blue", "lime", "pink", "gray", "light_gray", "cyan",
              "purple", "blue", "brown", "green", "red", "black"]:
        CombinedBlockFactory.generate_full_block_slab_wall(
            config, "minecraft:{}_wool".format(c), callback=set_wool,
            enable=(True, BLOCKS["minecraft:{}_wool_slab".format(c)], BLOCKS["minecraft:{}_wool_wall".format(c)]))
        CombinedBlockFactory.generate_full_block_slab_wall(
            config, "minecraft:{}_concrete".format(c), callback=set_concrete,
            enable=(True, BLOCKS["minecraft:{}_concrete_slab".format(c)],
                    BLOCKS["minecraft:{}_concrete_wall".format(c)]))
        CombinedBlockFactory.generate_full_block_slab_wall(
            config, "minecraft:{}_concrete_powder".format(c), callback=set_concrete_powder, enable=(True, False, False))
        CombinedBlockFactory.generate_full_block_slab_wall(
            config, "minecraft:{}_stained_glass".format(c), callback=set_glass,
            enable=(True, BLOCKS["minecraft:{}_stained_glass_slab".format(c)],
                    BLOCKS["minecraft:{}_stained_glass_wall".format(c)]))
        CombinedBlockFactory.generate_full_block_slab_wall(
            config, "minecraft:{}_terracotta".format(c), callback=set_terracotta,
            enable=(True, BLOCKS["minecraft:{}_terracotta_slab".format(c)],
                    BLOCKS["minecraft:{}_terracotta_wall".format(c)]))

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:dark_prismarine", callback=set_stone_properties, enable=(True, True, BLOCKS[
            "minecraft:dark_prismarine_wall"]))

    def set_end_stone(_, factory): factory.setStrenght(3, 9).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(1)

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:end_stone", callback=set_end_stone, enable=(True, BLOCKS["minecraft:end_stone_slab"],
                                                                       BLOCKS["minecraft:end_stone_wall"]))

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:end_stone_bricks", slab_name="minecraft:end_stone_brick_slab",
        wall_name="minecraft:end_stone_brick_wall", callback=set_end_stone)

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:glowstone", callback=lambda _, factory: factory.setStrenght(.3),
        enable=(True, BLOCKS["minecraft:glowstone_slab"], BLOCKS["minecraft:glowstone_wall"]))

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:magma_block", enable=(True, BLOCKS["minecraft:magma_block_slab"],
                                                 BLOCKS["minecraft:magma_block_wall"]),
        callback=lambda _, factory: factory.setStrenght(.5).setBestTools(ToolType.PICKAXE),
        texture="minecraft:block/magma")

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:nether_bricks", slab_name="minecraft:nether_brick_slab",
        wall_name="minecraft:nether_brick_wall",
        callback=lambda _, factory: factory.setStrenght(2., 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(1))

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:nether_wart_block", enable=(True, BLOCKS["minecraft:nether_wart_block_slab"],
                                                       BLOCKS["minecraft:nether_wart_block_wall"]),
        callback=lambda _, factory: factory.setStrenght(1.).setBestTools(ToolType.PICKAXE))

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:netherrack", enable=(True, BLOCKS["minecraft:netherrack_slab"],
                                                BLOCKS["minecraft:netherrack_wall"]),
        callback=set_stone_properties)

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:obsidian", enable=(True, BLOCKS["minecraft:obsidian_slab"],
                                              BLOCKS["minecraft:obsidian_wall"]),
        callback=lambda _, factory: factory.setStrenght(50., 1200.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
            5))

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:prismarine", callback=lambda _, factory: factory.setStrenght(1.5, 6.).setBestTools(
            ToolType.PICKAXE).setMinimumToolLevel(1))

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:prismarine_bricks", callback=lambda _, factory: factory.setStrenght(1.5, 6.).setBestTools(
            ToolType.PICKAXE).setMinimumToolLevel(1), slab_name="minecraft:prismarine_brick_slab",
        wall_name="minecraft:prismarine_brick_wall", enable=(True, True, BLOCKS["minecraft:prismarine_brick_wall"]))

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:purpur_block", callback=lambda _, factory: factory.setStrenght(1.5, 6.).setBestTools(
            ToolType.PICKAXE).setMinimumToolLevel(1), slab_name="minecraft:purpur_slab",
        wall_name="minecraft:purpur_wall", enable=(True, True, BLOCKS["minecraft:purpur_wall"]))

    def set_quartz(_, factory):
        factory.setStrenght(.8).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(3)

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:quartz_bricks", callback=set_quartz, slab_name="minecraft:quartz_brick_slab",
        enable=(True, BLOCKS["minecraft:quartz_brick_slab"], BLOCKS["minecraft:quartz_brick_wall"]),
        wall_name="minecraft:quartz_brick_wall")

