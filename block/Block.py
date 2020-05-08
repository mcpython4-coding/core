"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import gui.ItemStack
import item.ItemTool
import block.BoundingBox
import block.BlockFaceState
import event.Registry
import uuid
import util.enums


class Block(event.Registry.IRegistryContent):
    """
    base class for all blocks
    """

    CUSTOM_WALING_SPEED_MULTIPLIER = None  # used when the player walks in an different speed on this block
    TYPE = "minecraft:block_registry"

    BLOCK_ITEM_GENERATOR_STATE = None  # used internally to set the state the BlockItemGenerator uses

    BREAKABLE = True  # If this block can be broken in gamemode 0 and 2

    HARDNESS = 1
    MINIMUM_TOOL_LEVEL = 0
    BEST_TOOLS_TO_BREAK = []

    SOLID = None  # if the block is solid; None is unset and set by system by checking face_solid on an block instance

    CONDUCTS_REDSTONE_POWER = None  # if the block can conduct redstone power; None is unset and set by system to SOLID

    CAN_MOBS_SPAWN_ON = None  # if mobs can spawn on the block; None is unset and set by system to SOLID

    def __init__(self, position: tuple, set_to=None, real_hit=None, state=None):
        """
        creates new Block
        :param position: the position to create the block on
        :param set_to: when the block is set to an block, these parameter contains where
        :param real_hit: were the block the user set to was hit on
        """
        self.position = position
        self.set_to = set_to
        self.real_hit = real_hit
        if state is not None: self.set_model_state(state)
        self.face_state = block.BlockFaceState.BlockFaceState(self)
        self.block_state = None
        self.face_solid = {face: True for face in util.enums.EnumSide.iterate()}
        self.uuid = uuid.uuid4()
        self.injected_redstone_power = {}

    def __del__(self):
        # remove circular link of Block <-> BlockFaceState
        del self.face_state

    # block events

    def on_remove(self):
        """
        called when the block is removed
        """

    def on_random_update(self):
        """
        called on random update
        """

    def on_block_update(self):
        """
        called when an near-by block-position is updated by setting/removing an block
        """
        self.on_redstone_update()

    def on_redstone_update(self):
        """
        special event called in order to update redstone state. Not used by vanilla at the moment
        """

    def on_player_interact(self, player, itemstack, button, modifiers, exact_hit) -> bool:
        """
        called when the player pressed an mouse button on the block
        :param player: the entity instance that interacts. WARNING: may not be an player instance
        :param itemstack: the itemstack hold in hand, todo: remove
        :param button: the button pressed
        :param modifiers: the modifiers hold during press
        :param exact_hit: where the block was hit at
        :return: if default logic should be interrupted
        """
        return False

    def save(self):
        """
        :return: an pickle-able object representing the whole block, not including inventories
        """
        return self.get_model_state()

    def load(self, data):
        """
        loads block data
        :param data:  the data saved by save()
        """
        self.set_model_state(data)

    # block status functions

    def get_inventories(self):
        """
        called to get an list of inventories
        """
        return []

    def get_model_state(self) -> dict: return {}

    def set_model_state(self, state: dict): pass

    def get_provided_slots(self, side):
        return []

    def get_view_bbox(self):
        return block.BoundingBox.FULL_BLOCK_BOUNDING_BOX

    def on_request_item_for_block(self, itemstack):
        pass

    def inject_redstone_power(self, side, level: int):
        self.injected_redstone_power[side] = level

    def get_redstone_output(self, side):
        return max(self.get_redstone_source_power(side), *self.injected_redstone_power.values())

    def get_redstone_source_power(self, side):
        return 0

    # registry setup functions

    @classmethod
    def modify_block_item(cls, itemconstructor): pass  # todo: add an table for subscriptions

    @staticmethod
    def get_all_model_states() -> list: return [{}]  # todo: make attribute

