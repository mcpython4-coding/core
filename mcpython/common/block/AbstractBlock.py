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
import enum
import typing
from abc import ABC

import mcpython.client.gui.Slot
import mcpython.common.block.FaceInfo
import mcpython.common.container.ResourceStack
import mcpython.common.event.api
import mcpython.common.event.Registry
import mcpython.engine.physics.BoundingBox
import mcpython.util.enums
from mcpython import shared
from mcpython.common.capability.ICapabilityContainer import ICapabilityContainer
from mcpython.common.world.datafixers.NetworkFixers import BlockDataFixer
from mcpython.engine import logger
from mcpython.engine.network.util import IBufferSerializeAble, ReadBuffer, WriteBuffer
from mcpython.util.enums import BlockRemovalReason
from mcpython.util.enums import BlockRotationType, EnumSide

if shared.IS_CLIENT:
    import mcpython.client.rendering.model.api

    class parent(
        mcpython.common.event.api.IRegistryContent,
        mcpython.client.rendering.model.api.IBlockStateRenderingTarget,
    ):
        def __init__(self):
            super(
                mcpython.client.rendering.model.api.IBlockStateRenderingTarget, self
            ).__init__()


else:
    parent = mcpython.common.event.api.IRegistryContent


class AbstractBlock(parent, ICapabilityContainer, IBufferSerializeAble, ABC):
    """
    Abstract base class for all blocks
    All block classes should extend from this

    Defines interaction thingies for blocks with the environment

    todo: add custom properties to set_creation_properties() -> injected by add_block() call
    todo: cache somehow the block state for rendering here (-> also custom relinking)
    todo: optimise block state lookup by using a array internally & using integers for references
    """

    @classmethod
    def bind_block_item_to_creative_tab(cls, tab_getter: typing.Callable):
        """
        Util method for registering this block item to a specific CreativeTab
        Will be removed when BlockItem's must be registered manually somewhere in the future
        """

        @shared.mod_loader(
            cls.NAME.split(":")[0],
            "stage:item_groups:load",
            info=f"adding block-item for {cls.NAME} to creative tabs",
        )
        def add():
            from mcpython.common.container.ResourceStack import ItemStack

            try:
                (tab_getter() if callable(tab_getter) else tab_getter).group.add(
                    ItemStack(cls.NAME)
                )
            except ValueError:
                pass

    # Internal registry type name & capability buffer name; DO NOT CHANGE
    CAPABILITY_CONTAINER_NAME = "minecraft:block"
    TYPE: str = "minecraft:block_registry"

    NETWORK_BUFFER_SERIALIZER_VERSION = 0
    NETWORK_BUFFER_DATA_FIXERS: typing.Dict[int, BlockDataFixer] = {}

    # Used when the player walks in a different speed when on this block
    CUSTOM_WALING_SPEED_MULTIPLIER: typing.Optional[float] = None

    # Used internally to set the state in BlockItemGenerator
    # todo: allow str
    # todo: remove together with BlockItemGenerator when block rendering in inventory is ready
    BLOCK_ITEM_GENERATOR_STATE: typing.Optional[dict] = None

    # If this block can be broken in gamemode 0 and 2; can be manually implemented by player interaction events
    IS_BREAKABLE: bool = True

    HARDNESS: float = 1  # The hardness of the block
    BLAST_RESISTANCE: float = 0  # How good it is in resisting explosions
    MINIMUM_TOOL_LEVEL: int = (
        0  # The minimum tool level; todo: make str & add lookup table at global space
    )
    # the tools best to break
    ASSIGNED_TOOLS: typing.Set[mcpython.util.enums.ToolType] = set()

    # If the block is solid; None is unset and set by system by checking face_solid on a default block instance
    IS_SOLID: typing.Optional[bool] = None

    # If the block can conduct redstone power; None is unset and set by system to SOLID
    CAN_CONDUCT_REDSTONE_POWER: typing.Optional[bool] = None

    # If mobs can spawn on/in the block; None is unset and set by system to SOLID
    CAN_MOBS_SPAWN_ON: typing.Optional[bool] = None
    CAN_MOBS_SPAWN_IN: bool = False

    # if the random tick function should be called if needed or not
    ENABLE_RANDOM_TICKS: bool = False

    # if entities should not collide with this block todo: make method with entity
    NO_ENTITY_COLLISION: bool = False

    # entity gravity multiplier while in the block todo: merge with above
    ENTITY_FALL_MULTIPLIER: float = 1

    # a list of block states used in debug world
    # todo: add a manager for it like mc
    DEBUG_WORLD_BLOCK_STATES: typing.List[dict] = [{}]

    DEFAULT_FACE_SOLID = 0

    @classmethod
    def modify_block_item(cls, instance):
        """
        Used to modify the item factory instance generated by BlockItemFactory for this block
        """

    def __init__(self):
        """
        Creates new Block-instance.
        Sets up basic stuff and creates the attributes
        Sub-classes may want to override the constructor and super().__init__(...) this

        For modders:
            - setup attributes here
            - fill them with data in on_block_added, then player provided data is added
        """
        super(parent, self).__init__()
        self.prepare_capability_container()

        self.position: typing.Optional[typing.Tuple[float, float, float]] = None
        self.dimension = None  # dimension instance

        self.set_to: typing.Optional[typing.Tuple[float, float, float]] = None
        self.real_hit: typing.Optional[typing.Tuple[float, float, float]] = None
        self.set_by = None  # optional player

        # Reference to the FaceInfo instance; Only present on server
        self.face_info: mcpython.common.block.FaceInfo.FaceInfo = (
            mcpython.common.block.FaceInfo.FaceInfo(self) if shared.IS_CLIENT else None
        )

        # The block state id, for deciding which model to use
        # todo: make position based
        self.block_state: typing.Optional[int] = None

        # Which faces are solid
        self.face_solid: int = self.DEFAULT_FACE_SOLID

        # The redstone power values
        self.injected_redstone_power = [0, 0, 0, 0, 0, 0]

    def is_face_solid(self, face: EnumSide):
        return self.face_solid & face.bitflag

    def write_to_network_buffer(self, buffer: WriteBuffer):
        buffer.write_int(self.NETWORK_BUFFER_SERIALIZER_VERSION)

        super(ICapabilityContainer, self).write_to_network_buffer(buffer)
        state: dict = self.get_model_state()

        buffer.write_int(len(state))
        for key, value in state.items():
            if not isinstance(value, str):
                logger.println(
                    "Skipping serialization of block "
                    + self.NAME
                    + " as key "
                    + key
                    + " has the invalid value "
                    + str(value)
                )
                continue

            buffer.write_string(key).write_string(value)

    def read_from_network_buffer(self, buffer: ReadBuffer):
        version = buffer.read_int()
        super(ICapabilityContainer, self).read_from_network_buffer(buffer)

        # Apply these fixers locally
        if version != self.NETWORK_BUFFER_SERIALIZER_VERSION:
            while version in self.NETWORK_BUFFER_DATA_FIXERS:
                fixer = self.NETWORK_BUFFER_DATA_FIXERS[version]
                write = WriteBuffer()

                if fixer.apply2stream(self, buffer, write) is True:
                    return

                buffer = ReadBuffer(write.get_data())
                version = fixer.AFTER_VERSION

        state = {
            buffer.read_string(): buffer.read_string() for _ in range(buffer.read_int())
        }
        self.set_model_state(state)

    def schedule_network_update(self):
        if shared.IS_NETWORKING:
            from mcpython.common.network.packages.WorldDataExchangePackage import (
                ChunkBlockChangePackage,
            )

            shared.NETWORK_MANAGER.send_package_to_all(
                ChunkBlockChangePackage()
                .set_dimension(self.dimension)
                .change_position(self.position, self, update_only=True),
                not_including=shared.NETWORK_MANAGER.client_id,
            )

    def set_creation_properties(
        self, set_to=None, real_hit=None, player=None, state=None
    ):
        """
        Helper function for setting given properties of the block in one function call
        :return: the block
        """
        self.set_to = set_to
        self.real_hit = real_hit
        self.set_by = player
        if state is not None:
            self.set_model_state(state)
        return self

    def get_rotated_variant(self, rotation_type: BlockRotationType) -> "AbstractBlock":
        return self.__class__()

    # block events

    def on_block_added(self):
        """
        Called when the block is added to the world
        """

    def on_block_remove(self, reason: BlockRemovalReason):
        """
        Called when the block is removed
        Not cancelable. Block show data is removed, but the "current" state of the block is still stored.
        After this, the block might stay for some time in memory, but may also get deleted.
        :param reason: the reason of the removal, defaults to BlockRemovalReason.UNKNOWN
        todo: use reasons were possible
        todo: add cancel-able variant
        """

    def on_random_update(self):
        """
        Called on random update
        Needs ENABLE_RANDOM_TICKS to be set to True for being invoked
        """

    def on_block_update(self):
        """
        Called when an near-by block-position is updated by setting/removing an block
        Invokes a redstone update by default. Call if needed.
        todo: add optional source of update
        todo: add at source a method to cancel update calling
        """
        self.on_redstone_update()

    def on_redstone_update(self):
        """
        Special event called in order to update redstone state. Not used by vanilla at the moment
        Is also invoked o "normal" block update
        """

    def on_player_interaction(
        self,
        player,
        button: int,
        modifiers: int,
        hit_position: tuple,
        itemstack,
    ):
        """
        Called when the player pressed on mouse button on the block.
        :param player: the entity instance that interacts. WARNING: may not be an player instance
        :param button: the button pressed
        :param modifiers: the modifiers hold during press
        :param hit_position: where the block was hit at
        :param itemstack: the itemstack hit with
        :return: if default logic should be interrupted or not
        """
        return False

    def on_no_collision_collide(self, entity, previous: bool):
        """
        Called when NO_COLLIDE is True and the entity is in the block every collision check [so more than ones per tick]
        :param entity: the entity entering the block
        :param previous: if the player was in the block before
        """

    def get_item_saved_state(self) -> typing.Any:
        """
        Used by item system to get the state of the block for storing in the item
        Normally, parts of the block state if needed
        Defaults to no data (None)
        """

    def set_item_saved_state(self, state):
        """
        Previous saved state of another block instance
        Only called when the state is not None [so you need to override get_item_saved_state() to get this called]
        """

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
        The active model state
        Maybe want to cache it somewhere :-/
        """
        return {}

    def set_model_state(self, state: dict):
        """
        Sets the model state for the block
        :param state: the state to set, as an dict

        WARNING: do NOT raise an error if more data is provided, as sub-classes may want to add own data
        WARNING: data may not contain all data saved for some reason :-/
        """

    def get_view_bbox(
        self,
    ) -> mcpython.engine.physics.BoundingBox.AbstractBoundingBox:
        """
        Used to get the bbox of the block for ray collision
        :return: the bbox instance
        """
        return (
            mcpython.engine.physics.BoundingBox.FULL_BLOCK_BOUNDING_BOX
        )  # per default, every block is full

    def get_collision_bbox(
        self,
    ) -> mcpython.engine.physics.BoundingBox.AbstractBoundingBox:
        """
        Used to get the bbox of the block for physical body collision
        :return: the bbox instance
        """
        return self.get_view_bbox()

    def on_request_item_for_block(
        self, itemstack: mcpython.common.container.ResourceStack.ItemStack
    ):
        """
        Used when an item is requested exactly for this block. Useful for setting custom data to the itemstack
        Only modify the itemstack, not return it!
        :param itemstack: the itemstack generated for the block
        """
        if not itemstack.is_empty():
            itemstack.item.stored_block_state = self.get_item_saved_state()

    # Redstone API

    def inject_redstone_power(self, side: mcpython.util.enums.EnumSide, level: int):
        """
        Used to inject a redstone value into the system
        :param side: the side from which the redstone value comes
        :param level: the level of redstone, between 0 and 15
        """
        self.injected_redstone_power[side.index] = level

    def get_redstone_output(self, side: mcpython.util.enums.EnumSide) -> int:
        """
        Gets the redstone value on an given side
        :param side: the side to use
        :return: the value, as an integer between 0 and 15
        """
        return max(self.get_redstone_source_power(side), *self.injected_redstone_power)

    def get_redstone_source_power(self, side: mcpython.util.enums.EnumSide) -> int:
        """
        Gets source power of a given side
        :param side: the side to use
        :return: a value between 0 and 15 representing the redstone value
        """
        return 0

    def get_real_redstone_output(self, side: mcpython.util.enums.EnumSide) -> int:
        return max(
            self.get_redstone_source_power(side),
            self.injected_redstone_power[side.index],
        )

    def is_connecting_to_redstone(self, side: mcpython.util.enums.EnumSide) -> bool:
        return False

    # Debug methods

    def __repr__(self):
        return "MinecraftBlock::{}(internal={},position={},dimension={},block_state_entry={})".format(
            self.NAME,
            super().__repr__(),
            self.position,
            self.dimension,
            self.block_state,
        )

    def copy(self):
        instance = type(self)()
        instance.set_model_state(self.get_model_state())
        return instance
