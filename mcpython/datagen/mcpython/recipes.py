"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
from mcpython.datagen import Configuration
import shutil
import os
import sys

DEFAULT_OUTPUT = G.local + "/resources/generated"  # where to output data - in dev environment


@G.modloader("minecraft", "special:datagen:configure")
def generate_recipes():
    """
    generator for all recipes in minecraft
    """

    if "--data-gen" not in sys.argv: return  # data gen only when launched so, not when we think
    if os.path.exists(DEFAULT_OUTPUT):
        shutil.rmtree(DEFAULT_OUTPUT)
    os.makedirs(DEFAULT_OUTPUT)
    config = Configuration.DataGeneratorConfig("minecraft", G.local + "/resources/generated")
    config.setDefaultNamespace("minecraft")

    aaa = ['iron_pickaxe', 'iron_shovel', 'iron_axe', 'iron_hoe', 'iron_sword', 'iron_helmet', 'iron_chestplate',
           'iron_leggings', 'iron_boots', 'iron_horse_armor', 'chainmail_helmet', 'chainmail_chestplate',
           'chainmail_leggings', 'chainmail_boots']
    aab = ['golden_pickaxe', 'golden_shovel', 'golden_axe', 'golden_hoe', 'golden_sword', 'golden_helmet',
           'golden_chestplate', 'golden_leggings', 'golden_boots', 'golden_horse_armor']
    aac = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)]
    aad = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1), (2, 2)]
    aae = [(0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)]
    aaf = ['chiseled_quartz_block', 'quartz_block', 'quartz_pillar']
    aag = [(0, 0), (0, 1), (0, 2), (1, 0), (2, 0), (2, 1), (2, 2)]
    aah = [(0, 0), (0, 1), (0, 2), (1, 2), (2, 0), (2, 1), (2, 2)]
    aai = [(0, 0), (0, 1), (0, 2), (1, 1), (2, 0), (2, 1), (2, 2)]
    aaj = [(0, 0), (0, 2), (1, 0), (1, 2), (2, 0), (2, 2)]
    aak = [(0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2)]
    aal = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)]
    aam = [(0, 0), (0, 1), (0, 2), (2, 0), (2, 1), (2, 2)]
    aan = [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1)]
    aao = [(0, 0), (0, 1), (1, 1), (2, 0), (2, 1)]
    aap = [(0, 0), (0, 1), (1, 0), (2, 0), (2, 1)]
    aaq = "cracked_polished_blackstone_bricks"
    aar = "polished_blackstone_pressure_plate"
    aas = ['purpur_block', 'purpur_pillar']
    aat = [(0, 2), (1, 1), (1, 2), (2, 2)]
    aau = [(0, 0), (0, 1), (1, 0), (1, 1)]
    aav = [(0, 1), (0, 2), (1, 1), (1, 2)]
    aaw = [(0, 0), (0, 1), (2, 0), (2, 1)]
    aax = [(0, 1), (1, 0), (1, 2), (2, 1)]
    aay = "light_weighted_pressure_plate"
    aaz = "heavy_weighted_pressure_plate"
    aaA = "light_blue_glazed_terracotta"
    aaB = "chiseled_polished_blackstone"
    aaC = "light_gray_glazed_terracotta"
    aaD = "polished_blackstone_button"
    aaE = "minecraft:campfire_cooking"
    aaF = "polished_blackstone_bricks"
    aaG = "magenta_glazed_terracotta"
    aaH = "orange_glazed_terracotta"
    aaI = "yellow_glazed_terracotta"
    aaJ = "purple_glazed_terracotta"
    aaK = "light_gray_stained_glass"
    aaL = "light_blue_stained_glass"
    aaM = "polished_blackstone_slab"
    aaN = "warped_fungus_on_a_stick"
    aaO = "black_glazed_terracotta"
    aaP = "green_glazed_terracotta"
    aaQ = "white_glazed_terracotta"
    aaR = "brown_glazed_terracotta"
    aaS = "dark_oak_pressure_plate"
    aaT = "glistering_melon_slice"
    aaU = "#soul_fire_base_blocks"
    aaV = [(0, 1), (1, 0), (2, 1)]
    aaW = [(0, 0), (1, 1), (2, 0)]
    aaX = "blue_glazed_terracotta"
    aaY = "cyan_glazed_terracotta"
    aaZ = "pink_glazed_terracotta"
    aba = "crimson_pressure_plate"
    abb = [(0, 2), (1, 2), (2, 2)]
    abc = "chiseled_red_sandstone"
    abd = [(0, 0), (1, 0), (2, 0)]
    abe = "lime_glazed_terracotta"
    abf = "creeper_banner_pattern"
    abg = [(0, 0), (0, 1), (1, 0)]
    abh = "gray_glazed_terracotta"
    abi = "chiseled_nether_bricks"
    abj = [(0, 1), (1, 1), (2, 1)]
    abk = "light_blue_terracotta"
    abl = "#stone_tool_materials"
    abm = "spruce_pressure_plate"
    abn = "red_glazed_terracotta"
    abo = "acacia_pressure_plate"
    abp = "cracked_nether_bricks"
    abq = "wooden_pressure_plate"
    abr = "light_gray_terracotta"
    abs = "mojang_banner_pattern"
    abt = "warped_pressure_plate"
    abu = "chiseled_stone_bricks"
    abv = "magenta_stained_glass"
    abw = "flower_banner_pattern"
    abx = "jungle_pressure_plate"
    aby = "chiseled_quartz_block"
    abz = "skull_banner_pattern"
    abA = "yellow_stained_glass"
    abB = "fermented_spider_eye"
    abC = "cracked_stone_bricks"
    abD = "smooth_red_sandstone"
    abE = "stone_pressure_plate"
    abF = "orange_stained_glass"
    abG = "birch_pressure_plate"
    abH = "purple_stained_glass"
    abI = "leather_horse_armor"
    abJ = "dark_oak_fence_gate"
    abK = "brown_stained_glass"
    abL = "black_stained_glass"
    abM = "green_stained_glass"
    abN = "polished_blackstone"
    abO = "white_stained_glass"
    abP = "popped_chorus_fruit"
    abQ = "stained_glass_pane"
    abR = "lime_stained_glass"
    abS = "chiseled_sandstone"
    abT = "pink_stained_glass"
    abU = "magenta_terracotta"
    abV = "diamond_chestplate"
    abW = "leather_chestplate"
    abX = "minecraft:blasting"
    abY = "oak_pressure_plate"
    abZ = "mossy_stone_bricks"
    aca = "gray_stained_glass"
    acb = ['coal', 'charcoal']
    acc = "red_sandstone_slab"
    acd = "stained_terracotta"
    ace = "cyan_stained_glass"
    acf = "crimson_fence_gate"
    acg = "blue_stained_glass"
    ach = "spruce_fence_gate"
    aci = "red_stained_glass"
    acj = "acacia_fence_gate"
    ack = "prismarine_bricks"
    acl = "daylight_detector"
    acm = "nether_quartz_ore"
    acn = "red_nether_bricks"
    aco = "nether_brick_slab"
    acp = "wooden_fence_gate"
    acq = "purple_terracotta"
    acr = "jungle_fence_gate"
    acs = "cut_red_sandstone"
    act = "orange_terracotta"
    acu = "golden_chestplate"
    acv = "light_gray_banner"
    acw = "light_blue_banner"
    acx = "nether_wart_block"
    acy = "polished_andesite"
    acz = "warped_fence_gate"
    acA = "smooth_stone_slab"
    acB = "mossy_cobblestone"
    acC = "cartography_table"
    acD = "minecraft:smoking"
    acE = "yellow_terracotta"
    acF = "carrot_on_a_stick"
    acG = "brown_terracotta"
    acH = "prismarine_shard"
    acI = "black_terracotta"
    acJ = "polished_granite"
    acK = "enchanting_table"
    acL = "white_terracotta"
    acM = "stone_brick_slab"
    acN = "polished_diorite"
    acO = "green_terracotta"
    acP = "end_stone_bricks"
    acQ = "diamond_leggings"
    acR = "furnace_minecart"
    acS = "smooth_sandstone"
    acT = (2, "magenta_dye")
    acU = "dried_kelp_block"
    acV = "birch_fence_gate"
    acW = "leather_leggings"
    acX = "concrete_powder"
    acY = "cooked_porkchop"
    acZ = "diamond_pickaxe"
    ada = "netherite_ingot"
    adb = "dark_prismarine"
    adc = "fletching_table"
    add = "flint_and_steel"
    ade = "netherite_scrap"
    adf = "wooden_trapdoor"
    adg = "hopper_minecart"
    adh = "netherite_block"
    adi = "pink_terracotta"
    adj = "dark_oak_button"
    adk = "dark_oak_planks"
    adl = "gray_terracotta"
    adm = "light_blue_wool"
    adn = "golden_leggings"
    ado = "blue_terracotta"
    adp = "honeycomb_block"
    adq = "light_gray_wool"
    adr = "cyan_terracotta"
    ads = "iron_chestplate"
    adt = "lime_terracotta"
    adu = "redstone_block"
    adv = [(0, 1), (1, 0)]
    adw = [(1, 0), (1, 1)]
    adx = "crimson_planks"
    ady = [(0, 0), (1, 1)]
    adz = "leather_helmet"
    adA = "golden_pickaxe"
    adB = "light_gray_bed"
    adC = [(1, 0), (1, 2)]
    adD = "redstone_torch"
    adE = [(0, 0), (0, 1)]
    adF = "wooden_pickaxe"
    adG = "sandstone_slab"
    adH = [(0, 0), (0, 2)]
    adI = "chest_minecart"
    adJ = "respawn_anchor"
    adK = "crafting_table"
    adL = "diamond_shovel"
    adM = "cooked_chicken"
    adN = [(0, 1), (1, 1)]
    adO = [(1, 1), (1, 2)]
    adP = "red_terracotta"
    adQ = [(0, 0), (2, 0)]
    adR = "light_blue_bed"
    adS = "smithing_table"
    adT = [(0, 0), (1, 0)]
    adU = [(0, 1), (2, 1)]
    adV = "diamond_helmet"
    adW = "light_blue_dye"
    adX = "light_gray_dye"
    adY = "jack_o_lantern"
    adZ = "ancient_debris"
    aea = "oak_fence_gate"
    aeb = "glowstone_dust"
    aec = "magenta_banner"
    aed = [(0, 1), (0, 2)]
    aee = "crimson_button"
    aef = "tripwire_hook"
    aeg = "trapped_chest"
    aeh = "red_sandstone"
    aei = "iron_trapdoor"
    aej = "iron_leggings"
    aek = "beetroot_soup"
    ael = "leather_boots"
    aem = "cooked_mutton"
    aen = "dark_oak_boat"
    aeo = "turtle_helmet"
    aep = "stained_glass"
    aeq = "brewing_stand"
    aer = "blast_furnace"
    aes = "yellow_banner"
    aet = "diamond_sword"
    aeu = "#wooden_slabs"
    aev = "jungle_planks"
    aew = "jungle_button"
    aex = "golden_carrot"
    aey = "sticky_piston"
    aez = (2, "pink_dye")
    aeA = "purpur_pillar"
    aeB = "acacia_button"
    aeC = "wooden_button"
    aeD = "stone_pickaxe"
    aeE = "wooden_shovel"
    aeF = "diamond_boots"
    aeG = "spruce_button"
    aeH = "warped_button"
    aeI = "emerald_block"
    aeJ = "cooked_salmon"
    aeK = "writable_book"
    aeL = "orange_banner"
    aeM = "golden_helmet"
    aeN = "diamond_block"
    aeO = "spruce_planks"
    aeP = "cut_sandstone"
    aeQ = "soul_campfire"
    aeR = "golden_shovel"
    aeS = "cooked_rabbit"
    aeT = "purple_banner"
    aeU = "acacia_planks"
    aeV = "nether_bricks"
    aeW = "redstone_lamp"
    aeX = "mushroom_stew"
    aeY = "smooth_quartz"
    aeZ = "warped_planks"
    afa = "wooden_stairs"
    afb = "stone_button"
    afc = "quartz_block"
    afd = "soul_lantern"
    afe = "green_banner"
    aff = "iron_pickaxe"
    afg = "wooden_fence"
    afh = "stone_bricks"
    afi = "honey_bottle"
    afj = "golden_apple"
    afk = "nether_brick"
    afl = "black_banner"
    afm = "baked_potato"
    afn = "white_banner"
    afo = "wooden_sword"
    afp = "golden_sword"
    afq = "white_carpet"
    afr = "magenta_wool"
    afs = "redstone_ore"
    aft = "smooth_stone"
    afu = "stone_shovel"
    afv = "lapis_lazuli"
    afw = "birch_button"
    afx = "brown_banner"
    afy = "golden_boots"
    afz = "tnt_minecart"
    afA = "birch_planks"
    afB = "diamond_hoe"
    afC = "nether_wart"
    afD = "magenta_bed"
    afE = "fishing_rod"
    afF = "melon_seeds"
    afG = "jungle_boat"
    afH = "rabbit_stew"
    afI = "quartz_slab"
    afJ = "emerald_ore"
    afK = "wooden_door"
    afL = "magma_block"
    afM = "acacia_boat"
    afN = "iron_nugget"
    afO = "melon_slice"
    afP = "shulker_box"
    afQ = "lapis_block"
    afR = "stone_sword"
    afS = "cooked_beef"
    afT = "end_crystal"
    afU = "pink_banner"
    afV = "purpur_slab"
    afW = "lime_banner"
    afX = "iron_helmet"
    afY = "stonecutter"
    afZ = "purple_wool"
    aga = "yellow_wool"
    agb = "slime_block"
    agc = "gold_nugget"
    agd = "honey_block"
    age = "spruce_boat"
    agf = "diamond_ore"
    agg = "cocoa_beans"
    agh = "cobblestone"
    agi = "magma_cream"
    agj = "pumpkin_pie"
    agk = "gray_banner"
    agl = "diamond_axe"
    agm = "iron_shovel"
    agn = "blue_banner"
    ago = "orange_wool"
    agp = "magenta_dye"
    agq = "cyan_banner"
    agr = "wooden_slab"
    ags = "ender_chest"
    agt = "sea_lantern"
    agu = "armor_stand"
    agv = "iron_block"
    agw = "purple_dye"
    agx = "iron_sword"
    agy = "iron_ingot"
    agz = "green_wool"
    agA = "orange_bed"
    agB = "wooden_axe"
    agC = "item_frame"
    agD = "#gold_ores"
    agE = "golden_axe"
    agF = "iron_boots"
    agG = "golden_hoe"
    agH = "slime_ball"
    agI = "birch_boat"
    agJ = "prismarine"
    agK = "grindstone"
    agL = "yellow_bed"
    agM = "cooked_cod"
    agN = "oak_planks"
    agO = "sugar_cane"
    agP = "terracotta"
    agQ = "flower_pot"
    agR = "orange_dye"
    agS = "note_block"
    agT = "red_banner"
    agU = "wooden_hoe"
    agV = "blackstone"
    agW = "stone_slab"
    agX = "oak_button"
    agY = "dried_kelp"
    agZ = "black_wool"
    aha = "gold_block"
    ahb = "soul_torch"
    ahc = "purple_bed"
    ahd = "snow_block"
    ahe = "coal_block"
    ahf = "white_wool"
    ahg = "brown_wool"
    ahh = "gold_ingot"
    ahi = "comparator"
    ahj = "yellow_dye"
    ahk = "bone_block"
    ahl = "glass_pane"
    ahm = "packed_ice"
    ahn = "stone_hoe"
    aho = "gray_wool"
    ahp = "composter"
    ahq = "green_bed"
    ahr = "black_bed"
    ahs = "blaze_rod"
    aht = "cyan_wool"
    ahu = "glowstone"
    ahv = "ender_eye"
    ahw = "brown_dye"
    ahx = "bone_meal"
    ahy = "hay_block"
    ahz = "white_dye"
    ahA = "bookshelf"
    ahB = "gunpowder"
    ahC = "green_dye"
    ahD = "blue_wool"
    ahE = "pink_wool"
    ahF = "stone_axe"
    ahG = "dispenser"
    ahH = "lodestone"
    ahI = "white_bed"
    ahJ = "black_dye"
    ahK = "lime_wool"
    ahL = "honeycomb"
    ahM = "brown_bed"
    ahN = "clay_ball"
    ahO = "sandstone"
    ahP = "lapis_ore"
    ahQ = "painting"
    ahR = "iron_hoe"
    ahS = "lime_bed"
    ahT = "minecart"
    ahU = "oak_boat"
    ahV = "repeater"
    ahW = "cauldron"
    ahX = "gray_bed"
    ahY = "cyan_dye"
    ahZ = "observer"
    aia = "andesite"
    aib = "redstone"
    aic = "gray_dye"
    aid = "charcoal"
    aie = "cyan_bed"
    aif = "blue_dye"
    aig = "lime_dye"
    aih = "blue_ice"
    aii = "pink_bed"
    aij = "pink_dye"
    aik = "obsidian"
    ail = "red_wool"
    aim = "dyed_bed"
    ain = "blue_bed"
    aio = "iron_ore"
    aip = "bonemeal"
    aiq = "porkchop"
    air = "iron_axe"
    ais = "campfire"
    ait = "coal_ore"
    aiu = "crossbow"
    aiv = "lantern"
    aiw = "jukebox"
    aix = "granite"
    aiy = "diorite"
    aiz = "#planks"
    aiA = "beehive"
    aiB = "diamond"
    aiC = "leather"
    aiD = "chicken"
    aiE = "compass"
    aiF = "feather"
    aiG = "furnace"
    aiH = "conduit"
    aiI = "red_dye"
    aiJ = "dropper"
    aiK = "red_bed"
    aiL = "lectern"
    aiM = "emerald"
    aiN = "bamboo"
    aiO = "carrot"
    aiP = "bucket"
    aiQ = "beacon"
    aiR = "sticks"
    aiS = "sponge"
    aiT = [(1, 1)]
    aiU = "bricks"
    aiV = "planks"
    aiW = "mutton"
    aiX = [(1, 0)]
    aiY = [(0, 1)]
    aiZ = "banner"
    aja = "barrel"
    ajb = "smoker"
    ajc = "rabbit"
    ajd = "potato"
    aje = "hopper"
    ajf = "shield"
    ajg = [(1, 2)]
    ajh = "string"
    aji = "salmon"
    ajj = "target"
    ajk = [(0, 2)]
    ajl = "quartz"
    ajm = "shears"
    ajn = "carpet"
    ajo = "gravel"
    ajp = [(0, 0)]
    ajq = "piston"
    ajr = "wheat"
    ajs = "bread"
    ajt = "paper"
    aju = "arrow"
    ajv = "torch"
    ajw = "flint"
    ajx = "clock"
    ajy = "#logs"
    ajz = "anvil"
    ajA = "stone"
    ajB = "brick"
    ajC = "lever"
    ajD = "sugar"
    ajE = "chest"
    ajF = "glass"
    ajG = "chain"
    ajH = "stick"
    ajI = "melon"
    ajJ = "book"
    ajK = "loom"
    ajL = "kelp"
    ajM = "sand"
    ajN = "bark"
    ajO = "sign"
    ajP = "wool"
    ajQ = "cake"
    ajR = "boat"
    ajS = "beef"
    ajT = "coal"
    ajU = "clay"
    ajV = "map"
    ajW = "bow"
    ajX = "cod"
    ajY = "bed"
    ajZ = "egg"
    aka = "tnt"
    akb = 0.35
    akc = 0.15
    akd = 2.0
    ake = 0.1
    akf = 100
    akg = 0.2
    akh = 600
    aki = 1.0
    akj = 0.7
    config.shaped_recipe(afM).setEntries(aao, aeU).setOutput(afM).setGroup(ajR)
    config.shapeless_recipe(aeB).addInput(aeU, 1).setOutput(aeB).setGroup(aeC)
    config.shaped_recipe("acacia_door").setEntries(aal, aeU).setOutput((3, "acacia_door")).setGroup(afK)
    config.shaped_recipe("acacia_fence").setEntries(adw, ajH).setEntries(aaw, aeU).setOutput(
        (3, "acacia_fence")).setGroup(afg)
    config.shaped_recipe(acj).setEntries(aaw, ajH).setEntries(adw, aeU).setOutput(acj).setGroup(acp)
    config.shapeless_recipe(aeU).addInput("#acacia_logs", 1).setOutput((4, aeU)).setGroup(aiV)
    config.shaped_recipe(abo).setEntries(adT, aeU).setOutput(abo).setGroup(abq)
    config.shaped_recipe("acacia_sign").setEntries(aan, aeU).setEntries(ajg, ajH).setOutput(
        (3, "acacia_sign")).setGroup(ajO)
    config.shaped_recipe("acacia_stairs").setEntries(aak, aeU).setOutput((4, "acacia_stairs")).setGroup(afa)
    config.shaped_recipe("acacia_trapdoor").setEntries(aan, aeU).setOutput((2, "acacia_trapdoor")).setGroup(adf)
    config.shaped_recipe("acacia_wood").setEntries(aau, "acacia_log").setOutput((3, "acacia_wood")).setGroup(ajN)
    config.shaped_recipe("activator_rail").setEntries(aiT, adD).setEntries(adC, ajH).setEntries(aam, agy).setOutput(
        (6, "activator_rail"))
    config.shapeless_recipe(aia).addInput(aiy, 1).addInput(agh, 1).setOutput((2, aia))
    config.shaped_recipe("andesite_stairs").setEntries(aak, aia).setOutput((4, "andesite_stairs"))
    config.shaped_recipe(ajz).setEntries(abd, agv).setEntries(aat, agy).setOutput(ajz)
    config.shaped_recipe(agu).setEntries([(0, 0), (0, 2), (1, 0), (1, 1), (2, 0), (2, 2)], ajH).setEntries(ajg,
                                                                                                           acA).setOutput(
        agu)
    config.shaped_recipe(aju).setEntries(aiY, ajH).setEntries(ajp, ajw).setEntries(ajk, aiF).setOutput((4, aju))
    config.smelting_recipe(afm).add_ingredient(ajd).setXp(akb).setOutput(afm)
    config.smelting_recipe("baked_potato_from_campfire_cooking", aaE).add_ingredient(ajd).setXp(akb).setOutput(
        afm).setCookingTime(akh)
    config.smelting_recipe("baked_potato_from_smoking", acD).add_ingredient(ajd).setXp(akb).setOutput(
        afm).setCookingTime(akf)
    config.shaped_recipe(aja).setEntries(aam, aiz).setEntries(adC, aeu).setOutput(aja)
    config.shaped_recipe(aiQ).setEntries(aiT, "nether_star").setEntries(aap, ajF).setEntries(abb, aik).setOutput(aiQ)
    config.shaped_recipe(aiA).setEntries(aaj, aiz).setEntries(abj, ahL).setOutput(aiA)
    config.shapeless_recipe(aek).addInput("bowl", 1).addInput("beetroot", 6).setOutput(aek)
    config.shaped_recipe(agI).setEntries(aao, afA).setOutput(agI).setGroup(ajR)
    config.shapeless_recipe(afw).addInput(afA, 1).setOutput(afw).setGroup(aeC)
    config.shaped_recipe("birch_door").setEntries(aal, afA).setOutput((3, "birch_door")).setGroup(afK)
    config.shaped_recipe("birch_fence").setEntries(adw, ajH).setEntries(aaw, afA).setOutput(
        (3, "birch_fence")).setGroup(afg)
    config.shaped_recipe(acV).setEntries(aaw, ajH).setEntries(adw, afA).setOutput(acV).setGroup(acp)
    config.shapeless_recipe(afA).addInput("#birch_logs", 1).setOutput((4, afA)).setGroup(aiV)
    config.shaped_recipe(abG).setEntries(adT, afA).setOutput(abG).setGroup(abq)
    config.shaped_recipe("birch_sign").setEntries(aan, afA).setEntries(ajg, ajH).setOutput((3, "birch_sign")).setGroup(
        ajO)
    config.shaped_recipe("birch_stairs").setEntries(aak, afA).setOutput((4, "birch_stairs")).setGroup(afa)
    config.shaped_recipe("birch_trapdoor").setEntries(aan, afA).setOutput((2, "birch_trapdoor")).setGroup(adf)
    config.shaped_recipe("birch_wood").setEntries(aau, "birch_log").setOutput((3, "birch_wood")).setGroup(ajN)
    config.shaped_recipe("blackstone_slab").setEntries(abd, agV).setOutput((6, "blackstone_slab"))
    config.shaped_recipe("blackstone_stairs").setEntries(aak, agV).setOutput((4, "blackstone_stairs"))
    config.shaped_recipe("blackstone_wall").setEntries(aan, agV).setOutput((6, "blackstone_wall"))
    config.shaped_recipe(afl).setEntries(aan, agZ).setEntries(ajg, ajH).setOutput(afl).setGroup(aiZ)
    config.shaped_recipe(ahr).setEntries(abd, agZ).setEntries(abj, aiz).setOutput(ahr).setGroup(ajY)
    config.shapeless_recipe("black_bed_from_white_bed").addInput(ahI, 1).addInput(ahJ, 1).setOutput(ahr).setGroup(aim)
    config.shaped_recipe("black_carpet").setEntries(adT, agZ).setOutput((3, "black_carpet")).setGroup(ajn)
    config.shaped_recipe("black_carpet_from_white_carpet").setEntries(aad, afq).setEntries(aiT, ahJ).setOutput(
        (8, "black_carpet")).setGroup(ajn)
    config.shapeless_recipe("black_concrete_powder").addInput(ahJ, 1).addInput(ajM, 4).addInput(ajo, 4).setOutput(
        (8, "black_concrete_powder")).setGroup(acX)
    config.shapeless_recipe(ahJ).addInput("ink_sac", 1).setOutput(ahJ).setGroup(ahJ)
    config.shapeless_recipe("black_dye_from_wither_rose").addInput("wither_rose", 1).setOutput(ahJ).setGroup(ahJ)
    config.smelting_recipe(aaO).add_ingredient(acI).setXp(ake).setOutput(aaO)
    config.shaped_recipe(abL).setEntries(aad, ajF).setEntries(aiT, ahJ).setOutput((8, abL)).setGroup(aep)
    config.shaped_recipe("black_stained_glass_pane").setEntries(aan, abL).setOutput(
        (16, "black_stained_glass_pane")).setGroup(abQ)
    config.shaped_recipe("black_stained_glass_pane_from_glass_pane").setEntries(aad, ahl).setEntries(aiT,
                                                                                                     ahJ).setOutput(
        (8, "black_stained_glass_pane")).setGroup(abQ)
    config.shaped_recipe(acI).setEntries(aad, agP).setEntries(aiT, ahJ).setOutput((8, acI)).setGroup(acd)
    config.shapeless_recipe(agZ).addInput(ahJ, 1).addInput(ahf, 1).setOutput(agZ).setGroup(ajP)
    config.shaped_recipe(aer).setEntries(abb, aft).setEntries(aiT, aiG).setEntries(aap, agy).setOutput(aer)
    config.shapeless_recipe("blaze_powder").addInput(ahs, 1).setOutput((2, "blaze_powder"))
    config.shaped_recipe(agn).setEntries(aan, ahD).setEntries(ajg, ajH).setOutput(agn).setGroup(aiZ)
    config.shaped_recipe(ain).setEntries(abd, ahD).setEntries(abj, aiz).setOutput(ain).setGroup(ajY)
    config.shapeless_recipe("blue_bed_from_white_bed").addInput(ahI, 1).addInput(aif, 1).setOutput(ain).setGroup(aim)
    config.shaped_recipe("blue_carpet").setEntries(adT, ahD).setOutput((3, "blue_carpet")).setGroup(ajn)
    config.shaped_recipe("blue_carpet_from_white_carpet").setEntries(aad, afq).setEntries(aiT, aif).setOutput(
        (8, "blue_carpet")).setGroup(ajn)
    config.shapeless_recipe("blue_concrete_powder").addInput(aif, 1).addInput(ajM, 4).addInput(ajo, 4).setOutput(
        (8, "blue_concrete_powder")).setGroup(acX)
    config.shapeless_recipe(aif).addInput(afv, 1).setOutput(aif).setGroup(aif)
    config.shapeless_recipe("blue_dye_from_cornflower").addInput("cornflower", 1).setOutput(aif).setGroup(aif)
    config.smelting_recipe(aaX).add_ingredient(ado).setXp(ake).setOutput(aaX)
    config.shaped_recipe(aih).setEntries(aac, ahm).setOutput(aih)
    config.shaped_recipe(acg).setEntries(aad, ajF).setEntries(aiT, aif).setOutput((8, acg)).setGroup(aep)
    config.shaped_recipe("blue_stained_glass_pane").setEntries(aan, acg).setOutput(
        (16, "blue_stained_glass_pane")).setGroup(abQ)
    config.shaped_recipe("blue_stained_glass_pane_from_glass_pane").setEntries(aad, ahl).setEntries(aiT, aif).setOutput(
        (8, "blue_stained_glass_pane")).setGroup(abQ)
    config.shaped_recipe(ado).setEntries(aad, agP).setEntries(aiT, aif).setOutput((8, ado)).setGroup(acd)
    config.shapeless_recipe(ahD).addInput(aif, 1).addInput(ahf, 1).setOutput(ahD).setGroup(ajP)
    config.shaped_recipe(ahk).setEntries(aac, ahx).setOutput(ahk)
    config.shapeless_recipe(ahx).addInput("bone", 1).setOutput((3, ahx)).setGroup(aip)
    config.shapeless_recipe("bone_meal_from_bone_block").addInput(ahk, 1).setOutput((9, ahx)).setGroup(aip)
    config.shapeless_recipe(ajJ).addInput(ajt, 3).addInput(aiC, 1).setOutput(ajJ)
    config.shaped_recipe(ahA).setEntries(aaj, aiz).setEntries(abj, ajJ).setOutput(ahA)
    config.shaped_recipe(ajW).setEntries([(0, 1), (1, 0), (1, 2)], ajH).setEntries([(2, 0), (2, 1), (2, 2)],
                                                                                   ajh).setOutput(ajW)
    config.shaped_recipe("bowl").setEntries(aaW, aiz).setOutput((4, "bowl"))
    config.shaped_recipe(ajs).setEntries(abd, ajr).setOutput(ajs)
    config.shaped_recipe(aeq).setEntries(aiX, ahs).setEntries(abj, agh).setOutput(aeq)
    config.smelting_recipe(ajB).add_ingredient(ahN).setXp(0.3).setOutput(ajB)
    config.shaped_recipe(aiU).setEntries(aau, ajB).setOutput(aiU)
    config.shaped_recipe("brick_slab").setEntries(abd, aiU).setOutput((6, "brick_slab"))
    config.shaped_recipe("brick_stairs").setEntries(aak, aiU).setOutput((4, "brick_stairs"))
    config.shaped_recipe("brick_wall").setEntries(aan, aiU).setOutput((6, "brick_wall"))
    config.shaped_recipe(afx).setEntries(aan, ahg).setEntries(ajg, ajH).setOutput(afx).setGroup(aiZ)
    config.shaped_recipe(ahM).setEntries(abd, ahg).setEntries(abj, aiz).setOutput(ahM).setGroup(ajY)
    config.shapeless_recipe("brown_bed_from_white_bed").addInput(ahI, 1).addInput(ahw, 1).setOutput(ahM).setGroup(aim)
    config.shaped_recipe("brown_carpet").setEntries(adT, ahg).setOutput((3, "brown_carpet")).setGroup(ajn)
    config.shaped_recipe("brown_carpet_from_white_carpet").setEntries(aad, afq).setEntries(aiT, ahw).setOutput(
        (8, "brown_carpet")).setGroup(ajn)
    config.shapeless_recipe("brown_concrete_powder").addInput(ahw, 1).addInput(ajM, 4).addInput(ajo, 4).setOutput(
        (8, "brown_concrete_powder")).setGroup(acX)
    config.shapeless_recipe(ahw).addInput(agg, 1).setOutput(ahw).setGroup(ahw)
    config.smelting_recipe(aaR).add_ingredient(acG).setXp(ake).setOutput(aaR)
    config.shaped_recipe(abK).setEntries(aad, ajF).setEntries(aiT, ahw).setOutput((8, abK)).setGroup(aep)
    config.shaped_recipe("brown_stained_glass_pane").setEntries(aan, abK).setOutput(
        (16, "brown_stained_glass_pane")).setGroup(abQ)
    config.shaped_recipe("brown_stained_glass_pane_from_glass_pane").setEntries(aad, ahl).setEntries(aiT,
                                                                                                     ahw).setOutput(
        (8, "brown_stained_glass_pane")).setGroup(abQ)
    config.shaped_recipe(acG).setEntries(aad, agP).setEntries(aiT, ahw).setOutput((8, acG)).setGroup(acd)
    config.shapeless_recipe(ahg).addInput(ahw, 1).addInput(ahf, 1).setOutput(ahg).setGroup(ajP)
    config.shaped_recipe(aiP).setEntries(aaW, agy).setOutput(aiP)
    config.shaped_recipe(ajQ).setEntries(abd, "milk_bucket").setEntries(adU, ajD).setEntries(abb, ajr).setEntries(aiT,
                                                                                                                  ajZ).setOutput(
        ajQ)
    config.shaped_recipe(ais).setEntries(abb, ajy).setEntries(aaV, ajH).setEntries(aiT, "#coals").setOutput(ais)
    config.shaped_recipe(acF).setEntries(ajp, afE).setEntries(aiT, aiO).setOutput(acF)
    config.shaped_recipe(acC).setEntries(aav, aiz).setEntries(adT, ajt).setOutput(acC)
    config.shaped_recipe(ahW).setEntries(aah, agy).setOutput(ahW)
    config.shaped_recipe(ajG).setEntries(aiY, agy).setEntries(adH, afN).setOutput(ajG)
    config.smelting_recipe(aid).add_ingredient("#logs_that_burn").setXp(akc).setOutput(aid)
    config.shaped_recipe(ajE).setEntries(aad, aiz).setOutput(ajE)
    config.shaped_recipe(adI).setEntries(ajp, ajE).setEntries(aiY, ahT).setOutput(adI)
    config.shaped_recipe(abi).setEntries(adE, aco).setOutput(abi)
    config.shaped_recipe(aaB).setEntries(adE, aaM).setOutput(aaB)
    config.shaped_recipe(aby).setEntries(adE, afI).setOutput(aby)
    config.shaped_recipe(abc).setEntries(adE, acc).setOutput(abc)
    config.shaped_recipe(abS).setEntries(adE, adG).setOutput(abS)
    config.shaped_recipe(abu).setEntries(adE, acM).setOutput(abu)
    config.shaped_recipe(ajU).setEntries(aau, ahN).setOutput(ajU)
    config.shaped_recipe(ajx).setEntries(aax, ahh).setEntries(aiT, aib).setOutput(ajx)
    config.shapeless_recipe(ajT).addInput(ahe, 1).setOutput((9, ajT))
    config.shaped_recipe(ahe).setEntries(aac, ajT).setOutput(ahe)
    config.smelting_recipe("coal_from_blasting", abX).add_ingredient(ait).setXp(ake).setOutput(ajT).setCookingTime(akf)
    config.smelting_recipe("coal_from_smelting").add_ingredient(ait).setXp(ake).setOutput(ajT)
    config.shaped_recipe("coarse_dirt").setEntries(ady, "dirt").setEntries(adv, ajo).setOutput((4, "coarse_dirt"))
    config.shaped_recipe("cobblestone_stairs").setEntries(aak, agh).setOutput((4, "cobblestone_stairs"))
    config.shaped_recipe(ahi).setEntries(aaV, adD).setEntries(aiT, ajl).setEntries(abb, ajA).setOutput(ahi)
    config.shaped_recipe(aiE).setEntries(aax, agy).setEntries(aiT, aib).setOutput(aiE)
    config.shaped_recipe(ahp).setEntries(aah, aeu).setOutput(ahp)
    config.shaped_recipe(aiH).setEntries(aad, "nautilus_shell").setEntries(aiT, "heart_of_the_sea").setOutput(aiH)
    config.smelting_recipe(afS).add_ingredient(ajS).setXp(akb).setOutput(afS)
    config.smelting_recipe("cooked_beef_from_campfire_cooking", aaE).add_ingredient(ajS).setXp(akb).setOutput(
        afS).setCookingTime(akh)
    config.smelting_recipe("cooked_beef_from_smoking", acD).add_ingredient(ajS).setXp(akb).setOutput(
        afS).setCookingTime(akf)
    config.smelting_recipe(adM).add_ingredient(aiD).setXp(akb).setOutput(adM)
    config.smelting_recipe("cooked_chicken_from_campfire_cooking", aaE).add_ingredient(aiD).setXp(akb).setOutput(
        adM).setCookingTime(akh)
    config.smelting_recipe("cooked_chicken_from_smoking", acD).add_ingredient(aiD).setXp(akb).setOutput(
        adM).setCookingTime(akf)
    config.smelting_recipe(agM).add_ingredient(ajX).setXp(akb).setOutput(agM)
    config.smelting_recipe("cooked_cod_from_campfire_cooking", aaE).add_ingredient(ajX).setXp(akb).setOutput(
        agM).setCookingTime(akh)
    config.smelting_recipe("cooked_cod_from_smoking", acD).add_ingredient(ajX).setXp(akb).setOutput(agM).setCookingTime(
        akf)
    config.smelting_recipe(aem).add_ingredient(aiW).setXp(akb).setOutput(aem)
    config.smelting_recipe("cooked_mutton_from_campfire_cooking", aaE).add_ingredient(aiW).setXp(akb).setOutput(
        aem).setCookingTime(akh)
    config.smelting_recipe("cooked_mutton_from_smoking", acD).add_ingredient(aiW).setXp(akb).setOutput(
        aem).setCookingTime(akf)
    config.smelting_recipe(acY).add_ingredient(aiq).setXp(akb).setOutput(acY)
    config.smelting_recipe("cooked_porkchop_from_campfire_cooking", aaE).add_ingredient(aiq).setXp(akb).setOutput(
        acY).setCookingTime(akh)
    config.smelting_recipe("cooked_porkchop_from_smoking", acD).add_ingredient(aiq).setXp(akb).setOutput(
        acY).setCookingTime(akf)
    config.smelting_recipe(aeS).add_ingredient(ajc).setXp(akb).setOutput(aeS)
    config.smelting_recipe("cooked_rabbit_from_campfire_cooking", aaE).add_ingredient(ajc).setXp(akb).setOutput(
        aeS).setCookingTime(akh)
    config.smelting_recipe("cooked_rabbit_from_smoking", acD).add_ingredient(ajc).setXp(akb).setOutput(
        aeS).setCookingTime(akf)
    config.smelting_recipe(aeJ).add_ingredient(aji).setXp(akb).setOutput(aeJ)
    config.smelting_recipe("cooked_salmon_from_campfire_cooking", aaE).add_ingredient(aji).setXp(akb).setOutput(
        aeJ).setCookingTime(akh)
    config.smelting_recipe("cooked_salmon_from_smoking", acD).add_ingredient(aji).setXp(akb).setOutput(
        aeJ).setCookingTime(akf)
    config.shaped_recipe("cookie").setEntries(adQ, ajr).setEntries(aiX, agg).setOutput((8, "cookie"))
    config.smelting_recipe(abp).add_ingredient(aeV).setXp(ake).setOutput(abp)
    config.smelting_recipe(aaq).add_ingredient(aaF).setXp(ake).setOutput(aaq)
    config.smelting_recipe(abC).add_ingredient(afh).setXp(ake).setOutput(abC)
    config.shaped_recipe(adK).setEntries(aau, aiz).setOutput(adK)
    config.shapeless_recipe(abf).addInput(ajt, 1).addInput("creeper_head", 1).setOutput(abf)
    config.shapeless_recipe(aee).addInput(adx, 1).setOutput(aee).setGroup(aeC)
    config.shaped_recipe("crimson_door").setEntries(aal, adx).setOutput((3, "crimson_door")).setGroup(afK)
    config.shaped_recipe("crimson_fence").setEntries(adw, ajH).setEntries(aaw, adx).setOutput(
        (3, "crimson_fence")).setGroup(afg)
    config.shaped_recipe(acf).setEntries(aaw, ajH).setEntries(adw, adx).setOutput(acf).setGroup(acp)
    config.shaped_recipe("crimson_hyphae").setEntries(aau, "crimson_stem").setOutput((3, "crimson_hyphae")).setGroup(
        ajN)
    config.shapeless_recipe(adx).addInput("#crimson_stems", 1).setOutput((4, adx)).setGroup(aiV)
    config.shaped_recipe(aba).setEntries(adT, adx).setOutput(aba).setGroup(abq)
    config.shaped_recipe("crimson_sign").setEntries(aan, adx).setEntries(ajg, ajH).setOutput(
        (3, "crimson_sign")).setGroup(ajO)
    config.shaped_recipe("crimson_stairs").setEntries(aak, adx).setOutput((4, "crimson_stairs")).setGroup(afa)
    config.shaped_recipe("crimson_trapdoor").setEntries(aan, adx).setOutput((2, "crimson_trapdoor")).setGroup(adf)
    config.shaped_recipe(aiu).setEntries(adU, ajh).setEntries([(0, 0), (1, 2), (2, 0)], ajH).setEntries(aiX,
                                                                                                        agy).setEntries(
        aiT, aef).setOutput(aiu)
    config.shaped_recipe(acs).setEntries(aau, aeh).setOutput((4, acs))
    config.shaped_recipe("cut_red_sandstone_slab").setEntries(abd, acs).setOutput((6, "cut_red_sandstone_slab"))
    config.shaped_recipe(aeP).setEntries(aau, ahO).setOutput((4, aeP))
    config.shaped_recipe("cut_sandstone_slab").setEntries(abd, aeP).setOutput((6, "cut_sandstone_slab"))
    config.shaped_recipe(agq).setEntries(aan, aht).setEntries(ajg, ajH).setOutput(agq).setGroup(aiZ)
    config.shaped_recipe(aie).setEntries(abd, aht).setEntries(abj, aiz).setOutput(aie).setGroup(ajY)
    config.shapeless_recipe("cyan_bed_from_white_bed").addInput(ahI, 1).addInput(ahY, 1).setOutput(aie).setGroup(aim)
    config.shaped_recipe("cyan_carpet").setEntries(adT, aht).setOutput((3, "cyan_carpet")).setGroup(ajn)
    config.shaped_recipe("cyan_carpet_from_white_carpet").setEntries(aad, afq).setEntries(aiT, ahY).setOutput(
        (8, "cyan_carpet")).setGroup(ajn)
    config.shapeless_recipe("cyan_concrete_powder").addInput(ahY, 1).addInput(ajM, 4).addInput(ajo, 4).setOutput(
        (8, "cyan_concrete_powder")).setGroup(acX)
    config.shapeless_recipe(ahY).addInput(aif, 1).addInput(ahC, 1).setOutput((2, ahY))
    config.smelting_recipe(aaY).add_ingredient(adr).setXp(ake).setOutput(aaY)
    config.shaped_recipe(ace).setEntries(aad, ajF).setEntries(aiT, ahY).setOutput((8, ace)).setGroup(aep)
    config.shaped_recipe("cyan_stained_glass_pane").setEntries(aan, ace).setOutput(
        (16, "cyan_stained_glass_pane")).setGroup(abQ)
    config.shaped_recipe("cyan_stained_glass_pane_from_glass_pane").setEntries(aad, ahl).setEntries(aiT, ahY).setOutput(
        (8, "cyan_stained_glass_pane")).setGroup(abQ)
    config.shaped_recipe(adr).setEntries(aad, agP).setEntries(aiT, ahY).setOutput((8, adr)).setGroup(acd)
    config.shapeless_recipe(aht).addInput(ahY, 1).addInput(ahf, 1).setOutput(aht).setGroup(ajP)
    config.shaped_recipe(aen).setEntries(aao, adk).setOutput(aen).setGroup(ajR)
    config.shapeless_recipe(adj).addInput(adk, 1).setOutput(adj).setGroup(aeC)
    config.shaped_recipe("dark_oak_door").setEntries(aal, adk).setOutput((3, "dark_oak_door")).setGroup(afK)
    config.shaped_recipe("dark_oak_fence").setEntries(adw, ajH).setEntries(aaw, adk).setOutput(
        (3, "dark_oak_fence")).setGroup(afg)
    config.shaped_recipe(abJ).setEntries(aaw, ajH).setEntries(adw, adk).setOutput(abJ).setGroup(acp)
    config.shapeless_recipe(adk).addInput("#dark_oak_logs", 1).setOutput((4, adk)).setGroup(aiV)
    config.shaped_recipe(aaS).setEntries(adT, adk).setOutput(aaS).setGroup(abq)
    config.shaped_recipe("dark_oak_sign").setEntries(aan, adk).setEntries(ajg, ajH).setOutput(
        (3, "dark_oak_sign")).setGroup(ajO)
    config.shaped_recipe("dark_oak_stairs").setEntries(aak, adk).setOutput((4, "dark_oak_stairs")).setGroup(afa)
    config.shaped_recipe("dark_oak_trapdoor").setEntries(aan, adk).setOutput((2, "dark_oak_trapdoor")).setGroup(adf)
    config.shaped_recipe("dark_oak_wood").setEntries(aau, "dark_oak_log").setOutput((3, "dark_oak_wood")).setGroup(ajN)
    config.shaped_recipe(adb).setEntries(aad, acH).setEntries(aiT, ahJ).setOutput(adb)
    config.shaped_recipe("dark_prismarine_slab").setEntries(abd, adb).setOutput((6, "dark_prismarine_slab"))
    config.shaped_recipe("dark_prismarine_stairs").setEntries(aak, adb).setOutput((4, "dark_prismarine_stairs"))
    config.shaped_recipe(acl).setEntries(abj, ajl).setEntries(abd, ajF).setEntries(abb, aeu).setOutput(acl)
    config.shaped_recipe("detector_rail").setEntries(ajg, aib).setEntries(aiT, abE).setEntries(aam, agy).setOutput(
        (6, "detector_rail"))
    config.shapeless_recipe(aiB).addInput(aeN, 1).setOutput((9, aiB))
    config.shaped_recipe(agl).setEntries(adO, ajH).setEntries(abg, aiB).setOutput(agl)
    config.shaped_recipe(aeN).setEntries(aac, aiB).setOutput(aeN)
    config.shaped_recipe(aeF).setEntries(aaw, aiB).setOutput(aeF)
    config.shaped_recipe(abV).setEntries(aae, aiB).setOutput(abV)
    config.smelting_recipe("diamond_from_blasting", abX).add_ingredient(agf).setXp(aki).setOutput(aiB).setCookingTime(
        akf)
    config.smelting_recipe("diamond_from_smelting").add_ingredient(agf).setXp(aki).setOutput(aiB)
    config.shaped_recipe(adV).setEntries(aap, aiB).setOutput(adV)
    config.shaped_recipe(afB).setEntries(adO, ajH).setEntries(adT, aiB).setOutput(afB)
    config.shaped_recipe(acQ).setEntries(aag, aiB).setOutput(acQ)
    config.shaped_recipe(acZ).setEntries(adO, ajH).setEntries(abd, aiB).setOutput(acZ)
    config.shaped_recipe(adL).setEntries(aed, ajH).setEntries(ajp, aiB).setOutput(adL)
    config.shaped_recipe(aet).setEntries(ajk, ajH).setEntries(adE, aiB).setOutput(aet)
    config.shaped_recipe(aiy).setEntries(adv, ajl).setEntries(ady, agh).setOutput((2, aiy))
    config.shaped_recipe("diorite_stairs").setEntries(aak, aiy).setOutput((4, "diorite_stairs"))
    config.shaped_recipe(ahG).setEntries(ajg, aib).setEntries(aag, agh).setEntries(aiT, ajW).setOutput(ahG)
    config.shapeless_recipe(agY).addInput(acU, 1).setOutput((9, agY))
    config.shapeless_recipe(acU).addInput(agY, 9).setOutput(acU)
    config.smelting_recipe("dried_kelp_from_campfire_cooking", aaE).add_ingredient(ajL).setXp(ake).setOutput(
        agY).setCookingTime(akh)
    config.smelting_recipe("dried_kelp_from_smelting").add_ingredient(ajL).setXp(ake).setOutput(agY)
    config.smelting_recipe("dried_kelp_from_smoking", acD).add_ingredient(ajL).setXp(ake).setOutput(agY).setCookingTime(
        akf)
    config.shaped_recipe(aiJ).setEntries(ajg, aib).setEntries(aag, agh).setOutput(aiJ)
    config.shapeless_recipe(aiM).addInput(aeI, 1).setOutput((9, aiM))
    config.shaped_recipe(aeI).setEntries(aac, aiM).setOutput(aeI)
    config.smelting_recipe("emerald_from_blasting", abX).add_ingredient(afJ).setXp(aki).setOutput(aiM).setCookingTime(
        akf)
    config.smelting_recipe("emerald_from_smelting").add_ingredient(afJ).setXp(aki).setOutput(aiM)
    config.shaped_recipe(acK).setEntries(aiX, ajJ).setEntries(aat, aik).setEntries(adU, aiB).setOutput(acK)
    config.shaped_recipe(ags).setEntries(aad, aik).setEntries(aiT, ahv).setOutput(ags)
    config.shapeless_recipe(ahv).addInput("ender_pearl", 1).addInput("blaze_powder", 1).setOutput(ahv)
    config.shaped_recipe(afT).setEntries(ajg, "ghast_tear").setEntries(aiT, ahv).setEntries(aag, ajF).setOutput(afT)
    config.shaped_recipe("end_rod").setEntries(aiY, abP).setEntries(ajp, ahs).setOutput((4, "end_rod"))
    config.shaped_recipe(acP).setEntries(aau, "end_stone").setOutput((4, acP))
    config.shaped_recipe("end_stone_brick_slab").setEntries(abd, acP).setOutput((6, "end_stone_brick_slab"))
    config.shaped_recipe("end_stone_brick_stairs").setEntries(aak, acP).setOutput((4, "end_stone_brick_stairs"))
    config.shaped_recipe("end_stone_brick_wall").setEntries(aan, acP).setOutput((6, "end_stone_brick_wall"))
    config.shapeless_recipe(abB).addInput("spider_eye", 1).addInput("brown_mushroom", 1).addInput(ajD, 1).setOutput(abB)
    config.shapeless_recipe("fire_charge").addInput(ahB, 1).addInput("blaze_powder", 1).setOutput((3, "fire_charge"))
    config.shaped_recipe(afE).setEntries([(0, 2), (1, 1), (2, 0)], ajH).setEntries([(2, 1), (2, 2)], ajh).setOutput(afE)
    config.shaped_recipe(adc).setEntries(aav, aiz).setEntries(adT, ajw).setOutput(adc)
    config.shapeless_recipe(add).addInput(agy, 1).addInput(ajw, 1).setOutput(add)
    config.shapeless_recipe(abw).addInput(ajt, 1).addInput("oxeye_daisy", 1).setOutput(abw)
    config.shaped_recipe(agQ).setEntries(aaW, ajB).setOutput(agQ)
    config.shaped_recipe(aiG).setEntries(aad, "#furnace_materials").setOutput(aiG)
    config.shaped_recipe(acR).setEntries(ajp, aiG).setEntries(aiY, ahT).setOutput(acR)
    config.smelting_recipe(ajF).add_ingredient("#sand").setXp(ake).setOutput(ajF)
    config.shaped_recipe("glass_bottle").setEntries(aaW, ajF).setOutput((3, "glass_bottle"))
    config.shaped_recipe(ahl).setEntries(aan, ajF).setOutput((16, ahl))
    config.shaped_recipe(aaT).setEntries(aad, agc).setEntries(aiT, afO).setOutput(aaT)
    config.shaped_recipe(ahu).setEntries(aau, aeb).setOutput(ahu)
    config.shaped_recipe(afj).setEntries(aad, ahh).setEntries(aiT, "apple").setOutput(afj)
    config.shaped_recipe(agE).setEntries(adO, ajH).setEntries(abg, ahh).setOutput(agE)
    config.shaped_recipe(afy).setEntries(aaw, ahh).setOutput(afy)
    config.shaped_recipe(aex).setEntries(aad, agc).setEntries(aiT, aiO).setOutput(aex)
    config.shaped_recipe(acu).setEntries(aae, ahh).setOutput(acu)
    config.shaped_recipe(aeM).setEntries(aap, ahh).setOutput(aeM)
    config.shaped_recipe(agG).setEntries(adO, ajH).setEntries(adT, ahh).setOutput(agG)
    config.shaped_recipe(adn).setEntries(aag, ahh).setOutput(adn)
    config.shaped_recipe(adA).setEntries(adO, ajH).setEntries(abd, ahh).setOutput(adA)
    config.shaped_recipe(aeR).setEntries(aed, ajH).setEntries(ajp, ahh).setOutput(aeR)
    config.shaped_recipe(afp).setEntries(ajk, ajH).setEntries(adE, ahh).setOutput(afp)
    config.shaped_recipe(aha).setEntries(aac, ahh).setOutput(aha)
    config.smelting_recipe(ahh).add_ingredient(agD).setXp(aki).setOutput(ahh)
    config.smelting_recipe("gold_ingot_from_blasting", abX).add_ingredient(agD).setXp(aki).setOutput(
        ahh).setCookingTime(akf)
    config.shapeless_recipe("gold_ingot_from_gold_block").addInput(aha, 1).setOutput((9, ahh)).setGroup(ahh)
    config.shaped_recipe("gold_ingot_from_nuggets").setEntries(aac, agc).setOutput(ahh).setGroup(ahh)
    config.shapeless_recipe(agc).addInput(ahh, 1).setOutput((9, agc))
    config.smelting_recipe("gold_nugget_from_blasting", abX).add_ingredient(aab).setXp(ake).setOutput(
        agc).setCookingTime(akf)
    config.smelting_recipe("gold_nugget_from_smelting").add_ingredient(aab).setXp(ake).setOutput(agc)
    config.shapeless_recipe(aix).addInput(aiy, 1).addInput(ajl, 1).setOutput(aix)
    config.shaped_recipe("granite_stairs").setEntries(aak, aix).setOutput((4, "granite_stairs"))
    config.shaped_recipe(agk).setEntries(aan, aho).setEntries(ajg, ajH).setOutput(agk).setGroup(aiZ)
    config.shaped_recipe(ahX).setEntries(abd, aho).setEntries(abj, aiz).setOutput(ahX).setGroup(ajY)
    config.shapeless_recipe("gray_bed_from_white_bed").addInput(ahI, 1).addInput(aic, 1).setOutput(ahX).setGroup(aim)
    config.shaped_recipe("gray_carpet").setEntries(adT, aho).setOutput((3, "gray_carpet")).setGroup(ajn)
    config.shaped_recipe("gray_carpet_from_white_carpet").setEntries(aad, afq).setEntries(aiT, aic).setOutput(
        (8, "gray_carpet")).setGroup(ajn)
    config.shapeless_recipe("gray_concrete_powder").addInput(aic, 1).addInput(ajM, 4).addInput(ajo, 4).setOutput(
        (8, "gray_concrete_powder")).setGroup(acX)
    config.shapeless_recipe(aic).addInput(ahJ, 1).addInput(ahz, 1).setOutput((2, aic))
    config.smelting_recipe(abh).add_ingredient(adl).setXp(ake).setOutput(abh)
    config.shaped_recipe(aca).setEntries(aad, ajF).setEntries(aiT, aic).setOutput((8, aca)).setGroup(aep)
    config.shaped_recipe("gray_stained_glass_pane").setEntries(aan, aca).setOutput(
        (16, "gray_stained_glass_pane")).setGroup(abQ)
    config.shaped_recipe("gray_stained_glass_pane_from_glass_pane").setEntries(aad, ahl).setEntries(aiT, aic).setOutput(
        (8, "gray_stained_glass_pane")).setGroup(abQ)
    config.shaped_recipe(adl).setEntries(aad, agP).setEntries(aiT, aic).setOutput((8, adl)).setGroup(acd)
    config.shapeless_recipe(aho).addInput(aic, 1).addInput(ahf, 1).setOutput(aho).setGroup(ajP)
    config.shaped_recipe(afe).setEntries(aan, agz).setEntries(ajg, ajH).setOutput(afe).setGroup(aiZ)
    config.shaped_recipe(ahq).setEntries(abd, agz).setEntries(abj, aiz).setOutput(ahq).setGroup(ajY)
    config.shapeless_recipe("green_bed_from_white_bed").addInput(ahI, 1).addInput(ahC, 1).setOutput(ahq).setGroup(aim)
    config.shaped_recipe("green_carpet").setEntries(adT, agz).setOutput((3, "green_carpet")).setGroup(ajn)
    config.shaped_recipe("green_carpet_from_white_carpet").setEntries(aad, afq).setEntries(aiT, ahC).setOutput(
        (8, "green_carpet")).setGroup(ajn)
    config.shapeless_recipe("green_concrete_powder").addInput(ahC, 1).addInput(ajM, 4).addInput(ajo, 4).setOutput(
        (8, "green_concrete_powder")).setGroup(acX)
    config.smelting_recipe(ahC).add_ingredient("cactus").setXp(aki).setOutput(ahC)
    config.smelting_recipe(aaP).add_ingredient(acO).setXp(ake).setOutput(aaP)
    config.shaped_recipe(abM).setEntries(aad, ajF).setEntries(aiT, ahC).setOutput((8, abM)).setGroup(aep)
    config.shaped_recipe("green_stained_glass_pane").setEntries(aan, abM).setOutput(
        (16, "green_stained_glass_pane")).setGroup(abQ)
    config.shaped_recipe("green_stained_glass_pane_from_glass_pane").setEntries(aad, ahl).setEntries(aiT,
                                                                                                     ahC).setOutput(
        (8, "green_stained_glass_pane")).setGroup(abQ)
    config.shaped_recipe(acO).setEntries(aad, agP).setEntries(aiT, ahC).setOutput((8, acO)).setGroup(acd)
    config.shapeless_recipe(agz).addInput(ahC, 1).addInput(ahf, 1).setOutput(agz).setGroup(ajP)
    config.shaped_recipe(agK).setEntries(adQ, ajH).setEntries(aiX, agW).setEntries(adU, aiz).setOutput(agK)
    config.shaped_recipe(ahy).setEntries(aac, ajr).setOutput(ahy)
    config.shaped_recipe(aaz).setEntries(adT, agy).setOutput(aaz)
    config.shaped_recipe(adp).setEntries(aau, ahL).setOutput(adp)
    config.shaped_recipe(agd).setEntries(aau, afi).setOutput(agd)
    config.shapeless_recipe(afi).addInput(agd, 1).addInput("glass_bottle", 4).setOutput((4, afi))
    config.shaped_recipe(aje).setEntries(aiT, ajE).setEntries([(0, 0), (0, 1), (1, 2), (2, 0), (2, 1)], agy).setOutput(
        aje)
    config.shaped_recipe(adg).setEntries(ajp, aje).setEntries(aiY, ahT).setOutput(adg)
    config.shaped_recipe(air).setEntries(adO, ajH).setEntries(abg, agy).setOutput(air)
    config.shaped_recipe("iron_bars").setEntries(aan, agy).setOutput((16, "iron_bars"))
    config.shaped_recipe(agv).setEntries(aac, agy).setOutput(agv)
    config.shaped_recipe(agF).setEntries(aaw, agy).setOutput(agF)
    config.shaped_recipe(ads).setEntries(aae, agy).setOutput(ads)
    config.shaped_recipe("iron_door").setEntries(aal, agy).setOutput((3, "iron_door"))
    config.shaped_recipe(afX).setEntries(aap, agy).setOutput(afX)
    config.shaped_recipe(ahR).setEntries(adO, ajH).setEntries(adT, agy).setOutput(ahR)
    config.smelting_recipe(agy).add_ingredient(aio).setXp(akj).setOutput(agy)
    config.smelting_recipe("iron_ingot_from_blasting", abX).add_ingredient(aio).setXp(akj).setOutput(
        agy).setCookingTime(akf)
    config.shapeless_recipe("iron_ingot_from_iron_block").addInput(agv, 1).setOutput((9, agy)).setGroup(agy)
    config.shaped_recipe("iron_ingot_from_nuggets").setEntries(aac, afN).setOutput(agy).setGroup(agy)
    config.shaped_recipe(aej).setEntries(aag, agy).setOutput(aej)
    config.shapeless_recipe(afN).addInput(agy, 1).setOutput((9, afN))
    config.smelting_recipe("iron_nugget_from_blasting", abX).add_ingredient(aaa).setXp(ake).setOutput(
        afN).setCookingTime(akf)
    config.smelting_recipe("iron_nugget_from_smelting").add_ingredient(aaa).setXp(ake).setOutput(afN)
    config.shaped_recipe(aff).setEntries(adO, ajH).setEntries(abd, agy).setOutput(aff)
    config.shaped_recipe(agm).setEntries(aed, ajH).setEntries(ajp, agy).setOutput(agm)
    config.shaped_recipe(agx).setEntries(ajk, ajH).setEntries(adE, agy).setOutput(agx)
    config.shaped_recipe(aei).setEntries(aau, agy).setOutput(aei)
    config.shaped_recipe(agC).setEntries(aad, ajH).setEntries(aiT, aiC).setOutput(agC)
    config.shaped_recipe(adY).setEntries(ajp, "carved_pumpkin").setEntries(aiY, ajv).setOutput(adY)
    config.shaped_recipe(aiw).setEntries(aad, aiz).setEntries(aiT, aiB).setOutput(aiw)
    config.shaped_recipe(afG).setEntries(aao, aev).setOutput(afG).setGroup(ajR)
    config.shapeless_recipe(aew).addInput(aev, 1).setOutput(aew).setGroup(aeC)
    config.shaped_recipe("jungle_door").setEntries(aal, aev).setOutput((3, "jungle_door")).setGroup(afK)
    config.shaped_recipe("jungle_fence").setEntries(adw, ajH).setEntries(aaw, aev).setOutput(
        (3, "jungle_fence")).setGroup(afg)
    config.shaped_recipe(acr).setEntries(aaw, ajH).setEntries(adw, aev).setOutput(acr).setGroup(acp)
    config.shapeless_recipe(aev).addInput("#jungle_logs", 1).setOutput((4, aev)).setGroup(aiV)
    config.shaped_recipe(abx).setEntries(adT, aev).setOutput(abx).setGroup(abq)
    config.shaped_recipe("jungle_sign").setEntries(aan, aev).setEntries(ajg, ajH).setOutput(
        (3, "jungle_sign")).setGroup(ajO)
    config.shaped_recipe("jungle_stairs").setEntries(aak, aev).setOutput((4, "jungle_stairs")).setGroup(afa)
    config.shaped_recipe("jungle_trapdoor").setEntries(aan, aev).setOutput((2, "jungle_trapdoor")).setGroup(adf)
    config.shaped_recipe("jungle_wood").setEntries(aau, "jungle_log").setOutput((3, "jungle_wood")).setGroup(ajN)
    config.shaped_recipe("ladder").setEntries(aai, ajH).setOutput((3, "ladder"))
    config.shaped_recipe(aiv).setEntries(aiT, ajv).setEntries(aad, afN).setOutput(aiv)
    config.shaped_recipe(afQ).setEntries(aac, afv).setOutput(afQ)
    config.smelting_recipe("lapis_from_blasting", abX).add_ingredient(ahP).setXp(akg).setOutput(afv).setCookingTime(akf)
    config.smelting_recipe("lapis_from_smelting").add_ingredient(ahP).setXp(akg).setOutput(afv)
    config.shapeless_recipe(afv).addInput(afQ, 1).setOutput((9, afv))
    config.shaped_recipe("lead").setEntries([(0, 0), (0, 1), (1, 0), (2, 2)], ajh).setEntries(aiT, agH).setOutput(
        (2, "lead"))
    config.shaped_recipe(aiC).setEntries(aau, "rabbit_hide").setOutput(aiC)
    config.shaped_recipe(ael).setEntries(aaw, aiC).setOutput(ael)
    config.shaped_recipe(abW).setEntries(aae, aiC).setOutput(abW)
    config.shaped_recipe(adz).setEntries(aap, aiC).setOutput(adz)
    config.shaped_recipe(abI).setEntries(aai, aiC).setOutput(abI)
    config.shaped_recipe(acW).setEntries(aag, aiC).setOutput(acW)
    config.shaped_recipe(aiL).setEntries([(0, 0), (1, 0), (1, 2), (2, 0)], aeu).setEntries(aiT, ahA).setOutput(aiL)
    config.shaped_recipe(ajC).setEntries(aiY, agh).setEntries(ajp, ajH).setOutput(ajC)
    config.shaped_recipe(acw).setEntries(aan, adm).setEntries(ajg, ajH).setOutput(acw).setGroup(aiZ)
    config.shaped_recipe(adR).setEntries(abd, adm).setEntries(abj, aiz).setOutput(adR).setGroup(ajY)
    config.shapeless_recipe("light_blue_bed_from_white_bed").addInput(ahI, 1).addInput(adW, 1).setOutput(adR).setGroup(
        aim)
    config.shaped_recipe("light_blue_carpet").setEntries(adT, adm).setOutput((3, "light_blue_carpet")).setGroup(ajn)
    config.shaped_recipe("light_blue_carpet_from_white_carpet").setEntries(aad, afq).setEntries(aiT, adW).setOutput(
        (8, "light_blue_carpet")).setGroup(ajn)
    config.shapeless_recipe("light_blue_concrete_powder").addInput(adW, 1).addInput(ajM, 4).addInput(ajo, 4).setOutput(
        (8, "light_blue_concrete_powder")).setGroup(acX)
    config.shapeless_recipe("light_blue_dye_from_blue_orchid").addInput("blue_orchid", 1).setOutput(adW).setGroup(adW)
    config.shapeless_recipe("light_blue_dye_from_blue_white_dye").addInput(aif, 1).addInput(ahz, 1).setOutput(
        (2, adW)).setGroup(adW)
    config.smelting_recipe(aaA).add_ingredient(abk).setXp(ake).setOutput(aaA)
    config.shaped_recipe(aaL).setEntries(aad, ajF).setEntries(aiT, adW).setOutput((8, aaL)).setGroup(aep)
    config.shaped_recipe("light_blue_stained_glass_pane").setEntries(aan, aaL).setOutput(
        (16, "light_blue_stained_glass_pane")).setGroup(abQ)
    config.shaped_recipe("light_blue_stained_glass_pane_from_glass_pane").setEntries(aad, ahl).setEntries(aiT,
                                                                                                          adW).setOutput(
        (8, "light_blue_stained_glass_pane")).setGroup(abQ)
    config.shaped_recipe(abk).setEntries(aad, agP).setEntries(aiT, adW).setOutput((8, abk)).setGroup(acd)
    config.shapeless_recipe(adm).addInput(adW, 1).addInput(ahf, 1).setOutput(adm).setGroup(ajP)
    config.shaped_recipe(acv).setEntries(aan, adq).setEntries(ajg, ajH).setOutput(acv).setGroup(aiZ)
    config.shaped_recipe(adB).setEntries(abd, adq).setEntries(abj, aiz).setOutput(adB).setGroup(ajY)
    config.shapeless_recipe("light_gray_bed_from_white_bed").addInput(ahI, 1).addInput(adX, 1).setOutput(adB).setGroup(
        aim)
    config.shaped_recipe("light_gray_carpet").setEntries(adT, adq).setOutput((3, "light_gray_carpet")).setGroup(ajn)
    config.shaped_recipe("light_gray_carpet_from_white_carpet").setEntries(aad, afq).setEntries(aiT, adX).setOutput(
        (8, "light_gray_carpet")).setGroup(ajn)
    config.shapeless_recipe("light_gray_concrete_powder").addInput(adX, 1).addInput(ajM, 4).addInput(ajo, 4).setOutput(
        (8, "light_gray_concrete_powder")).setGroup(acX)
    config.shapeless_recipe("light_gray_dye_from_azure_bluet").addInput("azure_bluet", 1).setOutput(adX).setGroup(adX)
    config.shapeless_recipe("light_gray_dye_from_black_white_dye").addInput(ahJ, 1).addInput(ahz, 2).setOutput(
        (3, adX)).setGroup(adX)
    config.shapeless_recipe("light_gray_dye_from_gray_white_dye").addInput(aic, 1).addInput(ahz, 1).setOutput(
        (2, adX)).setGroup(adX)
    config.shapeless_recipe("light_gray_dye_from_oxeye_daisy").addInput("oxeye_daisy", 1).setOutput(adX).setGroup(adX)
    config.shapeless_recipe("light_gray_dye_from_white_tulip").addInput("white_tulip", 1).setOutput(adX).setGroup(adX)
    config.smelting_recipe(aaC).add_ingredient(abr).setXp(ake).setOutput(aaC)
    config.shaped_recipe(aaK).setEntries(aad, ajF).setEntries(aiT, adX).setOutput((8, aaK)).setGroup(aep)
    config.shaped_recipe("light_gray_stained_glass_pane").setEntries(aan, aaK).setOutput(
        (16, "light_gray_stained_glass_pane")).setGroup(abQ)
    config.shaped_recipe("light_gray_stained_glass_pane_from_glass_pane").setEntries(aad, ahl).setEntries(aiT,
                                                                                                          adX).setOutput(
        (8, "light_gray_stained_glass_pane")).setGroup(abQ)
    config.shaped_recipe(abr).setEntries(aad, agP).setEntries(aiT, adX).setOutput((8, abr)).setGroup(acd)
    config.shapeless_recipe(adq).addInput(adX, 1).addInput(ahf, 1).setOutput(adq).setGroup(ajP)
    config.shaped_recipe(aay).setEntries(adT, ahh).setOutput(aay)
    config.shaped_recipe(afW).setEntries(aan, ahK).setEntries(ajg, ajH).setOutput(afW).setGroup(aiZ)
    config.shaped_recipe(ahS).setEntries(abd, ahK).setEntries(abj, aiz).setOutput(ahS).setGroup(ajY)
    config.shapeless_recipe("lime_bed_from_white_bed").addInput(ahI, 1).addInput(aig, 1).setOutput(ahS).setGroup(aim)
    config.shaped_recipe("lime_carpet").setEntries(adT, ahK).setOutput((3, "lime_carpet")).setGroup(ajn)
    config.shaped_recipe("lime_carpet_from_white_carpet").setEntries(aad, afq).setEntries(aiT, aig).setOutput(
        (8, "lime_carpet")).setGroup(ajn)
    config.shapeless_recipe("lime_concrete_powder").addInput(aig, 1).addInput(ajM, 4).addInput(ajo, 4).setOutput(
        (8, "lime_concrete_powder")).setGroup(acX)
    config.shapeless_recipe(aig).addInput(ahC, 1).addInput(ahz, 1).setOutput((2, aig))
    config.smelting_recipe("lime_dye_from_smelting").add_ingredient("sea_pickle").setXp(ake).setOutput(aig)
    config.smelting_recipe(abe).add_ingredient(adt).setXp(ake).setOutput(abe)
    config.shaped_recipe(abR).setEntries(aad, ajF).setEntries(aiT, aig).setOutput((8, abR)).setGroup(aep)
    config.shaped_recipe("lime_stained_glass_pane").setEntries(aan, abR).setOutput(
        (16, "lime_stained_glass_pane")).setGroup(abQ)
    config.shaped_recipe("lime_stained_glass_pane_from_glass_pane").setEntries(aad, ahl).setEntries(aiT, aig).setOutput(
        (8, "lime_stained_glass_pane")).setGroup(abQ)
    config.shaped_recipe(adt).setEntries(aad, agP).setEntries(aiT, aig).setOutput((8, adt)).setGroup(acd)
    config.shapeless_recipe(ahK).addInput(aig, 1).addInput(ahf, 1).setOutput(ahK).setGroup(ajP)
    config.shaped_recipe(ahH).setEntries(aad, abu).setEntries(aiT, ada).setOutput(ahH)
    config.shaped_recipe(ajK).setEntries(adN, aiz).setEntries(adT, ajh).setOutput(ajK)
    config.shaped_recipe(aec).setEntries(aan, afr).setEntries(ajg, ajH).setOutput(aec).setGroup(aiZ)
    config.shaped_recipe(afD).setEntries(abd, afr).setEntries(abj, aiz).setOutput(afD).setGroup(ajY)
    config.shapeless_recipe("magenta_bed_from_white_bed").addInput(ahI, 1).addInput(agp, 1).setOutput(afD).setGroup(aim)
    config.shaped_recipe("magenta_carpet").setEntries(adT, afr).setOutput((3, "magenta_carpet")).setGroup(ajn)
    config.shaped_recipe("magenta_carpet_from_white_carpet").setEntries(aad, afq).setEntries(aiT, agp).setOutput(
        (8, "magenta_carpet")).setGroup(ajn)
    config.shapeless_recipe("magenta_concrete_powder").addInput(agp, 1).addInput(ajM, 4).addInput(ajo, 4).setOutput(
        (8, "magenta_concrete_powder")).setGroup(acX)
    config.shapeless_recipe("magenta_dye_from_allium").addInput("allium", 1).setOutput(agp).setGroup(agp)
    config.shapeless_recipe("magenta_dye_from_blue_red_pink").addInput(aif, 1).addInput(aiI, 1).addInput(aij,
                                                                                                         1).setOutput(
        (3, agp)).setGroup(agp)
    config.shapeless_recipe("magenta_dye_from_blue_red_white_dye").addInput(aif, 1).addInput(aiI, 2).addInput(ahz,
                                                                                                              1).setOutput(
        (4, agp)).setGroup(agp)
    config.shapeless_recipe("magenta_dye_from_lilac").addInput("lilac", 1).setOutput(acT).setGroup(agp)
    config.shapeless_recipe("magenta_dye_from_purple_and_pink").addInput(agw, 1).addInput(aij, 1).setOutput(
        acT).setGroup(agp)
    config.smelting_recipe(aaG).add_ingredient(abU).setXp(ake).setOutput(aaG)
    config.shaped_recipe(abv).setEntries(aad, ajF).setEntries(aiT, agp).setOutput((8, abv)).setGroup(aep)
    config.shaped_recipe("magenta_stained_glass_pane").setEntries(aan, abv).setOutput(
        (16, "magenta_stained_glass_pane")).setGroup(abQ)
    config.shaped_recipe("magenta_stained_glass_pane_from_glass_pane").setEntries(aad, ahl).setEntries(aiT,
                                                                                                       agp).setOutput(
        (8, "magenta_stained_glass_pane")).setGroup(abQ)
    config.shaped_recipe(abU).setEntries(aad, agP).setEntries(aiT, agp).setOutput((8, abU)).setGroup(acd)
    config.shapeless_recipe(afr).addInput(agp, 1).addInput(ahf, 1).setOutput(afr).setGroup(ajP)
    config.shaped_recipe(afL).setEntries(aau, agi).setOutput(afL)
    config.shapeless_recipe(agi).addInput("blaze_powder", 1).addInput(agH, 1).setOutput(agi)
    config.shaped_recipe(ajV).setEntries(aad, ajt).setEntries(aiT, aiE).setOutput(ajV)
    config.shaped_recipe(ajI).setEntries(aac, afO).setOutput(ajI)
    config.shapeless_recipe(afF).addInput(afO, 1).setOutput(afF)
    config.shaped_recipe(ahT).setEntries(aao, agy).setOutput(ahT)
    config.shapeless_recipe(abs).addInput(ajt, 1).addInput("enchanted_golden_apple", 1).setOutput(abs)
    config.shapeless_recipe(acB).addInput(agh, 1).addInput("vine", 1).setOutput(acB)
    config.shaped_recipe("mossy_cobblestone_slab").setEntries(abd, acB).setOutput((6, "mossy_cobblestone_slab"))
    config.shaped_recipe("mossy_cobblestone_stairs").setEntries(aak, acB).setOutput((4, "mossy_cobblestone_stairs"))
    config.shaped_recipe("mossy_cobblestone_wall").setEntries(aan, acB).setOutput((6, "mossy_cobblestone_wall"))
    config.shapeless_recipe(abZ).addInput(afh, 1).addInput("vine", 1).setOutput(abZ)
    config.shaped_recipe("mossy_stone_brick_slab").setEntries(abd, abZ).setOutput((6, "mossy_stone_brick_slab"))
    config.shaped_recipe("mossy_stone_brick_stairs").setEntries(aak, abZ).setOutput((4, "mossy_stone_brick_stairs"))
    config.shaped_recipe("mossy_stone_brick_wall").setEntries(aan, abZ).setOutput((6, "mossy_stone_brick_wall"))
    config.shapeless_recipe(aeX).addInput("brown_mushroom", 1).addInput("red_mushroom", 1).addInput("bowl",
                                                                                                    1).setOutput(aeX)
    config.shaped_recipe(adh).setEntries(aac, ada).setOutput(adh)
    config.shapeless_recipe(ada).addInput(ade, 4).addInput(ahh, 4).setOutput(ada).setGroup(ada)
    config.shapeless_recipe("netherite_ingot_from_netherite_block").addInput(adh, 1).setOutput((9, ada)).setGroup(ada)
    config.smelting_recipe(ade).add_ingredient(adZ).setXp(akd).setOutput(ade)
    config.smelting_recipe("netherite_scrap_from_blasting", abX).add_ingredient(adZ).setXp(akd).setOutput(
        ade).setCookingTime(akf)
    config.smelting_recipe(afk).add_ingredient("netherrack").setXp(ake).setOutput(afk)
    config.shaped_recipe(aeV).setEntries(aau, afk).setOutput(aeV)
    config.shaped_recipe("nether_brick_fence").setEntries(aaw, aeV).setEntries(adw, afk).setOutput(
        (6, "nether_brick_fence"))
    config.shaped_recipe(aco).setEntries(abd, aeV).setOutput((6, aco))
    config.shaped_recipe("nether_brick_stairs").setEntries(aak, aeV).setOutput((4, "nether_brick_stairs"))
    config.shaped_recipe("nether_brick_wall").setEntries(aan, aeV).setOutput((6, "nether_brick_wall"))
    config.shaped_recipe(acx).setEntries(aac, afC).setOutput(acx)
    config.shaped_recipe(agS).setEntries(aad, aiz).setEntries(aiT, aib).setOutput(agS)
    config.shaped_recipe(ahU).setEntries(aao, agN).setOutput(ahU).setGroup(ajR)
    config.shapeless_recipe(agX).addInput(agN, 1).setOutput(agX).setGroup(aeC)
    config.shaped_recipe("oak_door").setEntries(aal, agN).setOutput((3, "oak_door")).setGroup(afK)
    config.shaped_recipe("oak_fence").setEntries(adw, ajH).setEntries(aaw, agN).setOutput((3, "oak_fence")).setGroup(
        afg)
    config.shaped_recipe(aea).setEntries(aaw, ajH).setEntries(adw, agN).setOutput(aea).setGroup(acp)
    config.shapeless_recipe(agN).addInput("#oak_logs", 1).setOutput((4, agN)).setGroup(aiV)
    config.shaped_recipe(abY).setEntries(adT, agN).setOutput(abY).setGroup(abq)
    config.shaped_recipe("oak_sign").setEntries(aan, agN).setEntries(ajg, ajH).setOutput((3, "oak_sign")).setGroup(ajO)
    config.shaped_recipe("oak_stairs").setEntries(aak, agN).setOutput((4, "oak_stairs")).setGroup(afa)
    config.shaped_recipe("oak_trapdoor").setEntries(aan, agN).setOutput((2, "oak_trapdoor")).setGroup(adf)
    config.shaped_recipe("oak_wood").setEntries(aau, "oak_log").setOutput((3, "oak_wood")).setGroup(ajN)
    config.shaped_recipe(ahZ).setEntries([(2, 1)], ajl).setEntries(adN, aib).setEntries(aaj, agh).setOutput(ahZ)
    config.shaped_recipe(aeL).setEntries(aan, ago).setEntries(ajg, ajH).setOutput(aeL).setGroup(aiZ)
    config.shaped_recipe(agA).setEntries(abd, ago).setEntries(abj, aiz).setOutput(agA).setGroup(ajY)
    config.shapeless_recipe("orange_bed_from_white_bed").addInput(ahI, 1).addInput(agR, 1).setOutput(agA).setGroup(aim)
    config.shaped_recipe("orange_carpet").setEntries(adT, ago).setOutput((3, "orange_carpet")).setGroup(ajn)
    config.shaped_recipe("orange_carpet_from_white_carpet").setEntries(aad, afq).setEntries(aiT, agR).setOutput(
        (8, "orange_carpet")).setGroup(ajn)
    config.shapeless_recipe("orange_concrete_powder").addInput(agR, 1).addInput(ajM, 4).addInput(ajo, 4).setOutput(
        (8, "orange_concrete_powder")).setGroup(acX)
    config.shapeless_recipe("orange_dye_from_orange_tulip").addInput("orange_tulip", 1).setOutput(agR).setGroup(agR)
    config.shapeless_recipe("orange_dye_from_red_yellow").addInput(aiI, 1).addInput(ahj, 1).setOutput(
        (2, agR)).setGroup(agR)
    config.smelting_recipe(aaH).add_ingredient(act).setXp(ake).setOutput(aaH)
    config.shaped_recipe(abF).setEntries(aad, ajF).setEntries(aiT, agR).setOutput((8, abF)).setGroup(aep)
    config.shaped_recipe("orange_stained_glass_pane").setEntries(aan, abF).setOutput(
        (16, "orange_stained_glass_pane")).setGroup(abQ)
    config.shaped_recipe("orange_stained_glass_pane_from_glass_pane").setEntries(aad, ahl).setEntries(aiT,
                                                                                                      agR).setOutput(
        (8, "orange_stained_glass_pane")).setGroup(abQ)
    config.shaped_recipe(act).setEntries(aad, agP).setEntries(aiT, agR).setOutput((8, act)).setGroup(acd)
    config.shapeless_recipe(ago).addInput(agR, 1).addInput(ahf, 1).setOutput(ago).setGroup(ajP)
    config.shapeless_recipe(ahm).addInput("ice", 9).setOutput(ahm)
    config.shaped_recipe(ahQ).setEntries(aad, ajH).setEntries(aiT, "#wool").setOutput(ahQ)
    config.shaped_recipe(ajt).setEntries(abd, agO).setOutput((3, ajt))
    config.shaped_recipe(afU).setEntries(aan, ahE).setEntries(ajg, ajH).setOutput(afU).setGroup(aiZ)
    config.shaped_recipe(aii).setEntries(abd, ahE).setEntries(abj, aiz).setOutput(aii).setGroup(ajY)
    config.shapeless_recipe("pink_bed_from_white_bed").addInput(ahI, 1).addInput(aij, 1).setOutput(aii).setGroup(aim)
    config.shaped_recipe("pink_carpet").setEntries(adT, ahE).setOutput((3, "pink_carpet")).setGroup(ajn)
    config.shaped_recipe("pink_carpet_from_white_carpet").setEntries(aad, afq).setEntries(aiT, aij).setOutput(
        (8, "pink_carpet")).setGroup(ajn)
    config.shapeless_recipe("pink_concrete_powder").addInput(aij, 1).addInput(ajM, 4).addInput(ajo, 4).setOutput(
        (8, "pink_concrete_powder")).setGroup(acX)
    config.shapeless_recipe("pink_dye_from_peony").addInput("peony", 1).setOutput(aez).setGroup(aij)
    config.shapeless_recipe("pink_dye_from_pink_tulip").addInput("pink_tulip", 1).setOutput(aij).setGroup(aij)
    config.shapeless_recipe("pink_dye_from_red_white_dye").addInput(aiI, 1).addInput(ahz, 1).setOutput(aez).setGroup(
        aij)
    config.smelting_recipe(aaZ).add_ingredient(adi).setXp(ake).setOutput(aaZ)
    config.shaped_recipe(abT).setEntries(aad, ajF).setEntries(aiT, aij).setOutput((8, abT)).setGroup(aep)
    config.shaped_recipe("pink_stained_glass_pane").setEntries(aan, abT).setOutput(
        (16, "pink_stained_glass_pane")).setGroup(abQ)
    config.shaped_recipe("pink_stained_glass_pane_from_glass_pane").setEntries(aad, ahl).setEntries(aiT, aij).setOutput(
        (8, "pink_stained_glass_pane")).setGroup(abQ)
    config.shaped_recipe(adi).setEntries(aad, agP).setEntries(aiT, aij).setOutput((8, adi)).setGroup(acd)
    config.shapeless_recipe(ahE).addInput(aij, 1).addInput(ahf, 1).setOutput(ahE).setGroup(ajP)
    config.shaped_recipe(ajq).setEntries(ajg, aib).setEntries([(0, 1), (0, 2), (2, 1), (2, 2)], agh).setEntries(abd,
                                                                                                                aiz).setEntries(
        aiT, agy).setOutput(ajq)
    config.shaped_recipe(acy).setEntries(aau, aia).setOutput((4, acy))
    config.shaped_recipe("polished_andesite_slab").setEntries(abd, acy).setOutput((6, "polished_andesite_slab"))
    config.shaped_recipe("polished_andesite_stairs").setEntries(aak, acy).setOutput((4, "polished_andesite_stairs"))
    config.shaped_recipe("polished_basalt").setEntries(aau, "basalt").setOutput((4, "polished_basalt"))
    config.shaped_recipe(abN).setEntries(aau, agV).setOutput((4, abN))
    config.shaped_recipe(aaF).setEntries(aau, abN).setOutput((4, aaF))
    config.shaped_recipe("polished_blackstone_brick_slab").setEntries(abd, aaF).setOutput(
        (6, "polished_blackstone_brick_slab"))
    config.shaped_recipe("polished_blackstone_brick_stairs").setEntries(aak, aaF).setOutput(
        (4, "polished_blackstone_brick_stairs"))
    config.shaped_recipe("polished_blackstone_brick_wall").setEntries(aan, aaF).setOutput(
        (6, "polished_blackstone_brick_wall"))
    config.shapeless_recipe(aaD).addInput(abN, 1).setOutput(aaD)
    config.shaped_recipe(aar).setEntries(adT, abN).setOutput(aar)
    config.shaped_recipe(aaM).setEntries(abd, abN).setOutput((6, aaM))
    config.shaped_recipe("polished_blackstone_stairs").setEntries(aak, abN).setOutput((4, "polished_blackstone_stairs"))
    config.shaped_recipe("polished_blackstone_wall").setEntries(aan, abN).setOutput((6, "polished_blackstone_wall"))
    config.shaped_recipe(acN).setEntries(aau, aiy).setOutput((4, acN))
    config.shaped_recipe("polished_diorite_stairs").setEntries(aak, acN).setOutput((4, "polished_diorite_stairs"))
    config.shaped_recipe(acJ).setEntries(aau, aix).setOutput((4, acJ))
    config.shaped_recipe("polished_granite_stairs").setEntries(aak, acJ).setOutput((4, "polished_granite_stairs"))
    config.smelting_recipe(abP).add_ingredient("chorus_fruit").setXp(ake).setOutput(abP)
    config.shaped_recipe("powered_rail").setEntries(ajg, aib).setEntries(aiT, ajH).setEntries(aam, ahh).setOutput(
        (6, "powered_rail"))
    config.shaped_recipe(agJ).setEntries(aau, acH).setOutput(agJ)
    config.shaped_recipe(ack).setEntries(aac, acH).setOutput(ack)
    config.shaped_recipe("prismarine_brick_slab").setEntries(abd, ack).setOutput((6, "prismarine_brick_slab"))
    config.shaped_recipe("prismarine_brick_stairs").setEntries(aak, ack).setOutput((4, "prismarine_brick_stairs"))
    config.shaped_recipe("prismarine_slab").setEntries(abd, agJ).setOutput((6, "prismarine_slab"))
    config.shaped_recipe("prismarine_stairs").setEntries(aak, agJ).setOutput((4, "prismarine_stairs"))
    config.shaped_recipe("prismarine_wall").setEntries(aan, agJ).setOutput((6, "prismarine_wall"))
    config.shapeless_recipe(agj).addInput("pumpkin", 1).addInput(ajD, 1).addInput(ajZ, 1).setOutput(agj)
    config.shapeless_recipe("pumpkin_seeds").addInput("pumpkin", 1).setOutput((4, "pumpkin_seeds"))
    config.shaped_recipe(aeT).setEntries(aan, afZ).setEntries(ajg, ajH).setOutput(aeT).setGroup(aiZ)
    config.shaped_recipe(ahc).setEntries(abd, afZ).setEntries(abj, aiz).setOutput(ahc).setGroup(ajY)
    config.shapeless_recipe("purple_bed_from_white_bed").addInput(ahI, 1).addInput(agw, 1).setOutput(ahc).setGroup(aim)
    config.shaped_recipe("purple_carpet").setEntries(adT, afZ).setOutput((3, "purple_carpet")).setGroup(ajn)
    config.shaped_recipe("purple_carpet_from_white_carpet").setEntries(aad, afq).setEntries(aiT, agw).setOutput(
        (8, "purple_carpet")).setGroup(ajn)
    config.shapeless_recipe("purple_concrete_powder").addInput(agw, 1).addInput(ajM, 4).addInput(ajo, 4).setOutput(
        (8, "purple_concrete_powder")).setGroup(acX)
    config.shapeless_recipe(agw).addInput(aif, 1).addInput(aiI, 1).setOutput((2, agw))
    config.smelting_recipe(aaJ).add_ingredient(acq).setXp(ake).setOutput(aaJ)
    config.shaped_recipe(abH).setEntries(aad, ajF).setEntries(aiT, agw).setOutput((8, abH)).setGroup(aep)
    config.shaped_recipe("purple_stained_glass_pane").setEntries(aan, abH).setOutput(
        (16, "purple_stained_glass_pane")).setGroup(abQ)
    config.shaped_recipe("purple_stained_glass_pane_from_glass_pane").setEntries(aad, ahl).setEntries(aiT,
                                                                                                      agw).setOutput(
        (8, "purple_stained_glass_pane")).setGroup(abQ)
    config.shaped_recipe(acq).setEntries(aad, agP).setEntries(aiT, agw).setOutput((8, acq)).setGroup(acd)
    config.shapeless_recipe(afZ).addInput(agw, 1).addInput(ahf, 1).setOutput(afZ).setGroup(ajP)
    config.shaped_recipe("purpur_block").setEntries(aau, abP).setOutput((4, "purpur_block"))
    config.shaped_recipe(aeA).setEntries(adE, afV).setOutput(aeA)
    config.shaped_recipe(afV).setEntries(abd, aas).setOutput((6, afV))
    config.shaped_recipe("purpur_stairs").setEntries(aak, aas).setOutput((4, "purpur_stairs"))
    config.smelting_recipe(ajl).add_ingredient(acm).setXp(akg).setOutput(ajl)
    config.shaped_recipe(afc).setEntries(aau, ajl).setOutput(afc)
    config.shaped_recipe("quartz_bricks").setEntries(aau, afc).setOutput((4, "quartz_bricks"))
    config.smelting_recipe("quartz_from_blasting", abX).add_ingredient(acm).setXp(akg).setOutput(ajl).setCookingTime(
        akf)
    config.shaped_recipe("quartz_pillar").setEntries(adE, afc).setOutput((2, "quartz_pillar"))
    config.shaped_recipe(afI).setEntries(abd, aaf).setOutput((6, afI))
    config.shaped_recipe("quartz_stairs").setEntries(aak, aaf).setOutput((4, "quartz_stairs"))
    config.shapeless_recipe("rabbit_stew_from_brown_mushroom").addInput(afm, 1).addInput(aeS, 1).addInput("bowl",
                                                                                                          1).addInput(
        aiO, 1).addInput("brown_mushroom", 1).setOutput(afH).setGroup(afH)
    config.shapeless_recipe("rabbit_stew_from_red_mushroom").addInput(afm, 1).addInput(aeS, 1).addInput("bowl",
                                                                                                        1).addInput(aiO,
                                                                                                                    1).addInput(
        "red_mushroom", 1).setOutput(afH).setGroup(afH)
    config.shaped_recipe("rail").setEntries(aiT, ajH).setEntries(aam, agy).setOutput((16, "rail"))
    config.shapeless_recipe(aib).addInput(adu, 1).setOutput((9, aib))
    config.shaped_recipe(adu).setEntries(aac, aib).setOutput(adu)
    config.smelting_recipe("redstone_from_blasting", abX).add_ingredient(afs).setXp(akj).setOutput(aib).setCookingTime(
        akf)
    config.smelting_recipe("redstone_from_smelting").add_ingredient(afs).setXp(akj).setOutput(aib)
    config.shaped_recipe(aeW).setEntries(aax, aib).setEntries(aiT, ahu).setOutput(aeW)
    config.shaped_recipe(adD).setEntries(aiY, ajH).setEntries(ajp, aib).setOutput(adD)
    config.shaped_recipe(agT).setEntries(aan, ail).setEntries(ajg, ajH).setOutput(agT).setGroup(aiZ)
    config.shaped_recipe(aiK).setEntries(abd, ail).setEntries(abj, aiz).setOutput(aiK).setGroup(ajY)
    config.shapeless_recipe("red_bed_from_white_bed").addInput(ahI, 1).addInput(aiI, 1).setOutput(aiK).setGroup(aim)
    config.shaped_recipe("red_carpet").setEntries(adT, ail).setOutput((3, "red_carpet")).setGroup(ajn)
    config.shaped_recipe("red_carpet_from_white_carpet").setEntries(aad, afq).setEntries(aiT, aiI).setOutput(
        (8, "red_carpet")).setGroup(ajn)
    config.shapeless_recipe("red_concrete_powder").addInput(aiI, 1).addInput(ajM, 4).addInput(ajo, 4).setOutput(
        (8, "red_concrete_powder")).setGroup(acX)
    config.shapeless_recipe("red_dye_from_beetroot").addInput("beetroot", 1).setOutput(aiI).setGroup(aiI)
    config.shapeless_recipe("red_dye_from_poppy").addInput("poppy", 1).setOutput(aiI).setGroup(aiI)
    config.shapeless_recipe("red_dye_from_rose_bush").addInput("rose_bush", 1).setOutput((2, aiI)).setGroup(aiI)
    config.shapeless_recipe("red_dye_from_tulip").addInput("red_tulip", 1).setOutput(aiI).setGroup(aiI)
    config.smelting_recipe(abn).add_ingredient(adP).setXp(ake).setOutput(abn)
    config.shaped_recipe(acn).setEntries(adv, afC).setEntries(ady, afk).setOutput(acn)
    config.shaped_recipe("red_nether_brick_slab").setEntries(abd, acn).setOutput((6, "red_nether_brick_slab"))
    config.shaped_recipe("red_nether_brick_stairs").setEntries(aak, acn).setOutput((4, "red_nether_brick_stairs"))
    config.shaped_recipe("red_nether_brick_wall").setEntries(aan, acn).setOutput((6, "red_nether_brick_wall"))
    config.shaped_recipe(aeh).setEntries(aau, "red_sand").setOutput(aeh)
    config.shaped_recipe(acc).setEntries(abd, ['red_sandstone', 'chiseled_red_sandstone']).setOutput((6, acc))
    config.shaped_recipe("red_sandstone_stairs").setEntries(aak, ['red_sandstone', 'chiseled_red_sandstone',
                                                                  'cut_red_sandstone']).setOutput(
        (4, "red_sandstone_stairs"))
    config.shaped_recipe("red_sandstone_wall").setEntries(aan, aeh).setOutput((6, "red_sandstone_wall"))
    config.shaped_recipe(aci).setEntries(aad, ajF).setEntries(aiT, aiI).setOutput((8, aci)).setGroup(aep)
    config.shaped_recipe("red_stained_glass_pane").setEntries(aan, aci).setOutput(
        (16, "red_stained_glass_pane")).setGroup(abQ)
    config.shaped_recipe("red_stained_glass_pane_from_glass_pane").setEntries(aad, ahl).setEntries(aiT, aiI).setOutput(
        (8, "red_stained_glass_pane")).setGroup(abQ)
    config.shaped_recipe(adP).setEntries(aad, agP).setEntries(aiT, aiI).setOutput((8, adP)).setGroup(acd)
    config.shapeless_recipe(ail).addInput(aiI, 1).addInput(ahf, 1).setOutput(ail).setGroup(ajP)
    config.shaped_recipe(ahV).setEntries(adQ, adD).setEntries(aiX, aib).setEntries(abj, ajA).setOutput(ahV)
    config.shaped_recipe(adJ).setEntries(aaj, "crying_obsidian").setEntries(abj, ahu).setOutput(adJ)
    config.shaped_recipe(ahO).setEntries(aau, ajM).setOutput(ahO)
    config.shaped_recipe(adG).setEntries(abd, ['sandstone', 'chiseled_sandstone']).setOutput((6, adG))
    config.shaped_recipe("sandstone_stairs").setEntries(aak,
                                                        ['sandstone', 'chiseled_sandstone', 'cut_sandstone']).setOutput(
        (4, "sandstone_stairs"))
    config.shaped_recipe("sandstone_wall").setEntries(aan, ahO).setOutput((6, "sandstone_wall"))
    config.shaped_recipe("scaffolding").setEntries(aiX, ajh).setEntries(aam, aiN).setOutput((6, "scaffolding"))
    config.shaped_recipe(agt).setEntries([(0, 0), (0, 2), (2, 0), (2, 2)], acH).setEntries(
        [(0, 1), (1, 0), (1, 1), (1, 2), (2, 1)], "prismarine_crystals").setOutput(agt)
    config.shaped_recipe(ajm).setEntries(adv, agy).setOutput(ajm)
    config.shaped_recipe(ajf).setEntries([(0, 0), (0, 1), (1, 1), (1, 2), (2, 0), (2, 1)], aiz).setEntries(aiX,
                                                                                                           agy).setOutput(
        ajf)
    config.shaped_recipe(afP).setEntries(aiY, ajE).setEntries(adH, "shulker_shell").setOutput(afP)
    config.shapeless_recipe(abz).addInput(ajt, 1).addInput("wither_skeleton_skull", 1).setOutput(abz)
    config.shapeless_recipe(agH).addInput(agb, 1).setOutput((9, agH))
    config.shaped_recipe(agb).setEntries(aac, agH).setOutput(agb)
    config.shaped_recipe(adS).setEntries(aav, aiz).setEntries(adT, agy).setOutput(adS)
    config.shaped_recipe(ajb).setEntries(aax, ajy).setEntries(aiT, aiG).setOutput(ajb)
    config.smelting_recipe(aeY).add_ingredient(afc).setXp(ake).setOutput(aeY)
    config.shaped_recipe("smooth_quartz_slab").setEntries(abd, aeY).setOutput((6, "smooth_quartz_slab"))
    config.shaped_recipe("smooth_quartz_stairs").setEntries(aak, aeY).setOutput((4, "smooth_quartz_stairs"))
    config.smelting_recipe(abD).add_ingredient(aeh).setXp(ake).setOutput(abD)
    config.shaped_recipe("smooth_red_sandstone_slab").setEntries(abd, abD).setOutput((6, "smooth_red_sandstone_slab"))
    config.shaped_recipe("smooth_red_sandstone_stairs").setEntries(aak, abD).setOutput(
        (4, "smooth_red_sandstone_stairs"))
    config.smelting_recipe(acS).add_ingredient(ahO).setXp(ake).setOutput(acS)
    config.shaped_recipe("smooth_sandstone_slab").setEntries(abd, acS).setOutput((6, "smooth_sandstone_slab"))
    config.shaped_recipe("smooth_sandstone_stairs").setEntries(aak, acS).setOutput((4, "smooth_sandstone_stairs"))
    config.smelting_recipe(aft).add_ingredient(ajA).setXp(ake).setOutput(aft)
    config.shaped_recipe(acA).setEntries(abd, aft).setOutput((6, acA))
    config.shaped_recipe("snow").setEntries(abd, ahd).setOutput((6, "snow"))
    config.shaped_recipe(ahd).setEntries(aau, "snowball").setOutput(ahd)
    config.shaped_recipe(aeQ).setEntries(abb, ajy).setEntries(aaV, ajH).setEntries(aiT, aaU).setOutput(aeQ)
    config.shaped_recipe(afd).setEntries(aiT, ahb).setEntries(aad, afN).setOutput(afd)
    config.shaped_recipe(ahb).setEntries(ajp, acb).setEntries(aiY, ajH).setEntries(ajk, aaU).setOutput((4, ahb))
    config.shaped_recipe("spectral_arrow").setEntries(aax, aeb).setEntries(aiT, aju).setOutput((2, "spectral_arrow"))
    config.smelting_recipe(aiS).add_ingredient("wet_sponge").setXp(akc).setOutput(aiS)
    config.shaped_recipe(age).setEntries(aao, aeO).setOutput(age).setGroup(ajR)
    config.shapeless_recipe(aeG).addInput(aeO, 1).setOutput(aeG).setGroup(aeC)
    config.shaped_recipe("spruce_door").setEntries(aal, aeO).setOutput((3, "spruce_door")).setGroup(afK)
    config.shaped_recipe("spruce_fence").setEntries(adw, ajH).setEntries(aaw, aeO).setOutput(
        (3, "spruce_fence")).setGroup(afg)
    config.shaped_recipe(ach).setEntries(aaw, ajH).setEntries(adw, aeO).setOutput(ach).setGroup(acp)
    config.shapeless_recipe(aeO).addInput("#spruce_logs", 1).setOutput((4, aeO)).setGroup(aiV)
    config.shaped_recipe(abm).setEntries(adT, aeO).setOutput(abm).setGroup(abq)
    config.shaped_recipe("spruce_sign").setEntries(aan, aeO).setEntries(ajg, ajH).setOutput(
        (3, "spruce_sign")).setGroup(ajO)
    config.shaped_recipe("spruce_stairs").setEntries(aak, aeO).setOutput((4, "spruce_stairs")).setGroup(afa)
    config.shaped_recipe("spruce_trapdoor").setEntries(aan, aeO).setOutput((2, "spruce_trapdoor")).setGroup(adf)
    config.shaped_recipe("spruce_wood").setEntries(aau, "spruce_log").setOutput((3, "spruce_wood")).setGroup(ajN)
    config.shaped_recipe(ajH).setEntries(adE, aiz).setOutput((4, ajH)).setGroup(aiR)
    config.shaped_recipe(aey).setEntries(aiY, ajq).setEntries(ajp, agH).setOutput(aey)
    config.shaped_recipe("stick_from_bamboo_item").setEntries(adE, aiN).setOutput(ajH).setGroup(aiR)
    config.smelting_recipe(ajA).add_ingredient(agh).setXp(ake).setOutput(ajA)
    config.shaped_recipe(afY).setEntries(aiX, agy).setEntries(abj, ajA).setOutput(afY)
    config.shaped_recipe(ahF).setEntries(adO, ajH).setEntries(abg, abl).setOutput(ahF)
    config.shaped_recipe(afh).setEntries(aau, ajA).setOutput((4, afh))
    config.shaped_recipe(acM).setEntries(abd, afh).setOutput((6, acM))
    config.shaped_recipe("stone_brick_stairs").setEntries(aak, afh).setOutput((4, "stone_brick_stairs"))
    config.shaped_recipe("stone_brick_wall").setEntries(aan, afh).setOutput((6, "stone_brick_wall"))
    config.shapeless_recipe(afb).addInput(ajA, 1).setOutput(afb)
    config.shaped_recipe(ahn).setEntries(adO, ajH).setEntries(adT, abl).setOutput(ahn)
    config.shaped_recipe(aeD).setEntries(adO, ajH).setEntries(abd, abl).setOutput(aeD)
    config.shaped_recipe(abE).setEntries(adT, ajA).setOutput(abE)
    config.shaped_recipe(afu).setEntries(aed, ajH).setEntries(ajp, abl).setOutput(afu)
    config.shaped_recipe("stone_stairs").setEntries(aak, ajA).setOutput((4, "stone_stairs"))
    config.shaped_recipe(afR).setEntries(ajk, ajH).setEntries(adE, abl).setOutput(afR)
    config.shaped_recipe("stripped_acacia_wood").setEntries(aau, "stripped_acacia_log").setOutput(
        (3, "stripped_acacia_wood")).setGroup(ajN)
    config.shaped_recipe("stripped_birch_wood").setEntries(aau, "stripped_birch_log").setOutput(
        (3, "stripped_birch_wood")).setGroup(ajN)
    config.shaped_recipe("stripped_crimson_hyphae").setEntries(aau, "stripped_crimson_stem").setOutput(
        (3, "stripped_crimson_hyphae")).setGroup(ajN)
    config.shaped_recipe("stripped_dark_oak_wood").setEntries(aau, "stripped_dark_oak_log").setOutput(
        (3, "stripped_dark_oak_wood")).setGroup(ajN)
    config.shaped_recipe("stripped_jungle_wood").setEntries(aau, "stripped_jungle_log").setOutput(
        (3, "stripped_jungle_wood")).setGroup(ajN)
    config.shaped_recipe("stripped_oak_wood").setEntries(aau, "stripped_oak_log").setOutput(
        (3, "stripped_oak_wood")).setGroup(ajN)
    config.shaped_recipe("stripped_spruce_wood").setEntries(aau, "stripped_spruce_log").setOutput(
        (3, "stripped_spruce_wood")).setGroup(ajN)
    config.shaped_recipe("stripped_warped_hyphae").setEntries(aau, "stripped_warped_stem").setOutput(
        (3, "stripped_warped_hyphae")).setGroup(ajN)
    config.shapeless_recipe("sugar_from_honey_bottle").addInput(afi, 1).setOutput((3, ajD)).setGroup(ajD)
    config.shapeless_recipe("sugar_from_sugar_cane").addInput(agO, 1).setOutput(ajD).setGroup(ajD)
    config.shaped_recipe(ajj).setEntries(aiT, ahy).setEntries(aax, aib).setOutput(ajj)
    config.smelting_recipe(agP).add_ingredient(ajU).setXp(akb).setOutput(agP)
    config.shaped_recipe(aka).setEntries(aax, ['sand', 'red_sand']).setEntries([(0, 0), (0, 2), (1, 1), (2, 0), (2, 2)],
                                                                               ahB).setOutput(aka)
    config.shaped_recipe(afz).setEntries(ajp, aka).setEntries(aiY, ahT).setOutput(afz)
    config.shaped_recipe(ajv).setEntries(aiY, ajH).setEntries(ajp, acb).setOutput((4, ajv))
    config.shapeless_recipe(aeg).addInput(ajE, 1).addInput(aef, 1).setOutput(aeg)
    config.shaped_recipe(aef).setEntries(ajk, aiz).setEntries(aiY, ajH).setEntries(ajp, agy).setOutput((2, aef))
    config.shaped_recipe(aeo).setEntries(aap, "scute").setOutput(aeo)
    config.shapeless_recipe(aeH).addInput(aeZ, 1).setOutput(aeH).setGroup(aeC)
    config.shaped_recipe("warped_door").setEntries(aal, aeZ).setOutput((3, "warped_door")).setGroup(afK)
    config.shaped_recipe("warped_fence").setEntries(adw, ajH).setEntries(aaw, aeZ).setOutput(
        (3, "warped_fence")).setGroup(afg)
    config.shaped_recipe(acz).setEntries(aaw, ajH).setEntries(adw, aeZ).setOutput(acz).setGroup(acp)
    config.shaped_recipe(aaN).setEntries(ajp, afE).setEntries(aiT, "warped_fungus").setOutput(aaN)
    config.shaped_recipe("warped_hyphae").setEntries(aau, "warped_stem").setOutput((3, "warped_hyphae")).setGroup(ajN)
    config.shapeless_recipe(aeZ).addInput("#warped_stems", 1).setOutput((4, aeZ)).setGroup(aiV)
    config.shaped_recipe(abt).setEntries(adT, aeZ).setOutput(abt).setGroup(abq)
    config.shaped_recipe("warped_sign").setEntries(aan, aeZ).setEntries(ajg, ajH).setOutput(
        (3, "warped_sign")).setGroup(ajO)
    config.shaped_recipe("warped_stairs").setEntries(aak, aeZ).setOutput((4, "warped_stairs")).setGroup(afa)
    config.shaped_recipe("warped_trapdoor").setEntries(aan, aeZ).setOutput((2, "warped_trapdoor")).setGroup(adf)
    config.shapeless_recipe(ajr).addInput(ahy, 1).setOutput((9, ajr))
    config.shaped_recipe(afn).setEntries(aan, ahf).setEntries(ajg, ajH).setOutput(afn).setGroup(aiZ)
    config.shaped_recipe(ahI).setEntries(abd, ahf).setEntries(abj, aiz).setOutput(ahI).setGroup(ajY)
    config.shaped_recipe(afq).setEntries(adT, ahf).setOutput((3, afq)).setGroup(ajn)
    config.shapeless_recipe("white_concrete_powder").addInput(ahz, 1).addInput(ajM, 4).addInput(ajo, 4).setOutput(
        (8, "white_concrete_powder")).setGroup(acX)
    config.shapeless_recipe(ahz).addInput(ahx, 1).setOutput(ahz).setGroup(ahz)
    config.shapeless_recipe("white_dye_from_lily_of_the_valley").addInput("lily_of_the_valley", 1).setOutput(
        ahz).setGroup(ahz)
    config.smelting_recipe(aaQ).add_ingredient(acL).setXp(ake).setOutput(aaQ)
    config.shaped_recipe(abO).setEntries(aad, ajF).setEntries(aiT, ahz).setOutput((8, abO)).setGroup(aep)
    config.shaped_recipe("white_stained_glass_pane").setEntries(aan, abO).setOutput(
        (16, "white_stained_glass_pane")).setGroup(abQ)
    config.shaped_recipe("white_stained_glass_pane_from_glass_pane").setEntries(aad, ahl).setEntries(aiT,
                                                                                                     ahz).setOutput(
        (8, "white_stained_glass_pane")).setGroup(abQ)
    config.shaped_recipe(acL).setEntries(aad, agP).setEntries(aiT, ahz).setOutput((8, acL)).setGroup(acd)
    config.shaped_recipe("white_wool_from_string").setEntries(aau, ajh).setOutput(ahf)
    config.shaped_recipe(agB).setEntries(adO, ajH).setEntries(abg, aiz).setOutput(agB)
    config.shaped_recipe(agU).setEntries(adO, ajH).setEntries(adT, aiz).setOutput(agU)
    config.shaped_recipe(adF).setEntries(adO, ajH).setEntries(abd, aiz).setOutput(adF)
    config.shaped_recipe(aeE).setEntries(aed, ajH).setEntries(ajp, aiz).setOutput(aeE)
    config.shaped_recipe(afo).setEntries(ajk, ajH).setEntries(adE, aiz).setOutput(afo)
    config.shapeless_recipe(aeK).addInput(ajJ, 1).addInput("ink_sac", 1).addInput(aiF, 1).setOutput(aeK)
    config.shaped_recipe(aes).setEntries(aan, aga).setEntries(ajg, ajH).setOutput(aes).setGroup(aiZ)
    config.shaped_recipe(agL).setEntries(abd, aga).setEntries(abj, aiz).setOutput(agL).setGroup(ajY)
    config.shapeless_recipe("yellow_bed_from_white_bed").addInput(ahI, 1).addInput(ahj, 1).setOutput(agL).setGroup(aim)
    config.shaped_recipe("yellow_carpet").setEntries(adT, aga).setOutput((3, "yellow_carpet")).setGroup(ajn)
    config.shaped_recipe("yellow_carpet_from_white_carpet").setEntries(aad, afq).setEntries(aiT, ahj).setOutput(
        (8, "yellow_carpet")).setGroup(ajn)
    config.shapeless_recipe("yellow_concrete_powder").addInput(ahj, 1).addInput(ajM, 4).addInput(ajo, 4).setOutput(
        (8, "yellow_concrete_powder")).setGroup(acX)
    config.shapeless_recipe("yellow_dye_from_dandelion").addInput("dandelion", 1).setOutput(ahj).setGroup(ahj)
    config.shapeless_recipe("yellow_dye_from_sunflower").addInput("sunflower", 1).setOutput((2, ahj)).setGroup(ahj)
    config.smelting_recipe(aaI).add_ingredient(acE).setXp(ake).setOutput(aaI)
    config.shaped_recipe(abA).setEntries(aad, ajF).setEntries(aiT, ahj).setOutput((8, abA)).setGroup(aep)
    config.shaped_recipe("yellow_stained_glass_pane").setEntries(aan, abA).setOutput(
        (16, "yellow_stained_glass_pane")).setGroup(abQ)
    config.shaped_recipe("yellow_stained_glass_pane_from_glass_pane").setEntries(aad, ahl).setEntries(aiT,
                                                                                                      ahj).setOutput(
        (8, "yellow_stained_glass_pane")).setGroup(abQ)
    config.shaped_recipe(acE).setEntries(aad, agP).setEntries(aiT, ahj).setOutput((8, acE)).setGroup(acd)
    config.shapeless_recipe(aga).addInput(ahj, 1).addInput(ahf, 1).setOutput(aga).setGroup(ajP)
