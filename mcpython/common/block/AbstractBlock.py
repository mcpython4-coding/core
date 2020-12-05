"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from abc import ABC
import typing
import uuid
import enum

import mcpython.common.block.BlockFaceState
import mcpython.common.block.BoundingBox
import mcpython.common.event.Registry
import mcpython.common.container.ItemStack
import mcpython.client.gui.Slot
import mcpython.util.enums
import pickle


class BlockRemovalReason(enum.Enum):
    UNSET = 0
    PLAYER_REMOVAL = 1
    PISTON_MOTION = 2
    EXPLOSION = 3
    ENTITY_PICKUP = 4


class AbstractBlock(mcpython.common.event.Registry.IRegistryContent):
    """
    Abstract base class for all blocks
    All block classes should extend from this
    """

    TYPE: str = "minecraft:block_registry"  # internal registry type

    # used when the player walks in an different speed on this block
    CUSTOM_WALING_SPEED_MULTIPLIER: typing.Union[float, None] = None

    # used internally to set the state the BlockItemGenerator uses
    BLOCK_ITEM_GENERATOR_STATE: typing.Union[dict, None] = None

    # If this block can be broken in gamemode 0 and 2
    IS_BREAKABLE: bool = True

    HARDNESS: float = 1  # the hardness of the block
    BLAST_RESISTANCE: float = 0  # how good it is in resisting explosions
    MINIMUM_TOOL_LEVEL: float = 0  # the minimum tool level
    ASSIGNED_TOOLS: typing.List[
        mcpython.util.enums.ToolType
    ] = []  # the tools best to break

    # if the block is solid; None is unset and set by system by checking face_solid on an block instance
    # WARNING: in the future, these auto-set will be removed todo: do so
    IS_SOLID: typing.Union[bool, None] = None

    # if the block can conduct redstone power; None is unset and set by system to SOLID
    CAN_CONDUCT_REDSTONE_POWER: typing.Union[bool, None] = None

    # if mobs can spawn on the block; None is unset and set by system to SOLID
    CAN_MOBS_SPAWN_ON: typing.Union[bool, None] = None
    CAN_MOBS_SPAWN_IN = False

    ENABLE_RANDOM_TICKS = (
        False  # if the random tick function should be called if needed or not
    )

    NO_ENTITY_COLLISION = False
    ENTITY_FALL_MULTIPLIER = 1

    DEBUG_WORLD_BLOCK_STATES = [{}]

    def __init__(self):
        """
        creates new Block-instance.
        sets up basic stuff and creates the attributes
        Sub-classes may want to override the constructor and super().__init__(...) this
        """
        self.position = None
        self.dimension = None
        self.set_to = None
        self.real_hit = None
        self.face_state = mcpython.common.block.BlockFaceState.BlockFaceState(self)
        self.block_state = None
        self.set_by = None
        self.face_solid = {
            face: True for face in mcpython.util.enums.EnumSide.iterate()
        }
        self.uuid = uuid.uuid4()
        self.injected_redstone_power = {}

    def set_creation_properties(
        self, set_to=None, real_hit=None, player=None, state=None
    ):
        self.set_to = set_to
        self.real_hit = real_hit
        self.set_by = player
        if state is not None:
            self.set_model_state(state)
        return self

    # block events

    def on_block_added(self):
        pass

    def on_block_remove(self, reason: BlockRemovalReason):
        """
        Called when the block is removed
        Not cancelable. Block show data is removed, but the "current" state of the block is still stored.
        After this, the block might stay for some time in memory, but may also get deleted.
        :param reason: the reason of the removal
        """

    def on_random_update(self):
        """
        Called on random update
        Needs ENABLE_RANDOM_TICKS to be set to True for being invoked
        """

    def on_block_update(self):
        """
        Called when an near-by block-position is updated by setting/removing an block
        Invokes an redstone update by default. Call if needed.
        """
        self.on_redstone_update()

    def on_redstone_update(self):
        """
        Special event called in order to update redstone state. Not used by vanilla at the moment
        Is also invoked on "normal" block update
        """

    def on_player_interaction(
        self, player, button: int, modifiers: int, hit_position: tuple
    ):
        """
        Called when the player pressed on mouse button on the block.
        :param player: the entity instance that interacts. WARNING: may not be an player instance
        :param button: the button pressed
        :param modifiers: the modifiers hold during press
        :param hit_position: where the block was hit at
        :return: if default logic should be interrupted or not
        """
        return False

    def on_no_collision_collide(self, player, previous: bool):
        """
        Called when NO_COLLIDE is True and the player is in the block every collision check
        :param player: the player entering the block
        :param previous: if the player was in the block before
        """

    def get_save_data(self):
        return self.get_model_state()

    def dump_data(self) -> bytes:
        """
        :return: bytes representing the whole block, not including inventories
        todo: add an saver way of doing this!
        """
        return pickle.dumps(self.get_save_data())

    def load_data(self, data):
        """
        loads block data
        :param data:  the data saved by get_save_data()
        WARNING: if not providing DataFixers for old mod versions, these data may get very old!
        todo: add an saver way of doing this!
        """
        self.set_model_state(data)

    def inject(self, data: bytes):
        """
        loads block data
        :param data:  the data saved by save()
        WARNING: if not providing DataFixers for old mod versions, these data may get very old!
        """
        self.load_data(pickle.loads(data) if type(data) == bytes else data)

    # block status functions

    def get_inventories(self):
        """
        Called to get an list of inventories
        FOR MODDERS: use get_provided_slot_lists() where possible as it is the more "save" way to interact with the block
        todo: move to capabilities
        """
        return []

    def get_provided_slot_lists(self, side: mcpython.util.enums.EnumSide):
        """
        Similar to get_inventories, but specifies only slots & the side on which the interaction can happen.
        Useful for e.g. furnaces which can get fuel from the side, but from top the item to smelt.
        gets slots for various reasons for an given side
        :param side: the side asked for
        :return: an tuple of lists of input slots and output slots
        Slots may be in inputs AND output.
        todo: make default return None, None
        todo: move to capabilities
        """
        return [], []

    def get_model_state(self) -> dict:
        """
        the active model state
        :return: the model state as an dict
        """
        return {}

    def set_model_state(self, state: dict):
        """
        sets the model state for the block
        :param state: the state to set as an dict

        WARNING: do NOT raise an error if more data is provided, as sub-classes may want to add own data
        """

    def get_view_bbox(
        self,
    ) -> typing.Union[
        mcpython.common.block.BoundingBox.BoundingBox,
        mcpython.common.block.BoundingBox.BoundingArea,
    ]:
        """
        used to get the bbox of the block for ray collision
        :return: the bbox instance
        """
        return (
            mcpython.common.block.BoundingBox.FULL_BLOCK_BOUNDING_BOX
        )  # per default, every block is full

    def get_collision_bbox(
        self,
    ) -> typing.Union[
        mcpython.common.block.BoundingBox.BoundingBox,
        mcpython.common.block.BoundingBox.BoundingArea,
    ]:
        """
        used to get the bbox of the block for phyical body collision
        :return: the bbox instance
        """
        return self.get_view_bbox()

    def on_request_item_for_block(
        self, itemstack: mcpython.common.container.ItemStack.ItemStack
    ):
        """
        used when an item is requested exactly for this block. Useful for setting custom data to the itemstack
        :param itemstack: the itemstack generated for the block
        """

    # Redstone API

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
        return max(
            self.get_redstone_source_power(side), *self.injected_redstone_power.values()
        )

    def get_redstone_source_power(self, side: mcpython.util.enums.EnumSide):
        """
        gets source power of an given side
        :param side: the side to use
        :return: an value between 0 and 15 representing the redstone value
        """
        return 0
