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
import typing

from mcpython import shared
from mcpython.common.block.Candle import ICandleCake, ICandleGroup
from mcpython.common.block.Carpet import AbstractCarpet
from mcpython.common.block.IFoliageColoredBlock import IFoliageColoredBlock
from mcpython.common.block.IStairs import IStairs
from mcpython.common.container.crafting.GridRecipeInstances import GridShaped
from mcpython.common.container.crafting.StonecuttingRecipe import StoneCuttingRecipe
from mcpython.common.event.DeferredRegistryHelper import DeferredRegistry
from mcpython.common.factory.BlockFactory import BlockFactory
from mcpython.common.factory.combined.simple import CombinedFactoryInstance
from mcpython.util.enums import ToolType

# Missing:
# air
# attached_melon_stem
# attached_pumpkin_stem
# cave air
# command block
# creeper head & wall head
# dragon head
# glass pane
# glow item frame and glow lichen
# heavy_weighted_pressure_plate
# iron door
# iron trapdoor, item frame
# jigsaw block
# light_weighted_pressure_plate
# moving piston, mushroom stem
# powder_snow
# player head, player wall head
# bubble column, chain command block, redstone torch, wall torch
# red mushroom block, repeating command block, scaffolding
# skeleton skull, soul torch, spawner
# structure block, structure void, torch, tripwire, tripwire hook
# turtle egg, twisted vines, vine, void air, weeping vines
# wither skeleton skull, zombie head

DEFERRED_PIPE: DeferredRegistry = shared.registry.get_by_name(
    "minecraft:block"
).create_deferred("minecraft", base_factory=BlockFactory)


def plant(name: str):
    return BlockFactory().set_name(name).set_strength(0).set_flower_like()


def large_plant(name: str):
    return plant(name).set_default_model_state("half=lower")


async def wood(name: str, normal=True, pipe=DEFERRED_PIPE):
    pipe.create_later(
        BlockFactory()
        .set_name(f"minecraft:{name}_button")
        .set_button()
        .set_solid(False)
        .set_all_side_solid(False)
        .set_strength(0.5)
        .set_assigned_tools(ToolType.AXE)
    )

    pipe.create_later(
        BlockFactory()
        .set_name(f"minecraft:{name}_door")
        .set_default_model_state("facing=east,half=upper,hinge=left,open=false")
        .set_solid(False)
        .set_all_side_solid(False)
        .set_strength(0.5)
        .set_assigned_tools(ToolType.AXE)
    )

    pipe.create_later(
        BlockFactory()
        .set_name(f"minecraft:{name}_fence")
        .set_fence()
        .set_strength(0.5)
        .set_assigned_tools(ToolType.AXE)
    )

    pipe.create_later(
        BlockFactory()
        .set_name(f"minecraft:{name}_fence_gate")
        .set_fence_gate()
        .set_strength(0.5)
        .set_assigned_tools(ToolType.AXE)
    )

    pipe.create_later(
        BlockFactory()
        .set_name(f"minecraft:{name}_planks")
        .set_strength(2)
        .set_assigned_tools(ToolType.AXE)
    )
    pipe.create_later(
        BlockFactory()
        .set_name(f"minecraft:{name}_stairs")
        .set_strength(2)
        .set_assigned_tools(ToolType.AXE)
        .add_base_class(IStairs)
    )
    pipe.create_later(
        BlockFactory()
        .set_name(f"minecraft:{name}_pressure_plate")
        .set_default_model_state("powered=false")
        .set_solid(False)
        .set_all_side_solid(False)
        .set_strength(0.5)
        .set_assigned_tools(ToolType.AXE)
    )
    pipe.create_later(
        BlockFactory()
        .set_name(f"minecraft:{name}_slab")
        .set_slab()
        .set_strength(2)
        .set_assigned_tools(ToolType.AXE)
    )

    if normal:
        pipe.create_later(
            BlockFactory()
            .set_name(f"minecraft:{name}_leaves")
            .set_solid(False)
            .set_all_side_solid(False)
            .set_strength(0.2)
            .set_assigned_tools(ToolType.SHEAR)
            .add_base_class(IFoliageColoredBlock)
        )
        pipe.create_later(
            BlockFactory()
            .set_name(f"minecraft:{name}_log")
            .set_log()
            .set_strength(2)
            .set_assigned_tools(ToolType.AXE)
        )
        pipe.create_later(
            BlockFactory()
            .set_name(f"minecraft:stripped_{name}_log")
            .set_log()
            .set_strength(2)
            .set_assigned_tools(ToolType.AXE)
        )
        pipe.create_later(
            BlockFactory().set_name(f"minecraft:{name}_wood").set_log().set_strength(2)
        )
        pipe.create_later(
            BlockFactory()
            .set_name(f"minecraft:stripped_{name}_wood")
            .set_log()
            .set_strength(2)
            .set_assigned_tools(ToolType.AXE)
        )
        pipe.create_later(plant(f"minecraft:{name}_sapling"))
        pipe.create_later(plant(f"minecraft:potted_{name}_sapling"))
    else:
        pipe.create_later(
            BlockFactory().set_name(f"minecraft:{name}_stem").set_log().set_strength(2)
        )
        pipe.create_later(
            BlockFactory()
            .set_name(f"minecraft:stripped_{name}_stem")
            .set_log()
            .set_strength(2)
            .set_assigned_tools(ToolType.AXE)
        )
        pipe.create_later(
            BlockFactory()
            .set_name(f"minecraft:{name}_hyphae")
            .set_log()
            .set_strength(2)
            .set_assigned_tools(ToolType.AXE)
        )
        pipe.create_later(
            BlockFactory()
            .set_name(f"minecraft:stripped_{name}_hyphae")
            .set_log()
            .set_strength(2)
            .set_assigned_tools(ToolType.AXE)
        )

    await CombinedFactoryInstance(
        f"minecraft:{name}_wall",
        f"minecraft:block/{name}_planks",
        block_phase="stage:block:load_late",
    ).create_wall(
        suffix="_wall",
        block_factory_consumer=lambda _, instance: instance.set_strength(
            0.5
        ).set_assigned_tools(ToolType.AXE),
    )

    # todo: signs, stairs


async def stone_like(
    name: str,
    existing_full=True,
    existing_slab=True,
    existing_wall=True,
    existing_stairs=True,
    existing_fence=False,
    existing_button=False,
    existing_pressure_plate=False,
    texture=None,
    consumer=lambda _, __: None,
    strength: typing.Union[float, typing.Tuple[float, float]] = 2,
    tool=ToolType.PICKAXE,
    fname=None,
    deferred=DEFERRED_PIPE,
):
    consumer = (
        lambda _, inst: tool
        == inst.set_strength(strength).set_assigned_tools((tool,))
        == consumer(_, inst)
    )

    if ":" in name:
        modname, name = name.split(":")
    else:
        modname = "minecraft"

    if fname is None:
        fname = name.removesuffix("s")

    instance = CombinedFactoryInstance(
        f"{modname}:{name}",
        f"{modname}:block/{name}" if texture is None else texture,
        block_phase="stage:block:load_late",
    )

    if existing_full:
        obj = BlockFactory().set_name(f"{modname}:{name}")
        consumer(None, obj)
        deferred.create_later(obj)
    else:
        await instance.create_full_block(block_factory_consumer=consumer)

    if existing_slab:
        obj = BlockFactory().set_name(f"{modname}:{fname}_slab").set_slab()
        consumer(None, obj)
        deferred.create_later(obj)
    else:
        await instance.create_slab_block(
            f"{modname}:{fname}_slab", block_factory_consumer=consumer
        )
        shared.tick_handler.schedule_once(
            StoneCuttingRecipe(
                f"{modname}:{name}", f"{modname}:{fname}_slab", 2
            ).prepare_static()
        )
        key = [(f"{modname}:{name}", 1)]
        shared.tick_handler.schedule_once(
            GridShaped(
                {(0, 0): key, (1, 0): key, (2, 0): key}, (f"{modname}:{fname}_slab", 6)
            ).prepare_static()
        )

    if existing_wall:
        obj = BlockFactory().set_name(f"{modname}:{fname}_wall").set_wall()
        consumer(None, obj)
        deferred.create_later(obj)
    else:
        await instance.create_wall(
            f"{modname}:{fname}_wall", block_factory_consumer=consumer
        )
        shared.tick_handler.schedule_once(
            StoneCuttingRecipe(
                f"{modname}:{name}", f"{modname}:{fname}_wall", 6
            ).prepare_static()
        )
        key = [(f"{modname}:{name}", 1)]
        shared.tick_handler.schedule_once(
            GridShaped(
                {
                    (0, 0): key,
                    (1, 0): key,
                    (2, 0): key,
                    (0, 1): key,
                    (1, 1): key,
                    (2, 1): key,
                },
                (f"{modname}:{fname}_wall", 6),
            ).prepare_static()
        )

    if existing_stairs:
        obj = (
            BlockFactory()
            .set_name(f"{modname}:{fname}_stairs")
            .add_base_class(IStairs)
            .set_solid(False)
            .set_all_side_solid(False)
        )
        consumer(None, obj)
        deferred.create_later(obj)
    else:
        pass  # todo: implement

    if existing_fence:
        obj = BlockFactory().set_name(f"{modname}:{fname}_fence").set_fence()
        consumer(None, obj)
        deferred.create_later(obj)
    else:
        await instance.create_fence(
            f"{modname}:{fname}_fence", block_factory_consumer=consumer
        )
        shared.tick_handler.schedule_once(
            StoneCuttingRecipe(
                f"{modname}:{name}", f"{modname}:{fname}_fence"
            ).prepare_static()
        )

    if existing_button:
        deferred.create_later(
            BlockFactory()
            .set_name(f"{modname}:{fname}_button")
            .set_button()
            .set_solid(False)
            .set_all_side_solid(False)
        )
        shared.tick_handler.schedule_once(
            StoneCuttingRecipe(
                f"{modname}:{name}", f"{modname}:{fname}_button", 2
            ).prepare_static()
        )
    else:
        # instance.create_button_block(f"{modname}:{fname}_button", block_factory_consumer=consumer)
        # todo: implement
        pass


async def colored(name: str, pipe=DEFERRED_PIPE):
    pipe.create_later(
        BlockFactory()
        .set_name(f"minecraft:{name}_banner")
        .set_solid(False)
        .set_all_side_solid(False)
    )

    pipe.create_later(
        BlockFactory()
        .set_name(f"minecraft:{name}_bed")
        .set_solid(False)
        .set_all_side_solid(False)
    )

    pipe.create_later(
        BlockFactory()
        .set_name(f"minecraft:{name}_candle")
        .add_base_class(ICandleGroup)
        .set_solid(False)
        .set_all_side_solid(False)
    )

    pipe.create_later(
        BlockFactory()
        .set_name(f"minecraft:{name}_candle_cake")
        .add_base_class(ICandleCake)
        .set_solid(False)
        .set_all_side_solid(False)
    )

    pipe.create_later(
        BlockFactory()
        .set_name(f"minecraft:{name}_carpet")
        .add_base_class(AbstractCarpet)
    )
    shared.tick_handler.schedule_once(
        StoneCuttingRecipe(
            f"minecraft:{name}_wool", f"minecraft:{name}_carpet", 2
        ).prepare_static()
    )

    await stone_like(
        f"{name}_concrete",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
    )

    pipe.create_later(
        BlockFactory().set_name(f"minecraft:{name}_concrete_powder").set_fall_able()
    )

    pipe.create_later(
        BlockFactory()
        .set_name(f"minecraft:{name}_glazed_terracotta")
        .set_default_model_state("facing=east")
    )

    await stone_like(
        f"{name}_stained_glass",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
        consumer=lambda _, factory: factory.set_solid(False).set_all_side_solid(False),
    )

    pipe.create_later(
        BlockFactory().set_name(f"minecraft:{name}_stained_glass_pane").set_fence()
    )

    pipe.create_later(BlockFactory().set_name(f"minecraft:{name}_terracotta"))

    pipe.create_later(
        BlockFactory()
        .set_name(f"minecraft:{name}_wall_banner")
        .set_solid(False)
        .set_all_side_solid(False)
    )

    await stone_like(
        f"{name}_wool",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
        consumer=lambda _, factory: factory.set_solid(False).set_all_side_solid(False),
    )


async def load_blocks(pipe=DEFERRED_PIPE):
    # Technical blocks
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:barrier")
        .set_break_able_flag(False)
        .set_all_side_solid(False)
        .set_solid(False)
    )

    # Wood based
    await wood("acacia")

    # Stone based
    await stone_like("andesite", strength=(1.5, 6), tool=ToolType.PICKAXE)
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:basalt")
        .set_log()
        .set_strength(1.25, 4.2)
        .set_assigned_tools(ToolType.PICKAXE)
    )
    await stone_like(
        "bedrock",
        consumer=lambda _, factory: factory.set_break_able_flag(False),
        strength=(-1, 3600000),
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
    )

    # Value blocks
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:ancient_debris")
        .set_assigned_tools(ToolType.PICKAXE)
        .set_strength(30, 1200)
    )

    await stone_like(
        "amethyst_block",
        tool=ToolType.PICKAXE,
        strength=1.5,
    )
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:amethyst_cluster")
        .set_solid(False)
        .set_all_side_solid(False)
        .set_default_model_state("facing=up")
        .set_assigned_tools(ToolType.PICKAXE)
        .set_strength(1.5)
    )

    # Nature blocks
    pipe.create_later(plant("minecraft:allium"))
    pipe.create_later(plant("minecraft:azure_bluet"))
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:azalea_leaves")
        .set_solid(False)
        .set_all_side_solid(False)
        .set_assigned_tools(ToolType.SHEAR)
        .set_strength(0.2)
    )
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:flowering_azalea_leaves")
        .set_solid(False)
        .set_all_side_solid(False)
        .set_assigned_tools(ToolType.SHEAR)
        .set_strength(0.2)
    )

    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:big_dripleaf")
        .set_default_model_state("facing=east,tilt=none")
        .set_all_side_solid(False)
        .set_solid(False)
        .set_strength(0.1)
        .set_assigned_tools(ToolType.AXE)
    )
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:big_dripleaf_stem")
        .set_default_model_state("facing=south")
        .set_all_side_solid(False)
        .set_solid(False)
        .set_strength(0.1)
        .set_assigned_tools(ToolType.AXE)
    )

    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:beehive")
        .set_default_model_state("facing=east,honey_level=3")
        .set_strength(0.6)
        .set_assigned_tools(ToolType.AXE)
    )
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:bee_nest")
        .set_default_model_state("facing=east,honey_level=2")
        .set_strength(0.3)
        .set_assigned_tools(ToolType.AXE)
    )

    # todo: implement growth
    pipe.create_later(
        plant("minecraft:bamboo").set_default_model_state("age=0,leaves=small")
    )
    pipe.create_later(plant("minecraft:bamboo_sapling"))
    await wood("bamboo", pipe=pipe)
    pipe.create_later(plant("minecraft:beetroots").set_default_model_state("age=2"))

    # Unsorted

    # todo: implement UI
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:beacon")
        .set_all_side_solid(False)
        .set_solid(False)
        .set_strength(3)
    )

    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:bell")
        .set_default_model_state("attachment=ceiling,facing=north")
        .set_all_side_solid(False)
        .set_solid(False)
        .set_strength(5)
        .set_assigned_tools(ToolType.PICKAXE)
    )

    await wood("birch")
    await stone_like("blackstone", existing_fence=False, strength=6)
    await colored("black")
    await colored("blue")
    await stone_like(
        "blue_ice",
        strength=2.8,
        tool=ToolType.PICKAXE,
    )
    pipe.create_later(plant("minecraft:blue_orchid"))
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:bone_block")
        .set_log()
        .set_strength(2.0)
        .set_assigned_tools(ToolType.PICKAXE)
        .set_minimum_tool_level(1)
    )
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:bookshelf")
        .set_strength(1.5)
        .set_assigned_tools(ToolType.AXE)
    )
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:brewing_stand")
        .set_default_model_state(
            "has_bottle_0=false,has_bottle_1=false,has_bottle_2=false"
        )
        .set_solid(False)
        .set_all_side_solid(False)
        .set_strength(0.5)
        .set_assigned_tools(ToolType.PICKAXE)
        .set_minimum_tool_level(1)
    )
    await stone_like(
        "bricks",
        existing_slab=True,
        existing_wall=True,
        existing_stairs=True,
        strength=(6, 2),
    )
    await colored("brown")
    pipe.create_later(plant("minecraft:brown_mushroom"))
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:brown_mushroom_block")
        .set_default_model_state(
            "up=false,down=false,north=false,east=false,south=false,west=false"
        )
        .set_strength(0.2)
        .set_assigned_tools(ToolType.AXE)
    )
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:budding_amethyst")
        .set_strength(1.5)
        .set_assigned_tools(ToolType.PICKAXE)
    )
    pipe.create_later(plant("minecraft:cactus").set_strength(0.4))
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:cake")
        .set_default_model_state("bites=5")
        .set_strength(0.5)
    )
    await stone_like(
        "calcite",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
        strength=0.75,
    )
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:campfire")
        .set_default_model_state("facing=west,lit=true")
        .set_solid(False)
        .set_all_side_solid(False)
        .set_strength(2)
        .set_assigned_tools(ToolType.AXE)
    )
    pipe.create_later(
        BlockFactory().set_name("minecraft:candle").add_base_class(ICandleGroup)
    )
    pipe.create_later(
        BlockFactory().set_name("minecraft:candle_cake").add_base_class(ICandleCake)
    )
    pipe.create_later(plant("minecraft:carrots").set_default_model_state("age=3"))

    # todo: implement
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:cartography_table")
        .set_strength(2.5)
        .set_assigned_tools(ToolType.AXE)
    )

    # todo: emit light
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:carved_pumpkin")
        .set_horizontal_orientable()
        .set_strength(1)
    )

    # todo: add functionality
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:cauldron")
        .set_solid(False)
        .set_all_side_solid(False)
        .set_strength(2)
        .set_assigned_tools(ToolType.PICKAXE)
        .set_minimum_tool_level(1)
    )

    pipe.create_later(
        plant("minecraft:cave_vines").set_default_model_state("berries=false")
    )
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:chain")
        .set_log()
        .set_solid(False)
        .set_all_side_solid(False)
        .set_strength(5, 6)
        .set_assigned_tools(ToolType.PICKAXE)
        .set_minimum_tool_level(1)
    )
    await stone_like(
        "chiseled_deepslate",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
        strength=(3, 6),
        tool=ToolType.PICKAXE,
    )
    await stone_like(
        "chiseled_polished_blackstone",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
        strength=(1.5, 6),
        tool=ToolType.PICKAXE,
    )
    await stone_like(
        "chiseled_quartz_block",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
        strength=0.8,
        tool=ToolType.PICKAXE,
    )
    await stone_like(
        "chiseled_red_sandstone",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
        strength=0.8,
        tool=ToolType.PICKAXE,
    )
    await stone_like(
        "chiseled_sandstone",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
        strength=0.8,
        tool=ToolType.PICKAXE,
    )
    await stone_like(
        "chiseled_stone_bricks",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
        strength=(1.5, 6),
        tool=ToolType.PICKAXE,
    )

    # todo: implement
    pipe.create_later(
        plant("minecraft:chorus_flower")
        .set_default_model_state("age=3")
        .set_strength(0.4)
        .set_assigned_tools(ToolType.AXE)
    )
    pipe.create_later(
        plant("minecraft:chorus_plant")
        .set_default_model_state(
            "north=false,south=false,east=false,west=false,up=false,down=false"
        )
        .set_strength(0.4)
        .set_assigned_tools(ToolType.AXE)
    )

    await stone_like(
        "clay",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
        strength=0.6,
        tool=ToolType.SHOVEL,
    )
    await stone_like(
        "coal_block",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
        strength=(5, 6),
        tool=ToolType.PICKAXE,
    )
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:coal_ore")
        .set_strength(3)
        .set_assigned_tools(ToolType.PICKAXE)
        .set_minimum_tool_level(1)
    )
    await stone_like(
        "coarse_dirt",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
        strength=0.5,
        tool=ToolType.SHOVEL,
    )
    await stone_like(
        "cobbled_deepslate",
        existing_slab=True,
        existing_stairs=True,
        existing_wall=True,
        strength=(3.5, 6),
        tool=ToolType.PICKAXE,
    )
    await stone_like(
        "cobblestone",
        existing_slab=True,
        existing_stairs=True,
        existing_wall=True,
        strength=(2, 6),
        tool=ToolType.PICKAXE,
    )

    # todo: add reduced movement speed
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:cobweb")
        .set_solid(False)
        .set_all_side_solid(False)
        .set_strength(4)
        .set_assigned_tools((ToolType.SHEAR, ToolType.SWORD))
    )

    # todo: implement
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:cocoa")
        .set_default_model_state("age=2,facing=east")
        .set_solid(False)
        .set_all_side_solid(False)
        .set_strength(0.2, 3)
        .set_assigned_tools(ToolType.AXE)
    )
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:comparator")
        .set_default_model_state("facing=north,mode=compare,powered=true")
        .set_solid(False)
        .set_all_side_solid(False)
        .set_strength(0)
    )
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:composter")
        .set_default_model_state("level=2")
        .set_solid(False)
        .set_all_side_solid(False)
        .set_strength(0.6)
        .set_assigned_tools(ToolType.AXE)
    )
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:conduit")
        .set_solid(False)
        .set_all_side_solid(False)
        .set_strength(3)
        .set_assigned_tools(ToolType.PICKAXE)
    )

    await stone_like(
        "copper_block",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
        strength=(3, 6),
    )
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:copper_ore")
        .set_strength(3)
        .set_assigned_tools(ToolType.PICKAXE)
        .set_minimum_tool_level(2)
    )
    pipe.create_later(plant("cornflower"))
    await stone_like(
        "cracked_deepslate_bricks",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
        strength=(3, 6),
    )
    await stone_like(
        "cracked_deepslate_tiles",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
        strength=(3, 6),
    )
    await stone_like(
        "cracked_nether_bricks",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
        strength=(2, 6),
    )
    await stone_like(
        "cracked_polished_blackstone_bricks",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
        strength=(1.5, 6),
    )
    await stone_like(
        "cracked_stone_bricks",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
        strength=(1.5, 6),
    )
    await wood("crimson", normal=False)

    # todo: add hardness values!
    await stone_like(
        "crying_obsidian",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
        strength=(50, 1200),
    )
    await stone_like(
        "cut_copper",
        existing_slab=True,
        existing_stairs=True,
        existing_wall=False,
        strength=(3, 6),
    )
    await stone_like(
        "cut_red_sandstone",
        existing_slab=True,
        existing_stairs=False,
        existing_wall=False,
        strength=0.8,
    )
    await stone_like(
        "cut_sandstone",
        existing_slab=True,
        existing_stairs=False,
        existing_wall=False,
        strength=0.8,
    )
    await colored("cyan")
    pipe.create_later(plant("dandelion"))
    await wood("dark_oak")
    await stone_like(
        "dark_prismarine",
        existing_slab=True,
        existing_stairs=True,
        existing_wall=False,
        strength=(1.5, 6),
    )

    # todo: make functional
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:daylight_detector")
        .set_default_model_state("inverted=false")
        .set_solid(False)
        .set_all_side_solid(False)
        .set_strength(0.2)
        .set_assigned_tools(ToolType.AXE)
    )

    pipe.create_later(BlockFactory().set_name("minecraft:deepslate").set_log())
    await stone_like(
        "deepslate_bricks",
        existing_slab=True,
        existing_stairs=True,
        existing_wall=True,
        strength=(3, 6),
    )
    await stone_like(
        "deepslate_tiles",
        existing_slab=True,
        existing_stairs=True,
        existing_wall=True,
        strength=(3, 6),
    )

    # todo: set tool properties
    pipe.create_later(
        BlockFactory().set_name("minecraft:deepslate_coal_ore").set_strength(4.5, 3)
    )
    pipe.create_later(
        BlockFactory().set_name("minecraft:deepslate_copper_ore").set_strength(4.5, 3)
    )
    pipe.create_later(
        BlockFactory().set_name("minecraft:deepslate_diamond_ore").set_strength(4.5, 3)
    )
    pipe.create_later(
        BlockFactory().set_name("minecraft:deepslate_emerald_ore").set_strength(4.5, 3)
    )
    pipe.create_later(
        BlockFactory().set_name("minecraft:deepslate_gold_ore").set_strength(4.5, 3)
    )
    pipe.create_later(
        BlockFactory().set_name("minecraft:deepslate_iron_ore").set_strength(4.5, 3)
    )
    pipe.create_later(
        BlockFactory().set_name("minecraft:deepslate_lapis_ore").set_strength(4.5, 3)
    )
    pipe.create_later(
        BlockFactory().set_name("minecraft:deepslate_redstone_ore").set_strength(4.5, 3)
    )

    await stone_like(
        "diamond_block",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
        strength=(5, 6),
    )
    pipe.create_later(
        BlockFactory().set_name("minecraft:diamond_ore").set_strength(3, 3)
    )
    await stone_like(
        "diorite",
        existing_slab=True,
        existing_stairs=True,
        existing_wall=True,
        strength=(1.5, 6),
    )
    await stone_like(
        "dirt",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
        strength=(0.5, 0.5),
        tool=ToolType.SHOVEL,
    )
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:dirt_path")
        .set_solid(False)
        .set_all_side_solid(False)
        .set_strength(0.5)
        .set_assigned_tools(ToolType.SHOVEL)
    )

    # todo: make functional
    pipe.create_later(
        BlockFactory().set_name("minecraft:dispenser").set_all_direction_orientable()
    )

    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:dragon_egg")
        .set_solid(False)
        .set_all_side_solid(False)
        .set_fall_able()
        .set_strength(3, 9)
    )
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:dried_kelp_block")
        .set_strength(0.5, 2.5)
        .set_assigned_tools(ToolType.HOE)
    )
    await stone_like(
        "dripstone_block",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
        strength=(1, 1.5),
    )

    # todo: make functional
    pipe.create_later(
        BlockFactory().set_name("minecraft:dropper").set_all_direction_orientable()
    )

    await stone_like(
        "emerald_block", existing_slab=False, existing_stairs=False, existing_wall=False
    )
    pipe.create_later(BlockFactory().set_name("minecraft:emerald_ore"))

    # todo: implement
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:enchanting_table")
        .set_solid(False)
        .set_all_side_solid(False)
        .set_strength(3)
        .set_assigned_tools(ToolType.PICKAXE)
        .set_minimum_tool_level(3)
    )
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:end_gateway")
        .set_solid(False)
        .set_all_side_solid(False)
        .set_break_able_flag(False)
        .set_strength(-1, 3600000)
    )
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:end_portal")
        .set_solid(False)
        .set_all_side_solid(False)
        .set_break_able_flag(False)
        .set_strength(-1, 3600000)
    )
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:end_portal_frame")
        .set_default_model_state("eye=false,facing=south")
        .set_solid(False)
        .set_all_side_solid(False)
        .set_break_able_flag(False)
        .set_strength(-1, 3600000)
    )

    # todo: emit light
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:end_rod")
        .set_all_direction_orientable()
        .set_solid(False)
        .set_all_side_solid(False)
    )

    await stone_like(
        "end_stone", existing_slab=False, existing_stairs=False, existing_wall=False
    )
    await stone_like(
        "end_stone_bricks", existing_slab=True, existing_stairs=True, existing_wall=True
    )
    await stone_like(
        "exposed_copper",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
    )
    await stone_like(
        "exposed_cut_copper",
        existing_slab=True,
        existing_stairs=True,
        existing_wall=False,
    )

    # todo: implement crop interaction
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:farmland")
        .set_default_model_state("moisture=0")
        .set_solid(False)
        .set_all_side_solid(False)
    )

    pipe.create_later(plant("minecraft:fern").add_base_class(IFoliageColoredBlock))

    # todo: set player on fire
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:fire")
        .set_default_model_state("north=false,east=false,west=false,south=false")
        .set_solid(False)
        .set_all_side_solid(False)
    )

    pipe.create_later(BlockFactory().set_name("minecraft:fletching_table"))
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:flowering_azalea")
        .set_solid(False)
        .set_all_side_solid(False)
    )

    # todo: implement interaction
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:flower_pot")
        .set_solid(False)
        .set_all_side_solid(False)
    )

    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:frosted_ice")
        .set_default_model_state("age=1")
        .set_solid(False)
        .set_all_side_solid(False)
    )
    await stone_like(
        "gilded_blackstone",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
    )
    await stone_like(
        "glass",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
        consumer=lambda _, factory: factory.set_solid(False).set_all_side_solid(False),
    )
    pipe.create_later(BlockFactory().set_name(f"minecraft:glass_pane").set_fence())
    await stone_like(
        "glowstone", existing_slab=False, existing_stairs=False, existing_wall=False
    )
    await stone_like(
        "gold_block", existing_slab=False, existing_stairs=False, existing_wall=False
    )
    pipe.create_later(BlockFactory().set_name("minecraft:gold_ore"))
    await stone_like(
        "granite", existing_slab=True, existing_stairs=True, existing_wall=True
    )
    pipe.create_later(plant("grass").add_base_class(IFoliageColoredBlock))
    pipe.create_later(BlockFactory().set_name("minecraft:gravel").set_fall_able())
    await colored("gray")
    await colored("green")

    # todo: make functional
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:grindstone")
        .set_all_side_solid(False)
        .set_solid(False)
        .set_default_model_state("face=ceiling,facing=north")
    )

    pipe.create_later(BlockFactory().set_name("minecraft:hanging_roots"))
    pipe.create_later(BlockFactory().set_name("minecraft:hay_block").set_log())
    await stone_like(
        "honeycomb_block",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
    )

    # todo: add properties
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:honey_block")
        .set_all_side_solid(False)
        .set_solid(False)
    )

    # todo: create real block behaviour
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:hopper")
        .set_all_side_solid(False)
        .set_solid(False)
        .set_default_model_state("facing=east")
    )

    # todo: melting
    await stone_like("ice")

    # todo: add infection
    await stone_like(
        "infested_chiseled_stone_bricks",
        texture="minecraft:block/chiseled_stone_bricks",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
    )
    await stone_like(
        "infested_cobblestone",
        texture="minecraft:block/cobblestone",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
    )
    await stone_like(
        "infested_cracked_stone_bricks",
        texture="minecraft:block/cracked_stone_bricks",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
    )
    pipe.create_later(BlockFactory().set_name("minecraft:infested_deepslate").set_log())
    await stone_like(
        "infested_mossy_stone_bricks",
        texture="minecraft:block/mossy_stone_bricks",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
    )
    await stone_like(
        "infested_stone",
        texture="minecraft:block/stone",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
    )
    await stone_like(
        "infested_stone_bricks",
        texture="minecraft:block/stone_bricks",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
    )

    pipe.create_later(BlockFactory().set_name("minecraft:iron_bars").set_fence())
    await stone_like("iron_block")
    pipe.create_later(BlockFactory().set_name("minecraft:iron_ore"))
    pipe.create_later(
        BlockFactory().set_name("minecraft:jack_o_lantern").set_horizontal_orientable()
    )

    # todo: make functional
    pipe.create_later(BlockFactory().set_name("minecraft:jukebox"))

    await wood("jungle")
    pipe.create_later(plant("minecraft:kelp"))
    pipe.create_later(plant("minecraft:kelp_plant"))

    # todo: make functional
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:ladder")
        .set_horizontal_orientable()
        .set_all_side_solid(False)
        .set_solid(False)
    )

    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:lantern")
        .set_default_model_state("hanging=false")
        .set_all_side_solid(False)
        .set_solid(False)
    )
    await stone_like(
        "lapis_block", existing_slab=False, existing_stairs=False, existing_wall=False
    )
    pipe.create_later(BlockFactory().set_name("minecraft:lapis_ore"))
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:large_amethyst_bud")
        .set_all_direction_orientable()
    )
    pipe.create_later(
        large_plant("minecraft:large_fern").add_base_class(IFoliageColoredBlock)
    )

    # todo: make functional
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:lava_cauldron")
        .set_solid(False)
        .set_all_side_solid(False)
    )
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:lectern")
        .set_horizontal_orientable()
        .set_solid(False)
        .set_all_side_solid(False)
    )
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:lever")
        .set_default_model_state("face=ceiling,facing=north,powered=false")
        .set_all_side_solid(False)
        .set_solid(False)
    )

    # todo: lightning rod with lightning
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:lightning_rod")
        .set_default_model_state("facing=west,powered=false")
        .set_all_side_solid(False)
        .set_solid(False)
    )

    await colored("light_blue")
    await colored("light_gray")
    pipe.create_later(large_plant("minecraft:lilac"))
    pipe.create_later(plant("minecraft:lily_of_the_valley"))
    pipe.create_later(plant("minecraft:lily_pad"))
    await colored("lime")

    # todo: implement
    pipe.create_later(BlockFactory().set_name("minecraft:lodestone"))
    pipe.create_later(
        BlockFactory().set_name("minecraft:loom").set_horizontal_orientable()
    )

    await colored("magenta")

    # todo: add damage
    await stone_like(
        "magma_block",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
        texture="minecraft:block/magma",
    )

    await wood("mangrove", pipe=pipe)

    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:medium_amethyst_bud")
        .set_all_direction_orientable()
    )
    pipe.create_later(BlockFactory().set_name("minecraft:melon"))
    pipe.create_later(plant("minecraft:melon_stem").set_default_model_state("age=7"))
    await stone_like(
        "mossy_cobblestone",
        existing_slab=True,
        existing_stairs=True,
        existing_wall=True,
    )
    await stone_like(
        "mossy_stone_bricks",
        existing_slab=True,
        existing_stairs=True,
        existing_wall=True,
    )
    await stone_like(
        "moss_block", existing_slab=False, existing_stairs=False, existing_wall=False
    )
    pipe.create_later(
        BlockFactory().set_name("minecraft:moss_carpet").add_base_class(AbstractCarpet)
    )

    await stone_like("mud", existing_slab=False, existing_stairs=False, existing_wall=False)
    await stone_like("mud_bricks")

    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:mycelium")
        .set_default_model_state("snowy=false")
    )
    await stone_like(
        "netherite_block",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
    )
    await stone_like(
        "netherrack", existing_slab=False, existing_stairs=False, existing_wall=False
    )
    await stone_like(
        "nether_bricks", existing_slab=True, existing_stairs=True, existing_wall=True
    )
    pipe.create_later(BlockFactory().set_name("minecraft:nether_gold_ore"))
    pipe.create_later(BlockFactory().set_name("minecraft:nether_quartz_ore"))
    pipe.create_later(plant("minecraft:nether_sprouts"))
    pipe.create_later(plant("minecraft:nether_wart").set_default_model_state("age=2"))
    await stone_like(
        "nether_wart_block",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
    )

    # todo: make functional
    pipe.create_later(BlockFactory().set_name("minecraft:note_block"))

    await wood("oak")
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:observerer")
        .set_default_model_state("facing=north,powered=false")
    )
    await stone_like(
        "obsidian", existing_slab=False, existing_stairs=False, existing_wall=False
    )
    await colored("orange")
    pipe.create_later(plant("minecraft:oxeye_daisy"))
    await stone_like(
        "oxidized_copper",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
    )
    await stone_like(
        "oxidized_cut_copper",
        existing_slab=True,
        existing_stairs=True,
        existing_wall=False,
    )
    await stone_like(
        "packed_ice", existing_slab=False, existing_stairs=False, existing_wall=False
    )
    await stone_like("packed_mud", existing_slab=False, existing_stairs=False, existing_wall=False)
    pipe.create_later(large_plant("minecraft:peony"))
    pipe.create_later(
        BlockFactory().set_name("minecraft:petrified_oak_slab").set_slab()
    )
    await colored("pink")
    pipe.create_later(plant("minecraft:pink_tulip"))
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:podzol")
        .set_default_model_state("snowy=false")
    )
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:pointed_dripstone")
        .set_default_model_state("thickness=middle,vertical_direction=up")
    )
    await stone_like(
        "polished_andesite",
        existing_slab=True,
        existing_stairs=True,
        existing_wall=False,
    )
    pipe.create_later(BlockFactory().set_name("minecraft:polished_basalt").set_log())
    await stone_like(
        "polished_blackstone",
        existing_slab=True,
        existing_stairs=True,
        existing_wall=True,
        existing_button=True,
        existing_pressure_plate=True,
    )
    await stone_like(
        "polished_blackstone_bricks",
        existing_slab=True,
        existing_stairs=True,
        existing_wall=True,
    )
    await stone_like(
        "polished_deepslate",
        existing_slab=True,
        existing_stairs=True,
        existing_wall=True,
    )
    await stone_like(
        "polished_diorite",
        existing_slab=True,
        existing_stairs=True,
        existing_wall=False,
    )
    await stone_like(
        "polished_granite",
        existing_slab=True,
        existing_stairs=True,
        existing_wall=False,
    )
    pipe.create_later(plant("minecraft:poppy"))
    pipe.create_later(plant("minecraft:potatoes").set_default_model_state("age=4"))

    # todo: some clever stuff with flower pot
    pipe.create_later(plant("minecraft:potted_allium"))
    pipe.create_later(plant("minecraft:potted_azalea_bush"))
    pipe.create_later(plant("minecraft:potted_azure_bluet"))
    pipe.create_later(plant("minecraft:potted_bamboo"))
    pipe.create_later(plant("minecraft:potted_blue_orchid"))
    pipe.create_later(plant("minecraft:potted_brown_mushroom"))
    pipe.create_later(plant("minecraft:potted_cactus"))
    pipe.create_later(plant("minecraft:potted_cornflower"))
    pipe.create_later(plant("minecraft:potted_crimson_fungus"))
    pipe.create_later(plant("minecraft:potted_crimson_roots"))
    pipe.create_later(plant("minecraft:potted_dandelion"))
    pipe.create_later(plant("minecraft:potted_dead_bush"))
    pipe.create_later(plant("minecraft:potted_fern"))
    pipe.create_later(plant("minecraft:potted_flowering_azalea_bush"))
    pipe.create_later(plant("minecraft:potted_lily_of_the_valley"))
    pipe.create_later(plant("minecraft:potted_orange_tulip"))
    pipe.create_later(plant("minecraft:potted_pink_tulip"))
    pipe.create_later(plant("minecraft:potted_oxeye_daisy"))
    pipe.create_later(plant("minecraft:potted_pink_tulip"))
    pipe.create_later(plant("minecraft:potted_poppy"))
    pipe.create_later(plant("minecraft:potted_red_mushroom"))
    pipe.create_later(plant("minecraft:potted_red_tulip"))
    pipe.create_later(plant("minecraft:potted_warped_fungus"))
    pipe.create_later(plant("minecraft:potted_warped_roots"))
    pipe.create_later(plant("minecraft:potted_white_tulip"))
    pipe.create_later(plant("minecraft:potted_wither_rose"))

    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:powder_snow_cauldron")
        .set_solid(False)
        .set_all_side_solid(False)
        .set_default_model_state("level=2")
    )
    await stone_like(
        "prismarine", existing_slab=True, existing_stairs=True, existing_wall=True
    )
    await stone_like(
        "prismarine_bricks",
        existing_slab=True,
        existing_stairs=True,
        existing_wall=False,
    )
    pipe.create_later(BlockFactory().set_name("minecraft:pumpkin"))
    pipe.create_later(plant("minecraft:pumpkin_stem").set_default_model_state("age=2"))
    await colored("purple")
    await stone_like(
        "purpur_block",
        existing_slab=True,
        existing_stairs=True,
        existing_wall=False,
        fname="purpur",
    )
    pipe.create_later(BlockFactory().set_name("minecraft:purpur_pillar").set_log())
    pipe.create_later(BlockFactory().set_name("minecraft:quartz_block"))
    await stone_like(
        "quartz_bricks", existing_slab=False, existing_stairs=False, existing_wall=False
    )
    pipe.create_later(BlockFactory().set_name("minecraft:quartz_pillar").set_log())
    pipe.create_later(BlockFactory().set_name("minecraft:quartz_slab").set_slab())
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:quartz_stairs")
        .set_default_model_state("facing=east,half=bottom,shape=inner_left")
        .set_solid(False)
        .set_all_side_solid(False)
    )
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:rail")
        .set_default_model_state("shape=east_west")
        .set_solid(False)
        .set_all_side_solid(False)
    )
    await stone_like(
        "raw_copper_block",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
    )
    await stone_like(
        "raw_gold_block",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
    )
    await stone_like(
        "raw_iron_block",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
    )
    # await stone_like(
    #     "redstone_block",
    #     existing_slab=False,
    #     existing_stairs=False,
    #     existing_wall=False,
    # )
    # pipe.create_later(
    #     BlockFactory()
    #     .set_name("minecraft:redstone_lamp")
    #     .set_default_model_state("lit=false")
    # )
    pipe.create_later(BlockFactory().set_name("minecraft:redstone_ore"))
    await colored("red")
    pipe.create_later(plant("minecraft:red_mushroom"))
    await stone_like(
        "red_nether_bricks",
        existing_slab=True,
        existing_stairs=True,
        existing_wall=True,
    )
    pipe.create_later(BlockFactory().set_name("minecraft:red_sand").set_fall_able())
    await stone_like(
        "red_sandstone", existing_slab=True, existing_stairs=True, existing_wall=True
    )
    pipe.create_later(plant("minecraft:red_tulip"))
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:respawn_anchor")
        .set_default_model_state("charges=2")
    )
    pipe.create_later(BlockFactory().set_name("minecraft:rooted_dirt"))
    pipe.create_later(large_plant("minecraft:rose_bush"))
    pipe.create_later(BlockFactory().set_name("minecraft:sand").set_fall_able())
    await stone_like(
        "sandstone", existing_slab=True, existing_stairs=True, existing_wall=True
    )
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:sculk_sensor")
        .set_default_model_state("sculk_sensor_phase=inactive")
        .set_solid(False)
        .set_all_side_solid(False)
    )
    pipe.create_later(plant("minecraft:seagrass"))
    await stone_like(
        "sea_lantern", existing_slab=False, existing_stairs=False, existing_wall=False
    )
    pipe.create_later(
        plant("minecraft:sea_pickle").set_default_model_state(
            "pickles=1,waterlogged=true"
        )
    )
    await stone_like(
        "shroomlight", existing_slab=False, existing_stairs=False, existing_wall=False
    )
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:slime_block")
        .set_solid(False)
        .set_all_side_solid(False)
    )
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:small_amethyst_bud")
        .set_all_direction_orientable()
    )
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:small_dripleaf")
        .set_default_model_state("facing=north,half=upper")
        .set_solid(False)
        .set_all_side_solid(False)
    )
    pipe.create_later(BlockFactory().set_name("minecraft:smithing_table"))
    await stone_like(
        "smooth_basalt", existing_slab=False, existing_stairs=False, existing_wall=False
    )
    await stone_like(
        "smooth_quartz",
        existing_slab=True,
        existing_stairs=True,
        existing_wall=False,
        texture="minecraft:block/quartz_block_bottom",
    )
    await stone_like(
        "smooth_red_sandstone",
        existing_slab=True,
        existing_stairs=True,
        existing_wall=False,
        texture="minecraft:block/red_sandstone_top",
    )
    await stone_like(
        "smooth_sandstone",
        existing_slab=True,
        existing_stairs=True,
        existing_wall=False,
        texture="minecraft:block/sandstone_top",
    )
    await stone_like(
        "smooth_stone", existing_slab=True, existing_stairs=False, existing_wall=False
    )
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:snow")
        .set_default_model_state("layers=7")
        .set_solid(False)
        .set_all_side_solid(False)
    )
    pipe.create_later(BlockFactory().set_name("minecraft:snow_block"))
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:soul_campfire")
        .set_default_model_state("facing=west,lit=true")
        .set_solid(False)
        .set_all_side_solid(False)
    )
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:soul_fire")
        .set_default_model_state("north=false,east=false,west=false,south=false")
        .set_solid(False)
        .set_all_side_solid(False)
    )
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:soul_lantern")
        .set_default_model_state("hanging=false")
        .set_all_side_solid(False)
        .set_solid(False)
    )
    await stone_like(
        "soul_sand", existing_slab=False, existing_stairs=False, existing_wall=False
    )
    await stone_like(
        "soul_soil", existing_slab=False, existing_stairs=False, existing_wall=False
    )
    pipe.create_later(BlockFactory().set_name("minecraft:sponge"))
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:spore_blossom")
        .set_solid(False)
        .set_all_side_solid(False)
    )
    await wood("spruce")
    await stone_like(
        "stone",
        existing_slab=True,
        existing_stairs=True,
        existing_wall=False,
        existing_button=True,
        existing_pressure_plate=True,
    )
    await stone_like(
        "stone_bricks", existing_slab=True, existing_stairs=True, existing_wall=True
    )
    pipe.create_later(plant("minecraft:sugar_cane"))
    pipe.create_later(large_plant("minecraft:sunflower"))
    pipe.create_later(
        plant("minecraft:sweet_berry_bush").set_default_model_state("age=2")
    )
    pipe.create_later(
        large_plant("minecraft:tall_grass").add_base_class(IFoliageColoredBlock)
    )
    pipe.create_later(large_plant("minecraft:tall_seagrass"))
    pipe.create_later(BlockFactory().set_name("minecraft:target"))
    await stone_like(
        "terracotta", existing_slab=False, existing_stairs=False, existing_wall=False
    )
    await stone_like(
        "tinted_glass",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
        consumer=lambda _, factory: factory.set_solid(False).set_all_side_solid(False),
    )
    pipe.create_later(BlockFactory().set_name("minecraft:tnt"))
    await stone_like(
        "tuff",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
        consumer=lambda _, factory: factory.set_hardness(1.5, 6),
    )
    await wood("warped", normal=False)
    pipe.create_later(plant("minecraft:warped_fungus"))
    pipe.create_later(BlockFactory().set_name("minecraft:warped_nylium"))
    pipe.create_later(plant("minecraft:warped_roots"))
    await stone_like(
        "warped_wart_block",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
    )
    pipe.create_later(
        BlockFactory()
        .set_name("minecraft:water_cauldron")
        .set_default_model_state("level=2")
        .set_solid(False)
        .set_all_side_solid(False)
    )
    await stone_like(
        "waxed_copper_block",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
        texture="minecraft:block/copper_block",
    )
    await stone_like(
        "waxed_cut_copper",
        existing_slab=True,
        existing_stairs=True,
        existing_wall=False,
        texture="minecraft:block/cut_copper",
    )
    await stone_like(
        "waxed_exposed_copper",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
        texture="minecraft:block/exposed_copper",
    )
    await stone_like(
        "waxed_exposed_cut_copper",
        existing_slab=True,
        existing_stairs=True,
        existing_wall=False,
        texture="minecraft:block/exposed_cut_copper",
    )
    await stone_like(
        "waxed_oxidized_copper",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
        texture="minecraft:block/oxidized_copper",
    )
    await stone_like(
        "waxed_oxidized_cut_copper",
        existing_slab=True,
        existing_stairs=True,
        existing_wall=False,
        texture="minecraft:block/oxidized_cut_copper",
    )
    await stone_like(
        "waxed_weathered_copper",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
        texture="minecraft:block/weathered_copper",
    )
    await stone_like(
        "waxed_weathered_cut_copper",
        existing_slab=True,
        existing_stairs=True,
        existing_wall=False,
        texture="minecraft:block/weathered_cut_copper",
    )
    await stone_like(
        "weathered_copper",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
    )
    await stone_like(
        "weathered_cut_copper",
        existing_slab=True,
        existing_stairs=True,
        existing_wall=False,
    )
    pipe.create_later(BlockFactory().set_name("minecraft:wet_sponge"))
    pipe.create_later(plant("minecraft:wheat").set_default_model_state("age=3"))
    await colored("white")
    pipe.create_later(plant("minecraft:white_tulip"))
    pipe.create_later(plant("minecraft:wither_rose"))
    await colored("yellow")
