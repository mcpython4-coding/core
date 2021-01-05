"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import typing

from mcpython import shared, logger
import mcpython.common.factory.FactoryBuilder
from mcpython.common.factory.FactoryBuilder import FactoryBuilder
import mcpython.common.block.AbstractBlock
import mcpython.common.block.ILog as ILog
import mcpython.common.block.IFallingBlock as FallingBlock
import mcpython.common.block.ISlab as ISlab
import mcpython.common.block.BlockWall as BlockWall
import mcpython.common.block.IHorizontalOrientableBlock as IHorizontalOrientableBlock

import pickle
import mcpython.common.block.BoundingBox

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
def set_assigned_tools(instance: FactoryBuilder.IFactory, *tools):
    if len(tools) == 0:
        if type(tools[0]) in (list, tuple):
            tools = tools[0]
        else:
            tools = (tools,)
    instance.config_table["assigned_tools"] = tools
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
    name = instance.config_table["name"]
    if ":" not in name and "global_name" in instance.config_table:
        name = instance.config_table["global_name"] + ":" + name

    class ModifiedClass(cls):
        NAME = name
        HARDNESS = instance.config_table.setdefault("hardness", cls.HARDNESS)
        BLAST_RESISTANCE = instance.config_table.setdefault(
            "blast_resistance", cls.BLAST_RESISTANCE
        )

        MINIMUM_TOOL_LEVEL = instance.config_table.setdefault(
            "minimum_tool_level", cls.MINIMUM_TOOL_LEVEL
        )
        ASSIGNED_TOOLS = instance.config_table.setdefault(
            "assigned_tools", cls.ASSIGNED_TOOLS
        )

        IS_BREAKABLE = instance.config_table.setdefault(
            "break_able_flag", cls.IS_BREAKABLE
        )

        DEFAULT_FACE_SOLID = instance.config_table.setdefault(
            "solid_face_table", cls.DEFAULT_FACE_SOLID
        )

        CUSTOM_WALING_SPEED_MULTIPLIER = instance.config_table.setdefault(
            "speed_multiplier", cls.CUSTOM_WALING_SPEED_MULTIPLIER
        )

        BLOCK_ITEM_GENERATOR_STATE = instance.config_table.setdefault(
            "block_item_generator_state", cls.BLOCK_ITEM_GENERATOR_STATE
        )

        IS_SOLID = instance.config_table.setdefault("solid", cls.IS_SOLID)

        CAN_CONDUCT_REDSTONE_POWER = instance.config_table.setdefault(
            "can_conduct_redstone_power", cls.CAN_CONDUCT_REDSTONE_POWER
        )

        CAN_MOBS_SPAWN_ON = instance.config_table.setdefault(
            "can_mobs_spawn_on", cls.CAN_MOBS_SPAWN_ON
        )
        CAN_MOBS_SPAWN_IN = instance.config_table.setdefault(
            "can_mobs_spawn_in", cls.CAN_MOBS_SPAWN_IN
        )

        ENABLE_RANDOM_TICKS = instance.config_table.setdefault(
            "enable_random_ticks", cls.ENABLE_RANDOM_TICKS
        )

        NO_ENTITY_COLLISION = instance.config_table.setdefault(
            "no_entity_collision", cls.NO_ENTITY_COLLISION
        )
        ENTITY_FALL_MULTIPLIER = instance.config_table.setdefault(
            "entity_fall_multiplier", cls.ENTITY_FALL_MULTIPLIER
        )

        DEBUG_WORLD_BLOCK_STATES = instance.config_table.setdefault(
            "debug_world_states", cls.DEBUG_WORLD_BLOCK_STATES
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

    class ModifiedClass(cls):
        def __init__(self):
            if not is_super_base:
                super().__init__()

            for base in bases:
                super(base, self).__init__()

        def set_creation_properties(self, *args, **kwargs):
            if not is_super_base:
                super().set_creation_properties(*args, **kwargs)

            for base in bases:
                super(base, self).set_creation_properties(*args, **kwargs)

        def on_block_added(self, *args, **kwargs):
            if not is_super_base:
                super().on_block_added(*args, **kwargs)

            for base in bases:
                super(base, self).on_block_added(*args, **kwargs)

        def on_block_remove(self, *args, **kwargs):
            if not is_super_base:
                super().on_block_remove(*args, **kwargs)

            for base in bases:
                super(base, self).on_block_remove(*args, **kwargs)

        def on_random_update(self, *args, **kwargs):
            if not is_super_base:
                super().on_random_update(*args, **kwargs)

            for base in bases:
                super(base, self).on_random_update(*args, **kwargs)

        def on_block_update(self, *args, **kwargs):
            if not is_super_base:
                super().on_block_update(*args, **kwargs)

            for base in bases:
                super(base, self).on_block_update(*args, **kwargs)
            self.on_redstone_update()

        def on_redstone_update(self, *args, **kwargs):
            if not is_super_base:
                super().on_redstone_update(*args, **kwargs)

            for base in bases:
                super(base, self).on_redstone_update(*args, **kwargs)

        def on_player_interaction(self, *args, **kwargs):
            if not is_super_base:
                if super().on_player_interaction(*args, **kwargs):
                    return True

            for base in bases:
                if super(base, self).on_player_interaction(*args, **kwargs):
                    return True

            return False

        def on_no_collision_collide(self, *args, **kwargs):
            if not is_super_base:
                super().on_no_collision_collide(*args, **kwargs)

            for base in bases:
                super(base, self).on_no_collision_collide(*args, **kwargs)

        def get_save_data(self):
            if not is_super_base:
                return super().get_save_data()
            if len(bases) > 0:
                return super(self, bases[-1]).get_save_data()
            return self.get_model_state()

        def dump_data(self):
            if not is_super_base:
                return super().dump_data()
            if len(bases) > 0:
                return super(self, bases[-1]).dump_data()
            return pickle.dumps(self.get_save_data())

        def load_data(self, data):
            if not is_super_base:
                return super().load_data(data)
            if len(bases) > 0:
                return super(self, bases[-1]).load_data(data)
            self.set_model_state(data)

        def inject(self, data: bytes):
            if not is_super_base:
                return super().inject(data)
            if len(bases) > 0:
                return super(self, bases[-1]).inject(data)
            self.load_data(pickle.loads(data) if type(data) == bytes else data)

        def get_item_saved_state(self):
            if not is_super_base:
                return super().get_item_saved_state()
            if len(bases) > 0:
                return super(self, bases[-1]).get_item_saved_state()

        def set_item_saved_state(self, state):
            if not is_super_base:
                return super().set_item_saved_state(state)
            if len(bases) > 0:
                return super(self, bases[-1]).set_item_saved_state(state)

        def get_inventories(self):
            inventories = []
            if not is_super_base:
                inventories += super().get_inventories()
            if len(bases) > 0:
                inventories += super(self, bases[-1]).get_inventories()
            return inventories

        def get_provided_slot_lists(self, side: mcpython.util.enums.EnumSide):
            a, b = [], []
            if not is_super_base:
                x, y = super().get_provided_slot_lists(side)
                a += x
                b += y
            if len(bases) > 0:
                x, y = super(self, bases[-1]).get_provided_slot_lists(side)
                a += x
                b += y
            return a, b

        def get_model_state(self) -> dict:
            state = {}
            if not is_super_base:
                state.update(super().get_model_state())
            if len(bases) > 0:
                state.update(super(self, bases[-1]).get_model_state())

            state.update(instance.config_table["default_model_state"])
            return state

        def set_model_state(self, state: dict):
            if not is_super_base:
                super().set_model_state(state)

            for base in bases:
                super(base, self).set_model_state(state)

        def get_view_bbox(self):
            if not is_super_base:
                return super().get_view_bbox()
            if len(bases) > 0:
                return super(self, bases[-1]).get_view_bbox()

            return mcpython.common.block.BoundingBox.FULL_BLOCK_BOUNDING_BOX

        def get_collision_bbox(self):
            if not is_super_base:
                return super().get_collision_bbox()
            if len(bases) > 0:
                return super(self, bases[-1]).get_collision_bbox()

            return self.get_view_bbox()

        def on_request_item_for_block(
            self, itemstack: mcpython.common.container.ItemStack.ItemStack
        ):
            if not is_super_base:
                super().on_request_item_for_block(itemstack)

            for base in bases:
                super(base, self).on_request_item_for_block(itemstack)

        def inject_redstone_power(self, side: mcpython.util.enums.EnumSide, level: int):
            self.injected_redstone_power[side] = level

            if not is_super_base:
                super().inject_redstone_power(side, level)

            for base in bases:
                super(base, self).inject_redstone_power(side, level)

        def get_redstone_output(self, side: mcpython.util.enums.EnumSide) -> int:
            if not is_super_base:
                return super().get_redstone_output()
            if len(bases) > 0:
                return super(self, bases[-1]).get_redstone_output()

            return max(
                self.get_redstone_source_power(side),
                *self.injected_redstone_power.values()
            )

        def get_redstone_source_power(self, side: mcpython.util.enums.EnumSide):
            # todo: maybe use highest power?
            if not is_super_base:
                return super().get_redstone_source_power(side)
            if len(bases) > 0:
                return super(self, bases[-1]).get_redstone_source_power(side)

            return 0

    return ModifiedClass


block_factory_builder.register_direct_copy_attributes(
    "name",
    "global_name",
    "hardness",
    "blast_resistance",
    "minimum_tool_level",
    "assigned_tools",
    "break_able_flag",
    "default_model_state",
    "speed_multiplier",
    "block_item_generator_state",
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
    "debug_world_states", operation=lambda e: e.copy()
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
    FactoryBuilder.SetterFactoryConfigurator("set_solid", "solid", bool)
)
block_factory_builder.register_configurator(
    FactoryBuilder.SetterFactoryConfigurator(
        "set_can_conduct_redstone_power", "can_conduct_redstone_power", bool
    )
)
block_factory_builder.register_configurator(
    FactoryBuilder.SetterFactoryConfigurator(
        "set_can_mobs_spawn_on", "can_mobs_spawn_on", bool
    )
)
block_factory_builder.register_configurator(
    FactoryBuilder.SetterFactoryConfigurator(
        "set_can_mobs_spawn_in", "can_mobs_spawn_in", bool
    )
)
block_factory_builder.register_configurator(
    FactoryBuilder.SetterFactoryConfigurator(
        "set_enable_random_ticks", "enable_random_ticks", bool
    )
)
block_factory_builder.register_configurator(
    FactoryBuilder.SetterFactoryConfigurator(
        "set_no_entity_collision", "no_entity_collision", bool
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


BlockFactory = block_factory_builder.create_class()


import mcpython.common.container.ItemStack
import mcpython.util.enums
import mcpython.common.factory.IFactoryModifier


# todo: implement inventory opening helper with interaction and save of inventory


class OldBlockFactory(mcpython.common.factory.IFactoryModifier.IFactory):
    """
    Old implementation of the BlockFactory system

    Factory for creating on an simple way block classes
    Examples:
        BlockFactory().setName("test:block").setHardness(1).setBlastResistance(1).finish()
        BlockFactory().setName("test:log").setHardness(1).setBlastResistance(1).set_log().finish()
        BlockFactory().setName("test:slab").setHardness(1).setBlastResistance(1).set_slab().finish()
        BlockFactory().setName("some:complex_block").setHardness(1).setBlastResistance(1).set_default_model_state("your=default,model=state").set_all_side_solid(False).finish()

    Most functions will return the BlockFactory-object called on to allow above syntax.
    .setHardness and .setBlastResistance must be set on all objects
    The .finish() method will return the BlockItemFactory-instance for the block. Modifying it before the
        "stage:block:factory:finish"-phase will lead into changes in the base block. This can also lead into exceptions
        in this phase as their the data is read in and the classes are generated.

    for an long lists of examples, see Blocks.py; Be aware that it is using the template system described below.

    ---------------------------------
    Modifying existing BlockFactories
    ---------------------------------

    As mentioned above, using the instance and modifying it is not the ideal way of doing. You can go the "normal"
        route and replace the block-class in the registry. You can do this also over the BlockFactory route, but be
        aware that you have to register after the desired block and hope for the best. You can also, if you want to
        use BlockFactory-instances, use the on_class_create-event in the constructor of the BlockFactory-class and
        recycle your generated class afterwards.
    You can also call the finish()-method with immediate=True leading into an immediate class generation (may take
        some time).

    ---------------
    Template-system
    ---------------
    You are able to create BlockFactory templates (pre-configured BlockFactory objects from which you can create
        multiple blocks starting with the same foundation).
    You can store your config with .setTemplate() on an BlockFactory-object. It will store the active status
        for later usage. When you call .finish(), the block will be created and the system will reset to the state
        of your .setTemplate() call. You can manually reset it by calling .setToTemplate() and you can delete
        the template by calling .resetTemplate(). You can disable the reset to the template on finish-call if you
        pass reset_to_template=False to it.
    If you are creating an block in multiple colors with the configuration, templates should be used as they reduce
        are better internally.
    Templates can be extracted/inserted as the .template-attribute.
    Template-attribute changes will NOT affect active build block, you must call setToTemplate() first or finish your
        block

    Example:
        your_template = BlockFactory().[some calls].setTemplate()
        your_template.setName("test:block").finish()  # will create an block called "test:block" with pre-configured parameters
        your_template.setName("test:slab").set_slab().finish()  # will create an slab
        your_template.setName("test:block2").finish()   # This is now NOT an slab beside it be based on the same base

    ---------------------
    Extending the Factory
    ---------------------

    Currently, the only way is to create an sub-class of BlockFactory and re-send it into the variable holding the
        class. It is planned to re-write the foundation of the system (and leaving most of the surface) and porting
        things to an really simple-extendable system. This will take some while and has not the highest priority
        (As it is an API-only improvement). If you miss any setter for an Block-class API attribute, create an
        issue for it and we will try to implement it (and it fit the general look of the API's)

    """

    FACTORY_MODIFIERS = {}

    def __init__(self, on_class_create=None):
        """
        will create an new BlockFactory-instance
        :param on_class_create: optional: an function taking the generated class and optional returning an new one to
            replace
        """

        self.entity_fall_multiplier = 1
        self.can_mobs_spawn_in = False
        self.on_class_create = on_class_create

        self.set_name_finises_previous = False

        self.name = None
        self.modname = None
        self.breakable = True
        self.model_states = []
        self.solid_faces = None
        self.no_collision = False

        self.create_callback = None
        self.delete_callback = None
        self.random_update_callback = None
        self.update_callback = None
        self.interaction_callback = None
        self.hardness = 1
        self.minimum_tool_level = 0
        self.blast_resistance = 1
        self.best_tools = []
        self.speed_multiplier = None
        self.block_item_generator_state = None
        self.face_name = "facing"
        self.solid = True
        self.conducts_redstone = True
        self.can_mobs_spawn_on = True
        self.random_ticks_enabled = False

        self.custom_solid_side_function = None
        self.custom_model_state_function = None
        self.custom_itemstack_modification_function = None
        self.custom_block_item_modification_function = None

        self.is_log = False

        self.baseclass = [mcpython.common.block.AbstractBlock.AbstractBlock]

        self.template = None

    def __call__(self, name: str = None):
        if name is not None:
            self.setName(name)
        return self

    def copy(self):
        """
        will copy the BlockFactory-object with all its content (including its template-link)
        :return: an copy of this
        """
        obj = BlockFactory()
        if self.name is not None:
            obj.setName(self.name)
        obj.setGlobalModName(self.modname).set_break_able_flag(self.breakable)
        obj.model_states = self.model_states.copy()
        if self.solid_faces is not None:
            obj.solid_faces = self.solid_faces.copy()

        obj.create_callback, obj.delete_callback = (
            self.create_callback,
            self.delete_callback,
        )
        obj.random_update_callback, obj.update_callback = (
            self.random_update_callback,
            self.update_callback,
        )
        obj.interaction_callback = self.interaction_callback

        obj.hardness, obj.minimum_tool_level, obj.best_tools = (
            self.hardness,
            self.minimum_tool_level,
            self.best_tools.copy(),
        )
        obj.speed_multiplier, obj.block_item_generator_state = (
            self.speed_multiplier,
            self.block_item_generator_state,
        )
        obj.face_name, obj.blast_resistance = self.face_name, self.blast_resistance

        obj.custom_solid_side_function = self.custom_solid_side_function
        obj.custom_model_state_function = self.custom_model_state_function
        obj.custom_itemstack_modification_function = (
            self.custom_itemstack_modification_function
        )
        obj.custom_block_item_modification_function = (
            self.custom_block_item_modification_function
        )

        obj.is_log = self.is_log

        obj.baseclass = self.baseclass.copy()
        obj.template = self.template
        return obj

    def setTemplate(self, set_name_finises_previous=False):
        """
        sets the current status as "template". This status will be set to on every .finish() call, but will not affect
        the new generated entry.
        """
        self.set_name_finises_previous = set_name_finises_previous
        self.template = self.copy()
        return self

    def setToTemplate(self):
        """
        will reset the current object to the status right after the .setTemplate() call
        """
        assert self.template is not None

        template = self.template
        if template.name is not None:
            self.setName(template.name)

        self.setGlobalModName(template.modname).set_break_able_flag(template.breakable)
        self.model_states = template.model_states.copy()
        if template.solid_faces is not None:
            self.solid_faces = template.solid_faces.copy()

        self.create_callback, self.delete_callback = (
            template.create_callback,
            template.delete_callback,
        )
        self.random_update_callback, self.update_callback = (
            template.random_update_callback,
            template.update_callback,
        )
        self.interaction_callback = template.interaction_callback

        self.hardness, self.minimum_tool_level, self.best_tools = (
            template.hardness,
            template.minimum_tool_level,
            template.best_tools.copy(),
        )
        self.speed_multiplier, self.block_item_generator_state = (
            template.speed_multiplier,
            template.block_item_generator_state,
        )
        self.face_name, self.blast_resistance = (
            template.face_name,
            template.blast_resistance,
        )

        self.custom_solid_side_function = template.custom_solid_side_function
        self.custom_model_state_function = template.custom_model_state_function
        self.custom_itemstack_modification_function = (
            template.custom_itemstack_modification_function
        )
        self.custom_block_item_modification_function = (
            template.custom_block_item_modification_function
        )

        self.random_ticks_enabled = False

        self.is_log = template.is_log

        self.baseclass = template.baseclass.copy()

    def resetTemplate(self):
        """
        will delete the template-status
        """
        self.template = None
        return self

    def finish(self, reset_to_template=True, immediate=False):
        """
        will finish up the process of configuration and register the finish_up-call for the future event
        :param reset_to_template: if the system should be reset to the configured template (if arrival) after finishing
            up
        :param immediate: if class generation should go on immediately or not
        :return: the BlockFactory instance. When the template exists, it will be an copy of the active without the
            template instance
        """

        if self.name.count(":") == 0:
            logger.println(
                "[BLOCK FACTORY][FATAL] 'setName' was set to an not-prefixed name '{}'".format(
                    self.name
                )
            )
            logger.println(
                "[BLOCK FACTORY][FATAL] out of these error, the block is NOT constructed"
            )
            logger.println(
                "[BLOCK FACTORY][FATAL] (P.s. this does mean also that setGlobalModName() was not set)"
            )
            logger.println(
                "[BLOCK FACTORY][FATAL] (This could be an wrong template setup for the block factory)"
            )
            logger.print_stack("call stack")
            return

        if self.modname is None or self.name.count(":") > 0:
            modname, blockname = tuple(self.name.split(":"))
        else:
            modname, blockname = self.modname, self.name
        if modname not in shared.mod_loader.mods:
            modname = "minecraft"
        if self.template is None:
            obj = self
        else:
            obj = self.copy()
            obj.template = None
            if reset_to_template:
                self.setToTemplate()

        if immediate:
            obj.finish_up()
        else:
            shared.mod_loader.mods[modname].eventbus.subscribe(
                "stage:block:load",
                obj.finish_up,
                info="loading block {}".format(blockname),
            )
        return obj

    def finish_up(self):
        """
        will finish up the system
        todo: clean up this mess!!!
        """

        assert self.name is not None
        assert self.hardness is not None
        assert self.blast_resistance is not None

        class Baseclass(object):
            pass

        for cls in self.baseclass:

            class Baseclass(Baseclass, cls):
                pass

        master = self

        class ConstructedBlock(Baseclass):
            CUSTOM_WALING_SPEED_MULTIPLIER = self.speed_multiplier

            NAME = master.name

            BLOCK_ITEM_GENERATOR_STATE = master.block_item_generator_state

            IS_BREAKABLE = master.breakable

            BLAST_RESISTANCE = self.blast_resistance

            IS_SOLID = self.solid

            CAN_CONDUCT_REDSTONE_POWER = self.conducts_redstone

            CAN_MOBS_SPAWN_ON = self.can_mobs_spawn_on
            CAN_MOBS_SPAWN_IN = self.can_mobs_spawn_in

            ENABLE_RANDOM_TICKS = self.random_ticks_enabled

            NO_ENTITY_COLLISION = self.no_collision
            ENTITY_FALL_MULTIPLIER = self.entity_fall_multiplier

            @staticmethod
            def get_all_model_states():
                raw_states = self.model_states.copy()
                [raw_states.extend(e.DEBUG_WORLD_BLOCK_STATES) for e in self.baseclass]

                while {} in raw_states:
                    raw_states.remove({})  # we don't need them now

                # make the entries unique!
                states = []
                for e in raw_states:
                    if e not in states:
                        states.append(e)

                if len(states) == 0:
                    states.append({})  # if we have no, this is the default one

                return states

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                for baseclass in master.baseclass:
                    baseclass.__init__(self, *args, **kwargs)
                if master.create_callback:
                    master.create_callback(self)

            def on_remove(self):
                for baseclass in master.baseclass:
                    baseclass.on_block_remove(self)
                if master.delete_callback:
                    master.delete_callback(self)

            HARDNESS = master.hardness
            MINIMUM_TOOL_LEVEL = master.minimum_tool_level
            BEST_TOOLS_TO_BREAK = master.best_tools

            def set_model_state(self, state):
                for baseclass in master.baseclass:
                    baseclass.set_model_state(self, state)

            def get_model_state(self):
                state = (
                    master.custom_model_state_function(self).copy()
                    if master.custom_model_state_function is not None
                    else {}
                )
                for baseclass in master.baseclass:
                    state = {**state, **baseclass.get_model_state(self)}
                return state

        ConstructedBlock.DEBUG_WORLD_BLOCK_STATES = (
            ConstructedBlock.get_all_model_states()
        )

        if self.solid_faces:

            class ConstructedBlock(ConstructedBlock):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    self.face_solid = {
                        side: master.solid_faces[side]
                        if side in master.solid_faces
                        else all(
                            [
                                not hasattr(baseclass2, "face_solid")
                                or baseclass2.face_solid[side]
                                for baseclass2 in master.baseclass
                            ]
                        )
                        for side in mcpython.util.enums.EnumSide.iterate()
                    }

        if master.random_update_callback:

            class ConstructedBlock(ConstructedBlock):
                def on_random_update(self):
                    master.random_update_callback(self)

        if master.update_callback:

            class ConstructedBlock(ConstructedBlock):
                def on_block_update(self):
                    for baseclass in master.baseclass:
                        baseclass.on_block_update(self)
                    master.update_callback(self)

        if master.interaction_callback:

            class ConstructedBlock(ConstructedBlock):
                def on_player_interact(
                    self, player, itemstack, button, modifiers, exact_hit
                ) -> bool:
                    return master.interaction_callback(
                        self, player, itemstack, button, modifiers, exact_hit
                    )

        if master.custom_itemstack_modification_function:

            class ConstructedBlock(ConstructedBlock):
                def on_request_item_for_block(self, itemstack):
                    master.custom_itemstack_modification_function(self, itemstack)

        if master.face_name:

            class ConstructedBlock(ConstructedBlock):
                MODEL_FACE_NAME = master.face_name

        if callable(self.on_class_create):
            r = self.on_class_create(ConstructedBlock)
            if r is not None:
                ConstructedBlock = r

        if self.name in self.FACTORY_MODIFIERS:
            for modifier in self.FACTORY_MODIFIERS:
                ConstructedBlock = modifier.apply(self, ConstructedBlock)

        shared.registry.register(ConstructedBlock)

        return ConstructedBlock

    def setGlobalModName(self, name: str):
        """
        will set the mod-prefix for the future (only very useful in template systems)
        :param name: the mod-prefix
        """
        assert type(name) == str
        self.modname = name
        return self

    def setSolidFlag(self, state: bool):
        """
        will set the SOLID-flag of the class
        :param state: the value to set to
        """
        assert type(state) == bool
        self.solid = state
        return self

    def setConductsRedstonePowerFlag(self, state: bool):
        """
        will set the CAN_CONDUCT_REDSTONE-flag of the class
        :param state: the value to set to
        """
        assert type(state) == bool
        self.setSolidFlag(state)
        self.conducts_redstone = state
        return self

    def setCanMobsSpawnOnFlag(self, state: bool):
        """
        will set the CAN_MOBS_SPAWN_ON-flag of the class
        :param state: the state to set to
        """
        assert type(state) == bool
        self.can_mobs_spawn_on = state
        return self

    def setName(self, name: str):
        """
        will set the name of the block, when mod-prefix was set, the prefix is added in front with an ":" in between,
        but only if <name> has no ":" representing an "<mod-prefix>:<block name>".
        :param name: The name of the block
        """
        assert type(name) == str
        if self.set_name_finises_previous and self.name is not None:
            self.finish()
        self.name = (
            "" if self.modname is None or ":" in name else (self.modname + ":")
        ) + name
        if self.name.count(":") == 0:
            import traceback

            logger.println(
                "[BLOCK FACTORY][WARN] 'setName' was set to an not-prefixed name '{}'".format(
                    self.name
                )
            )
            traceback.print_stack()
        return self

    def setCreateCallback(self, function):
        """
        will set an callback for the block creation in __init__-function of final class
        :param function: the function to invoke on creation. It is called together with the block instance
        """
        assert callable(function)
        self.create_callback = function
        return self

    def setDeleteCallback(self, function):
        """
        will set an callback for the deletion of the block
        :param function: the function to invoke on deletion. It is called together with the block instance
        """
        assert callable(function)
        self.delete_callback = function
        return self

    def set_break_able_flag(self, state: bool):
        """
        will set the BREAKABLE-flag of the class
        :param state: the state to use
        """
        assert type(state) == bool
        self.breakable = state
        return self

    def setRandomUpdateCallback(self, function):
        """
        will set the callback for random updates
        :param function: the function to invoke on random update together with the block instance
        """
        assert callable(function)
        self.random_update_callback = function
        self.random_ticks_enabled = True
        return self

    def setUpdateCallback(self, function):
        """
        will set the callback for an block update
        :param function: the function to invoke on an block update together with the block instance
        """
        assert callable(function)
        self.update_callback = function
        return self

    def setCustomSolidSideFunction(self, function):
        """
        will set the callback for the solid side system
        :param function: the function to invoke
        """
        assert callable(function)
        self.custom_solid_side_function = function
        if self.solid_faces is not None:
            self.solid_faces.clear()  # only one at a time is allowed
        return self

    def setSolidSideTableEntry(self, side, state: bool):
        """
        will set one entry in the solid face table
        :param side: the side to set
        :param state: the state to set to
        """
        if self.solid_faces is None:
            self.solid_faces = {}
        if self.custom_solid_side_function:
            self.custom_solid_side_function = None  # only one at a time is allowed
        self.solid_faces[side] = state
        return self

    def setCustomModelStateFunction(self, function):
        """
        will set the model state getter callback for the class
        :param function: the function to invoke when needed
        """
        assert callable(function)
        self.custom_model_state_function = function
        return self

    def set_default_model_state(self, state):
        """
        Will set the default model state of the block
        :param state: the state as an dict or an string-representation like in the block-state files
        :return:
        """
        assert type(state) in (str, dict)
        if type(state) == str:
            state = {e.split("=")[0]: e.split("=")[1] for e in state.split(",")}

        def get_state(*_):
            return state

        self.setCustomModelStateFunction(get_state)
        return self

    def setAllModelStateInfo(self, model_states: list):
        """
        will set the list of all possible block states of the block
        :param model_states: the model states, as an list of dicts
        todo: implement stringifier support
        """
        assert type(model_states) == list
        self.model_states = model_states
        return self

    def setInteractionCallback(self, function):
        """
        sets the callback for the interaction event
        :param function: the function to invoke on
            (signature: block instance, player, itemstack, button, modifiers, exact_hit)
        """
        assert callable(function)
        self.interaction_callback = function
        return self

    def set_fall_able(self):
        """
        will make the block affected by gravity
        """
        self.baseclass.append(FallingBlock.IFallingBlock)
        return self

    def set_all_side_solid(self, state: bool):
        """
        sets all side status of solid
        :param state: the status
        """
        assert type(state) == bool
        for face in mcpython.util.enums.EnumSide.iterate():
            self.setSolidSideTableEntry(face, state)
        return self

    def set_log(self):
        """
        makes the block an log-like block; Will need the needed block-state variation
        """
        self.is_log = True
        if ILog.ILog not in self.baseclass:
            self.baseclass.append(ILog.ILog)
        return self

    def set_slab(self):
        """
        makes the block an slab-like block; Will need the needed block-state variation
        """
        if ISlab.ISlab not in self.baseclass:
            self.baseclass.append(ISlab.ISlab)
        return self

    def setWall(self):
        if BlockWall.IWall not in self.baseclass:
            self.baseclass.append(BlockWall.IWall)
        return self

    def setHardness(self, value: float):
        """
        will set the hardness of the block
        :param value: the value of the hardness
        """
        if value == -1:
            self.set_break_able_flag(False)
        self.hardness = value
        return self

    def setStrength(self, hardness: float, blast_resistance=None):
        """
        will set hardness and blasz resistance at ones
        :param hardness: value for hardness
        :param blast_resistance: value for blast resistance, if None, hardness is used
        """
        self.setHardness(hardness)
        self.setBlastResistance(
            blast_resistance if blast_resistance is not None else hardness
        )
        return self

    def enableRandomTicks(self):
        self.random_ticks_enabled = True
        return self

    def set_minimum_tool_level(self, value: int):
        """
        will set the minimum needed tool level for breaking the block
        :param value: the value representing an tool level
        """
        self.minimum_tool_level = value
        return self

    def setBestTools(self, tools):
        """
        will set the tools good in breaking the block
        :param tools: an list of tools or only one tool
        """
        self.best_tools = tools if type(tools) == list else [tools]
        return self

    def setCustomItemstackModificationFunction(self, function):
        """
        will set the callback to modify the itemstack generated when the block is broken
        :param function: the function to invoke
        """
        assert callable(function)
        self.custom_itemstack_modification_function = function
        return self

    def setCustomBlockItemModification(self, function):
        """
        will set the callback for the modification call for the ItemFactory-object generated by BlockItemFactory
        :param function: the function to invoke on callback
        """
        assert callable(function)
        self.custom_block_item_modification_function = function
        return self

    def setSpeedMultiplier(self, factor: float):
        """
        sets the factor applied to the player movement speed when the player is ontop of the block
        :param factor: the factor to use
        """
        self.speed_multiplier = factor
        return self

    def setBlockItemGeneratorState(self, state: dict):
        """
        sets the state of the block to use when the BlockItemGenerator makes the image for the item
        :param state: the state as an dict
        todo: make this also accept an string
        """
        self.block_item_generator_state = state
        return self

    def set_horizontal_orientable(self, face_name="facing"):
        """
        will set the block to horizontal orientable mode
        :param face_name: the name for the internal block-state reference for the orientation
        """
        self.baseclass.append(IHorizontalOrientableBlock.IHorizontalOrientableBlock)
        self.face_name = face_name
        return self

    def setBlastResistance(self, resistance: float):
        """
        will set the resistance against explosions (internally not used, but part of the Block-API
        :param resistance: the resistance of the block
        """
        self.blast_resistance = resistance
        return self

    def setNoCollision(self, value: bool = True):
        self.no_collision = value
        return self
