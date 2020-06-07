"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import typing
import uuid
import deprecation

import mcpython.block.BlockFaceState
import mcpython.block.BoundingBox
import mcpython.event.Registry
import mcpython.gui.ItemStack
import mcpython.gui.Slot
import mcpython.util.enums


class Block(mcpython.event.Registry.IRegistryContent):
    """
    base class for all blocks
    """

    # used when the player walks in an different speed on this block
    CUSTOM_WALING_SPEED_MULTIPLIER: typing.Union[float, None] = None
    TYPE: str = "minecraft:block_registry"

    # used internally to set the state the BlockItemGenerator uses
    BLOCK_ITEM_GENERATOR_STATE: typing.Union[dict, None] = None

    BREAKABLE: bool = True  # If this block can be broken in gamemode 0 and 2

    HARDNESS: float = 1  # the hardness of the block
    BLAST_RESISTANCE: float = 0  # how good it is in resisting explosions
    MINIMUM_TOOL_LEVEL: float = 0  # the minimum tool level
    BEST_TOOLS_TO_BREAK: typing.List[mcpython.util.enums.ToolType] = []  # the tools best to break

    # if the block is solid; None is unset and set by system by checking face_solid on an block instance
    SOLID: typing.Union[bool, None] = None

    # if the block can conduct redstone power; None is unset and set by system to SOLID
    CONDUCTS_REDSTONE_POWER: typing.Union[bool, None] = None

    # if mobs can spawn on the block; None is unset and set by system to SOLID
    CAN_MOBS_SPAWN_ON: typing.Union[bool, None] = None

    ENABLE_RANDOM_TICKS = False

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
        self.face_state = mcpython.block.BlockFaceState.BlockFaceState(self)
        self.block_state = None
        self.face_solid = {face: True for face in mcpython.util.enums.EnumSide.iterate()}
        self.uuid = uuid.uuid4()
        self.injected_redstone_power = {}

    def __del__(self):
        """
        used for removing the circular dependency between Block and BlockFaceState for gc
        """
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
        raise IOError()

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
        Called when the player pressed on mouse button on the block.
        :param player: the entity instance that interacts. WARNING: may not be an player instance
        :param itemstack: the itemstack hold in hand, todo: remove as it is published by player
        :param button: the button pressed
        :param modifiers: the modifiers hold during press
        :param exact_hit: where the block was hit at
        :return: if default logic should be interrupted or not
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

    def get_model_state(self) -> dict:
        """
        the active model state
        :return: the model state
        """
        return {}

    def set_model_state(self, state: dict):
        """
        sets the model state for the block
        :param state: the state to set
        """

    @deprecation.deprecated("dev1-2", "a1.3.0")
    def get_provided_slots(self, side: mcpython.util.enums.EnumSide) -> typing.List[
            typing.Union[mcpython.gui.Slot.Slot, mcpython.gui.Slot.SlotCopy]]:
        """
        gets the slots for an given side
        :param side: the side to check
        :return: an list of slot of the side
        """
        return []

    def get_provided_slot_lists(self, side: mcpython.util.enums.EnumSide):
        """
        gets slots for various reasons for an given side
        :param side: the side asked for
        :return: an tuple of lists of input slots and output slots
        """
        return [], []

    def get_view_bbox(self) -> typing.Union[mcpython.block.BoundingBox.BoundingBox,
                                            mcpython.block.BoundingBox.BoundingArea]:
        """
        used to get the bbox of the block
        :return: the bbox
        """
        return mcpython.block.BoundingBox.FULL_BLOCK_BOUNDING_BOX

    def on_request_item_for_block(self, itemstack: mcpython.gui.ItemStack.ItemStack):
        """
        used when an item is requested exactly for this block. Useful for setting custom data to the itemstack
        :param itemstack: the itemstack generated for the block
        """

    def inject_redstone_power(self, side: mcpython.util.enums.EnumSide, level: int):
        """
        used to inject an redstone value into the system
        :param side: the side from which the redstone value comes
        :param level: the level of redstone, between 0 and 15
        """
        self.injected_redstone_power[side] = level

    def get_redstone_output(self, side: mcpython.util.enums.EnumSide) -> int:
        """
        gets the redstone value on an given side
        :param side: the side to use
        :return: the value, as an integer between 0 and 15
        """
        return max(self.get_redstone_source_power(side), *self.injected_redstone_power.values())

    def get_redstone_source_power(self, side: mcpython.util.enums.EnumSide):
        """
        gets source power of an given side
        :param side: the side to use
        :return: an value between 0 and 15 representing the redstone value
        """
        return 0

    # registry setup functions, will be removed in future

    @classmethod
    def modify_block_item(cls, itemconstructor): pass  # todo: add an table for subscriptions

    @staticmethod
    def get_all_model_states() -> list: return [{}]  # todo: make attribute or external config file