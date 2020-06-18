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
    aag = [(0, 0), (0, 1), (0, 2), (1, 2), (2, 0), (2, 1), (2, 2)]
    aah = [(0, 0), (0, 1), (0, 2), (1, 0), (2, 0), (2, 1), (2, 2)]
    aai = [(0, 0), (0, 1), (0, 2), (1, 1), (2, 0), (2, 1), (2, 2)]
    aaj = [(0, 0), (0, 1), (0, 2), (2, 0), (2, 1), (2, 2)]
    aak = [(0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2)]
    aal = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)]
    aam = [(0, 0), (0, 2), (1, 0), (1, 2), (2, 0), (2, 2)]
    aan = [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1)]
    aao = [(0, 0), (0, 1), (1, 1), (2, 0), (2, 1)]
    aap = [(0, 0), (0, 1), (1, 0), (2, 0), (2, 1)]
    aaq = ['purpur_block', 'purpur_pillar']
    aar = [(0, 0), (0, 1), (1, 0), (1, 1)]
    aas = [(0, 0), (0, 1), (2, 0), (2, 1)]
    aat = [(0, 2), (1, 1), (1, 2), (2, 2)]
    aau = [(0, 1), (0, 2), (1, 1), (1, 2)]
    aav = [(0, 1), (1, 0), (1, 2), (2, 1)]
    aaw = "light_weighted_pressure_plate"
    aax = "heavy_weighted_pressure_plate"
    aay = "light_blue_glazed_terracotta"
    aaz = "light_gray_glazed_terracotta"
    aaA = "minecraft:campfire_cooking"
    aaB = "magenta_glazed_terracotta"
    aaC = "purple_glazed_terracotta"
    aaD = "light_gray_stained_glass"
    aaE = "orange_glazed_terracotta"
    aaF = "yellow_glazed_terracotta"
    aaG = "light_blue_stained_glass"
    aaH = "green_glazed_terracotta"
    aaI = "white_glazed_terracotta"
    aaJ = "dark_oak_pressure_plate"
    aaK = "brown_glazed_terracotta"
    aaL = "black_glazed_terracotta"
    aaM = [(0, 1), (1, 1), (2, 1)]
    aaN = [(0, 0), (0, 1), (1, 0)]
    aaO = "cyan_glazed_terracotta"
    aaP = "lime_glazed_terracotta"
    aaQ = "pink_glazed_terracotta"
    aaR = "glistering_melon_slice"
    aaS = "chiseled_red_sandstone"
    aaT = "gray_glazed_terracotta"
    aaU = "blue_glazed_terracotta"
    aaV = "creeper_banner_pattern"
    aaW = [(0, 1), (1, 0), (2, 1)]
    aaX = [(0, 2), (1, 2), (2, 2)]
    aaY = [(0, 0), (1, 1), (2, 0)]
    aaZ = [(0, 0), (1, 0), (2, 0)]
    aba = "red_glazed_terracotta"
    abb = "acacia_pressure_plate"
    abc = "chiseled_quartz_block"
    abd = "mojang_banner_pattern"
    abe = "light_gray_terracotta"
    abf = "light_blue_terracotta"
    abg = "chiseled_stone_bricks"
    abh = "magenta_stained_glass"
    abi = "wooden_pressure_plate"
    abj = "flower_banner_pattern"
    abk = "spruce_pressure_plate"
    abl = "jungle_pressure_plate"
    abm = "cracked_stone_bricks"
    abn = "purple_stained_glass"
    abo = "orange_stained_glass"
    abp = "smooth_red_sandstone"
    abq = "birch_pressure_plate"
    abr = "skull_banner_pattern"
    abs = "fermented_spider_eye"
    abt = "stone_pressure_plate"
    abu = "yellow_stained_glass"
    abv = "brown_stained_glass"
    abw = "popped_chorus_fruit"
    abx = "black_stained_glass"
    aby = "dark_oak_fence_gate"
    abz = "green_stained_glass"
    abA = "white_stained_glass"
    abB = "leather_horse_armor"
    abC = "stained_glass_pane"
    abD = "magenta_terracotta"
    abE = "blue_stained_glass"
    abF = "stained_terracotta"
    abG = "chiseled_sandstone"
    abH = "leather_chestplate"
    abI = "red_sandstone_slab"
    abJ = "mossy_stone_bricks"
    abK = "cyan_stained_glass"
    abL = "oak_pressure_plate"
    abM = "pink_stained_glass"
    abN = "diamond_chestplate"
    abO = "gray_stained_glass"
    abP = "minecraft:blasting"
    abQ = "lime_stained_glass"
    abR = "acacia_fence_gate"
    abS = "prismarine_bricks"
    abT = "wooden_fence_gate"
    abU = "purple_terracotta"
    abV = "nether_quartz_ore"
    abW = "smooth_stone_slab"
    abX = "light_gray_banner"
    abY = "minecraft:smoking"
    abZ = "nether_wart_block"
    aca = "red_stained_glass"
    acb = "spruce_fence_gate"
    acc = "light_blue_banner"
    acd = "red_nether_bricks"
    ace = "mossy_cobblestone"
    acf = "polished_andesite"
    acg = "yellow_terracotta"
    ach = "orange_terracotta"
    aci = "daylight_detector"
    acj = "carrot_on_a_stick"
    ack = "cartography_table"
    acl = "jungle_fence_gate"
    acm = "cut_red_sandstone"
    acn = "golden_chestplate"
    aco = "end_stone_bricks"
    acp = "prismarine_shard"
    acq = "polished_granite"
    acr = "polished_diorite"
    acs = "enchanting_table"
    act = "smooth_sandstone"
    acu = "brown_terracotta"
    acv = "leather_leggings"
    acw = "stone_brick_slab"
    acx = "birch_fence_gate"
    acy = "white_terracotta"
    acz = "furnace_minecart"
    acA = "diamond_leggings"
    acB = (2, "magenta_dye")
    acC = "black_terracotta"
    acD = "dried_kelp_block"
    acE = "green_terracotta"
    acF = "wooden_trapdoor"
    acG = "golden_leggings"
    acH = "light_blue_wool"
    acI = "dark_prismarine"
    acJ = "blue_terracotta"
    acK = "flint_and_steel"
    acL = "dark_oak_planks"
    acM = "honeycomb_block"
    acN = "hopper_minecart"
    acO = "concrete_powder"
    acP = "diamond_pickaxe"
    acQ = "cyan_terracotta"
    acR = "fletching_table"
    acS = "gray_terracotta"
    acT = "lime_terracotta"
    acU = "dark_oak_button"
    acV = "iron_chestplate"
    acW = "cooked_porkchop"
    acX = "pink_terracotta"
    acY = "light_gray_wool"
    acZ = "red_terracotta"
    ada = [(1, 0), (1, 1)]
    adb = "diamond_helmet"
    adc = "crafting_table"
    add = "wooden_pickaxe"
    ade = "magenta_banner"
    adf = "smithing_table"
    adg = [(0, 1), (2, 1)]
    adh = "redstone_block"
    adi = [(0, 0), (1, 0)]
    adj = [(0, 0), (1, 1)]
    adk = "jack_o_lantern"
    adl = "redstone_torch"
    adm = "leather_helmet"
    adn = [(0, 1), (0, 2)]
    ado = "golden_pickaxe"
    adp = "sandstone_slab"
    adq = [(0, 1), (1, 0)]
    adr = [(1, 0), (1, 2)]
    ads = "diamond_shovel"
    adt = [(1, 1), (1, 2)]
    adu = "light_gray_dye"
    adv = [(0, 0), (2, 0)]
    adw = "light_blue_bed"
    adx = "chest_minecart"
    ady = "cooked_chicken"
    adz = [(0, 1), (1, 1)]
    adA = [(0, 0), (0, 1)]
    adB = "light_gray_bed"
    adC = "oak_fence_gate"
    adD = "glowstone_dust"
    adE = "light_blue_dye"
    adF = "orange_banner"
    adG = "writable_book"
    adH = "#wooden_slabs"
    adI = "golden_shovel"
    adJ = "jungle_button"
    adK = "diamond_block"
    adL = "emerald_block"
    adM = "golden_helmet"
    adN = "cooked_rabbit"
    adO = "stone_pickaxe"
    adP = "wooden_stairs"
    adQ = "blast_furnace"
    adR = "yellow_banner"
    adS = "acacia_button"
    adT = "nether_bricks"
    adU = "cut_sandstone"
    adV = "iron_trapdoor"
    adW = "leather_boots"
    adX = (2, "pink_dye")
    adY = "red_sandstone"
    adZ = "wooden_shovel"
    aea = "sticky_piston"
    aeb = "turtle_helmet"
    aec = "tripwire_hook"
    aed = "stained_glass"
    aee = "cooked_mutton"
    aef = "mushroom_stew"
    aeg = "acacia_planks"
    aeh = "spruce_planks"
    aei = "smooth_quartz"
    aej = "spruce_button"
    aek = "iron_leggings"
    ael = "cooked_salmon"
    aem = "diamond_boots"
    aen = "purple_banner"
    aeo = "diamond_sword"
    aep = "trapped_chest"
    aeq = "dark_oak_boat"
    aer = "redstone_lamp"
    aes = "jungle_planks"
    aet = "purpur_pillar"
    aeu = "brewing_stand"
    aev = "golden_carrot"
    aew = "beetroot_soup"
    aex = "wooden_button"
    aey = "birch_planks"
    aez = "green_banner"
    aeA = "black_banner"
    aeB = "birch_button"
    aeC = "stone_button"
    aeD = "lapis_lazuli"
    aeE = "smooth_stone"
    aeF = "quartz_block"
    aeG = "iron_pickaxe"
    aeH = "golden_apple"
    aeI = "white_banner"
    aeJ = "baked_potato"
    aeK = "golden_sword"
    aeL = "wooden_sword"
    aeM = "honey_bottle"
    aeN = "magenta_wool"
    aeO = "golden_boots"
    aeP = "stone_bricks"
    aeQ = "stone_shovel"
    aeR = "wooden_fence"
    aeS = "tnt_minecart"
    aeT = "brown_banner"
    aeU = "redstone_ore"
    aeV = "nether_brick"
    aeW = "white_carpet"
    aeX = "pumpkin_pie"
    aeY = "purpur_slab"
    aeZ = "diamond_axe"
    afa = "honey_block"
    afb = "emerald_ore"
    afc = "lapis_block"
    afd = "lime_banner"
    afe = "diamond_hoe"
    aff = "rabbit_stew"
    afg = "fishing_rod"
    afh = "wooden_slab"
    afi = "quartz_slab"
    afj = "cocoa_beans"
    afk = "wooden_door"
    afl = "gray_banner"
    afm = "magenta_dye"
    afn = "gold_nugget"
    afo = "blue_banner"
    afp = "slime_block"
    afq = "nether_wart"
    afr = "jungle_boat"
    afs = "magma_block"
    aft = "acacia_boat"
    afu = "end_crystal"
    afv = "magma_cream"
    afw = "magenta_bed"
    afx = "ender_chest"
    afy = "pink_banner"
    afz = "melon_seeds"
    afA = "iron_nugget"
    afB = "sea_lantern"
    afC = "spruce_boat"
    afD = "diamond_ore"
    afE = "iron_helmet"
    afF = "iron_shovel"
    afG = "melon_slice"
    afH = "yellow_wool"
    afI = "cyan_banner"
    afJ = "armor_stand"
    afK = "orange_wool"
    afL = "purple_wool"
    afM = "shulker_box"
    afN = "cooked_beef"
    afO = "cobblestone"
    afP = "stone_sword"
    afQ = "stonecutter"
    afR = "orange_bed"
    afS = "wooden_hoe"
    afT = "wooden_axe"
    afU = "golden_hoe"
    afV = "green_wool"
    afW = "sugar_cane"
    afX = "purple_bed"
    afY = "flower_pot"
    afZ = "red_banner"
    aga = "packed_ice"
    agb = "iron_sword"
    agc = "iron_ingot"
    agd = "dried_kelp"
    age = "bone_block"
    agf = "yellow_bed"
    agg = "black_wool"
    agh = "brown_wool"
    agi = "gold_block"
    agj = "glass_pane"
    agk = "yellow_dye"
    agl = "terracotta"
    agm = "comparator"
    agn = "oak_planks"
    ago = "slime_ball"
    agp = "prismarine"
    agq = "birch_boat"
    agr = "stone_slab"
    ags = "gold_ingot"
    agt = "iron_boots"
    agu = "oak_button"
    agv = "cooked_cod"
    agw = "orange_dye"
    agx = "snow_block"
    agy = "iron_block"
    agz = "item_frame"
    agA = "grindstone"
    agB = "golden_axe"
    agC = "white_wool"
    agD = "coal_block"
    agE = "purple_dye"
    agF = "note_block"
    agG = "sandstone"
    agH = "green_dye"
    agI = "black_dye"
    agJ = "ender_eye"
    agK = "brown_bed"
    agL = "stone_hoe"
    agM = "stone_axe"
    agN = "composter"
    agO = "dispenser"
    agP = "white_bed"
    agQ = "brown_dye"
    agR = "black_bed"
    agS = "bone_meal"
    agT = "clay_ball"
    agU = "blue_wool"
    agV = "pink_wool"
    agW = "gray_wool"
    agX = "lime_wool"
    agY = "blaze_rod"
    agZ = "glowstone"
    aha = "cyan_wool"
    ahb = "white_dye"
    ahc = "bookshelf"
    ahd = "gunpowder"
    ahe = "hay_block"
    ahf = "lapis_ore"
    ahg = "honeycomb"
    ahh = "green_bed"
    ahi = "cyan_bed"
    ahj = "redstone"
    ahk = "lime_bed"
    ahl = "gray_bed"
    ahm = "iron_hoe"
    ahn = "gold_ore"
    aho = "cauldron"
    ahp = "coal_ore"
    ahq = "painting"
    ahr = "minecart"
    ahs = "blue_dye"
    aht = "porkchop"
    ahu = "pink_bed"
    ahv = "obsidian"
    ahw = "red_wool"
    ahx = "bonemeal"
    ahy = "oak_boat"
    ahz = "dyed_bed"
    ahA = "lime_dye"
    ahB = "andesite"
    ahC = "cyan_dye"
    ahD = "pink_dye"
    ahE = "iron_axe"
    ahF = "blue_ice"
    ahG = "blue_bed"
    ahH = "observer"
    ahI = "crossbow"
    ahJ = "repeater"
    ahK = "charcoal"
    ahL = "campfire"
    ahM = "iron_ore"
    ahN = "gray_dye"
    ahO = "chicken"
    ahP = "dropper"
    ahQ = "red_bed"
    ahR = "lectern"
    ahS = "feather"
    ahT = "red_dye"
    ahU = "granite"
    ahV = "compass"
    ahW = "emerald"
    ahX = "#planks"
    ahY = "diorite"
    ahZ = "leather"
    aia = "beehive"
    aib = "diamond"
    aic = "lantern"
    aid = "conduit"
    aie = "furnace"
    aif = "jukebox"
    aig = "string"
    aih = [(0, 0)]
    aii = "smoker"
    aij = "bucket"
    aik = "beacon"
    ail = "bamboo"
    aim = "carpet"
    ain = [(0, 1)]
    aio = "gravel"
    aip = "banner"
    aiq = "mutton"
    air = "potato"
    ais = "carrot"
    ait = "piston"
    aiu = "hopper"
    aiv = "sponge"
    aiw = "quartz"
    aix = "salmon"
    aiy = "shield"
    aiz = "bricks"
    aiA = "sticks"
    aiB = [(1, 0)]
    aiC = [(1, 1)]
    aiD = "shears"
    aiE = [(0, 2)]
    aiF = "barrel"
    aiG = "planks"
    aiH = [(1, 2)]
    aiI = "rabbit"
    aiJ = "sugar"
    aiK = "wheat"
    aiL = "lever"
    aiM = "anvil"
    aiN = "torch"
    aiO = "chest"
    aiP = "arrow"
    aiQ = "melon"
    aiR = "clock"
    aiS = "#logs"
    aiT = "bread"
    aiU = "paper"
    aiV = "brick"
    aiW = "flint"
    aiX = "stone"
    aiY = "stick"
    aiZ = "glass"
    aja = "bark"
    ajb = "book"
    ajc = "loom"
    ajd = "wool"
    aje = "coal"
    ajf = "sand"
    ajg = "cake"
    ajh = "kelp"
    aji = "clay"
    ajj = "beef"
    ajk = "boat"
    ajl = "egg"
    ajm = "cod"
    ajn = "tnt"
    ajo = "bow"
    ajp = "bed"
    ajq = "map"
    ajr = 0.35
    ajs = 0.15
    ajt = 0.2
    aju = 1.0
    ajv = 0.7
    ajw = 0.1
    ajx = 600
    ajy = 100
    config.shaped_recipe(aft).setEntries(aao, aeg).setOutput(aft).setGroup(ajk)
    config.shapeless_recipe(adS).addInput(aeg, 1).setOutput(adS).setGroup(aex)
    config.shaped_recipe("acacia_door").setEntries(aal, aeg).setOutput((3, "acacia_door")).setGroup(afk)
    config.shaped_recipe("acacia_fence").setEntries(ada, aiY).setEntries(aas, aeg).setOutput(
        (3, "acacia_fence")).setGroup(aeR)
    config.shaped_recipe(abR).setEntries(aas, aiY).setEntries(ada, aeg).setOutput(abR).setGroup(abT)
    config.shapeless_recipe(aeg).addInput("#acacia_logs", 1).setOutput((4, aeg)).setGroup(aiG)
    config.shaped_recipe(abb).setEntries(adi, aeg).setOutput(abb).setGroup(abi)
    config.shaped_recipe("acacia_sign").setEntries(aan, aeg).setEntries(aiH, aiY).setOutput((3, "acacia_sign"))
    config.shaped_recipe("acacia_slab").setEntries(aaZ, aeg).setOutput((6, "acacia_slab")).setGroup(afh)
    config.shaped_recipe("acacia_stairs").setEntries(aak, aeg).setOutput((4, "acacia_stairs")).setGroup(adP)
    config.shaped_recipe("acacia_trapdoor").setEntries(aan, aeg).setOutput((2, "acacia_trapdoor")).setGroup(acF)
    config.shaped_recipe("acacia_wood").setEntries(aar, "acacia_log").setOutput((3, "acacia_wood")).setGroup(aja)
    config.shaped_recipe("activator_rail").setEntries(aiC, adl).setEntries(adr, aiY).setEntries(aaj, agc).setOutput(
        (6, "activator_rail"))
    config.shapeless_recipe(ahB).addInput(ahY, 1).addInput(afO, 1).setOutput((2, ahB))
    config.shaped_recipe("andesite_slab").setEntries(aaZ, ahB).setOutput((6, "andesite_slab"))
    config.shaped_recipe("andesite_stairs").setEntries(aak, ahB).setOutput((4, "andesite_stairs"))
    config.shaped_recipe("andesite_wall").setEntries(aan, ahB).setOutput((6, "andesite_wall"))
    config.shaped_recipe(aiM).setEntries(aaZ, agy).setEntries(aat, agc).setOutput(aiM)
    config.shaped_recipe(afJ).setEntries([(0, 0), (0, 2), (1, 0), (1, 1), (2, 0), (2, 2)], aiY).setEntries(aiH,
                                                                                                           abW).setOutput(
        afJ)
    config.shaped_recipe(aiP).setEntries(ain, aiY).setEntries(aih, aiW).setEntries(aiE, ahS).setOutput((4, aiP))
    config.smelting_recipe(aeJ).add_ingredient(air).setXp(ajr).setOutput(aeJ)
    config.smelting_recipe("baked_potato_from_campfire_cooking", aaA).add_ingredient(air).setXp(ajr).setOutput(
        aeJ).setCookingTime(ajx)
    config.smelting_recipe("baked_potato_from_smoking", abY).add_ingredient(air).setXp(ajr).setOutput(
        aeJ).setCookingTime(ajy)
    config.shaped_recipe(aiF).setEntries(aaj, ahX).setEntries(adr, adH).setOutput(aiF)
    config.shaped_recipe(aik).setEntries(aiC, "nether_star").setEntries(aap, aiZ).setEntries(aaX, ahv).setOutput(aik)
    config.shaped_recipe(aia).setEntries(aam, ahX).setEntries(aaM, ahg).setOutput(aia)
    config.shapeless_recipe(aew).addInput("bowl", 1).addInput("beetroot", 6).setOutput(aew)
    config.shaped_recipe(agq).setEntries(aao, aey).setOutput(agq).setGroup(ajk)
    config.shapeless_recipe(aeB).addInput(aey, 1).setOutput(aeB).setGroup(aex)
    config.shaped_recipe("birch_door").setEntries(aal, aey).setOutput((3, "birch_door")).setGroup(afk)
    config.shaped_recipe("birch_fence").setEntries(ada, aiY).setEntries(aas, aey).setOutput(
        (3, "birch_fence")).setGroup(aeR)
    config.shaped_recipe(acx).setEntries(aas, aiY).setEntries(ada, aey).setOutput(acx).setGroup(abT)
    config.shapeless_recipe(aey).addInput("#birch_logs", 1).setOutput((4, aey)).setGroup(aiG)
    config.shaped_recipe(abq).setEntries(adi, aey).setOutput(abq).setGroup(abi)
    config.shaped_recipe("birch_sign").setEntries(aan, aey).setEntries(aiH, aiY).setOutput((3, "birch_sign"))
    config.shaped_recipe("birch_slab").setEntries(aaZ, aey).setOutput((6, "birch_slab")).setGroup(afh)
    config.shaped_recipe("birch_stairs").setEntries(aak, aey).setOutput((4, "birch_stairs")).setGroup(adP)
    config.shaped_recipe("birch_trapdoor").setEntries(aan, aey).setOutput((2, "birch_trapdoor")).setGroup(acF)
    config.shaped_recipe("birch_wood").setEntries(aar, "birch_log").setOutput((3, "birch_wood")).setGroup(aja)
    config.shaped_recipe(aeA).setEntries(aan, agg).setEntries(aiH, aiY).setOutput(aeA).setGroup(aip)
    config.shaped_recipe(agR).setEntries(aaZ, agg).setEntries(aaM, ahX).setOutput(agR).setGroup(ajp)
    config.shapeless_recipe("black_bed_from_white_bed").addInput(agP, 1).addInput(agI, 1).setOutput(agR).setGroup(ahz)
    config.shaped_recipe("black_carpet").setEntries(adi, agg).setOutput((3, "black_carpet")).setGroup(aim)
    config.shaped_recipe("black_carpet_from_white_carpet").setEntries(aad, aeW).setEntries(aiC, agI).setOutput(
        (8, "black_carpet")).setGroup(aim)
    config.shapeless_recipe("black_concrete_powder").addInput(agI, 1).addInput(ajf, 4).addInput(aio, 4).setOutput(
        (8, "black_concrete_powder")).setGroup(acO)
    config.shapeless_recipe(agI).addInput("ink_sac", 1).setOutput(agI).setGroup(agI)
    config.shapeless_recipe("black_dye_from_wither_rose").addInput("wither_rose", 1).setOutput(agI).setGroup(agI)
    config.smelting_recipe(aaL).add_ingredient(acC).setXp(ajw).setOutput(aaL)
    config.shaped_recipe(abx).setEntries(aad, aiZ).setEntries(aiC, agI).setOutput((8, abx)).setGroup(aed)
    config.shaped_recipe("black_stained_glass_pane").setEntries(aan, abx).setOutput(
        (16, "black_stained_glass_pane")).setGroup(abC)
    config.shaped_recipe("black_stained_glass_pane_from_glass_pane").setEntries(aad, agj).setEntries(aiC,
                                                                                                     agI).setOutput(
        (8, "black_stained_glass_pane")).setGroup(abC)
    config.shaped_recipe(acC).setEntries(aad, agl).setEntries(aiC, agI).setOutput((8, acC)).setGroup(abF)
    config.shapeless_recipe(agg).addInput(agI, 1).addInput(agC, 1).setOutput(agg).setGroup(ajd)
    config.shaped_recipe(adQ).setEntries(aaX, aeE).setEntries(aiC, aie).setEntries(aap, agc).setOutput(adQ)
    config.shapeless_recipe("blaze_powder").addInput(agY, 1).setOutput((2, "blaze_powder"))
    config.shaped_recipe(afo).setEntries(aan, agU).setEntries(aiH, aiY).setOutput(afo).setGroup(aip)
    config.shaped_recipe(ahG).setEntries(aaZ, agU).setEntries(aaM, ahX).setOutput(ahG).setGroup(ajp)
    config.shapeless_recipe("blue_bed_from_white_bed").addInput(agP, 1).addInput(ahs, 1).setOutput(ahG).setGroup(ahz)
    config.shaped_recipe("blue_carpet").setEntries(adi, agU).setOutput((3, "blue_carpet")).setGroup(aim)
    config.shaped_recipe("blue_carpet_from_white_carpet").setEntries(aad, aeW).setEntries(aiC, ahs).setOutput(
        (8, "blue_carpet")).setGroup(aim)
    config.shapeless_recipe("blue_concrete_powder").addInput(ahs, 1).addInput(ajf, 4).addInput(aio, 4).setOutput(
        (8, "blue_concrete_powder")).setGroup(acO)
    config.shapeless_recipe(ahs).addInput(aeD, 1).setOutput(ahs).setGroup(ahs)
    config.shapeless_recipe("blue_dye_from_cornflower").addInput("cornflower", 1).setOutput(ahs).setGroup(ahs)
    config.smelting_recipe(aaU).add_ingredient(acJ).setXp(ajw).setOutput(aaU)
    config.shaped_recipe(ahF).setEntries(aac, aga).setOutput(ahF)
    config.shaped_recipe(abE).setEntries(aad, aiZ).setEntries(aiC, ahs).setOutput((8, abE)).setGroup(aed)
    config.shaped_recipe("blue_stained_glass_pane").setEntries(aan, abE).setOutput(
        (16, "blue_stained_glass_pane")).setGroup(abC)
    config.shaped_recipe("blue_stained_glass_pane_from_glass_pane").setEntries(aad, agj).setEntries(aiC, ahs).setOutput(
        (8, "blue_stained_glass_pane")).setGroup(abC)
    config.shaped_recipe(acJ).setEntries(aad, agl).setEntries(aiC, ahs).setOutput((8, acJ)).setGroup(abF)
    config.shapeless_recipe(agU).addInput(ahs, 1).addInput(agC, 1).setOutput(agU).setGroup(ajd)
    config.shaped_recipe(age).setEntries(aac, agS).setOutput(age)
    config.shapeless_recipe(agS).addInput("bone", 1).setOutput((3, agS)).setGroup(ahx)
    config.shapeless_recipe("bone_meal_from_bone_block").addInput(age, 1).setOutput((9, agS)).setGroup(ahx)
    config.shapeless_recipe(ajb).addInput(aiU, 3).addInput(ahZ, 1).setOutput(ajb)
    config.shaped_recipe(ahc).setEntries(aam, ahX).setEntries(aaM, ajb).setOutput(ahc)
    config.shaped_recipe(ajo).setEntries([(0, 1), (1, 0), (1, 2)], aiY).setEntries([(2, 0), (2, 1), (2, 2)],
                                                                                   aig).setOutput(ajo)
    config.shaped_recipe("bowl").setEntries(aaY, ahX).setOutput((4, "bowl"))
    config.shaped_recipe(aiT).setEntries(aaZ, aiK).setOutput(aiT)
    config.shaped_recipe(aeu).setEntries(aiB, agY).setEntries(aaM, afO).setOutput(aeu)
    config.smelting_recipe(aiV).add_ingredient(agT).setXp(0.3).setOutput(aiV)
    config.shaped_recipe(aiz).setEntries(aar, aiV).setOutput(aiz)
    config.shaped_recipe("brick_slab").setEntries(aaZ, aiz).setOutput((6, "brick_slab"))
    config.shaped_recipe("brick_stairs").setEntries(aak, aiz).setOutput((4, "brick_stairs"))
    config.shaped_recipe("brick_wall").setEntries(aan, aiz).setOutput((6, "brick_wall"))
    config.shaped_recipe(aeT).setEntries(aan, agh).setEntries(aiH, aiY).setOutput(aeT).setGroup(aip)
    config.shaped_recipe(agK).setEntries(aaZ, agh).setEntries(aaM, ahX).setOutput(agK).setGroup(ajp)
    config.shapeless_recipe("brown_bed_from_white_bed").addInput(agP, 1).addInput(agQ, 1).setOutput(agK).setGroup(ahz)
    config.shaped_recipe("brown_carpet").setEntries(adi, agh).setOutput((3, "brown_carpet")).setGroup(aim)
    config.shaped_recipe("brown_carpet_from_white_carpet").setEntries(aad, aeW).setEntries(aiC, agQ).setOutput(
        (8, "brown_carpet")).setGroup(aim)
    config.shapeless_recipe("brown_concrete_powder").addInput(agQ, 1).addInput(ajf, 4).addInput(aio, 4).setOutput(
        (8, "brown_concrete_powder")).setGroup(acO)
    config.shapeless_recipe(agQ).addInput(afj, 1).setOutput(agQ).setGroup(agQ)
    config.smelting_recipe(aaK).add_ingredient(acu).setXp(ajw).setOutput(aaK)
    config.shaped_recipe(abv).setEntries(aad, aiZ).setEntries(aiC, agQ).setOutput((8, abv)).setGroup(aed)
    config.shaped_recipe("brown_stained_glass_pane").setEntries(aan, abv).setOutput(
        (16, "brown_stained_glass_pane")).setGroup(abC)
    config.shaped_recipe("brown_stained_glass_pane_from_glass_pane").setEntries(aad, agj).setEntries(aiC,
                                                                                                     agQ).setOutput(
        (8, "brown_stained_glass_pane")).setGroup(abC)
    config.shaped_recipe(acu).setEntries(aad, agl).setEntries(aiC, agQ).setOutput((8, acu)).setGroup(abF)
    config.shapeless_recipe(agh).addInput(agQ, 1).addInput(agC, 1).setOutput(agh).setGroup(ajd)
    config.shaped_recipe(aij).setEntries(aaY, agc).setOutput(aij)
    config.shaped_recipe(ajg).setEntries(aaZ, "milk_bucket").setEntries(adg, aiJ).setEntries(aaX, aiK).setEntries(aiC,
                                                                                                                  ajl).setOutput(
        ajg)
    config.shaped_recipe(ahL).setEntries(aaX, aiS).setEntries(aaW, aiY).setEntries(aiC, "#coals").setOutput(ahL)
    config.shaped_recipe(acj).setEntries(aih, afg).setEntries(aiC, ais).setOutput(acj)
    config.shaped_recipe(ack).setEntries(aau, ahX).setEntries(adi, aiU).setOutput(ack)
    config.shaped_recipe(aho).setEntries(aag, agc).setOutput(aho)
    config.smelting_recipe(ahK).add_ingredient(aiS).setXp(ajs).setOutput(ahK)
    config.shaped_recipe(aiO).setEntries(aad, ahX).setOutput(aiO)
    config.shaped_recipe(adx).setEntries(aih, aiO).setEntries(ain, ahr).setOutput(adx)
    config.shaped_recipe(abc).setEntries(adA, afi).setOutput(abc)
    config.shaped_recipe(aaS).setEntries(adA, abI).setOutput(aaS)
    config.shaped_recipe(abG).setEntries(adA, adp).setOutput(abG)
    config.shaped_recipe(abg).setEntries(adA, acw).setOutput(abg)
    config.shaped_recipe(aji).setEntries(aar, agT).setOutput(aji)
    config.shaped_recipe(aiR).setEntries(aav, ags).setEntries(aiC, ahj).setOutput(aiR)
    config.shapeless_recipe(aje).addInput(agD, 1).setOutput((9, aje))
    config.shaped_recipe(agD).setEntries(aac, aje).setOutput(agD)
    config.smelting_recipe("coal_from_blasting", abP).add_ingredient(ahp).setXp(ajw).setOutput(aje).setCookingTime(ajy)
    config.smelting_recipe("coal_from_smelting").add_ingredient(ahp).setXp(ajw).setOutput(aje)
    config.shaped_recipe("coarse_dirt").setEntries(adj, "dirt").setEntries(adq, aio).setOutput((4, "coarse_dirt"))
    config.shaped_recipe("cobblestone_slab").setEntries(aaZ, afO).setOutput((6, "cobblestone_slab"))
    config.shaped_recipe("cobblestone_stairs").setEntries(aak, afO).setOutput((4, "cobblestone_stairs"))
    config.shaped_recipe("cobblestone_wall").setEntries(aan, afO).setOutput((6, "cobblestone_wall"))
    config.shaped_recipe(agm).setEntries(aaW, adl).setEntries(aiC, aiw).setEntries(aaX, aiX).setOutput(agm)
    config.shaped_recipe(ahV).setEntries(aav, agc).setEntries(aiC, ahj).setOutput(ahV)
    config.shaped_recipe(agN).setEntries(aag, adH).setOutput(agN)
    config.shaped_recipe(aid).setEntries(aad, "nautilus_shell").setEntries(aiC, "heart_of_the_sea").setOutput(aid)
    config.smelting_recipe(afN).add_ingredient(ajj).setXp(ajr).setOutput(afN)
    config.smelting_recipe("cooked_beef_from_campfire_cooking", aaA).add_ingredient(ajj).setXp(ajr).setOutput(
        afN).setCookingTime(ajx)
    config.smelting_recipe("cooked_beef_from_smoking", abY).add_ingredient(ajj).setXp(ajr).setOutput(
        afN).setCookingTime(ajy)
    config.smelting_recipe(ady).add_ingredient(ahO).setXp(ajr).setOutput(ady)
    config.smelting_recipe("cooked_chicken_from_campfire_cooking", aaA).add_ingredient(ahO).setXp(ajr).setOutput(
        ady).setCookingTime(ajx)
    config.smelting_recipe("cooked_chicken_from_smoking", abY).add_ingredient(ahO).setXp(ajr).setOutput(
        ady).setCookingTime(ajy)
    config.smelting_recipe(agv).add_ingredient(ajm).setXp(ajr).setOutput(agv)
    config.smelting_recipe("cooked_cod_from_campfire_cooking", aaA).add_ingredient(ajm).setXp(ajr).setOutput(
        agv).setCookingTime(ajx)
    config.smelting_recipe("cooked_cod_from_smoking", abY).add_ingredient(ajm).setXp(ajr).setOutput(agv).setCookingTime(
        ajy)
    config.smelting_recipe(aee).add_ingredient(aiq).setXp(ajr).setOutput(aee)
    config.smelting_recipe("cooked_mutton_from_campfire_cooking", aaA).add_ingredient(aiq).setXp(ajr).setOutput(
        aee).setCookingTime(ajx)
    config.smelting_recipe("cooked_mutton_from_smoking", abY).add_ingredient(aiq).setXp(ajr).setOutput(
        aee).setCookingTime(ajy)
    config.smelting_recipe(acW).add_ingredient(aht).setXp(ajr).setOutput(acW)
    config.smelting_recipe("cooked_porkchop_from_campfire_cooking", aaA).add_ingredient(aht).setXp(ajr).setOutput(
        acW).setCookingTime(ajx)
    config.smelting_recipe("cooked_porkchop_from_smoking", abY).add_ingredient(aht).setXp(ajr).setOutput(
        acW).setCookingTime(ajy)
    config.smelting_recipe(adN).add_ingredient(aiI).setXp(ajr).setOutput(adN)
    config.smelting_recipe("cooked_rabbit_from_campfire_cooking", aaA).add_ingredient(aiI).setXp(ajr).setOutput(
        adN).setCookingTime(ajx)
    config.smelting_recipe("cooked_rabbit_from_smoking", abY).add_ingredient(aiI).setXp(ajr).setOutput(
        adN).setCookingTime(ajy)
    config.smelting_recipe(ael).add_ingredient(aix).setXp(ajr).setOutput(ael)
    config.smelting_recipe("cooked_salmon_from_campfire_cooking", aaA).add_ingredient(aix).setXp(ajr).setOutput(
        ael).setCookingTime(ajx)
    config.smelting_recipe("cooked_salmon_from_smoking", abY).add_ingredient(aix).setXp(ajr).setOutput(
        ael).setCookingTime(ajy)
    config.shaped_recipe("cookie").setEntries(adv, aiK).setEntries(aiB, afj).setOutput((8, "cookie"))
    config.smelting_recipe(abm).add_ingredient(aeP).setXp(ajw).setOutput(abm)
    config.shaped_recipe(adc).setEntries(aar, ahX).setOutput(adc)
    config.shapeless_recipe(aaV).addInput(aiU, 1).addInput("creeper_head", 1).setOutput(aaV)
    config.shaped_recipe(ahI).setEntries(adg, aig).setEntries([(0, 0), (1, 2), (2, 0)], aiY).setEntries(aiB,
                                                                                                        agc).setEntries(
        aiC, aec).setOutput(ahI)
    config.shaped_recipe(acm).setEntries(aar, adY).setOutput((4, acm))
    config.shaped_recipe("cut_red_sandstone_slab").setEntries(aaZ, acm).setOutput((6, "cut_red_sandstone_slab"))
    config.shaped_recipe(adU).setEntries(aar, agG).setOutput((4, adU))
    config.shaped_recipe("cut_sandstone_slab").setEntries(aaZ, adU).setOutput((6, "cut_sandstone_slab"))
    config.shaped_recipe(afI).setEntries(aan, aha).setEntries(aiH, aiY).setOutput(afI).setGroup(aip)
    config.shaped_recipe(ahi).setEntries(aaZ, aha).setEntries(aaM, ahX).setOutput(ahi).setGroup(ajp)
    config.shapeless_recipe("cyan_bed_from_white_bed").addInput(agP, 1).addInput(ahC, 1).setOutput(ahi).setGroup(ahz)
    config.shaped_recipe("cyan_carpet").setEntries(adi, aha).setOutput((3, "cyan_carpet")).setGroup(aim)
    config.shaped_recipe("cyan_carpet_from_white_carpet").setEntries(aad, aeW).setEntries(aiC, ahC).setOutput(
        (8, "cyan_carpet")).setGroup(aim)
    config.shapeless_recipe("cyan_concrete_powder").addInput(ahC, 1).addInput(ajf, 4).addInput(aio, 4).setOutput(
        (8, "cyan_concrete_powder")).setGroup(acO)
    config.shapeless_recipe(ahC).addInput(ahs, 1).addInput(agH, 1).setOutput((2, ahC))
    config.smelting_recipe(aaO).add_ingredient(acQ).setXp(ajw).setOutput(aaO)
    config.shaped_recipe(abK).setEntries(aad, aiZ).setEntries(aiC, ahC).setOutput((8, abK)).setGroup(aed)
    config.shaped_recipe("cyan_stained_glass_pane").setEntries(aan, abK).setOutput(
        (16, "cyan_stained_glass_pane")).setGroup(abC)
    config.shaped_recipe("cyan_stained_glass_pane_from_glass_pane").setEntries(aad, agj).setEntries(aiC, ahC).setOutput(
        (8, "cyan_stained_glass_pane")).setGroup(abC)
    config.shaped_recipe(acQ).setEntries(aad, agl).setEntries(aiC, ahC).setOutput((8, acQ)).setGroup(abF)
    config.shapeless_recipe(aha).addInput(ahC, 1).addInput(agC, 1).setOutput(aha).setGroup(ajd)
    config.shaped_recipe(aeq).setEntries(aao, acL).setOutput(aeq).setGroup(ajk)
    config.shapeless_recipe(acU).addInput(acL, 1).setOutput(acU).setGroup(aex)
    config.shaped_recipe("dark_oak_door").setEntries(aal, acL).setOutput((3, "dark_oak_door")).setGroup(afk)
    config.shaped_recipe("dark_oak_fence").setEntries(ada, aiY).setEntries(aas, acL).setOutput(
        (3, "dark_oak_fence")).setGroup(aeR)
    config.shaped_recipe(aby).setEntries(aas, aiY).setEntries(ada, acL).setOutput(aby).setGroup(abT)
    config.shapeless_recipe(acL).addInput("#dark_oak_logs", 1).setOutput((4, acL)).setGroup(aiG)
    config.shaped_recipe(aaJ).setEntries(adi, acL).setOutput(aaJ).setGroup(abi)
    config.shaped_recipe("dark_oak_sign").setEntries(aan, acL).setEntries(aiH, aiY).setOutput((3, "dark_oak_sign"))
    config.shaped_recipe("dark_oak_slab").setEntries(aaZ, acL).setOutput((6, "dark_oak_slab")).setGroup(afh)
    config.shaped_recipe("dark_oak_stairs").setEntries(aak, acL).setOutput((4, "dark_oak_stairs")).setGroup(adP)
    config.shaped_recipe("dark_oak_trapdoor").setEntries(aan, acL).setOutput((2, "dark_oak_trapdoor")).setGroup(acF)
    config.shaped_recipe("dark_oak_wood").setEntries(aar, "dark_oak_log").setOutput((3, "dark_oak_wood")).setGroup(aja)
    config.shaped_recipe(acI).setEntries(aad, acp).setEntries(aiC, agI).setOutput(acI)
    config.shaped_recipe("dark_prismarine_slab").setEntries(aaZ, acI).setOutput((6, "dark_prismarine_slab"))
    config.shaped_recipe("dark_prismarine_stairs").setEntries(aak, acI).setOutput((4, "dark_prismarine_stairs"))
    config.shaped_recipe(aci).setEntries(aaM, aiw).setEntries(aaZ, aiZ).setEntries(aaX, adH).setOutput(aci)
    config.shaped_recipe("detector_rail").setEntries(aiH, ahj).setEntries(aiC, abt).setEntries(aaj, agc).setOutput(
        (6, "detector_rail"))
    config.shapeless_recipe(aib).addInput(adK, 1).setOutput((9, aib))
    config.shaped_recipe(aeZ).setEntries(adt, aiY).setEntries(aaN, aib).setOutput(aeZ)
    config.shaped_recipe(adK).setEntries(aac, aib).setOutput(adK)
    config.shaped_recipe(aem).setEntries(aas, aib).setOutput(aem)
    config.shaped_recipe(abN).setEntries(aae, aib).setOutput(abN)
    config.smelting_recipe("diamond_from_blasting", abP).add_ingredient(afD).setXp(aju).setOutput(aib).setCookingTime(
        ajy)
    config.smelting_recipe("diamond_from_smelting").add_ingredient(afD).setXp(aju).setOutput(aib)
    config.shaped_recipe(adb).setEntries(aap, aib).setOutput(adb)
    config.shaped_recipe(afe).setEntries(adt, aiY).setEntries(adi, aib).setOutput(afe)
    config.shaped_recipe(acA).setEntries(aah, aib).setOutput(acA)
    config.shaped_recipe(acP).setEntries(adt, aiY).setEntries(aaZ, aib).setOutput(acP)
    config.shaped_recipe(ads).setEntries(adn, aiY).setEntries(aih, aib).setOutput(ads)
    config.shaped_recipe(aeo).setEntries(aiE, aiY).setEntries(adA, aib).setOutput(aeo)
    config.shaped_recipe(ahY).setEntries(adq, aiw).setEntries(adj, afO).setOutput((2, ahY))
    config.shaped_recipe("diorite_slab").setEntries(aaZ, ahY).setOutput((6, "diorite_slab"))
    config.shaped_recipe("diorite_stairs").setEntries(aak, ahY).setOutput((4, "diorite_stairs"))
    config.shaped_recipe("diorite_wall").setEntries(aan, ahY).setOutput((6, "diorite_wall"))
    config.shaped_recipe(agO).setEntries(aiH, ahj).setEntries(aah, afO).setEntries(aiC, ajo).setOutput(agO)
    config.shapeless_recipe(agd).addInput(acD, 1).setOutput((9, agd))
    config.shapeless_recipe(acD).addInput(agd, 9).setOutput(acD)
    config.smelting_recipe("dried_kelp_from_campfire_cooking", aaA).add_ingredient(ajh).setXp(ajw).setOutput(
        agd).setCookingTime(ajx)
    config.smelting_recipe("dried_kelp_from_smelting").add_ingredient(ajh).setXp(ajw).setOutput(agd)
    config.smelting_recipe("dried_kelp_from_smoking", abY).add_ingredient(ajh).setXp(ajw).setOutput(agd).setCookingTime(
        ajy)
    config.shaped_recipe(ahP).setEntries(aiH, ahj).setEntries(aah, afO).setOutput(ahP)
    config.shapeless_recipe(ahW).addInput(adL, 1).setOutput((9, ahW))
    config.shaped_recipe(adL).setEntries(aac, ahW).setOutput(adL)
    config.smelting_recipe("emerald_from_blasting", abP).add_ingredient(afb).setXp(aju).setOutput(ahW).setCookingTime(
        ajy)
    config.smelting_recipe("emerald_from_smelting").add_ingredient(afb).setXp(aju).setOutput(ahW)
    config.shaped_recipe(acs).setEntries(aiB, ajb).setEntries(aat, ahv).setEntries(adg, aib).setOutput(acs)
    config.shaped_recipe(afx).setEntries(aad, ahv).setEntries(aiC, agJ).setOutput(afx)
    config.shapeless_recipe(agJ).addInput("ender_pearl", 1).addInput("blaze_powder", 1).setOutput(agJ)
    config.shaped_recipe(afu).setEntries(aiH, "ghast_tear").setEntries(aiC, agJ).setEntries(aah, aiZ).setOutput(afu)
    config.shaped_recipe("end_rod").setEntries(ain, abw).setEntries(aih, agY).setOutput((4, "end_rod"))
    config.shaped_recipe(aco).setEntries(aar, "end_stone").setOutput((4, aco))
    config.shaped_recipe("end_stone_brick_slab").setEntries(aaZ, aco).setOutput((6, "end_stone_brick_slab"))
    config.shaped_recipe("end_stone_brick_stairs").setEntries(aak, aco).setOutput((4, "end_stone_brick_stairs"))
    config.shaped_recipe("end_stone_brick_wall").setEntries(aan, aco).setOutput((6, "end_stone_brick_wall"))
    config.shapeless_recipe(abs).addInput("spider_eye", 1).addInput("brown_mushroom", 1).addInput(aiJ, 1).setOutput(abs)
    config.shapeless_recipe("fire_charge").addInput(ahd, 1).addInput("blaze_powder", 1).setOutput((3, "fire_charge"))
    config.shaped_recipe(afg).setEntries([(0, 2), (1, 1), (2, 0)], aiY).setEntries([(2, 1), (2, 2)], aig).setOutput(afg)
    config.shaped_recipe(acR).setEntries(aau, ahX).setEntries(adi, aiW).setOutput(acR)
    config.shapeless_recipe(acK).addInput(agc, 1).addInput(aiW, 1).setOutput(acK)
    config.shapeless_recipe(abj).addInput(aiU, 1).addInput("oxeye_daisy", 1).setOutput(abj)
    config.shaped_recipe(afY).setEntries(aaY, aiV).setOutput(afY)
    config.shaped_recipe(aie).setEntries(aad, afO).setOutput(aie)
    config.shaped_recipe(acz).setEntries(aih, aie).setEntries(ain, ahr).setOutput(acz)
    config.smelting_recipe(aiZ).add_ingredient("#sand").setXp(ajw).setOutput(aiZ)
    config.shaped_recipe("glass_bottle").setEntries(aaY, aiZ).setOutput((3, "glass_bottle"))
    config.shaped_recipe(agj).setEntries(aan, aiZ).setOutput((16, agj))
    config.shaped_recipe(aaR).setEntries(aad, afn).setEntries(aiC, afG).setOutput(aaR)
    config.shaped_recipe(agZ).setEntries(aar, adD).setOutput(agZ)
    config.shaped_recipe(aeH).setEntries(aad, ags).setEntries(aiC, "apple").setOutput(aeH)
    config.shaped_recipe(agB).setEntries(adt, aiY).setEntries(aaN, ags).setOutput(agB)
    config.shaped_recipe(aeO).setEntries(aas, ags).setOutput(aeO)
    config.shaped_recipe(aev).setEntries(aad, afn).setEntries(aiC, ais).setOutput(aev)
    config.shaped_recipe(acn).setEntries(aae, ags).setOutput(acn)
    config.shaped_recipe(adM).setEntries(aap, ags).setOutput(adM)
    config.shaped_recipe(afU).setEntries(adt, aiY).setEntries(adi, ags).setOutput(afU)
    config.shaped_recipe(acG).setEntries(aah, ags).setOutput(acG)
    config.shaped_recipe(ado).setEntries(adt, aiY).setEntries(aaZ, ags).setOutput(ado)
    config.shaped_recipe(adI).setEntries(adn, aiY).setEntries(aih, ags).setOutput(adI)
    config.shaped_recipe(aeK).setEntries(aiE, aiY).setEntries(adA, ags).setOutput(aeK)
    config.shaped_recipe(agi).setEntries(aac, ags).setOutput(agi)
    config.smelting_recipe(ags).add_ingredient(ahn).setXp(aju).setOutput(ags)
    config.smelting_recipe("gold_ingot_from_blasting", abP).add_ingredient(ahn).setXp(aju).setOutput(
        ags).setCookingTime(ajy)
    config.shapeless_recipe("gold_ingot_from_gold_block").addInput(agi, 1).setOutput((9, ags)).setGroup(ags)
    config.shaped_recipe("gold_ingot_from_nuggets").setEntries(aac, afn).setOutput(ags).setGroup(ags)
    config.shapeless_recipe(afn).addInput(ags, 1).setOutput((9, afn))
    config.smelting_recipe("gold_nugget_from_blasting", abP).add_ingredient(aab).setXp(ajw).setOutput(
        afn).setCookingTime(ajy)
    config.smelting_recipe("gold_nugget_from_smelting").add_ingredient(aab).setXp(ajw).setOutput(afn)
    config.shapeless_recipe(ahU).addInput(ahY, 1).addInput(aiw, 1).setOutput(ahU)
    config.shaped_recipe("granite_slab").setEntries(aaZ, ahU).setOutput((6, "granite_slab"))
    config.shaped_recipe("granite_stairs").setEntries(aak, ahU).setOutput((4, "granite_stairs"))
    config.shaped_recipe("granite_wall").setEntries(aan, ahU).setOutput((6, "granite_wall"))
    config.shaped_recipe(afl).setEntries(aan, agW).setEntries(aiH, aiY).setOutput(afl).setGroup(aip)
    config.shaped_recipe(ahl).setEntries(aaZ, agW).setEntries(aaM, ahX).setOutput(ahl).setGroup(ajp)
    config.shapeless_recipe("gray_bed_from_white_bed").addInput(agP, 1).addInput(ahN, 1).setOutput(ahl).setGroup(ahz)
    config.shaped_recipe("gray_carpet").setEntries(adi, agW).setOutput((3, "gray_carpet")).setGroup(aim)
    config.shaped_recipe("gray_carpet_from_white_carpet").setEntries(aad, aeW).setEntries(aiC, ahN).setOutput(
        (8, "gray_carpet")).setGroup(aim)
    config.shapeless_recipe("gray_concrete_powder").addInput(ahN, 1).addInput(ajf, 4).addInput(aio, 4).setOutput(
        (8, "gray_concrete_powder")).setGroup(acO)
    config.shapeless_recipe(ahN).addInput(agI, 1).addInput(ahb, 1).setOutput((2, ahN))
    config.smelting_recipe(aaT).add_ingredient(acS).setXp(ajw).setOutput(aaT)
    config.shaped_recipe(abO).setEntries(aad, aiZ).setEntries(aiC, ahN).setOutput((8, abO)).setGroup(aed)
    config.shaped_recipe("gray_stained_glass_pane").setEntries(aan, abO).setOutput(
        (16, "gray_stained_glass_pane")).setGroup(abC)
    config.shaped_recipe("gray_stained_glass_pane_from_glass_pane").setEntries(aad, agj).setEntries(aiC, ahN).setOutput(
        (8, "gray_stained_glass_pane")).setGroup(abC)
    config.shaped_recipe(acS).setEntries(aad, agl).setEntries(aiC, ahN).setOutput((8, acS)).setGroup(abF)
    config.shapeless_recipe(agW).addInput(ahN, 1).addInput(agC, 1).setOutput(agW).setGroup(ajd)
    config.shaped_recipe(aez).setEntries(aan, afV).setEntries(aiH, aiY).setOutput(aez).setGroup(aip)
    config.shaped_recipe(ahh).setEntries(aaZ, afV).setEntries(aaM, ahX).setOutput(ahh).setGroup(ajp)
    config.shapeless_recipe("green_bed_from_white_bed").addInput(agP, 1).addInput(agH, 1).setOutput(ahh).setGroup(ahz)
    config.shaped_recipe("green_carpet").setEntries(adi, afV).setOutput((3, "green_carpet")).setGroup(aim)
    config.shaped_recipe("green_carpet_from_white_carpet").setEntries(aad, aeW).setEntries(aiC, agH).setOutput(
        (8, "green_carpet")).setGroup(aim)
    config.shapeless_recipe("green_concrete_powder").addInput(agH, 1).addInput(ajf, 4).addInput(aio, 4).setOutput(
        (8, "green_concrete_powder")).setGroup(acO)
    config.smelting_recipe(agH).add_ingredient("cactus").setXp(aju).setOutput(agH)
    config.smelting_recipe(aaH).add_ingredient(acE).setXp(ajw).setOutput(aaH)
    config.shaped_recipe(abz).setEntries(aad, aiZ).setEntries(aiC, agH).setOutput((8, abz)).setGroup(aed)
    config.shaped_recipe("green_stained_glass_pane").setEntries(aan, abz).setOutput(
        (16, "green_stained_glass_pane")).setGroup(abC)
    config.shaped_recipe("green_stained_glass_pane_from_glass_pane").setEntries(aad, agj).setEntries(aiC,
                                                                                                     agH).setOutput(
        (8, "green_stained_glass_pane")).setGroup(abC)
    config.shaped_recipe(acE).setEntries(aad, agl).setEntries(aiC, agH).setOutput((8, acE)).setGroup(abF)
    config.shapeless_recipe(afV).addInput(agH, 1).addInput(agC, 1).setOutput(afV).setGroup(ajd)
    config.shaped_recipe(agA).setEntries(adv, aiY).setEntries(aiB, agr).setEntries(adg, ahX).setOutput(agA)
    config.shaped_recipe(ahe).setEntries(aac, aiK).setOutput(ahe)
    config.shaped_recipe(aax).setEntries(adi, agc).setOutput(aax)
    config.shaped_recipe(acM).setEntries(aar, ahg).setOutput(acM)
    config.shaped_recipe(afa).setEntries(aar, aeM).setOutput(afa)
    config.shapeless_recipe(aeM).addInput(afa, 1).addInput("glass_bottle", 4).setOutput((4, aeM))
    config.shaped_recipe(aiu).setEntries(aiC, aiO).setEntries([(0, 0), (0, 1), (1, 2), (2, 0), (2, 1)], agc).setOutput(
        aiu)
    config.shaped_recipe(acN).setEntries(aih, aiu).setEntries(ain, ahr).setOutput(acN)
    config.shaped_recipe(ahE).setEntries(adt, aiY).setEntries(aaN, agc).setOutput(ahE)
    config.shaped_recipe("iron_bars").setEntries(aan, agc).setOutput((16, "iron_bars"))
    config.shaped_recipe(agy).setEntries(aac, agc).setOutput(agy)
    config.shaped_recipe(agt).setEntries(aas, agc).setOutput(agt)
    config.shaped_recipe(acV).setEntries(aae, agc).setOutput(acV)
    config.shaped_recipe("iron_door").setEntries(aal, agc).setOutput((3, "iron_door"))
    config.shaped_recipe(afE).setEntries(aap, agc).setOutput(afE)
    config.shaped_recipe(ahm).setEntries(adt, aiY).setEntries(adi, agc).setOutput(ahm)
    config.smelting_recipe(agc).add_ingredient(ahM).setXp(ajv).setOutput(agc)
    config.smelting_recipe("iron_ingot_from_blasting", abP).add_ingredient(ahM).setXp(ajv).setOutput(
        agc).setCookingTime(ajy)
    config.shapeless_recipe("iron_ingot_from_iron_block").addInput(agy, 1).setOutput((9, agc)).setGroup(agc)
    config.shaped_recipe("iron_ingot_from_nuggets").setEntries(aac, afA).setOutput(agc).setGroup(agc)
    config.shaped_recipe(aek).setEntries(aah, agc).setOutput(aek)
    config.shapeless_recipe(afA).addInput(agc, 1).setOutput((9, afA))
    config.smelting_recipe("iron_nugget_from_blasting", abP).add_ingredient(aaa).setXp(ajw).setOutput(
        afA).setCookingTime(ajy)
    config.smelting_recipe("iron_nugget_from_smelting").add_ingredient(aaa).setXp(ajw).setOutput(afA)
    config.shaped_recipe(aeG).setEntries(adt, aiY).setEntries(aaZ, agc).setOutput(aeG)
    config.shaped_recipe(afF).setEntries(adn, aiY).setEntries(aih, agc).setOutput(afF)
    config.shaped_recipe(agb).setEntries(aiE, aiY).setEntries(adA, agc).setOutput(agb)
    config.shaped_recipe(adV).setEntries(aar, agc).setOutput(adV)
    config.shaped_recipe(agz).setEntries(aad, aiY).setEntries(aiC, ahZ).setOutput(agz)
    config.shaped_recipe(adk).setEntries(aih, "carved_pumpkin").setEntries(ain, aiN).setOutput(adk)
    config.shaped_recipe(aif).setEntries(aad, ahX).setEntries(aiC, aib).setOutput(aif)
    config.shaped_recipe(afr).setEntries(aao, aes).setOutput(afr).setGroup(ajk)
    config.shapeless_recipe(adJ).addInput(aes, 1).setOutput(adJ).setGroup(aex)
    config.shaped_recipe("jungle_door").setEntries(aal, aes).setOutput((3, "jungle_door")).setGroup(afk)
    config.shaped_recipe("jungle_fence").setEntries(ada, aiY).setEntries(aas, aes).setOutput(
        (3, "jungle_fence")).setGroup(aeR)
    config.shaped_recipe(acl).setEntries(aas, aiY).setEntries(ada, aes).setOutput(acl).setGroup(abT)
    config.shapeless_recipe(aes).addInput("#jungle_logs", 1).setOutput((4, aes)).setGroup(aiG)
    config.shaped_recipe(abl).setEntries(adi, aes).setOutput(abl).setGroup(abi)
    config.shaped_recipe("jungle_sign").setEntries(aan, aes).setEntries(aiH, aiY).setOutput((3, "jungle_sign"))
    config.shaped_recipe("jungle_slab").setEntries(aaZ, aes).setOutput((6, "jungle_slab")).setGroup(afh)
    config.shaped_recipe("jungle_stairs").setEntries(aak, aes).setOutput((4, "jungle_stairs")).setGroup(adP)
    config.shaped_recipe("jungle_trapdoor").setEntries(aan, aes).setOutput((2, "jungle_trapdoor")).setGroup(acF)
    config.shaped_recipe("jungle_wood").setEntries(aar, "jungle_log").setOutput((3, "jungle_wood")).setGroup(aja)
    config.shaped_recipe("ladder").setEntries(aai, aiY).setOutput((3, "ladder"))
    config.shaped_recipe(aic).setEntries(aiC, aiN).setEntries(aad, afA).setOutput(aic)
    config.shaped_recipe(afc).setEntries(aac, aeD).setOutput(afc)
    config.smelting_recipe("lapis_from_blasting", abP).add_ingredient(ahf).setXp(ajt).setOutput(aeD).setCookingTime(ajy)
    config.smelting_recipe("lapis_from_smelting").add_ingredient(ahf).setXp(ajt).setOutput(aeD)
    config.shapeless_recipe(aeD).addInput(afc, 1).setOutput((9, aeD))
    config.shaped_recipe("lead").setEntries([(0, 0), (0, 1), (1, 0), (2, 2)], aig).setEntries(aiC, ago).setOutput(
        (2, "lead"))
    config.shaped_recipe(ahZ).setEntries(aar, "rabbit_hide").setOutput(ahZ)
    config.shaped_recipe(adW).setEntries(aas, ahZ).setOutput(adW)
    config.shaped_recipe(abH).setEntries(aae, ahZ).setOutput(abH)
    config.shaped_recipe(adm).setEntries(aap, ahZ).setOutput(adm)
    config.shaped_recipe(abB).setEntries(aai, ahZ).setOutput(abB)
    config.shaped_recipe(acv).setEntries(aah, ahZ).setOutput(acv)
    config.shaped_recipe(ahR).setEntries([(0, 0), (1, 0), (1, 2), (2, 0)], adH).setEntries(aiC, ahc).setOutput(ahR)
    config.shaped_recipe(aiL).setEntries(ain, afO).setEntries(aih, aiY).setOutput(aiL)
    config.shaped_recipe(acc).setEntries(aan, acH).setEntries(aiH, aiY).setOutput(acc).setGroup(aip)
    config.shaped_recipe(adw).setEntries(aaZ, acH).setEntries(aaM, ahX).setOutput(adw).setGroup(ajp)
    config.shapeless_recipe("light_blue_bed_from_white_bed").addInput(agP, 1).addInput(adE, 1).setOutput(adw).setGroup(
        ahz)
    config.shaped_recipe("light_blue_carpet").setEntries(adi, acH).setOutput((3, "light_blue_carpet")).setGroup(aim)
    config.shaped_recipe("light_blue_carpet_from_white_carpet").setEntries(aad, aeW).setEntries(aiC, adE).setOutput(
        (8, "light_blue_carpet")).setGroup(aim)
    config.shapeless_recipe("light_blue_concrete_powder").addInput(adE, 1).addInput(ajf, 4).addInput(aio, 4).setOutput(
        (8, "light_blue_concrete_powder")).setGroup(acO)
    config.shapeless_recipe("light_blue_dye_from_blue_orchid").addInput("blue_orchid", 1).setOutput(adE).setGroup(adE)
    config.shapeless_recipe("light_blue_dye_from_blue_white_dye").addInput(ahs, 1).addInput(ahb, 1).setOutput(
        (2, adE)).setGroup(adE)
    config.smelting_recipe(aay).add_ingredient(abf).setXp(ajw).setOutput(aay)
    config.shaped_recipe(aaG).setEntries(aad, aiZ).setEntries(aiC, adE).setOutput((8, aaG)).setGroup(aed)
    config.shaped_recipe("light_blue_stained_glass_pane").setEntries(aan, aaG).setOutput(
        (16, "light_blue_stained_glass_pane")).setGroup(abC)
    config.shaped_recipe("light_blue_stained_glass_pane_from_glass_pane").setEntries(aad, agj).setEntries(aiC,
                                                                                                          adE).setOutput(
        (8, "light_blue_stained_glass_pane")).setGroup(abC)
    config.shaped_recipe(abf).setEntries(aad, agl).setEntries(aiC, adE).setOutput((8, abf)).setGroup(abF)
    config.shapeless_recipe(acH).addInput(adE, 1).addInput(agC, 1).setOutput(acH).setGroup(ajd)
    config.shaped_recipe(abX).setEntries(aan, acY).setEntries(aiH, aiY).setOutput(abX).setGroup(aip)
    config.shaped_recipe(adB).setEntries(aaZ, acY).setEntries(aaM, ahX).setOutput(adB).setGroup(ajp)
    config.shapeless_recipe("light_gray_bed_from_white_bed").addInput(agP, 1).addInput(adu, 1).setOutput(adB).setGroup(
        ahz)
    config.shaped_recipe("light_gray_carpet").setEntries(adi, acY).setOutput((3, "light_gray_carpet")).setGroup(aim)
    config.shaped_recipe("light_gray_carpet_from_white_carpet").setEntries(aad, aeW).setEntries(aiC, adu).setOutput(
        (8, "light_gray_carpet")).setGroup(aim)
    config.shapeless_recipe("light_gray_concrete_powder").addInput(adu, 1).addInput(ajf, 4).addInput(aio, 4).setOutput(
        (8, "light_gray_concrete_powder")).setGroup(acO)
    config.shapeless_recipe("light_gray_dye_from_azure_bluet").addInput("azure_bluet", 1).setOutput(adu).setGroup(adu)
    config.shapeless_recipe("light_gray_dye_from_black_white_dye").addInput(agI, 1).addInput(ahb, 2).setOutput(
        (3, adu)).setGroup(adu)
    config.shapeless_recipe("light_gray_dye_from_gray_white_dye").addInput(ahN, 1).addInput(ahb, 1).setOutput(
        (2, adu)).setGroup(adu)
    config.shapeless_recipe("light_gray_dye_from_oxeye_daisy").addInput("oxeye_daisy", 1).setOutput(adu).setGroup(adu)
    config.shapeless_recipe("light_gray_dye_from_white_tulip").addInput("white_tulip", 1).setOutput(adu).setGroup(adu)
    config.smelting_recipe(aaz).add_ingredient(abe).setXp(ajw).setOutput(aaz)
    config.shaped_recipe(aaD).setEntries(aad, aiZ).setEntries(aiC, adu).setOutput((8, aaD)).setGroup(aed)
    config.shaped_recipe("light_gray_stained_glass_pane").setEntries(aan, aaD).setOutput(
        (16, "light_gray_stained_glass_pane")).setGroup(abC)
    config.shaped_recipe("light_gray_stained_glass_pane_from_glass_pane").setEntries(aad, agj).setEntries(aiC,
                                                                                                          adu).setOutput(
        (8, "light_gray_stained_glass_pane")).setGroup(abC)
    config.shaped_recipe(abe).setEntries(aad, agl).setEntries(aiC, adu).setOutput((8, abe)).setGroup(abF)
    config.shapeless_recipe(acY).addInput(adu, 1).addInput(agC, 1).setOutput(acY).setGroup(ajd)
    config.shaped_recipe(aaw).setEntries(adi, ags).setOutput(aaw)
    config.shaped_recipe(afd).setEntries(aan, agX).setEntries(aiH, aiY).setOutput(afd).setGroup(aip)
    config.shaped_recipe(ahk).setEntries(aaZ, agX).setEntries(aaM, ahX).setOutput(ahk).setGroup(ajp)
    config.shapeless_recipe("lime_bed_from_white_bed").addInput(agP, 1).addInput(ahA, 1).setOutput(ahk).setGroup(ahz)
    config.shaped_recipe("lime_carpet").setEntries(adi, agX).setOutput((3, "lime_carpet")).setGroup(aim)
    config.shaped_recipe("lime_carpet_from_white_carpet").setEntries(aad, aeW).setEntries(aiC, ahA).setOutput(
        (8, "lime_carpet")).setGroup(aim)
    config.shapeless_recipe("lime_concrete_powder").addInput(ahA, 1).addInput(ajf, 4).addInput(aio, 4).setOutput(
        (8, "lime_concrete_powder")).setGroup(acO)
    config.shapeless_recipe(ahA).addInput(agH, 1).addInput(ahb, 1).setOutput((2, ahA))
    config.smelting_recipe("lime_dye_from_smelting").add_ingredient("sea_pickle").setXp(ajw).setOutput(ahA)
    config.smelting_recipe(aaP).add_ingredient(acT).setXp(ajw).setOutput(aaP)
    config.shaped_recipe(abQ).setEntries(aad, aiZ).setEntries(aiC, ahA).setOutput((8, abQ)).setGroup(aed)
    config.shaped_recipe("lime_stained_glass_pane").setEntries(aan, abQ).setOutput(
        (16, "lime_stained_glass_pane")).setGroup(abC)
    config.shaped_recipe("lime_stained_glass_pane_from_glass_pane").setEntries(aad, agj).setEntries(aiC, ahA).setOutput(
        (8, "lime_stained_glass_pane")).setGroup(abC)
    config.shaped_recipe(acT).setEntries(aad, agl).setEntries(aiC, ahA).setOutput((8, acT)).setGroup(abF)
    config.shapeless_recipe(agX).addInput(ahA, 1).addInput(agC, 1).setOutput(agX).setGroup(ajd)
    config.shaped_recipe(ajc).setEntries(adz, ahX).setEntries(adi, aig).setOutput(ajc)
    config.shaped_recipe(ade).setEntries(aan, aeN).setEntries(aiH, aiY).setOutput(ade).setGroup(aip)
    config.shaped_recipe(afw).setEntries(aaZ, aeN).setEntries(aaM, ahX).setOutput(afw).setGroup(ajp)
    config.shapeless_recipe("magenta_bed_from_white_bed").addInput(agP, 1).addInput(afm, 1).setOutput(afw).setGroup(ahz)
    config.shaped_recipe("magenta_carpet").setEntries(adi, aeN).setOutput((3, "magenta_carpet")).setGroup(aim)
    config.shaped_recipe("magenta_carpet_from_white_carpet").setEntries(aad, aeW).setEntries(aiC, afm).setOutput(
        (8, "magenta_carpet")).setGroup(aim)
    config.shapeless_recipe("magenta_concrete_powder").addInput(afm, 1).addInput(ajf, 4).addInput(aio, 4).setOutput(
        (8, "magenta_concrete_powder")).setGroup(acO)
    config.shapeless_recipe("magenta_dye_from_allium").addInput("allium", 1).setOutput(afm).setGroup(afm)
    config.shapeless_recipe("magenta_dye_from_blue_red_pink").addInput(ahs, 1).addInput(ahT, 1).addInput(ahD,
                                                                                                         1).setOutput(
        (3, afm)).setGroup(afm)
    config.shapeless_recipe("magenta_dye_from_blue_red_white_dye").addInput(ahs, 1).addInput(ahT, 2).addInput(ahb,
                                                                                                              1).setOutput(
        (4, afm)).setGroup(afm)
    config.shapeless_recipe("magenta_dye_from_lilac").addInput("lilac", 1).setOutput(acB).setGroup(afm)
    config.shapeless_recipe("magenta_dye_from_purple_and_pink").addInput(agE, 1).addInput(ahD, 1).setOutput(
        acB).setGroup(afm)
    config.smelting_recipe(aaB).add_ingredient(abD).setXp(ajw).setOutput(aaB)
    config.shaped_recipe(abh).setEntries(aad, aiZ).setEntries(aiC, afm).setOutput((8, abh)).setGroup(aed)
    config.shaped_recipe("magenta_stained_glass_pane").setEntries(aan, abh).setOutput(
        (16, "magenta_stained_glass_pane")).setGroup(abC)
    config.shaped_recipe("magenta_stained_glass_pane_from_glass_pane").setEntries(aad, agj).setEntries(aiC,
                                                                                                       afm).setOutput(
        (8, "magenta_stained_glass_pane")).setGroup(abC)
    config.shaped_recipe(abD).setEntries(aad, agl).setEntries(aiC, afm).setOutput((8, abD)).setGroup(abF)
    config.shapeless_recipe(aeN).addInput(afm, 1).addInput(agC, 1).setOutput(aeN).setGroup(ajd)
    config.shaped_recipe(afs).setEntries(aar, afv).setOutput(afs)
    config.shapeless_recipe(afv).addInput("blaze_powder", 1).addInput(ago, 1).setOutput(afv)
    config.shaped_recipe(ajq).setEntries(aad, aiU).setEntries(aiC, ahV).setOutput(ajq)
    config.shaped_recipe(aiQ).setEntries(aac, afG).setOutput(aiQ)
    config.shapeless_recipe(afz).addInput(afG, 1).setOutput(afz)
    config.shaped_recipe(ahr).setEntries(aao, agc).setOutput(ahr)
    config.shapeless_recipe(abd).addInput(aiU, 1).addInput("enchanted_golden_apple", 1).setOutput(abd)
    config.shapeless_recipe(ace).addInput(afO, 1).addInput("vine", 1).setOutput(ace)
    config.shaped_recipe("mossy_cobblestone_slab").setEntries(aaZ, ace).setOutput((6, "mossy_cobblestone_slab"))
    config.shaped_recipe("mossy_cobblestone_stairs").setEntries(aak, ace).setOutput((4, "mossy_cobblestone_stairs"))
    config.shaped_recipe("mossy_cobblestone_wall").setEntries(aan, ace).setOutput((6, "mossy_cobblestone_wall"))
    config.shapeless_recipe(abJ).addInput(aeP, 1).addInput("vine", 1).setOutput(abJ)
    config.shaped_recipe("mossy_stone_brick_slab").setEntries(aaZ, abJ).setOutput((6, "mossy_stone_brick_slab"))
    config.shaped_recipe("mossy_stone_brick_stairs").setEntries(aak, abJ).setOutput((4, "mossy_stone_brick_stairs"))
    config.shaped_recipe("mossy_stone_brick_wall").setEntries(aan, abJ).setOutput((6, "mossy_stone_brick_wall"))
    config.shapeless_recipe(aef).addInput("brown_mushroom", 1).addInput("red_mushroom", 1).addInput("bowl",
                                                                                                    1).setOutput(aef)
    config.smelting_recipe(aeV).add_ingredient("netherrack").setXp(ajw).setOutput(aeV)
    config.shaped_recipe(adT).setEntries(aar, aeV).setOutput(adT)
    config.shaped_recipe("nether_brick_fence").setEntries(aas, adT).setEntries(ada, aeV).setOutput(
        (6, "nether_brick_fence"))
    config.shaped_recipe("nether_brick_slab").setEntries(aaZ, adT).setOutput((6, "nether_brick_slab"))
    config.shaped_recipe("nether_brick_stairs").setEntries(aak, adT).setOutput((4, "nether_brick_stairs"))
    config.shaped_recipe("nether_brick_wall").setEntries(aan, adT).setOutput((6, "nether_brick_wall"))
    config.shaped_recipe(abZ).setEntries(aac, afq).setOutput(abZ)
    config.shaped_recipe(agF).setEntries(aad, ahX).setEntries(aiC, ahj).setOutput(agF)
    config.shaped_recipe(ahy).setEntries(aao, agn).setOutput(ahy).setGroup(ajk)
    config.shapeless_recipe(agu).addInput(agn, 1).setOutput(agu).setGroup(aex)
    config.shaped_recipe("oak_door").setEntries(aal, agn).setOutput((3, "oak_door")).setGroup(afk)
    config.shaped_recipe("oak_fence").setEntries(ada, aiY).setEntries(aas, agn).setOutput((3, "oak_fence")).setGroup(
        aeR)
    config.shaped_recipe(adC).setEntries(aas, aiY).setEntries(ada, agn).setOutput(adC).setGroup(abT)
    config.shapeless_recipe(agn).addInput("#oak_logs", 1).setOutput((4, agn)).setGroup(aiG)
    config.shaped_recipe(abL).setEntries(adi, agn).setOutput(abL).setGroup(abi)
    config.shaped_recipe("oak_sign").setEntries(aan, agn).setEntries(aiH, aiY).setOutput((3, "oak_sign"))
    config.shaped_recipe("oak_slab").setEntries(aaZ, agn).setOutput((6, "oak_slab")).setGroup(afh)
    config.shaped_recipe("oak_stairs").setEntries(aak, agn).setOutput((4, "oak_stairs")).setGroup(adP)
    config.shaped_recipe("oak_trapdoor").setEntries(aan, agn).setOutput((2, "oak_trapdoor")).setGroup(acF)
    config.shaped_recipe("oak_wood").setEntries(aar, "oak_log").setOutput((3, "oak_wood")).setGroup(aja)
    config.shaped_recipe(ahH).setEntries([(2, 1)], aiw).setEntries(adz, ahj).setEntries(aam, afO).setOutput(ahH)
    config.shaped_recipe(adF).setEntries(aan, afK).setEntries(aiH, aiY).setOutput(adF).setGroup(aip)
    config.shaped_recipe(afR).setEntries(aaZ, afK).setEntries(aaM, ahX).setOutput(afR).setGroup(ajp)
    config.shapeless_recipe("orange_bed_from_white_bed").addInput(agP, 1).addInput(agw, 1).setOutput(afR).setGroup(ahz)
    config.shaped_recipe("orange_carpet").setEntries(adi, afK).setOutput((3, "orange_carpet")).setGroup(aim)
    config.shaped_recipe("orange_carpet_from_white_carpet").setEntries(aad, aeW).setEntries(aiC, agw).setOutput(
        (8, "orange_carpet")).setGroup(aim)
    config.shapeless_recipe("orange_concrete_powder").addInput(agw, 1).addInput(ajf, 4).addInput(aio, 4).setOutput(
        (8, "orange_concrete_powder")).setGroup(acO)
    config.shapeless_recipe("orange_dye_from_orange_tulip").addInput("orange_tulip", 1).setOutput(agw).setGroup(agw)
    config.shapeless_recipe("orange_dye_from_red_yellow").addInput(ahT, 1).addInput(agk, 1).setOutput(
        (2, agw)).setGroup(agw)
    config.smelting_recipe(aaE).add_ingredient(ach).setXp(ajw).setOutput(aaE)
    config.shaped_recipe(abo).setEntries(aad, aiZ).setEntries(aiC, agw).setOutput((8, abo)).setGroup(aed)
    config.shaped_recipe("orange_stained_glass_pane").setEntries(aan, abo).setOutput(
        (16, "orange_stained_glass_pane")).setGroup(abC)
    config.shaped_recipe("orange_stained_glass_pane_from_glass_pane").setEntries(aad, agj).setEntries(aiC,
                                                                                                      agw).setOutput(
        (8, "orange_stained_glass_pane")).setGroup(abC)
    config.shaped_recipe(ach).setEntries(aad, agl).setEntries(aiC, agw).setOutput((8, ach)).setGroup(abF)
    config.shapeless_recipe(afK).addInput(agw, 1).addInput(agC, 1).setOutput(afK).setGroup(ajd)
    config.shapeless_recipe(aga).addInput("ice", 9).setOutput(aga)
    config.shaped_recipe(ahq).setEntries(aad, aiY).setEntries(aiC, "#wool").setOutput(ahq)
    config.shaped_recipe(aiU).setEntries(aaZ, afW).setOutput((3, aiU))
    config.shaped_recipe(afy).setEntries(aan, agV).setEntries(aiH, aiY).setOutput(afy).setGroup(aip)
    config.shaped_recipe(ahu).setEntries(aaZ, agV).setEntries(aaM, ahX).setOutput(ahu).setGroup(ajp)
    config.shapeless_recipe("pink_bed_from_white_bed").addInput(agP, 1).addInput(ahD, 1).setOutput(ahu).setGroup(ahz)
    config.shaped_recipe("pink_carpet").setEntries(adi, agV).setOutput((3, "pink_carpet")).setGroup(aim)
    config.shaped_recipe("pink_carpet_from_white_carpet").setEntries(aad, aeW).setEntries(aiC, ahD).setOutput(
        (8, "pink_carpet")).setGroup(aim)
    config.shapeless_recipe("pink_concrete_powder").addInput(ahD, 1).addInput(ajf, 4).addInput(aio, 4).setOutput(
        (8, "pink_concrete_powder")).setGroup(acO)
    config.shapeless_recipe("pink_dye_from_peony").addInput("peony", 1).setOutput(adX).setGroup(ahD)
    config.shapeless_recipe("pink_dye_from_pink_tulip").addInput("pink_tulip", 1).setOutput(ahD).setGroup(ahD)
    config.shapeless_recipe("pink_dye_from_red_white_dye").addInput(ahT, 1).addInput(ahb, 1).setOutput(adX).setGroup(
        ahD)
    config.smelting_recipe(aaQ).add_ingredient(acX).setXp(ajw).setOutput(aaQ)
    config.shaped_recipe(abM).setEntries(aad, aiZ).setEntries(aiC, ahD).setOutput((8, abM)).setGroup(aed)
    config.shaped_recipe("pink_stained_glass_pane").setEntries(aan, abM).setOutput(
        (16, "pink_stained_glass_pane")).setGroup(abC)
    config.shaped_recipe("pink_stained_glass_pane_from_glass_pane").setEntries(aad, agj).setEntries(aiC, ahD).setOutput(
        (8, "pink_stained_glass_pane")).setGroup(abC)
    config.shaped_recipe(acX).setEntries(aad, agl).setEntries(aiC, ahD).setOutput((8, acX)).setGroup(abF)
    config.shapeless_recipe(agV).addInput(ahD, 1).addInput(agC, 1).setOutput(agV).setGroup(ajd)
    config.shaped_recipe(ait).setEntries(aiH, ahj).setEntries([(0, 1), (0, 2), (2, 1), (2, 2)], afO).setEntries(aaZ,
                                                                                                                ahX).setEntries(
        aiC, agc).setOutput(ait)
    config.shaped_recipe(acf).setEntries(aar, ahB).setOutput((4, acf))
    config.shaped_recipe("polished_andesite_slab").setEntries(aaZ, acf).setOutput((6, "polished_andesite_slab"))
    config.shaped_recipe("polished_andesite_stairs").setEntries(aak, acf).setOutput((4, "polished_andesite_stairs"))
    config.shaped_recipe(acr).setEntries(aar, ahY).setOutput((4, acr))
    config.shaped_recipe("polished_diorite_slab").setEntries(aaZ, acr).setOutput((6, "polished_diorite_slab"))
    config.shaped_recipe("polished_diorite_stairs").setEntries(aak, acr).setOutput((4, "polished_diorite_stairs"))
    config.shaped_recipe(acq).setEntries(aar, ahU).setOutput((4, acq))
    config.shaped_recipe("polished_granite_slab").setEntries(aaZ, acq).setOutput((6, "polished_granite_slab"))
    config.shaped_recipe("polished_granite_stairs").setEntries(aak, acq).setOutput((4, "polished_granite_stairs"))
    config.smelting_recipe(abw).add_ingredient("chorus_fruit").setXp(ajw).setOutput(abw)
    config.shaped_recipe("powered_rail").setEntries(aiH, ahj).setEntries(aiC, aiY).setEntries(aaj, ags).setOutput(
        (6, "powered_rail"))
    config.shaped_recipe(agp).setEntries(aar, acp).setOutput(agp)
    config.shaped_recipe(abS).setEntries(aac, acp).setOutput(abS)
    config.shaped_recipe("prismarine_brick_slab").setEntries(aaZ, abS).setOutput((6, "prismarine_brick_slab"))
    config.shaped_recipe("prismarine_brick_stairs").setEntries(aak, abS).setOutput((4, "prismarine_brick_stairs"))
    config.shaped_recipe("prismarine_slab").setEntries(aaZ, agp).setOutput((6, "prismarine_slab"))
    config.shaped_recipe("prismarine_stairs").setEntries(aak, agp).setOutput((4, "prismarine_stairs"))
    config.shaped_recipe("prismarine_wall").setEntries(aan, agp).setOutput((6, "prismarine_wall"))
    config.shapeless_recipe(aeX).addInput("pumpkin", 1).addInput(aiJ, 1).addInput(ajl, 1).setOutput(aeX)
    config.shapeless_recipe("pumpkin_seeds").addInput("pumpkin", 1).setOutput((4, "pumpkin_seeds"))
    config.shaped_recipe(aen).setEntries(aan, afL).setEntries(aiH, aiY).setOutput(aen).setGroup(aip)
    config.shaped_recipe(afX).setEntries(aaZ, afL).setEntries(aaM, ahX).setOutput(afX).setGroup(ajp)
    config.shapeless_recipe("purple_bed_from_white_bed").addInput(agP, 1).addInput(agE, 1).setOutput(afX).setGroup(ahz)
    config.shaped_recipe("purple_carpet").setEntries(adi, afL).setOutput((3, "purple_carpet")).setGroup(aim)
    config.shaped_recipe("purple_carpet_from_white_carpet").setEntries(aad, aeW).setEntries(aiC, agE).setOutput(
        (8, "purple_carpet")).setGroup(aim)
    config.shapeless_recipe("purple_concrete_powder").addInput(agE, 1).addInput(ajf, 4).addInput(aio, 4).setOutput(
        (8, "purple_concrete_powder")).setGroup(acO)
    config.shapeless_recipe(agE).addInput(ahs, 1).addInput(ahT, 1).setOutput((2, agE))
    config.smelting_recipe(aaC).add_ingredient(abU).setXp(ajw).setOutput(aaC)
    config.shaped_recipe(abn).setEntries(aad, aiZ).setEntries(aiC, agE).setOutput((8, abn)).setGroup(aed)
    config.shaped_recipe("purple_stained_glass_pane").setEntries(aan, abn).setOutput(
        (16, "purple_stained_glass_pane")).setGroup(abC)
    config.shaped_recipe("purple_stained_glass_pane_from_glass_pane").setEntries(aad, agj).setEntries(aiC,
                                                                                                      agE).setOutput(
        (8, "purple_stained_glass_pane")).setGroup(abC)
    config.shaped_recipe(abU).setEntries(aad, agl).setEntries(aiC, agE).setOutput((8, abU)).setGroup(abF)
    config.shapeless_recipe(afL).addInput(agE, 1).addInput(agC, 1).setOutput(afL).setGroup(ajd)
    config.shaped_recipe("purpur_block").setEntries(aar, abw).setOutput((4, "purpur_block"))
    config.shaped_recipe(aet).setEntries(adA, aeY).setOutput(aet)
    config.shaped_recipe(aeY).setEntries(aaZ, aaq).setOutput((6, aeY))
    config.shaped_recipe("purpur_stairs").setEntries(aak, aaq).setOutput((4, "purpur_stairs"))
    config.smelting_recipe(aiw).add_ingredient(abV).setXp(ajt).setOutput(aiw)
    config.shaped_recipe(aeF).setEntries(aar, aiw).setOutput(aeF)
    config.smelting_recipe("quartz_from_blasting", abP).add_ingredient(abV).setXp(ajt).setOutput(aiw).setCookingTime(
        ajy)
    config.shaped_recipe("quartz_pillar").setEntries(adA, aeF).setOutput((2, "quartz_pillar"))
    config.shaped_recipe(afi).setEntries(aaZ, aaf).setOutput((6, afi))
    config.shaped_recipe("quartz_stairs").setEntries(aak, aaf).setOutput((4, "quartz_stairs"))
    config.shapeless_recipe("rabbit_stew_from_brown_mushroom").addInput(aeJ, 1).addInput(adN, 1).addInput("bowl",
                                                                                                          1).addInput(
        ais, 1).addInput("brown_mushroom", 1).setOutput(aff).setGroup(aff)
    config.shapeless_recipe("rabbit_stew_from_red_mushroom").addInput(aeJ, 1).addInput(adN, 1).addInput("bowl",
                                                                                                        1).addInput(ais,
                                                                                                                    1).addInput(
        "red_mushroom", 1).setOutput(aff).setGroup(aff)
    config.shaped_recipe("rail").setEntries(aiC, aiY).setEntries(aaj, agc).setOutput((16, "rail"))
    config.shapeless_recipe(ahj).addInput(adh, 1).setOutput((9, ahj))
    config.shaped_recipe(adh).setEntries(aac, ahj).setOutput(adh)
    config.smelting_recipe("redstone_from_blasting", abP).add_ingredient(aeU).setXp(ajv).setOutput(ahj).setCookingTime(
        ajy)
    config.smelting_recipe("redstone_from_smelting").add_ingredient(aeU).setXp(ajv).setOutput(ahj)
    config.shaped_recipe(aer).setEntries(aav, ahj).setEntries(aiC, agZ).setOutput(aer)
    config.shaped_recipe(adl).setEntries(ain, aiY).setEntries(aih, ahj).setOutput(adl)
    config.shaped_recipe(afZ).setEntries(aan, ahw).setEntries(aiH, aiY).setOutput(afZ).setGroup(aip)
    config.shaped_recipe(ahQ).setEntries(aaZ, ahw).setEntries(aaM, ahX).setOutput(ahQ).setGroup(ajp)
    config.shapeless_recipe("red_bed_from_white_bed").addInput(agP, 1).addInput(ahT, 1).setOutput(ahQ).setGroup(ahz)
    config.shaped_recipe("red_carpet").setEntries(adi, ahw).setOutput((3, "red_carpet")).setGroup(aim)
    config.shaped_recipe("red_carpet_from_white_carpet").setEntries(aad, aeW).setEntries(aiC, ahT).setOutput(
        (8, "red_carpet")).setGroup(aim)
    config.shapeless_recipe("red_concrete_powder").addInput(ahT, 1).addInput(ajf, 4).addInput(aio, 4).setOutput(
        (8, "red_concrete_powder")).setGroup(acO)
    config.shapeless_recipe("red_dye_from_beetroot").addInput("beetroot", 1).setOutput(ahT).setGroup(ahT)
    config.shapeless_recipe("red_dye_from_poppy").addInput("poppy", 1).setOutput(ahT).setGroup(ahT)
    config.shapeless_recipe("red_dye_from_rose_bush").addInput("rose_bush", 1).setOutput((2, ahT)).setGroup(ahT)
    config.shapeless_recipe("red_dye_from_tulip").addInput("red_tulip", 1).setOutput(ahT).setGroup(ahT)
    config.smelting_recipe(aba).add_ingredient(acZ).setXp(ajw).setOutput(aba)
    config.shaped_recipe(acd).setEntries(adq, afq).setEntries(adj, aeV).setOutput(acd)
    config.shaped_recipe("red_nether_brick_slab").setEntries(aaZ, acd).setOutput((6, "red_nether_brick_slab"))
    config.shaped_recipe("red_nether_brick_stairs").setEntries(aak, acd).setOutput((4, "red_nether_brick_stairs"))
    config.shaped_recipe("red_nether_brick_wall").setEntries(aan, acd).setOutput((6, "red_nether_brick_wall"))
    config.shaped_recipe(adY).setEntries(aar, "red_sand").setOutput(adY)
    config.shaped_recipe(abI).setEntries(aaZ, ['red_sandstone', 'chiseled_red_sandstone']).setOutput((6, abI))
    config.shaped_recipe("red_sandstone_stairs").setEntries(aak, ['red_sandstone', 'chiseled_red_sandstone',
                                                                  'cut_red_sandstone']).setOutput(
        (4, "red_sandstone_stairs"))
    config.shaped_recipe("red_sandstone_wall").setEntries(aan, adY).setOutput((6, "red_sandstone_wall"))
    config.shaped_recipe(aca).setEntries(aad, aiZ).setEntries(aiC, ahT).setOutput((8, aca)).setGroup(aed)
    config.shaped_recipe("red_stained_glass_pane").setEntries(aan, aca).setOutput(
        (16, "red_stained_glass_pane")).setGroup(abC)
    config.shaped_recipe("red_stained_glass_pane_from_glass_pane").setEntries(aad, agj).setEntries(aiC, ahT).setOutput(
        (8, "red_stained_glass_pane")).setGroup(abC)
    config.shaped_recipe(acZ).setEntries(aad, agl).setEntries(aiC, ahT).setOutput((8, acZ)).setGroup(abF)
    config.shapeless_recipe(ahw).addInput(ahT, 1).addInput(agC, 1).setOutput(ahw).setGroup(ajd)
    config.shaped_recipe(ahJ).setEntries(adv, adl).setEntries(aiB, ahj).setEntries(aaM, aiX).setOutput(ahJ)
    config.shaped_recipe(agG).setEntries(aar, ajf).setOutput(agG)
    config.shaped_recipe(adp).setEntries(aaZ, ['sandstone', 'chiseled_sandstone']).setOutput((6, adp))
    config.shaped_recipe("sandstone_stairs").setEntries(aak,
                                                        ['sandstone', 'chiseled_sandstone', 'cut_sandstone']).setOutput(
        (4, "sandstone_stairs"))
    config.shaped_recipe("sandstone_wall").setEntries(aan, agG).setOutput((6, "sandstone_wall"))
    config.shaped_recipe("scaffolding").setEntries(aiB, aig).setEntries(aaj, ail).setOutput((6, "scaffolding"))
    config.shaped_recipe(afB).setEntries([(0, 0), (0, 2), (2, 0), (2, 2)], acp).setEntries(
        [(0, 1), (1, 0), (1, 1), (1, 2), (2, 1)], "prismarine_crystals").setOutput(afB)
    config.shaped_recipe(aiD).setEntries(adq, agc).setOutput(aiD)
    config.shaped_recipe(aiy).setEntries([(0, 0), (0, 1), (1, 1), (1, 2), (2, 0), (2, 1)], ahX).setEntries(aiB,
                                                                                                           agc).setOutput(
        aiy)
    config.shaped_recipe(afM).setEntries(ain, aiO).setEntries([(0, 0), (0, 2)], "shulker_shell").setOutput(afM)
    config.shapeless_recipe(abr).addInput(aiU, 1).addInput("wither_skeleton_skull", 1).setOutput(abr)
    config.shapeless_recipe(ago).addInput(afp, 1).setOutput((9, ago))
    config.shaped_recipe(afp).setEntries(aac, ago).setOutput(afp)
    config.shaped_recipe(adf).setEntries(aau, ahX).setEntries(adi, agc).setOutput(adf)
    config.shaped_recipe(aii).setEntries(aav, aiS).setEntries(aiC, aie).setOutput(aii)
    config.smelting_recipe(aei).add_ingredient(aeF).setXp(ajw).setOutput(aei)
    config.shaped_recipe("smooth_quartz_slab").setEntries(aaZ, aei).setOutput((6, "smooth_quartz_slab"))
    config.shaped_recipe("smooth_quartz_stairs").setEntries(aak, aei).setOutput((4, "smooth_quartz_stairs"))
    config.smelting_recipe(abp).add_ingredient(adY).setXp(ajw).setOutput(abp)
    config.shaped_recipe("smooth_red_sandstone_slab").setEntries(aaZ, abp).setOutput((6, "smooth_red_sandstone_slab"))
    config.shaped_recipe("smooth_red_sandstone_stairs").setEntries(aak, abp).setOutput(
        (4, "smooth_red_sandstone_stairs"))
    config.smelting_recipe(act).add_ingredient(agG).setXp(ajw).setOutput(act)
    config.shaped_recipe("smooth_sandstone_slab").setEntries(aaZ, act).setOutput((6, "smooth_sandstone_slab"))
    config.shaped_recipe("smooth_sandstone_stairs").setEntries(aak, act).setOutput((4, "smooth_sandstone_stairs"))
    config.smelting_recipe(aeE).add_ingredient(aiX).setXp(ajw).setOutput(aeE)
    config.shaped_recipe(abW).setEntries(aaZ, aeE).setOutput((6, abW))
    config.shaped_recipe("snow").setEntries(aaZ, agx).setOutput((6, "snow"))
    config.shaped_recipe(agx).setEntries(aar, "snowball").setOutput(agx)
    config.shaped_recipe("spectral_arrow").setEntries(aav, adD).setEntries(aiC, aiP).setOutput((2, "spectral_arrow"))
    config.smelting_recipe(aiv).add_ingredient("wet_sponge").setXp(ajs).setOutput(aiv)
    config.shaped_recipe(afC).setEntries(aao, aeh).setOutput(afC).setGroup(ajk)
    config.shapeless_recipe(aej).addInput(aeh, 1).setOutput(aej).setGroup(aex)
    config.shaped_recipe("spruce_door").setEntries(aal, aeh).setOutput((3, "spruce_door")).setGroup(afk)
    config.shaped_recipe("spruce_fence").setEntries(ada, aiY).setEntries(aas, aeh).setOutput(
        (3, "spruce_fence")).setGroup(aeR)
    config.shaped_recipe(acb).setEntries(aas, aiY).setEntries(ada, aeh).setOutput(acb).setGroup(abT)
    config.shapeless_recipe(aeh).addInput("#spruce_logs", 1).setOutput((4, aeh)).setGroup(aiG)
    config.shaped_recipe(abk).setEntries(adi, aeh).setOutput(abk).setGroup(abi)
    config.shaped_recipe("spruce_sign").setEntries(aan, aeh).setEntries(aiH, aiY).setOutput((3, "spruce_sign"))
    config.shaped_recipe("spruce_slab").setEntries(aaZ, aeh).setOutput((6, "spruce_slab")).setGroup(afh)
    config.shaped_recipe("spruce_stairs").setEntries(aak, aeh).setOutput((4, "spruce_stairs")).setGroup(adP)
    config.shaped_recipe("spruce_trapdoor").setEntries(aan, aeh).setOutput((2, "spruce_trapdoor")).setGroup(acF)
    config.shaped_recipe("spruce_wood").setEntries(aar, "spruce_log").setOutput((3, "spruce_wood")).setGroup(aja)
    config.shaped_recipe(aiY).setEntries(adA, ahX).setOutput((4, aiY)).setGroup(aiA)
    config.shaped_recipe(aea).setEntries(ain, ait).setEntries(aih, ago).setOutput(aea)
    config.shaped_recipe("stick_from_bamboo_item").setEntries(adA, ail).setOutput(aiY).setGroup(aiA)
    config.smelting_recipe(aiX).add_ingredient(afO).setXp(ajw).setOutput(aiX)
    config.shaped_recipe(afQ).setEntries(aiB, agc).setEntries(aaM, aiX).setOutput(afQ)
    config.shaped_recipe(agM).setEntries(adt, aiY).setEntries(aaN, afO).setOutput(agM)
    config.shaped_recipe(aeP).setEntries(aar, aiX).setOutput((4, aeP))
    config.shaped_recipe(acw).setEntries(aaZ, aeP).setOutput((6, acw))
    config.shaped_recipe("stone_brick_stairs").setEntries(aak, aeP).setOutput((4, "stone_brick_stairs"))
    config.shaped_recipe("stone_brick_wall").setEntries(aan, aeP).setOutput((6, "stone_brick_wall"))
    config.shapeless_recipe(aeC).addInput(aiX, 1).setOutput(aeC)
    config.shaped_recipe(agL).setEntries(adt, aiY).setEntries(adi, afO).setOutput(agL)
    config.shaped_recipe(adO).setEntries(adt, aiY).setEntries(aaZ, afO).setOutput(adO)
    config.shaped_recipe(abt).setEntries(adi, aiX).setOutput(abt)
    config.shaped_recipe(aeQ).setEntries(adn, aiY).setEntries(aih, afO).setOutput(aeQ)
    config.shaped_recipe(agr).setEntries(aaZ, aiX).setOutput((6, agr))
    config.shaped_recipe("stone_stairs").setEntries(aak, aiX).setOutput((4, "stone_stairs"))
    config.shaped_recipe(afP).setEntries(aiE, aiY).setEntries(adA, afO).setOutput(afP)
    config.shaped_recipe("stripped_acacia_wood").setEntries(aar, "stripped_acacia_log").setOutput(
        (3, "stripped_acacia_wood")).setGroup(aja)
    config.shaped_recipe("stripped_birch_wood").setEntries(aar, "stripped_birch_log").setOutput(
        (3, "stripped_birch_wood")).setGroup(aja)
    config.shaped_recipe("stripped_dark_oak_wood").setEntries(aar, "stripped_dark_oak_log").setOutput(
        (3, "stripped_dark_oak_wood")).setGroup(aja)
    config.shaped_recipe("stripped_jungle_wood").setEntries(aar, "stripped_jungle_log").setOutput(
        (3, "stripped_jungle_wood")).setGroup(aja)
    config.shaped_recipe("stripped_oak_wood").setEntries(aar, "stripped_oak_log").setOutput(
        (3, "stripped_oak_wood")).setGroup(aja)
    config.shaped_recipe("stripped_spruce_wood").setEntries(aar, "stripped_spruce_log").setOutput(
        (3, "stripped_spruce_wood")).setGroup(aja)
    config.shapeless_recipe("sugar_from_honey_bottle").addInput(aeM, 1).setOutput((3, aiJ)).setGroup(aiJ)
    config.shapeless_recipe("sugar_from_sugar_cane").addInput(afW, 1).setOutput(aiJ).setGroup(aiJ)
    config.smelting_recipe(agl).add_ingredient(aji).setXp(ajr).setOutput(agl)
    config.shaped_recipe(ajn).setEntries(aav, ['sand', 'red_sand']).setEntries([(0, 0), (0, 2), (1, 1), (2, 0), (2, 2)],
                                                                               ahd).setOutput(ajn)
    config.shaped_recipe(aeS).setEntries(aih, ajn).setEntries(ain, ahr).setOutput(aeS)
    config.shaped_recipe(aiN).setEntries(ain, aiY).setEntries(aih, ['coal', 'charcoal']).setOutput((4, aiN))
    config.shapeless_recipe(aep).addInput(aiO, 1).addInput(aec, 1).setOutput(aep)
    config.shaped_recipe(aec).setEntries(aiE, ahX).setEntries(ain, aiY).setEntries(aih, agc).setOutput((2, aec))
    config.shaped_recipe(aeb).setEntries(aap, "scute").setOutput(aeb)
    config.shapeless_recipe(aiK).addInput(ahe, 1).setOutput((9, aiK))
    config.shaped_recipe(aeI).setEntries(aan, agC).setEntries(aiH, aiY).setOutput(aeI).setGroup(aip)
    config.shaped_recipe(agP).setEntries(aaZ, agC).setEntries(aaM, ahX).setOutput(agP).setGroup(ajp)
    config.shaped_recipe(aeW).setEntries(adi, agC).setOutput((3, aeW)).setGroup(aim)
    config.shapeless_recipe("white_concrete_powder").addInput(ahb, 1).addInput(ajf, 4).addInput(aio, 4).setOutput(
        (8, "white_concrete_powder")).setGroup(acO)
    config.shapeless_recipe(ahb).addInput(agS, 1).setOutput(ahb).setGroup(ahb)
    config.shapeless_recipe("white_dye_from_lily_of_the_valley").addInput("lily_of_the_valley", 1).setOutput(
        ahb).setGroup(ahb)
    config.smelting_recipe(aaI).add_ingredient(acy).setXp(ajw).setOutput(aaI)
    config.shaped_recipe(abA).setEntries(aad, aiZ).setEntries(aiC, ahb).setOutput((8, abA)).setGroup(aed)
    config.shaped_recipe("white_stained_glass_pane").setEntries(aan, abA).setOutput(
        (16, "white_stained_glass_pane")).setGroup(abC)
    config.shaped_recipe("white_stained_glass_pane_from_glass_pane").setEntries(aad, agj).setEntries(aiC,
                                                                                                     ahb).setOutput(
        (8, "white_stained_glass_pane")).setGroup(abC)
    config.shaped_recipe(acy).setEntries(aad, agl).setEntries(aiC, ahb).setOutput((8, acy)).setGroup(abF)
    config.shaped_recipe("white_wool_from_string").setEntries(aar, aig).setOutput(agC)
    config.shaped_recipe(afT).setEntries(adt, aiY).setEntries(aaN, ahX).setOutput(afT)
    config.shaped_recipe(afS).setEntries(adt, aiY).setEntries(adi, ahX).setOutput(afS)
    config.shaped_recipe(add).setEntries(adt, aiY).setEntries(aaZ, ahX).setOutput(add)
    config.shaped_recipe(adZ).setEntries(adn, aiY).setEntries(aih, ahX).setOutput(adZ)
    config.shaped_recipe(aeL).setEntries(aiE, aiY).setEntries(adA, ahX).setOutput(aeL)
    config.shapeless_recipe(adG).addInput(ajb, 1).addInput("ink_sac", 1).addInput(ahS, 1).setOutput(adG)
    config.shaped_recipe(adR).setEntries(aan, afH).setEntries(aiH, aiY).setOutput(adR).setGroup(aip)
    config.shaped_recipe(agf).setEntries(aaZ, afH).setEntries(aaM, ahX).setOutput(agf).setGroup(ajp)
    config.shapeless_recipe("yellow_bed_from_white_bed").addInput(agP, 1).addInput(agk, 1).setOutput(agf).setGroup(ahz)
    config.shaped_recipe("yellow_carpet").setEntries(adi, afH).setOutput((3, "yellow_carpet")).setGroup(aim)
    config.shaped_recipe("yellow_carpet_from_white_carpet").setEntries(aad, aeW).setEntries(aiC, agk).setOutput(
        (8, "yellow_carpet")).setGroup(aim)
    config.shapeless_recipe("yellow_concrete_powder").addInput(agk, 1).addInput(ajf, 4).addInput(aio, 4).setOutput(
        (8, "yellow_concrete_powder")).setGroup(acO)
    config.shapeless_recipe("yellow_dye_from_dandelion").addInput("dandelion", 1).setOutput(agk).setGroup(agk)
    config.shapeless_recipe("yellow_dye_from_sunflower").addInput("sunflower", 1).setOutput((2, agk)).setGroup(agk)
    config.smelting_recipe(aaF).add_ingredient(acg).setXp(ajw).setOutput(aaF)
    config.shaped_recipe(abu).setEntries(aad, aiZ).setEntries(aiC, agk).setOutput((8, abu)).setGroup(aed)
    config.shaped_recipe("yellow_stained_glass_pane").setEntries(aan, abu).setOutput(
        (16, "yellow_stained_glass_pane")).setGroup(abC)
    config.shaped_recipe("yellow_stained_glass_pane_from_glass_pane").setEntries(aad, agj).setEntries(aiC,
                                                                                                      agk).setOutput(
        (8, "yellow_stained_glass_pane")).setGroup(abC)
    config.shaped_recipe(acg).setEntries(aad, agl).setEntries(aiC, agk).setOutput((8, acg)).setGroup(abF)
    config.shapeless_recipe(afH).addInput(agk, 1).addInput(agC, 1).setOutput(afH).setGroup(ajd)
