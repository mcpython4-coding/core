"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared as G, logger
import mcpython.common.container.ItemStack
import mcpython.common.block.AbstractBlock
import mcpython.common.block.IFallingBlock as FallingBlock
import mcpython.common.block.ILog as ILog
import mcpython.util.enums
import mcpython.common.block.ISlab as ISlab
import mcpython.common.block.IHorizontalOrientableBlock as IHorizontalOrientableBlock
import mcpython.common.block.BlockWall as BlockWall


# todo: implement inventory opening notations


class BlockFactory:
    """
    Factory for creating on an simple way block classes
    Examples:
        BlockFactory().setName("test:block").setHardness(1).setBlastResistance(1).finish()
        BlockFactory().setName("test:log").setHardness(1).setBlastResistance(1).setLog().finish()
        BlockFactory().setName("test:slab").setHardness(1).setBlastResistance(1).setSlab().finish()
        BlockFactory().setName("some:complex_block").setHardness(1).setBlastResistance(1).setDefaultModelState("your=default,model=state").setAllSideSolid(False).finish()

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
        your_template.setName("test:slab").setSlab().finish()  # will create an slab
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
        obj.setGlobalModName(self.modname).setBreakAbleFlag(self.breakable)
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
        self.setGlobalModName(template.modname).setBreakAbleFlag(template.breakable)
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
        # logger.println("[INFO] finishing up '{}'".format(self.name))
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
            return
        if self.modname is None or self.name.count(":") > 0:
            modname, blockname = tuple(self.name.split(":"))
        else:
            modname, blockname = self.modname, self.name
        if modname not in G.mod_loader.mods:
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
            G.mod_loader.mods[modname].eventbus.subscribe(
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

        G.registry.register(ConstructedBlock)

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

    def setBreakAbleFlag(self, state: bool):
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

    def setDefaultModelState(self, state):
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

    def setFallAble(self):
        """
        will make the block affected by gravity
        """
        self.baseclass.append(FallingBlock.IFallingBlock)
        return self

    def setAllSideSolid(self, state: bool):
        """
        sets all side status of solid
        :param state: the status
        """
        assert type(state) == bool
        for face in mcpython.util.enums.EnumSide.iterate():
            self.setSolidSideTableEntry(face, state)
        return self

    def setLog(self):
        """
        makes the block an log-like block; Will need the needed block-state variation
        """
        self.is_log = True
        if ILog.ILog not in self.baseclass:
            self.baseclass.append(ILog.ILog)
        return self

    def setSlab(self):
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
            self.setBreakAbleFlag(False)
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

    def setMinimumToolLevel(self, value: int):
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

    def setHorizontalOrientable(self, face_name="facing"):
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
