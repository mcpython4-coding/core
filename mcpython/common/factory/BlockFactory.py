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
import pickle
import typing

import mcpython.common.block.AbstractBlock
import mcpython.common.block.BlockWall as BlockWall
import mcpython.common.block.BoundingBox
import mcpython.common.block.IFallingBlock as FallingBlock
import mcpython.common.block.IHorizontalOrientableBlock as IHorizontalOrientableBlock
import mcpython.common.block.ILog as ILog
import mcpython.common.block.ISlab as ISlab
import mcpython.common.block.BlockFence as BlockFence
import mcpython.common.container.ItemStack
import mcpython.common.factory.FactoryBuilder
import mcpython.common.factory.IFactoryModifier
import mcpython.util.enums
from mcpython.common.factory.FactoryBuilder import FactoryBuilder

block_factory_builder = FactoryBuilder(
    "minecraft:block", mcpython.common.block.AbstractBlock.AbstractBlock
)


block_factory_builder.register_configurator(
    FactoryBuilder.SetterFactoryConfigurator("set_name", "name", str)
)
block_factory_builder.register_configurator(
    FactoryBuilder.SetterFactoryConfigurator("set_global_mod_name", "global_name", str)
)


@block_factory_builder.register_configurator(
    FactoryBuilder.AnnotationFactoryConfigurator("set_log")
)
def set_log(instance: FactoryBuilder.IFactory):
    instance.base_classes.append(ILog.ILog)
    return instance


@block_factory_builder.register_configurator(
    FactoryBuilder.AnnotationFactoryConfigurator("set_fall_able")
)
def set_fall_able(instance: FactoryBuilder.IFactory):
    instance.base_classes.append(FallingBlock.IFallingBlock)
    return instance


@block_factory_builder.register_configurator(
    FactoryBuilder.AnnotationFactoryConfigurator("set_slab")
)
def set_slab(instance: FactoryBuilder.IFactory):
    instance.base_classes.append(ISlab.ISlab)
    return instance


@block_factory_builder.register_configurator(
    FactoryBuilder.AnnotationFactoryConfigurator("set_wall")
)
def set_wall(instance: FactoryBuilder.IFactory):
    instance.base_classes.append(BlockWall.IWall)
    return instance


@block_factory_builder.register_configurator(
    FactoryBuilder.AnnotationFactoryConfigurator("set_fence")
)
def set_fence(instance: FactoryBuilder.IFactory, *types: str):
    instance.base_classes.append(BlockFence.IFence)
    instance.config_table["fence_type_name"] = set(types) if len(types) > 0 else {"minecraft:wooden_fence"}
    instance.set_solid(False).set_all_side_solid(False)
    return instance


@block_factory_builder.register_configurator(
    FactoryBuilder.AnnotationFactoryConfigurator("set_horizontal_orientable")
)
def set_horizontal_orientable(instance: FactoryBuilder.IFactory):
    instance.base_classes.append(IHorizontalOrientableBlock.IHorizontalOrientableBlock)
    return instance


@block_factory_builder.register_configurator(
    FactoryBuilder.AnnotationFactoryConfigurator("set_strength")
)
def set_strength(
    instance: FactoryBuilder.IFactory, hardness: float, blast_resistance: float = None
):
    instance.config_table["hardness"] = hardness
    instance.config_table["blast_resistance"] = blast_resistance
    return instance


@block_factory_builder.register_configurator(
    FactoryBuilder.AnnotationFactoryConfigurator("set_assigned_tools")
)
def set_assigned_tools(instance: FactoryBuilder.IFactory, *tools, tool_level=None):
    if len(tools) == 1:
        if type(tools[0]) in (list, tuple):
            tools = tools[0]
        else:
            tools = (tools,)
    instance.config_table["assigned_tools"] = tools
    if tool_level is not None:
        instance.set_minimum_tool_level(tool_level)
    return instance


@block_factory_builder.register_configurator(
    FactoryBuilder.AnnotationFactoryConfigurator("set_all_side_solid")
)
def set_all_side_solid(instance: FactoryBuilder.IFactory, solid: bool):
    instance.config_table["solid_face_table"] = (
        mcpython.common.block.AbstractBlock.AbstractBlock.DEFAULT_FACE_SOLID
        if solid
        else mcpython.common.block.AbstractBlock.AbstractBlock.UNSOLID_FACE_SOLID
    )
    return instance


@block_factory_builder.register_configurator(
    FactoryBuilder.AnnotationFactoryConfigurator("set_default_model_state")
)
def set_default_model_state(
    instance: FactoryBuilder.IFactory, state: typing.Union[dict, str]
):
    if type(state) == str:
        state = {
            e.split("=")[0].strip(): e.split("=")[1].strip() for e in state.split(",")
        }

    instance.config_table["default_model_state"] = state
    return instance


@block_factory_builder.register_class_builder(
    FactoryBuilder.AnnotationFactoryClassBuilder()
)
def build_class(
    cls: typing.Type[mcpython.common.block.AbstractBlock.AbstractBlock],
    instance: FactoryBuilder.IFactory,
):
    configs = instance.config_table

    name = configs["name"]
    if ":" not in name and "global_name" in configs:
        name = configs["global_name"] + ":" + name

    class ModifiedClass(cls):
        NAME = name
        HARDNESS = configs.setdefault("hardness", cls.HARDNESS)
        BLAST_RESISTANCE = configs.setdefault("blast_resistance", cls.BLAST_RESISTANCE)

        MINIMUM_TOOL_LEVEL = configs.setdefault(
            "minimum_tool_level", cls.MINIMUM_TOOL_LEVEL
        )
        ASSIGNED_TOOLS = configs.setdefault("assigned_tools", cls.ASSIGNED_TOOLS)

        IS_BREAKABLE = configs.setdefault("break_able_flag", cls.IS_BREAKABLE)

        DEFAULT_FACE_SOLID = configs.setdefault(
            "solid_face_table", cls.DEFAULT_FACE_SOLID
        )

        CUSTOM_WALING_SPEED_MULTIPLIER = configs.setdefault(
            "speed_multiplier", cls.CUSTOM_WALING_SPEED_MULTIPLIER
        )

        BLOCK_ITEM_GENERATOR_STATE = configs.setdefault(
            "block_item_generator_state", cls.BLOCK_ITEM_GENERATOR_STATE
        )

        IS_SOLID = configs.setdefault("solid", cls.IS_SOLID)

        CAN_CONDUCT_REDSTONE_POWER = configs.setdefault(
            "can_conduct_redstone_power", cls.CAN_CONDUCT_REDSTONE_POWER
        )

        CAN_MOBS_SPAWN_ON = configs.setdefault(
            "can_mobs_spawn_on", cls.CAN_MOBS_SPAWN_ON
        )
        CAN_MOBS_SPAWN_IN = configs.setdefault(
            "can_mobs_spawn_in", cls.CAN_MOBS_SPAWN_IN
        )

        ENABLE_RANDOM_TICKS = configs.setdefault(
            "enable_random_ticks", cls.ENABLE_RANDOM_TICKS
        ) or len(configs["on_random_update"])

        NO_ENTITY_COLLISION = configs.setdefault(
            "no_entity_collision", cls.NO_ENTITY_COLLISION
        )
        ENTITY_FALL_MULTIPLIER = configs.setdefault(
            "entity_fall_multiplier", cls.ENTITY_FALL_MULTIPLIER
        )

        DEBUG_WORLD_BLOCK_STATES = configs.setdefault(
            "debug_world_states", cls.DEBUG_WORLD_BLOCK_STATES
        )

        FENCE_TYPE_NAME = configs.setdefault(
            "fence_type_name", tuple()
        )

    return ModifiedClass


@block_factory_builder.register_class_builder(
    FactoryBuilder.AnnotationFactoryClassBuilder()
)
def build_class_default_state(
    cls: typing.Type[mcpython.common.block.AbstractBlock.AbstractBlock],
    instance: FactoryBuilder.IFactory,
):
    if "default_model_state" not in instance.config_table:
        return cls

    is_super_base = any([base == cls for base in instance.master.base_classes])
    bases = instance.master.base_classes
    configs = instance.config_table

    class ModifiedClass(cls):
        def __init__(self):
            if not is_super_base:
                super().__init__()

            for base in bases:
                base.__init__(self)

            for function in configs["on_instance_creation"]:
                function(self)

        def set_creation_properties(self, *args, **kwargs):
            if not is_super_base:
                super().set_creation_properties(*args, **kwargs)

            for base in bases:
                base.set_creation_properties(self, *args, **kwargs)

            for function in configs["on_properties_set"]:
                function(self)

        def on_block_added(self, *args, **kwargs):
            if not is_super_base:
                super().on_block_added(*args, **kwargs)

            for base in bases:
                base.on_block_added(self, *args, **kwargs)

            for function in configs["on_block_added"]:
                function(self)

        def on_block_remove(self, *args, **kwargs):
            if not is_super_base:
                super().on_block_remove(*args, **kwargs)

            for base in bases:
                base.on_block_remove(self, *args, **kwargs)

            for function in configs["on_block_remove"]:
                function(self, *args, **kwargs)

        def on_random_update(self, *args, **kwargs):
            if not is_super_base:
                super().on_random_update(*args, **kwargs)

            for base in bases:
                base.on_random_update(self, *args, **kwargs)

            for function in configs["on_random_update"]:
                function(self)

        def on_block_update(self, *args, **kwargs):
            if not is_super_base:
                super().on_block_update(*args, **kwargs)

            for base in bases:
                base.on_block_update(self, *args, **kwargs)

            for function in configs["on_block_update"]:
                function(self)

            self.on_redstone_update()

        def on_redstone_update(self, *args, **kwargs):
            if not is_super_base:
                super().on_redstone_update(*args, **kwargs)

            for base in bases:
                base.on_redstone_update(self, *args, **kwargs)

            for function in configs["on_redstone_update"]:
                function(self)

        def on_player_interaction(self, *args, **kwargs):
            for function in configs["on_player_interaction"]:
                if not function(self, *args, **kwargs):
                    return True

            if not is_super_base:
                if super().on_player_interaction(*args, **kwargs):
                    return True

            for base in bases:
                if base.on_player_interaction(self, *args, **kwargs):
                    return True

            return False

        def on_no_collision_collide(self, *args, **kwargs):
            if not is_super_base:
                super().on_no_collision_collide(*args, **kwargs)

            for base in bases:
                base.on_no_collision_collide(self, *args, **kwargs)

            for function in configs["on_no_collision_collide"]:
                function(self, *args, **kwargs)

        def get_save_data(self):
            if len(configs["get_save_data"]) > 0:
                return configs["get_save_data"][-1](self)

            if not is_super_base:
                return super().get_save_data()
            if len(bases) > 0:
                return bases[-1].get_save_data(self)
            return self.get_model_state()

        def dump_data(self):
            if len(configs["dump_data"]) > 0:
                return configs["dump_data"][-1](self)

            if not is_super_base:
                return super().dump_data()
            if len(bases) > 0:
                return bases[-1].dump_data(self)
            return pickle.dumps(self.get_save_data())

        def load_data(self, data):
            if len(configs["load_data"]) > 0:
                return configs["load_data"][-1](self, data)

            if not is_super_base:
                return super().load_data(data)
            if len(bases) > 0:
                return bases[-1].load_data(self, data)

            self.set_model_state(data)

        def inject(self, data: bytes):
            if len(configs["on_data_inject"]) > 0:
                return configs["on_data_inject"][-1](self, data)

            if not is_super_base:
                return super().inject(data)
            if len(bases) > 0:
                return bases[-1].inject(self, data)

            self.load_data(pickle.loads(data) if type(data) == bytes else data)

        def get_item_saved_state(self):
            if len(configs["get_item_save_data"]) > 0:
                return configs["get_item_save_data"][-1](self)

            if not is_super_base:
                return super().get_item_saved_state()
            if len(bases) > 0:
                return bases[-1].get_item_saved_state(self)

        def set_item_saved_state(self, state):
            if len(configs["set_item_saved_data"]) > 0:
                return configs["set_item_saved_data"][-1](self, state)

            if not is_super_base:
                return super().set_item_saved_state(state)
            if len(bases) > 0:
                return bases[-1].set_item_saved_state(self, state)

        def get_inventories(self):
            inventories = []
            if not is_super_base:
                inventories += super().get_inventories()
            for base in bases:
                inventories += base.get_inventories(self)
            for function in configs["get_inventories"]:
                inventories += function(self)
            return inventories

        def get_provided_slot_lists(self, side: mcpython.util.enums.EnumSide):
            a, b = [], []
            if not is_super_base:
                x, y = super().get_provided_slot_lists(side)
                a += x
                b += y
            for base in bases:
                x, y = base.get_provided_slot_lists(side)
                a += x
                b += y
            for function in configs["get_provided_slot_lists"]:
                x, y = function(self, side)
                a += x
                b += y
            return a, b

        def get_model_state(self) -> dict:
            state = {}
            if not is_super_base:
                state.update(super().get_model_state())
            for base in bases:
                state.update(base.get_model_state(self))

            state.update(configs["default_model_state"])
            return state

        def set_model_state(self, state: dict):
            if not is_super_base:
                super().set_model_state(state)

            for base in bases:
                base.set_model_state(self, state)

            for function in configs["set_model_state"]:
                function(self, state)

        def get_view_bbox(self):
            if len(configs["get_view_bbox"]) > 0:
                return configs["get_view_bbox"][-1](self)

            if not is_super_base:
                return super().get_view_bbox()
            if len(bases) > 0:
                return bases[-1].get_view_bbox(self)

            return mcpython.common.block.BoundingBox.FULL_BLOCK_BOUNDING_BOX

        def get_collision_bbox(self):
            if len(configs["get_collision_bbox"]) > 0:
                return configs["get_collision_bbox"][-1](self)

            if not is_super_base:
                return super().get_collision_bbox()
            if len(bases) > 0:
                return bases[-1].get_collision_bbox(self)

            return self.get_view_bbox()

        def on_request_item_for_block(
            self, itemstack: mcpython.common.container.ItemStack.ItemStack
        ):
            if not is_super_base:
                super().on_request_item_for_block(itemstack)

            for base in bases:
                base.on_request_item_for_block(self, itemstack)

            for function in configs["on_request_item_for_block"]:
                function(self, itemstack)

        def inject_redstone_power(self, side: mcpython.util.enums.EnumSide, level: int):
            self.injected_redstone_power[side] = level

            if not is_super_base:
                super().inject_redstone_power(side, level)

            for base in bases:
                base.inject_redstone_power(self, side, level)

            for function in configs["inject_redstone_power"]:
                function(self, side, level)

        def get_redstone_output(self, side: mcpython.util.enums.EnumSide) -> int:
            if len(configs["get_redstone_output"]) > 0:
                return configs["get_redstone_output"][-1](self, side)

            if not is_super_base:
                return super().get_redstone_output(side)
            if len(bases) > 0:
                return bases[-1].get_redstone_output(self, side)

            return max(
                self.get_redstone_source_power(side),
                *self.injected_redstone_power.values()
            )

        def get_redstone_source_power(self, side: mcpython.util.enums.EnumSide):
            # todo: maybe use highest power?

            if len(configs["get_redstone_source_power"]) > 0:
                return configs["get_redstone_source_power"][-1](self, side)

            if not is_super_base:
                return super().get_redstone_source_power(side)
            if len(bases) > 0:
                return bases[-1].get_redstone_source_power(self, side)

            return 0

    return ModifiedClass


block_factory_builder.register_direct_copy_attributes(
    "name",
    "global_name",
    ("hardness", 0),
    ("blast_resistance", 0),
    ("minimum_tool_level", 0),
    ("assigned_tools", tuple()),
    ("break_able_flag", True),
    ("speed_multiplier", 0),
    "solid",
    "can_conduct_redstone_power",
    "can_mobs_spawn_on",
    "can_mobs_spawn_in",
    "enable_random_ticks",
    "no_entity_collision",
    "entity_fall_multiplier",
)

block_factory_builder.register_direct_copy_attributes(
    "solid_face_table", operation=lambda x: x
)
block_factory_builder.register_direct_copy_attributes(
    "debug_world_states",
    "on_instance_creation",
    "on_properties_set",
    "on_block_added",
    "on_random_update",
    "on_redstone_update",
    "on_player_interaction",
    "on_no_collision_collide",
    "get_save_data",
    "dump_data",
    "load_data",
    "on_data_inject",
    "get_item_save_data",
    "set_item_save_data",
    "get_inventories",
    "get_provided_slot_lists",
    "set_model_state",
    "get_view_bbox",
    "get_collision_bbox",
    "on_request_item_for_block",
    "inject_redstone_power",
    "get_redstone_output",
    "get_redstone_source_power",
    ("default_model_state", {}),
    ("block_item_generator_state", {}),
    operation=lambda e: e.copy(),
)


block_factory_builder.register_configurator(
    FactoryBuilder.SetterFactoryConfigurator(
        "set_minimum_tool_level", "minimum_tool_level", int
    )
)
block_factory_builder.register_configurator(
    FactoryBuilder.SetterFactoryConfigurator(
        "set_break_able_flag", "break_able_flag", bool
    )
)
block_factory_builder.register_configurator(
    FactoryBuilder.SetterFactoryConfigurator(
        "set_walking_speed_multiplier", "speed_multiplier", float
    )
)
block_factory_builder.register_configurator(
    FactoryBuilder.SetterFactoryConfigurator(
        "set_block_item_generator_state", "block_item_generator_state", dict
    )
)
block_factory_builder.register_configurator(
    FactoryBuilder.SetterFactoryConfigurator(
        "set_solid", "solid", bool, default_value=True
    )
)
block_factory_builder.register_configurator(
    FactoryBuilder.SetterFactoryConfigurator(
        "set_can_conduct_redstone_power",
        "can_conduct_redstone_power",
        bool,
        default_value=True,
    )
)
block_factory_builder.register_configurator(
    FactoryBuilder.SetterFactoryConfigurator(
        "set_can_mobs_spawn_on", "can_mobs_spawn_on", bool, default_value=True
    )
)
block_factory_builder.register_configurator(
    FactoryBuilder.SetterFactoryConfigurator(
        "set_can_mobs_spawn_in", "can_mobs_spawn_in", bool, default_value=True
    )
)
block_factory_builder.register_configurator(
    FactoryBuilder.SetterFactoryConfigurator(
        "set_enable_random_ticks", "enable_random_ticks", bool, default_value=True
    )
)
block_factory_builder.register_configurator(
    FactoryBuilder.SetterFactoryConfigurator(
        "set_no_entity_collision", "no_entity_collision", bool, default_value=True
    )
)
block_factory_builder.register_configurator(
    FactoryBuilder.SetterFactoryConfigurator(
        "set_entity_fall_multiplier", "entity_fall_multiplier", float
    )
)
block_factory_builder.register_configurator(
    FactoryBuilder.SetterFactoryConfigurator(
        "set_debug_world_states", "debug_world_states", list
    )
)

block_factory_builder.register_configurator(
    FactoryBuilder.FunctionStackedAnnotator(
        "on_instance_creation", "on_instance_creation"
    )
)
block_factory_builder.register_configurator(
    FactoryBuilder.FunctionStackedAnnotator("on_properties_set", "on_properties_set")
)
block_factory_builder.register_configurator(
    FactoryBuilder.FunctionStackedAnnotator("on_block_added", "on_block_added")
)
block_factory_builder.register_configurator(
    FactoryBuilder.FunctionStackedAnnotator("on_block_remove", "on_block_remove")
)
block_factory_builder.register_configurator(
    FactoryBuilder.FunctionStackedAnnotator("on_random_update", "on_random_update")
)
block_factory_builder.register_configurator(
    FactoryBuilder.FunctionStackedAnnotator("on_block_update", "on_block_update")
)
block_factory_builder.register_configurator(
    FactoryBuilder.FunctionStackedAnnotator("on_redstone_update", "on_redstone_update")
)
block_factory_builder.register_configurator(
    FactoryBuilder.FunctionStackedAnnotator(
        "on_player_interaction", "on_player_interaction"
    )
)
block_factory_builder.register_configurator(
    FactoryBuilder.FunctionStackedAnnotator(
        "on_no_collision_collide", "on_no_collision_collide"
    )
)
block_factory_builder.register_configurator(
    FactoryBuilder.FunctionStackedAnnotator("get_save_data", "get_save_data")
)
block_factory_builder.register_configurator(
    FactoryBuilder.FunctionStackedAnnotator("dump_data", "dump_data")
)
block_factory_builder.register_configurator(
    FactoryBuilder.FunctionStackedAnnotator("load_data", "load_data")
)
block_factory_builder.register_configurator(
    FactoryBuilder.FunctionStackedAnnotator("on_data_inject", "on_data_inject")
)
block_factory_builder.register_configurator(
    FactoryBuilder.FunctionStackedAnnotator("get_item_save_data", "get_item_save_data")
)
block_factory_builder.register_configurator(
    FactoryBuilder.FunctionStackedAnnotator("set_item_save_data", "set_item_save_data")
)
block_factory_builder.register_configurator(
    FactoryBuilder.FunctionStackedAnnotator("get_inventories", "get_inventories")
)
block_factory_builder.register_configurator(
    FactoryBuilder.FunctionStackedAnnotator(
        "get_provided_slot_lists", "get_provided_slot_lists"
    )
)
block_factory_builder.register_configurator(
    FactoryBuilder.FunctionStackedAnnotator("set_model_state", "set_model_state")
)
block_factory_builder.register_configurator(
    FactoryBuilder.FunctionStackedAnnotator("get_view_bbox", "get_view_bbox")
)
block_factory_builder.register_configurator(
    FactoryBuilder.FunctionStackedAnnotator("get_collision_bbox", "get_collision_bbox")
)
block_factory_builder.register_configurator(
    FactoryBuilder.FunctionStackedAnnotator(
        "on_request_item_for_block", "on_request_item_for_block"
    )
)
block_factory_builder.register_configurator(
    FactoryBuilder.FunctionStackedAnnotator(
        "inject_redstone_power", "inject_redstone_power"
    )
)
block_factory_builder.register_configurator(
    FactoryBuilder.FunctionStackedAnnotator(
        "get_redstone_output", "get_redstone_output"
    )
)
block_factory_builder.register_configurator(
    FactoryBuilder.FunctionStackedAnnotator(
        "get_redstone_source_power", "get_redstone_source_power"
    )
)


BlockFactory = block_factory_builder.create_class()
