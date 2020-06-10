"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
from . import Configuration
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
    aad = [(0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)]
    aae = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1), (2, 2)]
    aaf = ['chiseled_quartz_block', 'quartz_block', 'quartz_pillar']
    aag = [(0, 0), (0, 1), (0, 2), (1, 0), (2, 0), (2, 1), (2, 2)]
    aah = [(0, 0), (0, 1), (0, 2), (1, 2), (2, 0), (2, 1), (2, 2)]
    aai = [(0, 0), (0, 1), (0, 2), (1, 1), (2, 0), (2, 1), (2, 2)]
    aaj = [(0, 0), (0, 2), (1, 0), (1, 2), (2, 0), (2, 2)]
    aak = [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1)]
    aal = [(0, 0), (0, 1), (0, 2), (2, 0), (2, 1), (2, 2)]
    aam = [(0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2)]
    aan = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)]
    aao = [(0, 0), (0, 1), (1, 0), (2, 0), (2, 1)]
    aap = [(0, 0), (0, 1), (1, 1), (2, 0), (2, 1)]
    aaq = ['purpur_block', 'purpur_pillar']
    aar = [(0, 0), (0, 1), (1, 0), (1, 1)]
    aas = [(0, 0), (0, 1), (2, 0), (2, 1)]
    aat = [(0, 1), (0, 2), (1, 1), (1, 2)]
    aau = [(0, 1), (1, 0), (1, 2), (2, 1)]
    aav = [(0, 2), (1, 1), (1, 2), (2, 2)]
    aaw = "light_weighted_pressure_plate"
    aax = "light_blue_stained_glass_pane"
    aay = "heavy_weighted_pressure_plate"
    aaz = "light_gray_stained_glass_pane"
    aaA = "light_gray_glazed_terracotta"
    aaB = "light_blue_glazed_terracotta"
    aaC = "smooth_red_sandstone_stairs"
    aaD = "light_blue_concrete_powder"
    aaE = "magenta_stained_glass_pane"
    aaF = "light_gray_concrete_powder"
    aaG = "minecraft:campfire_cooking"
    aaH = "magenta_glazed_terracotta"
    aaI = "orange_stained_glass_pane"
    aaJ = "yellow_stained_glass_pane"
    aaK = "purple_stained_glass_pane"
    aaL = "smooth_red_sandstone_slab"
    aaM = "light_gray_stained_glass"
    aaN = "orange_glazed_terracotta"
    aaO = "brown_stained_glass_pane"
    aaP = "mossy_cobblestone_stairs"
    aaQ = "light_blue_stained_glass"
    aaR = "yellow_glazed_terracotta"
    aaS = "green_stained_glass_pane"
    aaT = "polished_andesite_stairs"
    aaU = "white_stained_glass_pane"
    aaV = "black_stained_glass_pane"
    aaW = "mossy_stone_brick_stairs"
    aaX = "purple_glazed_terracotta"
    aaY = "white_glazed_terracotta"
    aaZ = "lime_stained_glass_pane"
    aba = "magenta_concrete_powder"
    abb = "red_nether_brick_stairs"
    abc = "polished_diorite_stairs"
    abd = "black_glazed_terracotta"
    abe = "prismarine_brick_stairs"
    abf = "polished_granite_stairs"
    abg = "dark_oak_pressure_plate"
    abh = "cyan_stained_glass_pane"
    abi = "gray_stained_glass_pane"
    abj = "brown_glazed_terracotta"
    abk = "green_glazed_terracotta"
    abl = "pink_stained_glass_pane"
    abm = "smooth_sandstone_stairs"
    abn = "blue_stained_glass_pane"
    abo = [(0, 0), (1, 1), (2, 0)]
    abp = [(0, 2), (1, 2), (2, 2)]
    abq = "mossy_stone_brick_wall"
    abr = "stripped_dark_oak_wood"
    abs = "glistering_melon_slice"
    abt = "pink_glazed_terracotta"
    abu = "cut_red_sandstone_slab"
    abv = "mossy_cobblestone_slab"
    abw = "chiseled_red_sandstone"
    abx = "red_stained_glass_pane"
    aby = "polished_andesite_slab"
    abz = "cyan_glazed_terracotta"
    abA = [(0, 1), (1, 0), (2, 1)]
    abB = "mossy_cobblestone_wall"
    abC = "creeper_banner_pattern"
    abD = "yellow_concrete_powder"
    abE = "dark_prismarine_stairs"
    abF = [(0, 0), (1, 0), (2, 0)]
    abG = "gray_glazed_terracotta"
    abH = "orange_concrete_powder"
    abI = [(0, 1), (1, 1), (2, 1)]
    abJ = "blue_glazed_terracotta"
    abK = "mossy_stone_brick_slab"
    abL = "end_stone_brick_stairs"
    abM = "purple_concrete_powder"
    abN = [(0, 0), (0, 1), (1, 0)]
    abO = "lime_glazed_terracotta"
    abP = "polished_granite_slab"
    abQ = "chiseled_quartz_block"
    abR = "chiseled_stone_bricks"
    abS = "wooden_pressure_plate"
    abT = "red_nether_brick_wall"
    abU = "black_concrete_powder"
    abV = "flower_banner_pattern"
    abW = "red_glazed_terracotta"
    abX = "spruce_pressure_plate"
    abY = "light_gray_terracotta"
    abZ = "prismarine_brick_slab"
    aca = "green_concrete_powder"
    acb = "smooth_sandstone_slab"
    acc = "red_nether_brick_slab"
    acd = "jungle_pressure_plate"
    ace = "mojang_banner_pattern"
    acf = "magenta_stained_glass"
    acg = "light_blue_terracotta"
    ach = "polished_diorite_slab"
    aci = "white_concrete_powder"
    acj = "acacia_pressure_plate"
    ack = "brown_concrete_powder"
    acl = "end_stone_brick_wall"
    acm = "orange_stained_glass"
    acn = "pink_concrete_powder"
    aco = "cracked_stone_bricks"
    acp = "stripped_acacia_wood"
    acq = "blue_concrete_powder"
    acr = "end_stone_brick_slab"
    acs = "dark_prismarine_slab"
    act = "red_sandstone_stairs"
    acu = "gray_concrete_powder"
    acv = "smooth_quartz_stairs"
    acw = "fermented_spider_eye"
    acx = "stone_pressure_plate"
    acy = "birch_pressure_plate"
    acz = "stripped_spruce_wood"
    acA = "cyan_concrete_powder"
    acB = "yellow_stained_glass"
    acC = "skull_banner_pattern"
    acD = "purple_stained_glass"
    acE = "smooth_red_sandstone"
    acF = "stripped_jungle_wood"
    acG = "lime_concrete_powder"
    acH = "nether_brick_stairs"
    acI = "dark_oak_fence_gate"
    acJ = "popped_chorus_fruit"
    acK = "white_stained_glass"
    acL = "black_stained_glass"
    acM = "leather_horse_armor"
    acN = "stripped_birch_wood"
    acO = "brown_stained_glass"
    acP = "green_stained_glass"
    acQ = "red_concrete_powder"
    acR = "smooth_quartz_slab"
    acS = "minecraft:blasting"
    acT = "stained_terracotta"
    acU = "stone_brick_stairs"
    acV = "diamond_chestplate"
    acW = "magenta_terracotta"
    acX = "leather_chestplate"
    acY = "lime_stained_glass"
    acZ = "oak_pressure_plate"
    ada = "mossy_stone_bricks"
    adb = "cyan_stained_glass"
    adc = "gray_stained_glass"
    add = "pink_stained_glass"
    ade = "stained_glass_pane"
    adf = "red_sandstone_wall"
    adg = "cobblestone_stairs"
    adh = "red_sandstone_slab"
    adi = "blue_stained_glass"
    adj = "cut_sandstone_slab"
    adk = "nether_brick_fence"
    adl = "chiseled_sandstone"
    adm = "mossy_cobblestone"
    adn = "nether_brick_slab"
    ado = "prismarine_stairs"
    adp = "orange_terracotta"
    adq = "golden_chestplate"
    adr = "yellow_terracotta"
    ads = "nether_wart_block"
    adt = "red_stained_glass"
    adu = "cut_red_sandstone"
    adv = "dark_oak_trapdoor"
    adw = "prismarine_bricks"
    adx = "smooth_stone_slab"
    ady = "spruce_fence_gate"
    adz = "light_blue_banner"
    adA = "polished_andesite"
    adB = "minecraft:smoking"
    adC = "acacia_fence_gate"
    adD = "jungle_fence_gate"
    adE = "wooden_fence_gate"
    adF = "light_gray_carpet"
    adG = "nether_brick_wall"
    adH = "nether_quartz_ore"
    adI = "light_gray_banner"
    adJ = "cartography_table"
    adK = "stripped_oak_wood"
    adL = "light_blue_carpet"
    adM = "red_nether_bricks"
    adN = "daylight_detector"
    adO = "carrot_on_a_stick"
    adP = "purple_terracotta"
    adQ = "end_stone_bricks"
    adR = "leather_leggings"
    adS = "dried_kelp_block"
    adT = "green_terracotta"
    adU = "diamond_leggings"
    adV = "stone_brick_wall"
    adW = "white_terracotta"
    adX = "cobblestone_slab"
    adY = "stone_brick_slab"
    adZ = "polished_granite"
    aea = "enchanting_table"
    aeb = "smooth_sandstone"
    aec = "prismarine_shard"
    aed = "cobblestone_wall"
    aee = "black_terracotta"
    aef = "polished_diorite"
    aeg = "birch_fence_gate"
    aeh = "furnace_minecart"
    aei = "sandstone_stairs"
    aej = "brown_terracotta"
    aek = "pink_terracotta"
    ael = "cooked_porkchop"
    aem = "dark_oak_stairs"
    aen = "gray_terracotta"
    aeo = "dark_prismarine"
    aep = "dark_oak_planks"
    aeq = "acacia_trapdoor"
    aer = "wooden_trapdoor"
    aes = "dark_oak_button"
    aet = "andesite_stairs"
    aeu = "jungle_trapdoor"
    aev = "honeycomb_block"
    aew = "light_blue_wool"
    aex = "prismarine_wall"
    aey = "flint_and_steel"
    aez = "spruce_trapdoor"
    aeA = "hopper_minecart"
    aeB = "fletching_table"
    aeC = "iron_chestplate"
    aeD = "golden_leggings"
    aeE = "light_gray_wool"
    aeF = "prismarine_slab"
    aeG = "cyan_terracotta"
    aeH = "blue_terracotta"
    aeI = "diamond_pickaxe"
    aeJ = "concrete_powder"
    aeK = "lime_terracotta"
    aeL = "redstone_torch"
    aeM = "diamond_shovel"
    aeN = "golden_pickaxe"
    aeO = "magenta_banner"
    aeP = "chest_minecart"
    aeQ = [(1, 0), (1, 1)]
    aeR = "light_blue_dye"
    aeS = [(0, 1), (1, 0)]
    aeT = [(0, 0), (0, 1)]
    aeU = "granite_stairs"
    aeV = "activator_rail"
    aeW = [(1, 0), (1, 2)]
    aeX = "sandstone_slab"
    aeY = "light_gray_bed"
    aeZ = "diamond_helmet"
    afa = "light_blue_bed"
    afb = "spectral_arrow"
    afc = "sandstone_wall"
    afd = [(0, 0), (1, 0)]
    afe = [(0, 1), (2, 1)]
    aff = "diorite_stairs"
    afg = "leather_helmet"
    afh = "magenta_carpet"
    afi = "oak_fence_gate"
    afj = [(0, 0), (2, 0)]
    afk = "glowstone_dust"
    afl = "cooked_chicken"
    afm = [(0, 1), (0, 2)]
    afn = "birch_trapdoor"
    afo = [(0, 0), (1, 1)]
    afp = "dark_oak_fence"
    afq = "wooden_pickaxe"
    afr = "crafting_table"
    afs = "light_gray_dye"
    aft = "red_terracotta"
    afu = [(0, 1), (1, 1)]
    afv = "jack_o_lantern"
    afw = "smithing_table"
    afx = "redstone_block"
    afy = [(1, 1), (1, 2)]
    afz = "dark_oak_slab"
    afA = "trapped_chest"
    afB = "beetroot_soup"
    afC = "detector_rail"
    afD = "acacia_planks"
    afE = "tripwire_hook"
    afF = "brewing_stand"
    afG = "purple_banner"
    afH = "sticky_piston"
    afI = "dark_oak_sign"
    afJ = "orange_carpet"
    afK = "#wooden_slabs"
    afL = "wooden_shovel"
    afM = "jungle_planks"
    afN = "mushroom_stew"
    afO = "emerald_block"
    afP = "cooked_salmon"
    afQ = "diamond_block"
    afR = "dark_oak_boat"
    afS = "nether_bricks"
    afT = "quartz_stairs"
    afU = "dark_oak_wood"
    afV = "spruce_button"
    afW = "golden_carrot"
    afX = "wooden_stairs"
    afY = "cut_sandstone"
    afZ = "turtle_helmet"
    aga = "orange_banner"
    agb = "andesite_slab"
    agc = "cooked_mutton"
    agd = "pumpkin_seeds"
    age = "golden_shovel"
    agf = "iron_trapdoor"
    agg = "acacia_button"
    agh = "cooked_rabbit"
    agi = "yellow_carpet"
    agj = "purpur_stairs"
    agk = "smooth_quartz"
    agl = "jungle_button"
    agm = "jungle_stairs"
    agn = "redstone_lamp"
    ago = "wooden_button"
    agp = "diamond_boots"
    agq = "yellow_banner"
    agr = "purple_carpet"
    ags = "stained_glass"
    agt = "iron_leggings"
    agu = "spruce_planks"
    agv = "acacia_stairs"
    agw = "writable_book"
    agx = "quartz_pillar"
    agy = "blast_furnace"
    agz = "red_sandstone"
    agA = "dark_oak_door"
    agB = "diamond_sword"
    agC = "andesite_wall"
    agD = "golden_helmet"
    agE = "leather_boots"
    agF = "purpur_pillar"
    agG = "spruce_stairs"
    agH = "stone_pickaxe"
    agI = "baked_potato"
    agJ = "honey_bottle"
    agK = "purpur_block"
    agL = "diorite_wall"
    agM = "brick_stairs"
    agN = "diorite_slab"
    agO = "spruce_fence"
    agP = "black_carpet"
    agQ = "powered_rail"
    agR = "lapis_lazuli"
    agS = "iron_pickaxe"
    agT = "acacia_fence"
    agU = "stone_stairs"
    agV = "white_banner"
    agW = "birch_button"
    agX = "birch_stairs"
    agY = "white_carpet"
    agZ = "glass_bottle"
    aha = "granite_slab"
    ahb = "tnt_minecart"
    ahc = "nether_brick"
    ahd = "brown_carpet"
    ahe = "blaze_powder"
    ahf = "granite_wall"
    ahg = "black_banner"
    ahh = "brown_banner"
    ahi = "golden_sword"
    ahj = "quartz_block"
    ahk = "wooden_fence"
    ahl = "golden_apple"
    ahm = "stone_bricks"
    ahn = "stone_shovel"
    aho = "wooden_sword"
    ahp = "smooth_stone"
    ahq = "birch_planks"
    ahr = "redstone_ore"
    ahs = "jungle_fence"
    aht = "green_banner"
    ahu = "magenta_wool"
    ahv = "stone_button"
    ahw = "green_carpet"
    ahx = "golden_boots"
    ahy = "oak_trapdoor"
    ahz = "cooked_beef"
    ahA = "scaffolding"
    ahB = "cyan_carpet"
    ahC = "gray_banner"
    ahD = "sea_lantern"
    ahE = "pink_carpet"
    ahF = "acacia_slab"
    ahG = "iron_nugget"
    ahH = "acacia_boat"
    ahI = "magenta_bed"
    ahJ = "diamond_ore"
    ahK = "cobblestone"
    ahL = "rabbit_stew"
    ahM = "ender_chest"
    ahN = "lapis_block"
    ahO = "lime_banner"
    ahP = "iron_helmet"
    ahQ = "jungle_wood"
    ahR = "acacia_door"
    ahS = "spruce_slab"
    ahT = "jungle_slab"
    ahU = "spruce_door"
    ahV = "pumpkin_pie"
    ahW = "slime_block"
    ahX = "spruce_wood"
    ahY = "fishing_rod"
    ahZ = "blue_banner"
    aia = "gold_nugget"
    aib = "yellow_wool"
    aic = "iron_shovel"
    aid = "acacia_wood"
    aie = "wooden_door"
    aif = "honey_block"
    aig = "jungle_sign"
    aih = "diamond_hoe"
    aii = "quartz_slab"
    aij = "melon_seeds"
    aik = "end_crystal"
    ail = "diamond_axe"
    aim = "shulker_box"
    ain = "magma_block"
    aio = "jungle_door"
    aip = "wooden_slab"
    aiq = "cyan_banner"
    air = "purpur_slab"
    ais = "jungle_boat"
    ait = "magenta_dye"
    aiu = "birch_fence"
    aiv = "melon_slice"
    aiw = "gray_carpet"
    aix = "cocoa_beans"
    aiy = "fire_charge"
    aiz = "nether_wart"
    aiA = "stone_sword"
    aiB = "stonecutter"
    aiC = "acacia_sign"
    aiD = "spruce_sign"
    aiE = "spruce_boat"
    aiF = "coarse_dirt"
    aiG = "blue_carpet"
    aiH = "pink_banner"
    aiI = "emerald_ore"
    aiJ = "magma_cream"
    aiK = "armor_stand"
    aiL = "purple_wool"
    aiM = "lime_carpet"
    aiN = "orange_wool"
    aiO = "note_block"
    aiP = "purple_bed"
    aiQ = "golden_axe"
    aiR = "wooden_axe"
    aiS = "black_wool"
    aiT = "slime_ball"
    aiU = "gold_block"
    aiV = "white_wool"
    aiW = "brick_slab"
    aiX = "stone_slab"
    aiY = "snow_block"
    aiZ = "terracotta"
    aja = "yellow_bed"
    ajb = "brick_wall"
    ajc = "flower_pot"
    ajd = "birch_wood"
    aje = "bone_block"
    ajf = "sugar_cane"
    ajg = "iron_boots"
    ajh = "oak_planks"
    aji = "orange_bed"
    ajj = "birch_boat"
    ajk = "wooden_hoe"
    ajl = "dried_kelp"
    ajm = "iron_block"
    ajn = "birch_sign"
    ajo = "grindstone"
    ajp = "red_banner"
    ajq = "golden_hoe"
    ajr = "yellow_dye"
    ajs = "item_frame"
    ajt = "birch_door"
    aju = "birch_slab"
    ajv = "purple_dye"
    ajw = "iron_ingot"
    ajx = "oak_stairs"
    ajy = "glass_pane"
    ajz = "iron_sword"
    ajA = "gold_ingot"
    ajB = "oak_button"
    ajC = "cooked_cod"
    ajD = "brown_wool"
    ajE = "prismarine"
    ajF = "packed_ice"
    ajG = "coal_block"
    ajH = "orange_dye"
    ajI = "comparator"
    ajJ = "red_carpet"
    ajK = "green_wool"
    ajL = "gray_wool"
    ajM = "lapis_ore"
    ajN = "stone_axe"
    ajO = "iron_bars"
    ajP = "cyan_wool"
    ajQ = "blue_wool"
    ajR = "oak_fence"
    ajS = "white_bed"
    ajT = "brown_bed"
    ajU = "gunpowder"
    ajV = "blaze_rod"
    ajW = "black_bed"
    ajX = "black_dye"
    ajY = "bone_meal"
    ajZ = "ender_eye"
    aka = "white_dye"
    akb = "dispenser"
    akc = "stone_hoe"
    akd = "honeycomb"
    ake = "clay_ball"
    akf = "bookshelf"
    akg = "iron_door"
    akh = "glowstone"
    aki = "composter"
    akj = "brown_dye"
    akk = "sandstone"
    akl = "green_bed"
    akm = "hay_block"
    akn = "pink_wool"
    ako = "green_dye"
    akp = "lime_wool"
    akq = "oak_slab"
    akr = "blue_dye"
    aks = "bonemeal"
    akt = "iron_hoe"
    aku = "painting"
    akv = "iron_axe"
    akw = "campfire"
    akx = "minecart"
    aky = "cauldron"
    akz = "coal_ore"
    akA = "cyan_dye"
    akB = "gray_dye"
    akC = "pink_bed"
    akD = "gold_ore"
    akE = "obsidian"
    akF = "oak_boat"
    akG = "dyed_bed"
    akH = "porkchop"
    akI = "pink_dye"
    akJ = "oak_door"
    akK = "red_wool"
    akL = "blue_ice"
    akM = "charcoal"
    akN = "cyan_bed"
    akO = "crossbow"
    akP = "lime_bed"
    akQ = "redstone"
    akR = "lime_dye"
    akS = "oak_sign"
    akT = "andesite"
    akU = "gray_bed"
    akV = "oak_wood"
    akW = "iron_ore"
    akX = "observer"
    akY = "repeater"
    akZ = "blue_bed"
    ala = "compass"
    alb = "#planks"
    alc = "lantern"
    ald = "red_dye"
    ale = "beehive"
    alf = "dropper"
    alg = "granite"
    alh = "jukebox"
    ali = "end_rod"
    alj = "diamond"
    alk = "leather"
    all = "feather"
    alm = "diorite"
    aln = "emerald"
    alo = "chicken"
    alp = "red_bed"
    alq = "conduit"
    alr = "furnace"
    als = "lectern"
    alt = "salmon"
    alu = "carpet"
    alv = "beacon"
    alw = "ladder"
    alx = "banner"
    aly = [(1, 1)]
    alz = "planks"
    alA = "quartz"
    alB = "carrot"
    alC = "bricks"
    alD = "piston"
    alE = "barrel"
    alF = "potato"
    alG = [(0, 0)]
    alH = "sticks"
    alI = "smoker"
    alJ = [(0, 1)]
    alK = "hopper"
    alL = [(1, 0)]
    alM = "rabbit"
    alN = "gravel"
    alO = "cookie"
    alP = [(1, 2)]
    alQ = "mutton"
    alR = "string"
    alS = "shears"
    alT = "bucket"
    alU = "sponge"
    alV = "shield"
    alW = [(0, 2)]
    alX = "bamboo"
    alY = "paper"
    alZ = "wheat"
    ama = "torch"
    amb = "melon"
    amc = "stick"
    amd = "lever"
    ame = "#logs"
    amf = "brick"
    amg = "flint"
    amh = "anvil"
    ami = "stone"
    amj = "chest"
    amk = "sugar"
    aml = "arrow"
    amm = "bread"
    amn = "clock"
    amo = "glass"
    amp = "snow"
    amq = "bowl"
    amr = "boat"
    ams = "book"
    amt = "kelp"
    amu = "rail"
    amv = "beef"
    amw = "sand"
    amx = "cake"
    amy = "wool"
    amz = "coal"
    amA = "loom"
    amB = "bark"
    amC = "lead"
    amD = "clay"
    amE = "bow"
    amF = "cod"
    amG = "map"
    amH = "tnt"
    amI = "egg"
    amJ = "bed"
    amK = 0.15
    amL = 0.35
    amM = 0.7
    amN = 100
    amO = 0.2
    amP = 0.1
    amQ = 1.0
    amR = 600
    config.shaped_recipe(ahH).setEntries(aap, afD).setOutput(ahH).setGroup(amr)
    config.shapeless_recipe(agg).addInput(afD, 1).setOutput(agg).setGroup(ago)
    config.shaped_recipe(ahR).setEntries(aan, afD).setOutput(ahR).setGroup(aie)
    config.shaped_recipe(agT).setEntries(aeQ, amc).setEntries(aas, afD).setOutput(agT).setGroup(ahk)
    config.shaped_recipe(adC).setEntries(aas, amc).setEntries(aeQ, afD).setOutput(adC).setGroup(adE)
    config.shapeless_recipe(afD).addInput("#acacia_logs", 1).setOutput(afD).setGroup(alz)
    config.shaped_recipe(acj).setEntries(afd, afD).setOutput(acj).setGroup(abS)
    config.shaped_recipe(aiC).setEntries(aak, afD).setEntries(alP, amc).setOutput(aiC)
    config.shaped_recipe(ahF).setEntries(abF, afD).setOutput(ahF).setGroup(aip)
    config.shaped_recipe(agv).setEntries(aam, afD).setOutput(agv).setGroup(afX)
    config.shaped_recipe(aeq).setEntries(aak, afD).setOutput(aeq).setGroup(aer)
    config.shaped_recipe(aid).setEntries(aar, "acacia_log").setOutput(aid).setGroup(amB)
    config.shaped_recipe(aeV).setEntries(aly, aeL).setEntries(aeW, amc).setEntries(aal, ajw).setOutput(aeV)
    config.shapeless_recipe(akT).addInput(alm, 1).addInput(ahK, 1).setOutput(akT)
    config.shaped_recipe(agb).setEntries(abF, akT).setOutput(agb)
    config.shaped_recipe(aet).setEntries(aam, akT).setOutput(aet)
    config.shaped_recipe(agC).setEntries(aak, akT).setOutput(agC)
    config.shaped_recipe(amh).setEntries(abF, ajm).setEntries(aav, ajw).setOutput(amh)
    config.shaped_recipe(aiK).setEntries([(0, 0), (0, 2), (1, 0), (1, 1), (2, 0), (2, 2)], amc).setEntries(alP,
                                                                                                           adx).setOutput(
        aiK)
    config.shaped_recipe(aml).setEntries(alJ, amc).setEntries(alG, amg).setEntries(alW, all).setOutput(aml)
    config.smelting_recipe(agI).add_ingredient(alF).setXp(amL).setOutput(agI)
    config.smelting_recipe("baked_potato_from_campfire_cooking", aaG).add_ingredient(alF).setXp(amL).setOutput(
        agI).setCookingTime(amR)
    config.smelting_recipe("baked_potato_from_smoking", adB).add_ingredient(alF).setXp(amL).setOutput(
        agI).setCookingTime(amN)
    config.shaped_recipe(alE).setEntries(aal, alb).setEntries(aeW, afK).setOutput(alE)
    config.shaped_recipe(alv).setEntries(aly, "nether_star").setEntries(aao, amo).setEntries(abp, akE).setOutput(alv)
    config.shaped_recipe(ale).setEntries(aaj, alb).setEntries(abI, akd).setOutput(ale)
    config.shapeless_recipe(afB).addInput(amq, 1).addInput("beetroot", 6).setOutput(afB)
    config.shaped_recipe(ajj).setEntries(aap, ahq).setOutput(ajj).setGroup(amr)
    config.shapeless_recipe(agW).addInput(ahq, 1).setOutput(agW).setGroup(ago)
    config.shaped_recipe(ajt).setEntries(aan, ahq).setOutput(ajt).setGroup(aie)
    config.shaped_recipe(aiu).setEntries(aeQ, amc).setEntries(aas, ahq).setOutput(aiu).setGroup(ahk)
    config.shaped_recipe(aeg).setEntries(aas, amc).setEntries(aeQ, ahq).setOutput(aeg).setGroup(adE)
    config.shapeless_recipe(ahq).addInput("#birch_logs", 1).setOutput(ahq).setGroup(alz)
    config.shaped_recipe(acy).setEntries(afd, ahq).setOutput(acy).setGroup(abS)
    config.shaped_recipe(ajn).setEntries(aak, ahq).setEntries(alP, amc).setOutput(ajn)
    config.shaped_recipe(aju).setEntries(abF, ahq).setOutput(aju).setGroup(aip)
    config.shaped_recipe(agX).setEntries(aam, ahq).setOutput(agX).setGroup(afX)
    config.shaped_recipe(afn).setEntries(aak, ahq).setOutput(afn).setGroup(aer)
    config.shaped_recipe(ajd).setEntries(aar, "birch_log").setOutput(ajd).setGroup(amB)
    config.shaped_recipe(ahg).setEntries(aak, aiS).setEntries(alP, amc).setOutput(ahg).setGroup(alx)
    config.shaped_recipe(ajW).setEntries(abF, aiS).setEntries(abI, alb).setOutput(ajW).setGroup(amJ)
    config.shapeless_recipe("black_bed_from_white_bed").addInput(ajS, 1).addInput(ajX, 1).setOutput(ajW).setGroup(akG)
    config.shaped_recipe(agP).setEntries(afd, aiS).setOutput(agP).setGroup(alu)
    config.shaped_recipe("black_carpet_from_white_carpet").setEntries(aae, agY).setEntries(aly, ajX).setOutput(
        agP).setGroup(alu)
    config.shapeless_recipe(abU).addInput(ajX, 1).addInput(amw, 4).addInput(alN, 4).setOutput(abU).setGroup(aeJ)
    config.shapeless_recipe(ajX).addInput("ink_sac", 1).setOutput(ajX).setGroup(ajX)
    config.shapeless_recipe("black_dye_from_wither_rose").addInput("wither_rose", 1).setOutput(ajX).setGroup(ajX)
    config.smelting_recipe(abd).add_ingredient(aee).setXp(amP).setOutput(abd)
    config.shaped_recipe(acL).setEntries(aae, amo).setEntries(aly, ajX).setOutput(acL).setGroup(ags)
    config.shaped_recipe(aaV).setEntries(aak, acL).setOutput(aaV).setGroup(ade)
    config.shaped_recipe("black_stained_glass_pane_from_glass_pane").setEntries(aae, ajy).setEntries(aly,
                                                                                                     ajX).setOutput(
        aaV).setGroup(ade)
    config.shaped_recipe(aee).setEntries(aae, aiZ).setEntries(aly, ajX).setOutput(aee).setGroup(acT)
    config.shapeless_recipe(aiS).addInput(ajX, 1).addInput(aiV, 1).setOutput(aiS).setGroup(amy)
    config.shaped_recipe(agy).setEntries(abp, ahp).setEntries(aly, alr).setEntries(aao, ajw).setOutput(agy)
    config.shapeless_recipe(ahe).addInput(ajV, 1).setOutput(ahe)
    config.shaped_recipe(ahZ).setEntries(aak, ajQ).setEntries(alP, amc).setOutput(ahZ).setGroup(alx)
    config.shaped_recipe(akZ).setEntries(abF, ajQ).setEntries(abI, alb).setOutput(akZ).setGroup(amJ)
    config.shapeless_recipe("blue_bed_from_white_bed").addInput(ajS, 1).addInput(akr, 1).setOutput(akZ).setGroup(akG)
    config.shaped_recipe(aiG).setEntries(afd, ajQ).setOutput(aiG).setGroup(alu)
    config.shaped_recipe("blue_carpet_from_white_carpet").setEntries(aae, agY).setEntries(aly, akr).setOutput(
        aiG).setGroup(alu)
    config.shapeless_recipe(acq).addInput(akr, 1).addInput(amw, 4).addInput(alN, 4).setOutput(acq).setGroup(aeJ)
    config.shapeless_recipe(akr).addInput(agR, 1).setOutput(akr).setGroup(akr)
    config.shapeless_recipe("blue_dye_from_cornflower").addInput("cornflower", 1).setOutput(akr).setGroup(akr)
    config.smelting_recipe(abJ).add_ingredient(aeH).setXp(amP).setOutput(abJ)
    config.shaped_recipe(akL).setEntries(aac, ajF).setOutput(akL)
    config.shaped_recipe(adi).setEntries(aae, amo).setEntries(aly, akr).setOutput(adi).setGroup(ags)
    config.shaped_recipe(abn).setEntries(aak, adi).setOutput(abn).setGroup(ade)
    config.shaped_recipe("blue_stained_glass_pane_from_glass_pane").setEntries(aae, ajy).setEntries(aly, akr).setOutput(
        abn).setGroup(ade)
    config.shaped_recipe(aeH).setEntries(aae, aiZ).setEntries(aly, akr).setOutput(aeH).setGroup(acT)
    config.shapeless_recipe(ajQ).addInput(akr, 1).addInput(aiV, 1).setOutput(ajQ).setGroup(amy)
    config.shaped_recipe(aje).setEntries(aac, ajY).setOutput(aje)
    config.shapeless_recipe(ajY).addInput("bone", 1).setOutput(ajY).setGroup(aks)
    config.shapeless_recipe("bone_meal_from_bone_block").addInput(aje, 1).setOutput(ajY).setGroup(aks)
    config.shapeless_recipe(ams).addInput(alY, 3).addInput(alk, 1).setOutput(ams)
    config.shaped_recipe(akf).setEntries(aaj, alb).setEntries(abI, ams).setOutput(akf)
    config.shaped_recipe(amE).setEntries([(0, 1), (1, 0), (1, 2)], amc).setEntries([(2, 0), (2, 1), (2, 2)],
                                                                                   alR).setOutput(amE)
    config.shaped_recipe(amq).setEntries(abo, alb).setOutput(amq)
    config.shaped_recipe(amm).setEntries(abF, alZ).setOutput(amm)
    config.shaped_recipe(afF).setEntries(alL, ajV).setEntries(abI, ahK).setOutput(afF)
    config.smelting_recipe(amf).add_ingredient(ake).setXp(0.3).setOutput(amf)
    config.shaped_recipe(alC).setEntries(aar, amf).setOutput(alC)
    config.shaped_recipe(aiW).setEntries(abF, alC).setOutput(aiW)
    config.shaped_recipe(agM).setEntries(aam, alC).setOutput(agM)
    config.shaped_recipe(ajb).setEntries(aak, alC).setOutput(ajb)
    config.shaped_recipe(ahh).setEntries(aak, ajD).setEntries(alP, amc).setOutput(ahh).setGroup(alx)
    config.shaped_recipe(ajT).setEntries(abF, ajD).setEntries(abI, alb).setOutput(ajT).setGroup(amJ)
    config.shapeless_recipe("brown_bed_from_white_bed").addInput(ajS, 1).addInput(akj, 1).setOutput(ajT).setGroup(akG)
    config.shaped_recipe(ahd).setEntries(afd, ajD).setOutput(ahd).setGroup(alu)
    config.shaped_recipe("brown_carpet_from_white_carpet").setEntries(aae, agY).setEntries(aly, akj).setOutput(
        ahd).setGroup(alu)
    config.shapeless_recipe(ack).addInput(akj, 1).addInput(amw, 4).addInput(alN, 4).setOutput(ack).setGroup(aeJ)
    config.shapeless_recipe(akj).addInput(aix, 1).setOutput(akj).setGroup(akj)
    config.smelting_recipe(abj).add_ingredient(aej).setXp(amP).setOutput(abj)
    config.shaped_recipe(acO).setEntries(aae, amo).setEntries(aly, akj).setOutput(acO).setGroup(ags)
    config.shaped_recipe(aaO).setEntries(aak, acO).setOutput(aaO).setGroup(ade)
    config.shaped_recipe("brown_stained_glass_pane_from_glass_pane").setEntries(aae, ajy).setEntries(aly,
                                                                                                     akj).setOutput(
        aaO).setGroup(ade)
    config.shaped_recipe(aej).setEntries(aae, aiZ).setEntries(aly, akj).setOutput(aej).setGroup(acT)
    config.shapeless_recipe(ajD).addInput(akj, 1).addInput(aiV, 1).setOutput(ajD).setGroup(amy)
    config.shaped_recipe(alT).setEntries(abo, ajw).setOutput(alT)
    config.shaped_recipe(amx).setEntries(abF, "milk_bucket").setEntries(afe, amk).setEntries(abp, alZ).setEntries(aly,
                                                                                                                  amI).setOutput(
        amx)
    config.shaped_recipe(akw).setEntries(abp, ame).setEntries(abA, amc).setEntries(aly, "#coals").setOutput(akw)
    config.shaped_recipe(adO).setEntries(alG, ahY).setEntries(aly, alB).setOutput(adO)
    config.shaped_recipe(adJ).setEntries(aat, alb).setEntries(afd, alY).setOutput(adJ)
    config.shaped_recipe(aky).setEntries(aah, ajw).setOutput(aky)
    config.smelting_recipe(akM).add_ingredient(ame).setXp(amK).setOutput(akM)
    config.shaped_recipe(amj).setEntries(aae, alb).setOutput(amj)
    config.shaped_recipe(aeP).setEntries(alG, amj).setEntries(alJ, akx).setOutput(aeP)
    config.shaped_recipe(abQ).setEntries(aeT, aii).setOutput(abQ)
    config.shaped_recipe(abw).setEntries(aeT, adh).setOutput(abw)
    config.shaped_recipe(adl).setEntries(aeT, aeX).setOutput(adl)
    config.shaped_recipe(abR).setEntries(aeT, adY).setOutput(abR)
    config.shaped_recipe(amD).setEntries(aar, ake).setOutput(amD)
    config.shaped_recipe(amn).setEntries(aau, ajA).setEntries(aly, akQ).setOutput(amn)
    config.shapeless_recipe(amz).addInput(ajG, 1).setOutput(amz)
    config.shaped_recipe(ajG).setEntries(aac, amz).setOutput(ajG)
    config.smelting_recipe("coal_from_blasting", acS).add_ingredient(akz).setXp(amP).setOutput(amz).setCookingTime(amN)
    config.smelting_recipe("coal_from_smelting").add_ingredient(akz).setXp(amP).setOutput(amz)
    config.shaped_recipe(aiF).setEntries(afo, "dirt").setEntries(aeS, alN).setOutput(aiF)
    config.shaped_recipe(adX).setEntries(abF, ahK).setOutput(adX)
    config.shaped_recipe(adg).setEntries(aam, ahK).setOutput(adg)
    config.shaped_recipe(aed).setEntries(aak, ahK).setOutput(aed)
    config.shaped_recipe(ajI).setEntries(abA, aeL).setEntries(aly, alA).setEntries(abp, ami).setOutput(ajI)
    config.shaped_recipe(ala).setEntries(aau, ajw).setEntries(aly, akQ).setOutput(ala)
    config.shaped_recipe(aki).setEntries(aah, afK).setOutput(aki)
    config.shaped_recipe(alq).setEntries(aae, "nautilus_shell").setEntries(aly, "heart_of_the_sea").setOutput(alq)
    config.smelting_recipe(ahz).add_ingredient(amv).setXp(amL).setOutput(ahz)
    config.smelting_recipe("cooked_beef_from_campfire_cooking", aaG).add_ingredient(amv).setXp(amL).setOutput(
        ahz).setCookingTime(amR)
    config.smelting_recipe("cooked_beef_from_smoking", adB).add_ingredient(amv).setXp(amL).setOutput(
        ahz).setCookingTime(amN)
    config.smelting_recipe(afl).add_ingredient(alo).setXp(amL).setOutput(afl)
    config.smelting_recipe("cooked_chicken_from_campfire_cooking", aaG).add_ingredient(alo).setXp(amL).setOutput(
        afl).setCookingTime(amR)
    config.smelting_recipe("cooked_chicken_from_smoking", adB).add_ingredient(alo).setXp(amL).setOutput(
        afl).setCookingTime(amN)
    config.smelting_recipe(ajC).add_ingredient(amF).setXp(amL).setOutput(ajC)
    config.smelting_recipe("cooked_cod_from_campfire_cooking", aaG).add_ingredient(amF).setXp(amL).setOutput(
        ajC).setCookingTime(amR)
    config.smelting_recipe("cooked_cod_from_smoking", adB).add_ingredient(amF).setXp(amL).setOutput(ajC).setCookingTime(
        amN)
    config.smelting_recipe(agc).add_ingredient(alQ).setXp(amL).setOutput(agc)
    config.smelting_recipe("cooked_mutton_from_campfire_cooking", aaG).add_ingredient(alQ).setXp(amL).setOutput(
        agc).setCookingTime(amR)
    config.smelting_recipe("cooked_mutton_from_smoking", adB).add_ingredient(alQ).setXp(amL).setOutput(
        agc).setCookingTime(amN)
    config.smelting_recipe(ael).add_ingredient(akH).setXp(amL).setOutput(ael)
    config.smelting_recipe("cooked_porkchop_from_campfire_cooking", aaG).add_ingredient(akH).setXp(amL).setOutput(
        ael).setCookingTime(amR)
    config.smelting_recipe("cooked_porkchop_from_smoking", adB).add_ingredient(akH).setXp(amL).setOutput(
        ael).setCookingTime(amN)
    config.smelting_recipe(agh).add_ingredient(alM).setXp(amL).setOutput(agh)
    config.smelting_recipe("cooked_rabbit_from_campfire_cooking", aaG).add_ingredient(alM).setXp(amL).setOutput(
        agh).setCookingTime(amR)
    config.smelting_recipe("cooked_rabbit_from_smoking", adB).add_ingredient(alM).setXp(amL).setOutput(
        agh).setCookingTime(amN)
    config.smelting_recipe(afP).add_ingredient(alt).setXp(amL).setOutput(afP)
    config.smelting_recipe("cooked_salmon_from_campfire_cooking", aaG).add_ingredient(alt).setXp(amL).setOutput(
        afP).setCookingTime(amR)
    config.smelting_recipe("cooked_salmon_from_smoking", adB).add_ingredient(alt).setXp(amL).setOutput(
        afP).setCookingTime(amN)
    config.shaped_recipe(alO).setEntries(afj, alZ).setEntries(alL, aix).setOutput(alO)
    config.smelting_recipe(aco).add_ingredient(ahm).setXp(amP).setOutput(aco)
    config.shaped_recipe(afr).setEntries(aar, alb).setOutput(afr)
    config.shapeless_recipe(abC).addInput(alY, 1).addInput("creeper_head", 1).setOutput(abC)
    config.shaped_recipe(akO).setEntries(afe, alR).setEntries([(0, 0), (1, 2), (2, 0)], amc).setEntries(alL,
                                                                                                        ajw).setEntries(
        aly, afE).setOutput(akO)
    config.shaped_recipe(adu).setEntries(aar, agz).setOutput(adu)
    config.shaped_recipe(abu).setEntries(abF, adu).setOutput(abu)
    config.shaped_recipe(afY).setEntries(aar, akk).setOutput(afY)
    config.shaped_recipe(adj).setEntries(abF, afY).setOutput(adj)
    config.shaped_recipe(aiq).setEntries(aak, ajP).setEntries(alP, amc).setOutput(aiq).setGroup(alx)
    config.shaped_recipe(akN).setEntries(abF, ajP).setEntries(abI, alb).setOutput(akN).setGroup(amJ)
    config.shapeless_recipe("cyan_bed_from_white_bed").addInput(ajS, 1).addInput(akA, 1).setOutput(akN).setGroup(akG)
    config.shaped_recipe(ahB).setEntries(afd, ajP).setOutput(ahB).setGroup(alu)
    config.shaped_recipe("cyan_carpet_from_white_carpet").setEntries(aae, agY).setEntries(aly, akA).setOutput(
        ahB).setGroup(alu)
    config.shapeless_recipe(acA).addInput(akA, 1).addInput(amw, 4).addInput(alN, 4).setOutput(acA).setGroup(aeJ)
    config.shapeless_recipe(akA).addInput(akr, 1).addInput(ako, 1).setOutput(akA)
    config.smelting_recipe(abz).add_ingredient(aeG).setXp(amP).setOutput(abz)
    config.shaped_recipe(adb).setEntries(aae, amo).setEntries(aly, akA).setOutput(adb).setGroup(ags)
    config.shaped_recipe(abh).setEntries(aak, adb).setOutput(abh).setGroup(ade)
    config.shaped_recipe("cyan_stained_glass_pane_from_glass_pane").setEntries(aae, ajy).setEntries(aly, akA).setOutput(
        abh).setGroup(ade)
    config.shaped_recipe(aeG).setEntries(aae, aiZ).setEntries(aly, akA).setOutput(aeG).setGroup(acT)
    config.shapeless_recipe(ajP).addInput(akA, 1).addInput(aiV, 1).setOutput(ajP).setGroup(amy)
    config.shaped_recipe(afR).setEntries(aap, aep).setOutput(afR).setGroup(amr)
    config.shapeless_recipe(aes).addInput(aep, 1).setOutput(aes).setGroup(ago)
    config.shaped_recipe(agA).setEntries(aan, aep).setOutput(agA).setGroup(aie)
    config.shaped_recipe(afp).setEntries(aeQ, amc).setEntries(aas, aep).setOutput(afp).setGroup(ahk)
    config.shaped_recipe(acI).setEntries(aas, amc).setEntries(aeQ, aep).setOutput(acI).setGroup(adE)
    config.shapeless_recipe(aep).addInput("#dark_oak_logs", 1).setOutput(aep).setGroup(alz)
    config.shaped_recipe(abg).setEntries(afd, aep).setOutput(abg).setGroup(abS)
    config.shaped_recipe(afI).setEntries(aak, aep).setEntries(alP, amc).setOutput(afI)
    config.shaped_recipe(afz).setEntries(abF, aep).setOutput(afz).setGroup(aip)
    config.shaped_recipe(aem).setEntries(aam, aep).setOutput(aem).setGroup(afX)
    config.shaped_recipe(adv).setEntries(aak, aep).setOutput(adv).setGroup(aer)
    config.shaped_recipe(afU).setEntries(aar, "dark_oak_log").setOutput(afU).setGroup(amB)
    config.shaped_recipe(aeo).setEntries(aae, aec).setEntries(aly, ajX).setOutput(aeo)
    config.shaped_recipe(acs).setEntries(abF, aeo).setOutput(acs)
    config.shaped_recipe(abE).setEntries(aam, aeo).setOutput(abE)
    config.shaped_recipe(adN).setEntries(abI, alA).setEntries(abF, amo).setEntries(abp, afK).setOutput(adN)
    config.shaped_recipe(afC).setEntries(alP, akQ).setEntries(aly, acx).setEntries(aal, ajw).setOutput(afC)
    config.shapeless_recipe(alj).addInput(afQ, 1).setOutput(alj)
    config.shaped_recipe(ail).setEntries(afy, amc).setEntries(abN, alj).setOutput(ail)
    config.shaped_recipe(afQ).setEntries(aac, alj).setOutput(afQ)
    config.shaped_recipe(agp).setEntries(aas, alj).setOutput(agp)
    config.shaped_recipe(acV).setEntries(aad, alj).setOutput(acV)
    config.smelting_recipe("diamond_from_blasting", acS).add_ingredient(ahJ).setXp(amQ).setOutput(alj).setCookingTime(
        amN)
    config.smelting_recipe("diamond_from_smelting").add_ingredient(ahJ).setXp(amQ).setOutput(alj)
    config.shaped_recipe(aeZ).setEntries(aao, alj).setOutput(aeZ)
    config.shaped_recipe(aih).setEntries(afy, amc).setEntries(afd, alj).setOutput(aih)
    config.shaped_recipe(adU).setEntries(aag, alj).setOutput(adU)
    config.shaped_recipe(aeI).setEntries(afy, amc).setEntries(abF, alj).setOutput(aeI)
    config.shaped_recipe(aeM).setEntries(afm, amc).setEntries(alG, alj).setOutput(aeM)
    config.shaped_recipe(agB).setEntries(alW, amc).setEntries(aeT, alj).setOutput(agB)
    config.shaped_recipe(alm).setEntries(aeS, alA).setEntries(afo, ahK).setOutput(alm)
    config.shaped_recipe(agN).setEntries(abF, alm).setOutput(agN)
    config.shaped_recipe(aff).setEntries(aam, alm).setOutput(aff)
    config.shaped_recipe(agL).setEntries(aak, alm).setOutput(agL)
    config.shaped_recipe(akb).setEntries(alP, akQ).setEntries(aag, ahK).setEntries(aly, amE).setOutput(akb)
    config.shapeless_recipe(ajl).addInput(adS, 1).setOutput(ajl)
    config.shapeless_recipe(adS).addInput(ajl, 9).setOutput(adS)
    config.smelting_recipe("dried_kelp_from_campfire_cooking", aaG).add_ingredient(amt).setXp(amP).setOutput(
        ajl).setCookingTime(amR)
    config.smelting_recipe("dried_kelp_from_smelting").add_ingredient(amt).setXp(amP).setOutput(ajl)
    config.smelting_recipe("dried_kelp_from_smoking", adB).add_ingredient(amt).setXp(amP).setOutput(ajl).setCookingTime(
        amN)
    config.shaped_recipe(alf).setEntries(alP, akQ).setEntries(aag, ahK).setOutput(alf)
    config.shapeless_recipe(aln).addInput(afO, 1).setOutput(aln)
    config.shaped_recipe(afO).setEntries(aac, aln).setOutput(afO)
    config.smelting_recipe("emerald_from_blasting", acS).add_ingredient(aiI).setXp(amQ).setOutput(aln).setCookingTime(
        amN)
    config.smelting_recipe("emerald_from_smelting").add_ingredient(aiI).setXp(amQ).setOutput(aln)
    config.shaped_recipe(aea).setEntries(alL, ams).setEntries(aav, akE).setEntries(afe, alj).setOutput(aea)
    config.shaped_recipe(ahM).setEntries(aae, akE).setEntries(aly, ajZ).setOutput(ahM)
    config.shapeless_recipe(ajZ).addInput("ender_pearl", 1).addInput(ahe, 1).setOutput(ajZ)
    config.shaped_recipe(aik).setEntries(alP, "ghast_tear").setEntries(aly, ajZ).setEntries(aag, amo).setOutput(aik)
    config.shaped_recipe(ali).setEntries(alJ, acJ).setEntries(alG, ajV).setOutput(ali)
    config.shaped_recipe(adQ).setEntries(aar, "end_stone").setOutput(adQ)
    config.shaped_recipe(acr).setEntries(abF, adQ).setOutput(acr)
    config.shaped_recipe(abL).setEntries(aam, adQ).setOutput(abL)
    config.shaped_recipe(acl).setEntries(aak, adQ).setOutput(acl)
    config.shapeless_recipe(acw).addInput("spider_eye", 1).addInput("brown_mushroom", 1).addInput(amk, 1).setOutput(acw)
    config.shapeless_recipe(aiy).addInput(ajU, 1).addInput(ahe, 1).setOutput(aiy)
    config.shaped_recipe(ahY).setEntries([(0, 2), (1, 1), (2, 0)], amc).setEntries([(2, 1), (2, 2)], alR).setOutput(ahY)
    config.shaped_recipe(aeB).setEntries(aat, alb).setEntries(afd, amg).setOutput(aeB)
    config.shapeless_recipe(aey).addInput(ajw, 1).addInput(amg, 1).setOutput(aey)
    config.shapeless_recipe(abV).addInput(alY, 1).addInput("oxeye_daisy", 1).setOutput(abV)
    config.shaped_recipe(ajc).setEntries(abo, amf).setOutput(ajc)
    config.shaped_recipe(alr).setEntries(aae, ahK).setOutput(alr)
    config.shaped_recipe(aeh).setEntries(alG, alr).setEntries(alJ, akx).setOutput(aeh)
    config.smelting_recipe(amo).add_ingredient("#sand").setXp(amP).setOutput(amo)
    config.shaped_recipe(agZ).setEntries(abo, amo).setOutput(agZ)
    config.shaped_recipe(ajy).setEntries(aak, amo).setOutput(ajy)
    config.shaped_recipe(abs).setEntries(aae, aia).setEntries(aly, aiv).setOutput(abs)
    config.shaped_recipe(akh).setEntries(aar, afk).setOutput(akh)
    config.shaped_recipe(ahl).setEntries(aae, ajA).setEntries(aly, "apple").setOutput(ahl)
    config.shaped_recipe(aiQ).setEntries(afy, amc).setEntries(abN, ajA).setOutput(aiQ)
    config.shaped_recipe(ahx).setEntries(aas, ajA).setOutput(ahx)
    config.shaped_recipe(afW).setEntries(aae, aia).setEntries(aly, alB).setOutput(afW)
    config.shaped_recipe(adq).setEntries(aad, ajA).setOutput(adq)
    config.shaped_recipe(agD).setEntries(aao, ajA).setOutput(agD)
    config.shaped_recipe(ajq).setEntries(afy, amc).setEntries(afd, ajA).setOutput(ajq)
    config.shaped_recipe(aeD).setEntries(aag, ajA).setOutput(aeD)
    config.shaped_recipe(aeN).setEntries(afy, amc).setEntries(abF, ajA).setOutput(aeN)
    config.shaped_recipe(age).setEntries(afm, amc).setEntries(alG, ajA).setOutput(age)
    config.shaped_recipe(ahi).setEntries(alW, amc).setEntries(aeT, ajA).setOutput(ahi)
    config.shaped_recipe(aiU).setEntries(aac, ajA).setOutput(aiU)
    config.smelting_recipe(ajA).add_ingredient(akD).setXp(amQ).setOutput(ajA)
    config.smelting_recipe("gold_ingot_from_blasting", acS).add_ingredient(akD).setXp(amQ).setOutput(
        ajA).setCookingTime(amN)
    config.shapeless_recipe("gold_ingot_from_gold_block").addInput(aiU, 1).setOutput(ajA).setGroup(ajA)
    config.shaped_recipe("gold_ingot_from_nuggets").setEntries(aac, aia).setOutput(ajA).setGroup(ajA)
    config.shapeless_recipe(aia).addInput(ajA, 1).setOutput(aia)
    config.smelting_recipe("gold_nugget_from_blasting", acS).add_ingredient(aab).setXp(amP).setOutput(
        aia).setCookingTime(amN)
    config.smelting_recipe("gold_nugget_from_smelting").add_ingredient(aab).setXp(amP).setOutput(aia)
    config.shapeless_recipe(alg).addInput(alm, 1).addInput(alA, 1).setOutput(alg)
    config.shaped_recipe(aha).setEntries(abF, alg).setOutput(aha)
    config.shaped_recipe(aeU).setEntries(aam, alg).setOutput(aeU)
    config.shaped_recipe(ahf).setEntries(aak, alg).setOutput(ahf)
    config.shaped_recipe(ahC).setEntries(aak, ajL).setEntries(alP, amc).setOutput(ahC).setGroup(alx)
    config.shaped_recipe(akU).setEntries(abF, ajL).setEntries(abI, alb).setOutput(akU).setGroup(amJ)
    config.shapeless_recipe("gray_bed_from_white_bed").addInput(ajS, 1).addInput(akB, 1).setOutput(akU).setGroup(akG)
    config.shaped_recipe(aiw).setEntries(afd, ajL).setOutput(aiw).setGroup(alu)
    config.shaped_recipe("gray_carpet_from_white_carpet").setEntries(aae, agY).setEntries(aly, akB).setOutput(
        aiw).setGroup(alu)
    config.shapeless_recipe(acu).addInput(akB, 1).addInput(amw, 4).addInput(alN, 4).setOutput(acu).setGroup(aeJ)
    config.shapeless_recipe(akB).addInput(ajX, 1).addInput(aka, 1).setOutput(akB)
    config.smelting_recipe(abG).add_ingredient(aen).setXp(amP).setOutput(abG)
    config.shaped_recipe(adc).setEntries(aae, amo).setEntries(aly, akB).setOutput(adc).setGroup(ags)
    config.shaped_recipe(abi).setEntries(aak, adc).setOutput(abi).setGroup(ade)
    config.shaped_recipe("gray_stained_glass_pane_from_glass_pane").setEntries(aae, ajy).setEntries(aly, akB).setOutput(
        abi).setGroup(ade)
    config.shaped_recipe(aen).setEntries(aae, aiZ).setEntries(aly, akB).setOutput(aen).setGroup(acT)
    config.shapeless_recipe(ajL).addInput(akB, 1).addInput(aiV, 1).setOutput(ajL).setGroup(amy)
    config.shaped_recipe(aht).setEntries(aak, ajK).setEntries(alP, amc).setOutput(aht).setGroup(alx)
    config.shaped_recipe(akl).setEntries(abF, ajK).setEntries(abI, alb).setOutput(akl).setGroup(amJ)
    config.shapeless_recipe("green_bed_from_white_bed").addInput(ajS, 1).addInput(ako, 1).setOutput(akl).setGroup(akG)
    config.shaped_recipe(ahw).setEntries(afd, ajK).setOutput(ahw).setGroup(alu)
    config.shaped_recipe("green_carpet_from_white_carpet").setEntries(aae, agY).setEntries(aly, ako).setOutput(
        ahw).setGroup(alu)
    config.shapeless_recipe(aca).addInput(ako, 1).addInput(amw, 4).addInput(alN, 4).setOutput(aca).setGroup(aeJ)
    config.smelting_recipe(ako).add_ingredient("cactus").setXp(amQ).setOutput(ako)
    config.smelting_recipe(abk).add_ingredient(adT).setXp(amP).setOutput(abk)
    config.shaped_recipe(acP).setEntries(aae, amo).setEntries(aly, ako).setOutput(acP).setGroup(ags)
    config.shaped_recipe(aaS).setEntries(aak, acP).setOutput(aaS).setGroup(ade)
    config.shaped_recipe("green_stained_glass_pane_from_glass_pane").setEntries(aae, ajy).setEntries(aly,
                                                                                                     ako).setOutput(
        aaS).setGroup(ade)
    config.shaped_recipe(adT).setEntries(aae, aiZ).setEntries(aly, ako).setOutput(adT).setGroup(acT)
    config.shapeless_recipe(ajK).addInput(ako, 1).addInput(aiV, 1).setOutput(ajK).setGroup(amy)
    config.shaped_recipe(ajo).setEntries(afj, amc).setEntries(alL, aiX).setEntries(afe, alb).setOutput(ajo)
    config.shaped_recipe(akm).setEntries(aac, alZ).setOutput(akm)
    config.shaped_recipe(aay).setEntries(afd, ajw).setOutput(aay)
    config.shaped_recipe(aev).setEntries(aar, akd).setOutput(aev)
    config.shaped_recipe(aif).setEntries(aar, agJ).setOutput(aif)
    config.shapeless_recipe(agJ).addInput(aif, 1).addInput(agZ, 4).setOutput(agJ)
    config.shaped_recipe(alK).setEntries(aly, amj).setEntries([(0, 0), (0, 1), (1, 2), (2, 0), (2, 1)], ajw).setOutput(
        alK)
    config.shaped_recipe(aeA).setEntries(alG, alK).setEntries(alJ, akx).setOutput(aeA)
    config.shaped_recipe(akv).setEntries(afy, amc).setEntries(abN, ajw).setOutput(akv)
    config.shaped_recipe(ajO).setEntries(aak, ajw).setOutput(ajO)
    config.shaped_recipe(ajm).setEntries(aac, ajw).setOutput(ajm)
    config.shaped_recipe(ajg).setEntries(aas, ajw).setOutput(ajg)
    config.shaped_recipe(aeC).setEntries(aad, ajw).setOutput(aeC)
    config.shaped_recipe(akg).setEntries(aan, ajw).setOutput(akg)
    config.shaped_recipe(ahP).setEntries(aao, ajw).setOutput(ahP)
    config.shaped_recipe(akt).setEntries(afy, amc).setEntries(afd, ajw).setOutput(akt)
    config.smelting_recipe(ajw).add_ingredient(akW).setXp(amM).setOutput(ajw)
    config.smelting_recipe("iron_ingot_from_blasting", acS).add_ingredient(akW).setXp(amM).setOutput(
        ajw).setCookingTime(amN)
    config.shapeless_recipe("iron_ingot_from_iron_block").addInput(ajm, 1).setOutput(ajw).setGroup(ajw)
    config.shaped_recipe("iron_ingot_from_nuggets").setEntries(aac, ahG).setOutput(ajw).setGroup(ajw)
    config.shaped_recipe(agt).setEntries(aag, ajw).setOutput(agt)
    config.shapeless_recipe(ahG).addInput(ajw, 1).setOutput(ahG)
    config.smelting_recipe("iron_nugget_from_blasting", acS).add_ingredient(aaa).setXp(amP).setOutput(
        ahG).setCookingTime(amN)
    config.smelting_recipe("iron_nugget_from_smelting").add_ingredient(aaa).setXp(amP).setOutput(ahG)
    config.shaped_recipe(agS).setEntries(afy, amc).setEntries(abF, ajw).setOutput(agS)
    config.shaped_recipe(aic).setEntries(afm, amc).setEntries(alG, ajw).setOutput(aic)
    config.shaped_recipe(ajz).setEntries(alW, amc).setEntries(aeT, ajw).setOutput(ajz)
    config.shaped_recipe(agf).setEntries(aar, ajw).setOutput(agf)
    config.shaped_recipe(ajs).setEntries(aae, amc).setEntries(aly, alk).setOutput(ajs)
    config.shaped_recipe(afv).setEntries(alG, "carved_pumpkin").setEntries(alJ, ama).setOutput(afv)
    config.shaped_recipe(alh).setEntries(aae, alb).setEntries(aly, alj).setOutput(alh)
    config.shaped_recipe(ais).setEntries(aap, afM).setOutput(ais).setGroup(amr)
    config.shapeless_recipe(agl).addInput(afM, 1).setOutput(agl).setGroup(ago)
    config.shaped_recipe(aio).setEntries(aan, afM).setOutput(aio).setGroup(aie)
    config.shaped_recipe(ahs).setEntries(aeQ, amc).setEntries(aas, afM).setOutput(ahs).setGroup(ahk)
    config.shaped_recipe(adD).setEntries(aas, amc).setEntries(aeQ, afM).setOutput(adD).setGroup(adE)
    config.shapeless_recipe(afM).addInput("#jungle_logs", 1).setOutput(afM).setGroup(alz)
    config.shaped_recipe(acd).setEntries(afd, afM).setOutput(acd).setGroup(abS)
    config.shaped_recipe(aig).setEntries(aak, afM).setEntries(alP, amc).setOutput(aig)
    config.shaped_recipe(ahT).setEntries(abF, afM).setOutput(ahT).setGroup(aip)
    config.shaped_recipe(agm).setEntries(aam, afM).setOutput(agm).setGroup(afX)
    config.shaped_recipe(aeu).setEntries(aak, afM).setOutput(aeu).setGroup(aer)
    config.shaped_recipe(ahQ).setEntries(aar, "jungle_log").setOutput(ahQ).setGroup(amB)
    config.shaped_recipe(alw).setEntries(aai, amc).setOutput(alw)
    config.shaped_recipe(alc).setEntries(aly, ama).setEntries(aae, ahG).setOutput(alc)
    config.shaped_recipe(ahN).setEntries(aac, agR).setOutput(ahN)
    config.smelting_recipe("lapis_from_blasting", acS).add_ingredient(ajM).setXp(amO).setOutput(agR).setCookingTime(amN)
    config.smelting_recipe("lapis_from_smelting").add_ingredient(ajM).setXp(amO).setOutput(agR)
    config.shapeless_recipe(agR).addInput(ahN, 1).setOutput(agR)
    config.shaped_recipe(amC).setEntries([(0, 0), (0, 1), (1, 0), (2, 2)], alR).setEntries(aly, aiT).setOutput(amC)
    config.shaped_recipe(alk).setEntries(aar, "rabbit_hide").setOutput(alk)
    config.shaped_recipe(agE).setEntries(aas, alk).setOutput(agE)
    config.shaped_recipe(acX).setEntries(aad, alk).setOutput(acX)
    config.shaped_recipe(afg).setEntries(aao, alk).setOutput(afg)
    config.shaped_recipe(acM).setEntries(aai, alk).setOutput(acM)
    config.shaped_recipe(adR).setEntries(aag, alk).setOutput(adR)
    config.shaped_recipe(als).setEntries([(0, 0), (1, 0), (1, 2), (2, 0)], afK).setEntries(aly, akf).setOutput(als)
    config.shaped_recipe(amd).setEntries(alJ, ahK).setEntries(alG, amc).setOutput(amd)
    config.shaped_recipe(adz).setEntries(aak, aew).setEntries(alP, amc).setOutput(adz).setGroup(alx)
    config.shaped_recipe(afa).setEntries(abF, aew).setEntries(abI, alb).setOutput(afa).setGroup(amJ)
    config.shapeless_recipe("light_blue_bed_from_white_bed").addInput(ajS, 1).addInput(aeR, 1).setOutput(afa).setGroup(
        akG)
    config.shaped_recipe(adL).setEntries(afd, aew).setOutput(adL).setGroup(alu)
    config.shaped_recipe("light_blue_carpet_from_white_carpet").setEntries(aae, agY).setEntries(aly, aeR).setOutput(
        adL).setGroup(alu)
    config.shapeless_recipe(aaD).addInput(aeR, 1).addInput(amw, 4).addInput(alN, 4).setOutput(aaD).setGroup(aeJ)
    config.shapeless_recipe("light_blue_dye_from_blue_orchid").addInput("blue_orchid", 1).setOutput(aeR).setGroup(aeR)
    config.shapeless_recipe("light_blue_dye_from_blue_white_dye").addInput(akr, 1).addInput(aka, 1).setOutput(
        aeR).setGroup(aeR)
    config.smelting_recipe(aaB).add_ingredient(acg).setXp(amP).setOutput(aaB)
    config.shaped_recipe(aaQ).setEntries(aae, amo).setEntries(aly, aeR).setOutput(aaQ).setGroup(ags)
    config.shaped_recipe(aax).setEntries(aak, aaQ).setOutput(aax).setGroup(ade)
    config.shaped_recipe("light_blue_stained_glass_pane_from_glass_pane").setEntries(aae, ajy).setEntries(aly,
                                                                                                          aeR).setOutput(
        aax).setGroup(ade)
    config.shaped_recipe(acg).setEntries(aae, aiZ).setEntries(aly, aeR).setOutput(acg).setGroup(acT)
    config.shapeless_recipe(aew).addInput(aeR, 1).addInput(aiV, 1).setOutput(aew).setGroup(amy)
    config.shaped_recipe(adI).setEntries(aak, aeE).setEntries(alP, amc).setOutput(adI).setGroup(alx)
    config.shaped_recipe(aeY).setEntries(abF, aeE).setEntries(abI, alb).setOutput(aeY).setGroup(amJ)
    config.shapeless_recipe("light_gray_bed_from_white_bed").addInput(ajS, 1).addInput(afs, 1).setOutput(aeY).setGroup(
        akG)
    config.shaped_recipe(adF).setEntries(afd, aeE).setOutput(adF).setGroup(alu)
    config.shaped_recipe("light_gray_carpet_from_white_carpet").setEntries(aae, agY).setEntries(aly, afs).setOutput(
        adF).setGroup(alu)
    config.shapeless_recipe(aaF).addInput(afs, 1).addInput(amw, 4).addInput(alN, 4).setOutput(aaF).setGroup(aeJ)
    config.shapeless_recipe("light_gray_dye_from_azure_bluet").addInput("azure_bluet", 1).setOutput(afs).setGroup(afs)
    config.shapeless_recipe("light_gray_dye_from_black_white_dye").addInput(ajX, 1).addInput(aka, 2).setOutput(
        afs).setGroup(afs)
    config.shapeless_recipe("light_gray_dye_from_gray_white_dye").addInput(akB, 1).addInput(aka, 1).setOutput(
        afs).setGroup(afs)
    config.shapeless_recipe("light_gray_dye_from_oxeye_daisy").addInput("oxeye_daisy", 1).setOutput(afs).setGroup(afs)
    config.shapeless_recipe("light_gray_dye_from_white_tulip").addInput("white_tulip", 1).setOutput(afs).setGroup(afs)
    config.smelting_recipe(aaA).add_ingredient(abY).setXp(amP).setOutput(aaA)
    config.shaped_recipe(aaM).setEntries(aae, amo).setEntries(aly, afs).setOutput(aaM).setGroup(ags)
    config.shaped_recipe(aaz).setEntries(aak, aaM).setOutput(aaz).setGroup(ade)
    config.shaped_recipe("light_gray_stained_glass_pane_from_glass_pane").setEntries(aae, ajy).setEntries(aly,
                                                                                                          afs).setOutput(
        aaz).setGroup(ade)
    config.shaped_recipe(abY).setEntries(aae, aiZ).setEntries(aly, afs).setOutput(abY).setGroup(acT)
    config.shapeless_recipe(aeE).addInput(afs, 1).addInput(aiV, 1).setOutput(aeE).setGroup(amy)
    config.shaped_recipe(aaw).setEntries(afd, ajA).setOutput(aaw)
    config.shaped_recipe(ahO).setEntries(aak, akp).setEntries(alP, amc).setOutput(ahO).setGroup(alx)
    config.shaped_recipe(akP).setEntries(abF, akp).setEntries(abI, alb).setOutput(akP).setGroup(amJ)
    config.shapeless_recipe("lime_bed_from_white_bed").addInput(ajS, 1).addInput(akR, 1).setOutput(akP).setGroup(akG)
    config.shaped_recipe(aiM).setEntries(afd, akp).setOutput(aiM).setGroup(alu)
    config.shaped_recipe("lime_carpet_from_white_carpet").setEntries(aae, agY).setEntries(aly, akR).setOutput(
        aiM).setGroup(alu)
    config.shapeless_recipe(acG).addInput(akR, 1).addInput(amw, 4).addInput(alN, 4).setOutput(acG).setGroup(aeJ)
    config.shapeless_recipe(akR).addInput(ako, 1).addInput(aka, 1).setOutput(akR)
    config.smelting_recipe("lime_dye_from_smelting").add_ingredient("sea_pickle").setXp(amP).setOutput(akR)
    config.smelting_recipe(abO).add_ingredient(aeK).setXp(amP).setOutput(abO)
    config.shaped_recipe(acY).setEntries(aae, amo).setEntries(aly, akR).setOutput(acY).setGroup(ags)
    config.shaped_recipe(aaZ).setEntries(aak, acY).setOutput(aaZ).setGroup(ade)
    config.shaped_recipe("lime_stained_glass_pane_from_glass_pane").setEntries(aae, ajy).setEntries(aly, akR).setOutput(
        aaZ).setGroup(ade)
    config.shaped_recipe(aeK).setEntries(aae, aiZ).setEntries(aly, akR).setOutput(aeK).setGroup(acT)
    config.shapeless_recipe(akp).addInput(akR, 1).addInput(aiV, 1).setOutput(akp).setGroup(amy)
    config.shaped_recipe(amA).setEntries(afu, alb).setEntries(afd, alR).setOutput(amA)
    config.shaped_recipe(aeO).setEntries(aak, ahu).setEntries(alP, amc).setOutput(aeO).setGroup(alx)
    config.shaped_recipe(ahI).setEntries(abF, ahu).setEntries(abI, alb).setOutput(ahI).setGroup(amJ)
    config.shapeless_recipe("magenta_bed_from_white_bed").addInput(ajS, 1).addInput(ait, 1).setOutput(ahI).setGroup(akG)
    config.shaped_recipe(afh).setEntries(afd, ahu).setOutput(afh).setGroup(alu)
    config.shaped_recipe("magenta_carpet_from_white_carpet").setEntries(aae, agY).setEntries(aly, ait).setOutput(
        afh).setGroup(alu)
    config.shapeless_recipe(aba).addInput(ait, 1).addInput(amw, 4).addInput(alN, 4).setOutput(aba).setGroup(aeJ)
    config.shapeless_recipe("magenta_dye_from_allium").addInput("allium", 1).setOutput(ait).setGroup(ait)
    config.shapeless_recipe("magenta_dye_from_blue_red_pink").addInput(akr, 1).addInput(ald, 1).addInput(akI,
                                                                                                         1).setOutput(
        ait).setGroup(ait)
    config.shapeless_recipe("magenta_dye_from_blue_red_white_dye").addInput(akr, 1).addInput(ald, 2).addInput(aka,
                                                                                                              1).setOutput(
        ait).setGroup(ait)
    config.shapeless_recipe("magenta_dye_from_lilac").addInput("lilac", 1).setOutput(ait).setGroup(ait)
    config.shapeless_recipe("magenta_dye_from_purple_and_pink").addInput(ajv, 1).addInput(akI, 1).setOutput(
        ait).setGroup(ait)
    config.smelting_recipe(aaH).add_ingredient(acW).setXp(amP).setOutput(aaH)
    config.shaped_recipe(acf).setEntries(aae, amo).setEntries(aly, ait).setOutput(acf).setGroup(ags)
    config.shaped_recipe(aaE).setEntries(aak, acf).setOutput(aaE).setGroup(ade)
    config.shaped_recipe("magenta_stained_glass_pane_from_glass_pane").setEntries(aae, ajy).setEntries(aly,
                                                                                                       ait).setOutput(
        aaE).setGroup(ade)
    config.shaped_recipe(acW).setEntries(aae, aiZ).setEntries(aly, ait).setOutput(acW).setGroup(acT)
    config.shapeless_recipe(ahu).addInput(ait, 1).addInput(aiV, 1).setOutput(ahu).setGroup(amy)
    config.shaped_recipe(ain).setEntries(aar, aiJ).setOutput(ain)
    config.shapeless_recipe(aiJ).addInput(ahe, 1).addInput(aiT, 1).setOutput(aiJ)
    config.shaped_recipe(amG).setEntries(aae, alY).setEntries(aly, ala).setOutput(amG)
    config.shaped_recipe(amb).setEntries(aac, aiv).setOutput(amb)
    config.shapeless_recipe(aij).addInput(aiv, 1).setOutput(aij)
    config.shaped_recipe(akx).setEntries(aap, ajw).setOutput(akx)
    config.shapeless_recipe(ace).addInput(alY, 1).addInput("enchanted_golden_apple", 1).setOutput(ace)
    config.shapeless_recipe(adm).addInput(ahK, 1).addInput("vine", 1).setOutput(adm)
    config.shaped_recipe(abv).setEntries(abF, adm).setOutput(abv)
    config.shaped_recipe(aaP).setEntries(aam, adm).setOutput(aaP)
    config.shaped_recipe(abB).setEntries(aak, adm).setOutput(abB)
    config.shapeless_recipe(ada).addInput(ahm, 1).addInput("vine", 1).setOutput(ada)
    config.shaped_recipe(abK).setEntries(abF, ada).setOutput(abK)
    config.shaped_recipe(aaW).setEntries(aam, ada).setOutput(aaW)
    config.shaped_recipe(abq).setEntries(aak, ada).setOutput(abq)
    config.shapeless_recipe(afN).addInput("brown_mushroom", 1).addInput("red_mushroom", 1).addInput(amq, 1).setOutput(
        afN)
    config.smelting_recipe(ahc).add_ingredient("netherrack").setXp(amP).setOutput(ahc)
    config.shaped_recipe(afS).setEntries(aar, ahc).setOutput(afS)
    config.shaped_recipe(adk).setEntries(aas, afS).setEntries(aeQ, ahc).setOutput(adk)
    config.shaped_recipe(adn).setEntries(abF, afS).setOutput(adn)
    config.shaped_recipe(acH).setEntries(aam, afS).setOutput(acH)
    config.shaped_recipe(adG).setEntries(aak, afS).setOutput(adG)
    config.shaped_recipe(ads).setEntries(aac, aiz).setOutput(ads)
    config.shaped_recipe(aiO).setEntries(aae, alb).setEntries(aly, akQ).setOutput(aiO)
    config.shaped_recipe(akF).setEntries(aap, ajh).setOutput(akF).setGroup(amr)
    config.shapeless_recipe(ajB).addInput(ajh, 1).setOutput(ajB).setGroup(ago)
    config.shaped_recipe(akJ).setEntries(aan, ajh).setOutput(akJ).setGroup(aie)
    config.shaped_recipe(ajR).setEntries(aeQ, amc).setEntries(aas, ajh).setOutput(ajR).setGroup(ahk)
    config.shaped_recipe(afi).setEntries(aas, amc).setEntries(aeQ, ajh).setOutput(afi).setGroup(adE)
    config.shapeless_recipe(ajh).addInput("#oak_logs", 1).setOutput(ajh).setGroup(alz)
    config.shaped_recipe(acZ).setEntries(afd, ajh).setOutput(acZ).setGroup(abS)
    config.shaped_recipe(akS).setEntries(aak, ajh).setEntries(alP, amc).setOutput(akS)
    config.shaped_recipe(akq).setEntries(abF, ajh).setOutput(akq).setGroup(aip)
    config.shaped_recipe(ajx).setEntries(aam, ajh).setOutput(ajx).setGroup(afX)
    config.shaped_recipe(ahy).setEntries(aak, ajh).setOutput(ahy).setGroup(aer)
    config.shaped_recipe(akV).setEntries(aar, "oak_log").setOutput(akV).setGroup(amB)
    config.shaped_recipe(akX).setEntries([(2, 1)], alA).setEntries(afu, akQ).setEntries(aaj, ahK).setOutput(akX)
    config.shaped_recipe(aga).setEntries(aak, aiN).setEntries(alP, amc).setOutput(aga).setGroup(alx)
    config.shaped_recipe(aji).setEntries(abF, aiN).setEntries(abI, alb).setOutput(aji).setGroup(amJ)
    config.shapeless_recipe("orange_bed_from_white_bed").addInput(ajS, 1).addInput(ajH, 1).setOutput(aji).setGroup(akG)
    config.shaped_recipe(afJ).setEntries(afd, aiN).setOutput(afJ).setGroup(alu)
    config.shaped_recipe("orange_carpet_from_white_carpet").setEntries(aae, agY).setEntries(aly, ajH).setOutput(
        afJ).setGroup(alu)
    config.shapeless_recipe(abH).addInput(ajH, 1).addInput(amw, 4).addInput(alN, 4).setOutput(abH).setGroup(aeJ)
    config.shapeless_recipe("orange_dye_from_orange_tulip").addInput("orange_tulip", 1).setOutput(ajH).setGroup(ajH)
    config.shapeless_recipe("orange_dye_from_red_yellow").addInput(ald, 1).addInput(ajr, 1).setOutput(ajH).setGroup(ajH)
    config.smelting_recipe(aaN).add_ingredient(adp).setXp(amP).setOutput(aaN)
    config.shaped_recipe(acm).setEntries(aae, amo).setEntries(aly, ajH).setOutput(acm).setGroup(ags)
    config.shaped_recipe(aaI).setEntries(aak, acm).setOutput(aaI).setGroup(ade)
    config.shaped_recipe("orange_stained_glass_pane_from_glass_pane").setEntries(aae, ajy).setEntries(aly,
                                                                                                      ajH).setOutput(
        aaI).setGroup(ade)
    config.shaped_recipe(adp).setEntries(aae, aiZ).setEntries(aly, ajH).setOutput(adp).setGroup(acT)
    config.shapeless_recipe(aiN).addInput(ajH, 1).addInput(aiV, 1).setOutput(aiN).setGroup(amy)
    config.shapeless_recipe(ajF).addInput("ice", 9).setOutput(ajF)
    config.shaped_recipe(aku).setEntries(aae, amc).setEntries(aly, "#wool").setOutput(aku)
    config.shaped_recipe(alY).setEntries(abF, ajf).setOutput(alY)
    config.shaped_recipe(aiH).setEntries(aak, akn).setEntries(alP, amc).setOutput(aiH).setGroup(alx)
    config.shaped_recipe(akC).setEntries(abF, akn).setEntries(abI, alb).setOutput(akC).setGroup(amJ)
    config.shapeless_recipe("pink_bed_from_white_bed").addInput(ajS, 1).addInput(akI, 1).setOutput(akC).setGroup(akG)
    config.shaped_recipe(ahE).setEntries(afd, akn).setOutput(ahE).setGroup(alu)
    config.shaped_recipe("pink_carpet_from_white_carpet").setEntries(aae, agY).setEntries(aly, akI).setOutput(
        ahE).setGroup(alu)
    config.shapeless_recipe(acn).addInput(akI, 1).addInput(amw, 4).addInput(alN, 4).setOutput(acn).setGroup(aeJ)
    config.shapeless_recipe("pink_dye_from_peony").addInput("peony", 1).setOutput(akI).setGroup(akI)
    config.shapeless_recipe("pink_dye_from_pink_tulip").addInput("pink_tulip", 1).setOutput(akI).setGroup(akI)
    config.shapeless_recipe("pink_dye_from_red_white_dye").addInput(ald, 1).addInput(aka, 1).setOutput(akI).setGroup(
        akI)
    config.smelting_recipe(abt).add_ingredient(aek).setXp(amP).setOutput(abt)
    config.shaped_recipe(add).setEntries(aae, amo).setEntries(aly, akI).setOutput(add).setGroup(ags)
    config.shaped_recipe(abl).setEntries(aak, add).setOutput(abl).setGroup(ade)
    config.shaped_recipe("pink_stained_glass_pane_from_glass_pane").setEntries(aae, ajy).setEntries(aly, akI).setOutput(
        abl).setGroup(ade)
    config.shaped_recipe(aek).setEntries(aae, aiZ).setEntries(aly, akI).setOutput(aek).setGroup(acT)
    config.shapeless_recipe(akn).addInput(akI, 1).addInput(aiV, 1).setOutput(akn).setGroup(amy)
    config.shaped_recipe(alD).setEntries(alP, akQ).setEntries([(0, 1), (0, 2), (2, 1), (2, 2)], ahK).setEntries(abF,
                                                                                                                alb).setEntries(
        aly, ajw).setOutput(alD)
    config.shaped_recipe(adA).setEntries(aar, akT).setOutput(adA)
    config.shaped_recipe(aby).setEntries(abF, adA).setOutput(aby)
    config.shaped_recipe(aaT).setEntries(aam, adA).setOutput(aaT)
    config.shaped_recipe(aef).setEntries(aar, alm).setOutput(aef)
    config.shaped_recipe(ach).setEntries(abF, aef).setOutput(ach)
    config.shaped_recipe(abc).setEntries(aam, aef).setOutput(abc)
    config.shaped_recipe(adZ).setEntries(aar, alg).setOutput(adZ)
    config.shaped_recipe(abP).setEntries(abF, adZ).setOutput(abP)
    config.shaped_recipe(abf).setEntries(aam, adZ).setOutput(abf)
    config.smelting_recipe(acJ).add_ingredient("chorus_fruit").setXp(amP).setOutput(acJ)
    config.shaped_recipe(agQ).setEntries(alP, akQ).setEntries(aly, amc).setEntries(aal, ajA).setOutput(agQ)
    config.shaped_recipe(ajE).setEntries(aar, aec).setOutput(ajE)
    config.shaped_recipe(adw).setEntries(aac, aec).setOutput(adw)
    config.shaped_recipe(abZ).setEntries(abF, adw).setOutput(abZ)
    config.shaped_recipe(abe).setEntries(aam, adw).setOutput(abe)
    config.shaped_recipe(aeF).setEntries(abF, ajE).setOutput(aeF)
    config.shaped_recipe(ado).setEntries(aam, ajE).setOutput(ado)
    config.shaped_recipe(aex).setEntries(aak, ajE).setOutput(aex)
    config.shapeless_recipe(ahV).addInput("pumpkin", 1).addInput(amk, 1).addInput(amI, 1).setOutput(ahV)
    config.shapeless_recipe(agd).addInput("pumpkin", 1).setOutput(agd)
    config.shaped_recipe(afG).setEntries(aak, aiL).setEntries(alP, amc).setOutput(afG).setGroup(alx)
    config.shaped_recipe(aiP).setEntries(abF, aiL).setEntries(abI, alb).setOutput(aiP).setGroup(amJ)
    config.shapeless_recipe("purple_bed_from_white_bed").addInput(ajS, 1).addInput(ajv, 1).setOutput(aiP).setGroup(akG)
    config.shaped_recipe(agr).setEntries(afd, aiL).setOutput(agr).setGroup(alu)
    config.shaped_recipe("purple_carpet_from_white_carpet").setEntries(aae, agY).setEntries(aly, ajv).setOutput(
        agr).setGroup(alu)
    config.shapeless_recipe(abM).addInput(ajv, 1).addInput(amw, 4).addInput(alN, 4).setOutput(abM).setGroup(aeJ)
    config.shapeless_recipe(ajv).addInput(akr, 1).addInput(ald, 1).setOutput(ajv)
    config.smelting_recipe(aaX).add_ingredient(adP).setXp(amP).setOutput(aaX)
    config.shaped_recipe(acD).setEntries(aae, amo).setEntries(aly, ajv).setOutput(acD).setGroup(ags)
    config.shaped_recipe(aaK).setEntries(aak, acD).setOutput(aaK).setGroup(ade)
    config.shaped_recipe("purple_stained_glass_pane_from_glass_pane").setEntries(aae, ajy).setEntries(aly,
                                                                                                      ajv).setOutput(
        aaK).setGroup(ade)
    config.shaped_recipe(adP).setEntries(aae, aiZ).setEntries(aly, ajv).setOutput(adP).setGroup(acT)
    config.shapeless_recipe(aiL).addInput(ajv, 1).addInput(aiV, 1).setOutput(aiL).setGroup(amy)
    config.shaped_recipe(agK).setEntries(aar, acJ).setOutput(agK)
    config.shaped_recipe(agF).setEntries(aeT, air).setOutput(agF)
    config.shaped_recipe(air).setEntries(abF, aaq).setOutput(air)
    config.shaped_recipe(agj).setEntries(aam, aaq).setOutput(agj)
    config.smelting_recipe(alA).add_ingredient(adH).setXp(amO).setOutput(alA)
    config.shaped_recipe(ahj).setEntries(aar, alA).setOutput(ahj)
    config.smelting_recipe("quartz_from_blasting", acS).add_ingredient(adH).setXp(amO).setOutput(alA).setCookingTime(
        amN)
    config.shaped_recipe(agx).setEntries(aeT, ahj).setOutput(agx)
    config.shaped_recipe(aii).setEntries(abF, aaf).setOutput(aii)
    config.shaped_recipe(afT).setEntries(aam, aaf).setOutput(afT)
    config.shapeless_recipe("rabbit_stew_from_brown_mushroom").addInput(agI, 1).addInput(agh, 1).addInput(amq,
                                                                                                          1).addInput(
        alB, 1).addInput("brown_mushroom", 1).setOutput(ahL).setGroup(ahL)
    config.shapeless_recipe("rabbit_stew_from_red_mushroom").addInput(agI, 1).addInput(agh, 1).addInput(amq,
                                                                                                        1).addInput(alB,
                                                                                                                    1).addInput(
        "red_mushroom", 1).setOutput(ahL).setGroup(ahL)
    config.shaped_recipe(amu).setEntries(aly, amc).setEntries(aal, ajw).setOutput(amu)
    config.shapeless_recipe(akQ).addInput(afx, 1).setOutput(akQ)
    config.shaped_recipe(afx).setEntries(aac, akQ).setOutput(afx)
    config.smelting_recipe("redstone_from_blasting", acS).add_ingredient(ahr).setXp(amM).setOutput(akQ).setCookingTime(
        amN)
    config.smelting_recipe("redstone_from_smelting").add_ingredient(ahr).setXp(amM).setOutput(akQ)
    config.shaped_recipe(agn).setEntries(aau, akQ).setEntries(aly, akh).setOutput(agn)
    config.shaped_recipe(aeL).setEntries(alJ, amc).setEntries(alG, akQ).setOutput(aeL)
    config.shaped_recipe(ajp).setEntries(aak, akK).setEntries(alP, amc).setOutput(ajp).setGroup(alx)
    config.shaped_recipe(alp).setEntries(abF, akK).setEntries(abI, alb).setOutput(alp).setGroup(amJ)
    config.shapeless_recipe("red_bed_from_white_bed").addInput(ajS, 1).addInput(ald, 1).setOutput(alp).setGroup(akG)
    config.shaped_recipe(ajJ).setEntries(afd, akK).setOutput(ajJ).setGroup(alu)
    config.shaped_recipe("red_carpet_from_white_carpet").setEntries(aae, agY).setEntries(aly, ald).setOutput(
        ajJ).setGroup(alu)
    config.shapeless_recipe(acQ).addInput(ald, 1).addInput(amw, 4).addInput(alN, 4).setOutput(acQ).setGroup(aeJ)
    config.shapeless_recipe("red_dye_from_beetroot").addInput("beetroot", 1).setOutput(ald).setGroup(ald)
    config.shapeless_recipe("red_dye_from_poppy").addInput("poppy", 1).setOutput(ald).setGroup(ald)
    config.shapeless_recipe("red_dye_from_rose_bush").addInput("rose_bush", 1).setOutput(ald).setGroup(ald)
    config.shapeless_recipe("red_dye_from_tulip").addInput("red_tulip", 1).setOutput(ald).setGroup(ald)
    config.smelting_recipe(abW).add_ingredient(aft).setXp(amP).setOutput(abW)
    config.shaped_recipe(adM).setEntries(aeS, aiz).setEntries(afo, ahc).setOutput(adM)
    config.shaped_recipe(acc).setEntries(abF, adM).setOutput(acc)
    config.shaped_recipe(abb).setEntries(aam, adM).setOutput(abb)
    config.shaped_recipe(abT).setEntries(aak, adM).setOutput(abT)
    config.shaped_recipe(agz).setEntries(aar, "red_sand").setOutput(agz)
    config.shaped_recipe(adh).setEntries(abF, ['red_sandstone', 'chiseled_red_sandstone']).setOutput(adh)
    config.shaped_recipe(act).setEntries(aam,
                                         ['red_sandstone', 'chiseled_red_sandstone', 'cut_red_sandstone']).setOutput(
        act)
    config.shaped_recipe(adf).setEntries(aak, agz).setOutput(adf)
    config.shaped_recipe(adt).setEntries(aae, amo).setEntries(aly, ald).setOutput(adt).setGroup(ags)
    config.shaped_recipe(abx).setEntries(aak, adt).setOutput(abx).setGroup(ade)
    config.shaped_recipe("red_stained_glass_pane_from_glass_pane").setEntries(aae, ajy).setEntries(aly, ald).setOutput(
        abx).setGroup(ade)
    config.shaped_recipe(aft).setEntries(aae, aiZ).setEntries(aly, ald).setOutput(aft).setGroup(acT)
    config.shapeless_recipe(akK).addInput(ald, 1).addInput(aiV, 1).setOutput(akK).setGroup(amy)
    config.shaped_recipe(akY).setEntries(afj, aeL).setEntries(alL, akQ).setEntries(abI, ami).setOutput(akY)
    config.shaped_recipe(akk).setEntries(aar, amw).setOutput(akk)
    config.shaped_recipe(aeX).setEntries(abF, ['sandstone', 'chiseled_sandstone']).setOutput(aeX)
    config.shaped_recipe(aei).setEntries(aam, ['sandstone', 'chiseled_sandstone', 'cut_sandstone']).setOutput(aei)
    config.shaped_recipe(afc).setEntries(aak, akk).setOutput(afc)
    config.shaped_recipe(ahA).setEntries(alL, alR).setEntries(aal, alX).setOutput(ahA)
    config.shaped_recipe(ahD).setEntries([(0, 0), (0, 2), (2, 0), (2, 2)], aec).setEntries(
        [(0, 1), (1, 0), (1, 1), (1, 2), (2, 1)], "prismarine_crystals").setOutput(ahD)
    config.shaped_recipe(alS).setEntries(aeS, ajw).setOutput(alS)
    config.shaped_recipe(alV).setEntries([(0, 0), (0, 1), (1, 1), (1, 2), (2, 0), (2, 1)], alb).setEntries(alL,
                                                                                                           ajw).setOutput(
        alV)
    config.shaped_recipe(aim).setEntries(alJ, amj).setEntries([(0, 0), (0, 2)], "shulker_shell").setOutput(aim)
    config.shapeless_recipe(acC).addInput(alY, 1).addInput("wither_skeleton_skull", 1).setOutput(acC)
    config.shapeless_recipe(aiT).addInput(ahW, 1).setOutput(aiT)
    config.shaped_recipe(ahW).setEntries(aac, aiT).setOutput(ahW)
    config.shaped_recipe(afw).setEntries(aat, alb).setEntries(afd, ajw).setOutput(afw)
    config.shaped_recipe(alI).setEntries(aau, ame).setEntries(aly, alr).setOutput(alI)
    config.smelting_recipe(agk).add_ingredient(ahj).setXp(amP).setOutput(agk)
    config.shaped_recipe(acR).setEntries(abF, agk).setOutput(acR)
    config.shaped_recipe(acv).setEntries(aam, agk).setOutput(acv)
    config.smelting_recipe(acE).add_ingredient(agz).setXp(amP).setOutput(acE)
    config.shaped_recipe(aaL).setEntries(abF, acE).setOutput(aaL)
    config.shaped_recipe(aaC).setEntries(aam, acE).setOutput(aaC)
    config.smelting_recipe(aeb).add_ingredient(akk).setXp(amP).setOutput(aeb)
    config.shaped_recipe(acb).setEntries(abF, aeb).setOutput(acb)
    config.shaped_recipe(abm).setEntries(aam, aeb).setOutput(abm)
    config.smelting_recipe(ahp).add_ingredient(ami).setXp(amP).setOutput(ahp)
    config.shaped_recipe(adx).setEntries(abF, ahp).setOutput(adx)
    config.shaped_recipe(amp).setEntries(abF, aiY).setOutput(amp)
    config.shaped_recipe(aiY).setEntries(aar, "snowball").setOutput(aiY)
    config.shaped_recipe(afb).setEntries(aau, afk).setEntries(aly, aml).setOutput(afb)
    config.smelting_recipe(alU).add_ingredient("wet_sponge").setXp(amK).setOutput(alU)
    config.shaped_recipe(aiE).setEntries(aap, agu).setOutput(aiE).setGroup(amr)
    config.shapeless_recipe(afV).addInput(agu, 1).setOutput(afV).setGroup(ago)
    config.shaped_recipe(ahU).setEntries(aan, agu).setOutput(ahU).setGroup(aie)
    config.shaped_recipe(agO).setEntries(aeQ, amc).setEntries(aas, agu).setOutput(agO).setGroup(ahk)
    config.shaped_recipe(ady).setEntries(aas, amc).setEntries(aeQ, agu).setOutput(ady).setGroup(adE)
    config.shapeless_recipe(agu).addInput("#spruce_logs", 1).setOutput(agu).setGroup(alz)
    config.shaped_recipe(abX).setEntries(afd, agu).setOutput(abX).setGroup(abS)
    config.shaped_recipe(aiD).setEntries(aak, agu).setEntries(alP, amc).setOutput(aiD)
    config.shaped_recipe(ahS).setEntries(abF, agu).setOutput(ahS).setGroup(aip)
    config.shaped_recipe(agG).setEntries(aam, agu).setOutput(agG).setGroup(afX)
    config.shaped_recipe(aez).setEntries(aak, agu).setOutput(aez).setGroup(aer)
    config.shaped_recipe(ahX).setEntries(aar, "spruce_log").setOutput(ahX).setGroup(amB)
    config.shaped_recipe(amc).setEntries(aeT, alb).setOutput(amc).setGroup(alH)
    config.shaped_recipe(afH).setEntries(alJ, alD).setEntries(alG, aiT).setOutput(afH)
    config.shaped_recipe("stick_from_bamboo_item").setEntries(aeT, alX).setOutput(amc).setGroup(alH)
    config.smelting_recipe(ami).add_ingredient(ahK).setXp(amP).setOutput(ami)
    config.shaped_recipe(aiB).setEntries(alL, ajw).setEntries(abI, ami).setOutput(aiB)
    config.shaped_recipe(ajN).setEntries(afy, amc).setEntries(abN, ahK).setOutput(ajN)
    config.shaped_recipe(ahm).setEntries(aar, ami).setOutput(ahm)
    config.shaped_recipe(adY).setEntries(abF, ahm).setOutput(adY)
    config.shaped_recipe(acU).setEntries(aam, ahm).setOutput(acU)
    config.shaped_recipe(adV).setEntries(aak, ahm).setOutput(adV)
    config.shapeless_recipe(ahv).addInput(ami, 1).setOutput(ahv)
    config.shaped_recipe(akc).setEntries(afy, amc).setEntries(afd, ahK).setOutput(akc)
    config.shaped_recipe(agH).setEntries(afy, amc).setEntries(abF, ahK).setOutput(agH)
    config.shaped_recipe(acx).setEntries(afd, ami).setOutput(acx)
    config.shaped_recipe(ahn).setEntries(afm, amc).setEntries(alG, ahK).setOutput(ahn)
    config.shaped_recipe(aiX).setEntries(abF, ami).setOutput(aiX)
    config.shaped_recipe(agU).setEntries(aam, ami).setOutput(agU)
    config.shaped_recipe(aiA).setEntries(alW, amc).setEntries(aeT, ahK).setOutput(aiA)
    config.shaped_recipe(acp).setEntries(aar, "stripped_acacia_log").setOutput(acp).setGroup(amB)
    config.shaped_recipe(acN).setEntries(aar, "stripped_birch_log").setOutput(acN).setGroup(amB)
    config.shaped_recipe(abr).setEntries(aar, "stripped_dark_oak_log").setOutput(abr).setGroup(amB)
    config.shaped_recipe(acF).setEntries(aar, "stripped_jungle_log").setOutput(acF).setGroup(amB)
    config.shaped_recipe(adK).setEntries(aar, "stripped_oak_log").setOutput(adK).setGroup(amB)
    config.shaped_recipe(acz).setEntries(aar, "stripped_spruce_log").setOutput(acz).setGroup(amB)
    config.shapeless_recipe("sugar_from_honey_bottle").addInput(agJ, 1).setOutput(amk).setGroup(amk)
    config.shapeless_recipe("sugar_from_sugar_cane").addInput(ajf, 1).setOutput(amk).setGroup(amk)
    config.smelting_recipe(aiZ).add_ingredient(amD).setXp(amL).setOutput(aiZ)
    config.shaped_recipe(amH).setEntries(aau, ['sand', 'red_sand']).setEntries([(0, 0), (0, 2), (1, 1), (2, 0), (2, 2)],
                                                                               ajU).setOutput(amH)
    config.shaped_recipe(ahb).setEntries(alG, amH).setEntries(alJ, akx).setOutput(ahb)
    config.shaped_recipe(ama).setEntries(alJ, amc).setEntries(alG, ['coal', 'charcoal']).setOutput(ama)
    config.shapeless_recipe(afA).addInput(amj, 1).addInput(afE, 1).setOutput(afA)
    config.shaped_recipe(afE).setEntries(alW, alb).setEntries(alJ, amc).setEntries(alG, ajw).setOutput(afE)
    config.shaped_recipe(afZ).setEntries(aao, "scute").setOutput(afZ)
    config.shapeless_recipe(alZ).addInput(akm, 1).setOutput(alZ)
    config.shaped_recipe(agV).setEntries(aak, aiV).setEntries(alP, amc).setOutput(agV).setGroup(alx)
    config.shaped_recipe(ajS).setEntries(abF, aiV).setEntries(abI, alb).setOutput(ajS).setGroup(amJ)
    config.shaped_recipe(agY).setEntries(afd, aiV).setOutput(agY).setGroup(alu)
    config.shapeless_recipe(aci).addInput(aka, 1).addInput(amw, 4).addInput(alN, 4).setOutput(aci).setGroup(aeJ)
    config.shapeless_recipe(aka).addInput(ajY, 1).setOutput(aka).setGroup(aka)
    config.shapeless_recipe("white_dye_from_lily_of_the_valley").addInput("lily_of_the_valley", 1).setOutput(
        aka).setGroup(aka)
    config.smelting_recipe(aaY).add_ingredient(adW).setXp(amP).setOutput(aaY)
    config.shaped_recipe(acK).setEntries(aae, amo).setEntries(aly, aka).setOutput(acK).setGroup(ags)
    config.shaped_recipe(aaU).setEntries(aak, acK).setOutput(aaU).setGroup(ade)
    config.shaped_recipe("white_stained_glass_pane_from_glass_pane").setEntries(aae, ajy).setEntries(aly,
                                                                                                     aka).setOutput(
        aaU).setGroup(ade)
    config.shaped_recipe(adW).setEntries(aae, aiZ).setEntries(aly, aka).setOutput(adW).setGroup(acT)
    config.shaped_recipe("white_wool_from_string").setEntries(aar, alR).setOutput(aiV)
    config.shaped_recipe(aiR).setEntries(afy, amc).setEntries(abN, alb).setOutput(aiR)
    config.shaped_recipe(ajk).setEntries(afy, amc).setEntries(afd, alb).setOutput(ajk)
    config.shaped_recipe(afq).setEntries(afy, amc).setEntries(abF, alb).setOutput(afq)
    config.shaped_recipe(afL).setEntries(afm, amc).setEntries(alG, alb).setOutput(afL)
    config.shaped_recipe(aho).setEntries(alW, amc).setEntries(aeT, alb).setOutput(aho)
    config.shapeless_recipe(agw).addInput(ams, 1).addInput("ink_sac", 1).addInput(all, 1).setOutput(agw)
    config.shaped_recipe(agq).setEntries(aak, aib).setEntries(alP, amc).setOutput(agq).setGroup(alx)
    config.shaped_recipe(aja).setEntries(abF, aib).setEntries(abI, alb).setOutput(aja).setGroup(amJ)
    config.shapeless_recipe("yellow_bed_from_white_bed").addInput(ajS, 1).addInput(ajr, 1).setOutput(aja).setGroup(akG)
    config.shaped_recipe(agi).setEntries(afd, aib).setOutput(agi).setGroup(alu)
    config.shaped_recipe("yellow_carpet_from_white_carpet").setEntries(aae, agY).setEntries(aly, ajr).setOutput(
        agi).setGroup(alu)
    config.shapeless_recipe(abD).addInput(ajr, 1).addInput(amw, 4).addInput(alN, 4).setOutput(abD).setGroup(aeJ)
    config.shapeless_recipe("yellow_dye_from_dandelion").addInput("dandelion", 1).setOutput(ajr).setGroup(ajr)
    config.shapeless_recipe("yellow_dye_from_sunflower").addInput("sunflower", 1).setOutput(ajr).setGroup(ajr)
    config.smelting_recipe(aaR).add_ingredient(adr).setXp(amP).setOutput(aaR)
    config.shaped_recipe(acB).setEntries(aae, amo).setEntries(aly, ajr).setOutput(acB).setGroup(ags)
    config.shaped_recipe(aaJ).setEntries(aak, acB).setOutput(aaJ).setGroup(ade)
    config.shaped_recipe("yellow_stained_glass_pane_from_glass_pane").setEntries(aae, ajy).setEntries(aly,
                                                                                                      ajr).setOutput(
        aaJ).setGroup(ade)
    config.shaped_recipe(adr).setEntries(aae, aiZ).setEntries(aly, ajr).setOutput(adr).setGroup(acT)
    config.shapeless_recipe(aib).addInput(ajr, 1).addInput(aiV, 1).setOutput(aib).setGroup(amy)
