"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import mcpython.gui.ItemStack
import mcpython.block.Block
import mcpython.block.IFallingBlock as FallingBlock
import mcpython.block.ILog as ILog
import mcpython.util.enums
import mcpython.block.ISlab as ISlab
import mcpython.block.IHorizontalOrientableBlock as IHorizontalOrientableBlock
import deprecation
import logger


# todo: implement inventory opening notations


class BlockFactory:
    """
    factory for creating on an simple way block classes
    examples:
        BlockFactory().setName("test:block").setHardness(1).setBlastResistance(1).finish()
        BlockFactory().setName("test:log").setHardness(1).setBlastResistance(1).setLog().finish()
        BlockFactory().setName("test:slab").setHardness(1).setBlastResistance(1).setSlab().finish()
        BlockFactory().setName("some:complex_block").setHardness(1).setBlastResistance(1).setDefaultModelState("your=default,model=state").setAllSideSolid(False).finish()

    Most functions will return the BlockFactory-object called on to allow above syntax.
    .setHardness and .setBlastResistance should be set on ALL blocks created as they will be NOT optional in the future.
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

        self.on_class_create = on_class_create

        self.name = None
        self.modname = None
        self.breakable = True
        self.modelstates = [{}]
        self.solid_faces = None

        self.create_callback = None
        self.delete_callback = None
        self.randomupdate_callback = None
        self.update_callback = None
        self.interaction_callback = None
        self.hardness = 1
        self.minmum_toollevel = 0
        self.blast_resistance = 1
        self.besttools = []
        self.speed_multiplier = None
        self.block_item_generator_state = None
        self.face_name = "facing"
        self.solid = True
        self.conducts_redstone = True
        self.can_mobs_spawn_on = True
        self.random_ticks_enabled = False

        self.customsolidsidefunction = None
        self.custommodelstatefunction = None
        self.customitemstackmodifcationfunction = None
        self.customblockitemmodificationfunction = None

        self.islog = False

        self.baseclass = [mcpython.block.Block.Block]

        self.template = None

    def copy(self):
        """
        will copy the BlockFactory-object with all its content (including its template-link)
        :return: an copy of this
        """
        obj = BlockFactory()
        if self.name is not None: obj.setName(self.name)
        obj.setGlobalModName(self.modname).setBreakAbleFlag(self.breakable)
        obj.modelstates = self.modelstates.copy()
        if self.solid_faces is not None: obj.solid_faces = self.solid_faces.copy()

        obj.create_callback, obj.delete_callback = self.create_callback, self.delete_callback
        obj.randomupdate_callback, obj.update_callback = self.randomupdate_callback, self.update_callback
        obj.interaction_callback = self.interaction_callback

        obj.hardness, obj.minmum_toollevel, obj.besttools = self.hardness, self.minmum_toollevel, self.besttools.copy()
        obj.speed_multiplier, obj.block_item_generator_state = self.speed_multiplier, self.block_item_generator_state
        obj.face_name, obj.blast_resistance = self.face_name, self.blast_resistance

        obj.customsolidsidefunction = self.customsolidsidefunction
        obj.custommodelstatefunction = self.custommodelstatefunction
        obj.customitemstackmodifcationfunction = self.customitemstackmodifcationfunction
        obj.customblockitemmodificationfunction = self.customblockitemmodificationfunction

        obj.islog = self.islog

        obj.baseclass = self.baseclass.copy()
        obj.template = self.template
        return obj

    def setTemplate(self):
        """
        sets the current status as "template". This status will be set to on every .finish() call, but will not affect
        the new generated entry.
        """
        self.template = self.copy()
        return self

    def setToTemplate(self):
        """
        will reset the current object to the status right after the .setTemplate() call
        """
        assert self.template is not None
        template = self.template
        if template.name is not None: self.setName(template.name)
        self.setGlobalModName(template.modname).setBreakAbleFlag(template.breakable)
        self.modelstates = template.modelstates.copy()
        if template.solid_faces is not None: self.solid_faces = template.solid_faces.copy()

        self.create_callback, self.delete_callback = template.create_callback, template.delete_callback
        self.randomupdate_callback, self.update_callback = template.randomupdate_callback, template.update_callback
        self.interaction_callback = template.interaction_callback

        self.hardness, self.minmum_toollevel, self.besttools = template.hardness, template.minmum_toollevel, template.besttools.copy()
        self.speed_multiplier, self.block_item_generator_state = template.speed_multiplier, template.block_item_generator_state
        self.face_name, self.blast_resistance = template.face_name, template.blast_resistance

        self.customsolidsidefunction = template.customsolidsidefunction
        self.custommodelstatefunction = template.custommodelstatefunction
        self.customitemstackmodifcationfunction = template.customitemstackmodifcationfunction
        self.customblockitemmodificationfunction = template.customblockitemmodificationfunction

        self.random_ticks_enabled = False

        self.islog = template.islog

        self.baseclass = template.baseclass.copy()

    def resetTemplate(self):
        """
        will delete the template-status
        """
        self.template = None
        return self

    def finish(self, register=True, reset_to_template=True, immediate=False):
        """
        will finish up the process of configuration and register the finish_up-call for the future event
        :param register: unused
        :param reset_to_template: if the system should be reset to the configured template (if arrival) after finishing
            up
        :param immediate: if class generation should go on immediately or not
        :return: the BlockFactory instance. When the template exists, it will be an copy of the active without the
            template instance
        """
        if self.modname is None:
            modname, blockname = tuple(self.name.split(":"))
        else:
            modname, blockname = self.modname, self.name
        if modname not in G.modloader.mods: modname = "minecraft"
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
            G.modloader.mods[modname].eventbus.subscribe("stage:block:load", obj.finish_up,
                                                         info="loading block {}".format(blockname))
        return obj

    @deprecation.deprecated("dev1-2", "a1.2.0")
    def _finish(self, register: bool):
        self.finish_up()

    def finish_up(self):
        """
        will finish up the system
        todo: clean up this mess!!!
        """

        assert self.name is not None

        if self.hardness is None:
            logger.println("[WARN] hardness-attribute of block '{}' not set. This will get incompatible in the future!".
                           format(self.name))
            self.hardness = 1

        if self.blast_resistance is None:
            logger.println("[WARN] blast-resistance-attribute of block {} not set. "
                           "This will get incompatible in the future!".format(self.name))
            self.blast_resistance = 1

        class Baseclass(object):
            pass

        for cls in self.baseclass:
            class Baseclass(Baseclass, cls): pass

        master = self

        class ConstructedBlock(Baseclass):
            CUSTOM_WALING_SPEED_MULTIPLIER = self.speed_multiplier

            NAME = master.name

            BLOCK_ITEM_GENERATOR_STATE = master.block_item_generator_state

            BREAKABLE = master.breakable

            BLAST_RESISTANCE = self.blast_resistance

            SOLID = self.solid

            CONDUCTS_REDSTONE_POWER = self.conducts_redstone

            CAN_MOBS_SPAWN_ON = self.can_mobs_spawn_on

            ENABLE_RANDOM_TICKS = self.random_ticks_enabled

            @staticmethod
            def get_all_model_states():
                states = self.modelstates.copy()
                [states.extend(e.get_all_model_states()) for e in self.baseclass]
                if states.count({}) != len(states):
                    while {} in states: states.remove({})
                return states

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                for baseclass in master.baseclass:
                    baseclass.__init__(self, *args, **kwargs)
                if master.create_callback: master.create_callback(self)

            def on_remove(self):
                for baseclass in master.baseclass:
                    baseclass.on_remove(self)
                if master.delete_callback: master.delete_callback(self)

            HARDNESS = master.hardness
            MINIMUM_TOOL_LEVEL = master.minmum_toollevel
            BEST_TOOLS_TO_BREAK = master.besttools

            def set_model_state(self, state):
                for baseclass in master.baseclass:
                    baseclass.set_model_state(self, state)

            def get_model_state(self):
                state = {}
                for baseclass in master.baseclass:
                    state = {**state, **baseclass.get_model_state(self)}
                return state

        if self.solid_faces:
            class ConstructedBlock(ConstructedBlock):
                self.face_solid = {side: master.solid_faces[side] if side in master.solid_faces else all(
                    [not hasattr(baseclass2, "face_solid") or baseclass2.face_solid[side] for baseclass2 in
                     master.baseclass]) for side in mcpython.util.enums.EnumSide.iterate()}

        if master.randomupdate_callback:
            class ConstructedBlock(ConstructedBlock):
                def on_random_update(self): master.randomupdate_callback(self)

        if master.update_callback:
            class ConstructedBlock(ConstructedBlock):
                def on_block_update(self):
                    for baseclass in master.baseclass:
                        baseclass.on_block_update(self)
                    master.update_callback(self)

        if master.custommodelstatefunction:
            class ConstructedBlock(ConstructedBlock):
                def get_model_state(self) -> dict:
                    return master.custommodelstatefunction(self)

        if master.interaction_callback:
            class ConstructedBlock(ConstructedBlock):
                def on_player_interact(self, player, itemstack, button, modifiers, exact_hit) -> bool:
                    return master.interaction_callback(self, player, itemstack, button, modifiers, exact_hit)

        if master.customitemstackmodifcationfunction:
            class ConstructedBlock(ConstructedBlock):
                def on_request_item_for_block(self, itemstack):
                    master.customitemstackmodifcationfunction(self, itemstack)

        if master.customblockitemmodificationfunction:
            class ConstructedBlock(ConstructedBlock):
                @classmethod
                def modify_block_item(cls, itemconstructor):
                    master.customblockitemmodificationfunction(cls, itemconstructor)

        if master.face_name:
            class ConstructedBlock(ConstructedBlock):
                MODEL_FACE_NAME = master.face_name

        if callable(self.on_class_create):
            r = self.on_class_create(ConstructedBlock)
            if r is not None: ConstructedBlock = r

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
        self.name = ("" if self.modname is None or ":" in name else (self.modname + ":")) + name
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

    @deprecation.deprecated("dev1-2", "a1.3.0")
    def setBrakeAbleFlag(self, state: bool):
        return self.setBreakAbleFlag(state)

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
        self.randomupdate_callback = function
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
        self.customsolidsidefunction = function
        if self.solid_faces is not None: self.solid_faces.clear()  # only one at a time is allowed
        return self

    def setSolidSideTableEntry(self, side, state: bool):
        """
        will set one entry in the solid face table
        :param side: the side to set
        :param state: the state to set to
        """
        if self.solid_faces is None: self.solid_faces = {}
        if self.customsolidsidefunction: self.customsolidsidefunction = None  # only one at a time is allowed
        self.solid_faces[side] = state
        return self

    def setCustomModelStateFunction(self, function):
        """
        will set the model state getter callback for the class
        :param function: the function to invoke when needed
        """
        assert callable(function)
        self.custommodelstatefunction = function
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

        def get_state(*_): return state

        self.setCustomModelStateFunction(get_state)
        return self

    def setAllModelStateInfo(self, modelstates: list):
        """
        will set the list of all possible block states of the block
        :param modelstates: the model states, as an list of dicts
        todo: implement stringifier support
        """
        assert type(modelstates) == list
        self.modelstates = modelstates
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

    def setFallable(self):
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
        self.islog = True
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

    def setHardness(self, value: float):
        """
        will set the hardness of the block
        :param value: the value of the hardness
        """
        if value == -1:
            self.setBreakAbleFlag(False)
        self.hardness = value
        return self

    def setStrenght(self, hardness: float, blast_resistance=None):
        """
        will set hardness and blasz resistance at ones
        :param hardness: value for hardness
        :param blast_resistance: value for blast resistance, if None, hardness is used
        """
        self.setHardness(hardness)
        self.setBlastResistance(blast_resistance if blast_resistance is not None else
                                hardness)
        return self

    def enableRandomTicks(self):
        self.random_ticks_enabled = True
        return self

    def setMinimumToolLevel(self, value: int):
        """
        will set the minimum needed tool level for breaking the block
        :param value: the value representing an tool level
        """
        self.minmum_toollevel = value
        return self

    def setBestTools(self, tools):
        """
        will set the tools good in breaking the block
        :param tools: an list of tools or only one tool
        """
        self.besttools = tools if type(tools) == list else [tools]
        return self

    def setCustomItemstackModificationFunction(self, function):
        """
        will set the callback to modify the itemstack generated when the block is broken
        :param function: the function to invoke
        """
        assert callable(function)
        self.customitemstackmodifcationfunction = function
        return self

    def setCustomBlockItemModification(self, function):
        """
        will set the callback for the modification call for the ItemFactory-object generated by BlockItemFactory
        :param function: the function to invoke on callback
        """
        assert callable(function)
        self.customblockitemmodificationfunction = function
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
