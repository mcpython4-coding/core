"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import gui.ItemStack
import block.Block
import block.IFallingBlock as FallingBlock
import block.ILog as ILog
import util.enums
import block.ISlab as ISlab
import block.IHorizontalOrientableBlock as IHorizontalOrientableBlock


# todo: implement inventory opening notations


class BlockFactory:
    def __init__(self):
        self.name = None
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
        self.besttools = []
        self.speed_multiplier = None
        self.block_item_generator_state = None
        self.face_name = "facing"

        self.customsolidsidefunction = None
        self.custommodelstatefunction = None
        self.customitemstackmodifcationfunction = None
        self.customblockitemmodificationfunction = None

        self.islog = False

        self.baseclass = [block.Block.Block]

    def copy(self):
        block = BlockFactory()
        block.__dict__ = self.__dict__
        return block

    def finish(self, register=True):
        modname, blockname = tuple(self.name.split(":"))
        if modname not in G.modloader.mods: modname = "minecraft"
        G.modloader.mods[modname].eventbus.subscribe("stage:block:load", self._finish, register,
                                                     info="loading block {}".format(blockname))

    def _finish(self, register):

        class baseclass(object): pass

        for cls in self.baseclass:
            class baseclass(baseclass, cls): pass

        master = self

        class ConstructedBlock(baseclass):
            CUSTOM_WALING_SPEED_MULTIPLIER = self.speed_multiplier

            NAME = master.name

            BLOCK_ITEM_GENERATOR_STATE = master.block_item_generator_state

            BREAKABLE = master.breakable

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
                         master.baseclass]) for side in util.enums.EnumSide.iterate()}

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
                    return master.interaction_callback(self, itemstack, button, modifiers)

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

        if register: G.registry.register(ConstructedBlock)

        return ConstructedBlock

    def setName(self, name: str):
        self.name = name
        return self

    def setCreateCallback(self, function):
        self.create_callback = function
        return self

    def setDeleteCallback(self, function):
        self.delete_callback = function
        return self

    def setBrakeAbleFlag(self, state: bool):
        self.breakable = state
        return self

    def setRandomUpdateCallback(self, function):
        self.randomupdate_callback = function
        return self

    def setUpdateCallback(self, function):
        self.update_callback = function
        return self

    def setCustomSolidSideFunction(self, function):
        self.customsolidsidefunction = function
        if self.solid_faces: self.solid_faces = {}  # only one at a time is allowed
        return self

    def setSolidSideTableEntry(self, side, state: bool):
        if self.solid_faces is None: self.solid_faces = {}
        if self.customsolidsidefunction: self.customsolidsidefunction = None  # only one at a time is allowed
        self.solid_faces[side] = state
        return self

    def setCustomModelStateFunction(self, function):
        self.custommodelstatefunction = function
        return self

    def setDefaultModelState(self, state: dict):
        if type(state) == str:
            state = {e.split("=")[0]: e.split("=")[1] for e in state.split(",")}
        def get_state(*_): return state
        self.setCustomModelStateFunction(get_state)
        return self

    def setAllModelStateInfo(self, modelstates):
        self.modelstates = modelstates
        return self

    def setInteractionCallback(self, function):
        self.interaction_callback = function
        return self

    def setFallable(self):
        self.baseclass.append(FallingBlock.IFallingBlock)
        return self

    def setAllSideSolid(self, state):
        for face in util.enums.EnumSide.iterate():
            self.setSolidSideTableEntry(face, state)
        return self

    def setLog(self):
        self.islog = True
        if ILog.ILog not in self.baseclass:
            self.baseclass.append(ILog.ILog)
        return self

    def setSlab(self):
        if ISlab.ISlab not in self.baseclass:
            self.baseclass.append(ISlab.ISlab)
        return self

    def setHardness(self, value: float):
        self.hardness = value
        return self

    def setMinimumToolLevel(self, value: int):
        self.minmum_toollevel = value
        return self

    def setBestTools(self, tools):
        self.besttools = tools
        return self

    def setCustomItemstackModificationFunction(self, function):
        self.customitemstackmodifcationfunction = function
        return self

    def setCustomBlockItemModification(self, function):
        self.customblockitemmodificationfunction = function
        return self

    def setSpeedMultiplier(self, factor):
        self.speed_multiplier = factor
        return self

    def setBlockItemGeneratorState(self, state: dict):
        self.block_item_generator_state = state
        return self

    def setHorizontalOrientable(self, face_name="facing"):
        self.baseclass.append(IHorizontalOrientableBlock.IHorizontalOrientableBlock)
        self.face_name = face_name
        return self

