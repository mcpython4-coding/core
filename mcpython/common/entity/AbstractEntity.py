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
import io
import traceback
import typing
import uuid
from abc import ABC

import mcpython.common.container.ResourceStack
import mcpython.common.entity.DamageSource
import mcpython.common.entity.EntityManager
import mcpython.common.event.api
import mcpython.common.event.Registry
import mcpython.util.math
from mcpython import shared
from mcpython.common.capability.ICapabilityContainer import ICapabilityContainer
from mcpython.common.world.datafixers.NetworkFixers import EntityDataFixer
from mcpython.engine import logger
from mcpython.engine.network.util import IBufferSerializeAble, ReadBuffer, WriteBuffer
from mcpython.engine.physics.AxisAlignedBoundingBox import EMPTY_BOUNDING_BOX


class AbstractEntity(
    mcpython.common.event.api.IRegistryContent,
    ICapabilityContainer,
    IBufferSerializeAble,
    ABC,
):
    """
    Base class for every entity in the game

    MUST be implemented by all entities scheduled to be used with the EntityManager system

    Allows capability injects & lookups via the capability API

    DO NOT CHANGE STUFF AT THE FILE HEAD BY SUBCLASSES. IT WILL BREAK THE UNDERLYING STUFF

    Capabilities are auto-saved and this behaviour cannot be disabled currently.
    """

    # ---------------------
    # Internal Region START
    # ---------------------

    CAPABILITY_CONTAINER_NAME = "minecraft:entity"
    TYPE = "minecraft:entity"

    # -------------------
    # Internal Region END
    # -------------------

    VERSION = 0
    DATA_FIXERS: typing.Dict[int, EntityDataFixer] = {}

    # If the entity can be used in /summon-command
    SUMMON_ABLE = True

    @classmethod
    def create_new_entity(cls, position, *args, dimension=None, **kwargs):
        """
        Creates a new entity and set up it correctly for later use
        :param position: the position to create at
        :param args: args to send to the constructor
        :param dimension: the dimension to spawn in
        :param kwargs: kwargs to send to the constructor
        :return: the created entity
        for moder: use this rather than raw constructor as it is the more "safe" way of doing it

        Does not spawn the entity in the real dimension
        """
        entity = cls(*args, dimension=dimension, **kwargs)
        entity.position = position
        return entity

    @classmethod
    async def create_from_buffer(cls, buffer: ReadBuffer):
        instance = cls()
        await instance.read_from_network_buffer(buffer)
        return instance

    @classmethod
    def init_renderers(cls):
        """
        Use this to create your entity renderers
        Invoked only on client
        """

    def __init__(self, dimension=None):
        """
        Creates a new entity for the world
        for moder: you SHOULD implement a custom constructor which set the bellow values to "good" values

        For creating entities, use create_new_entity() - it is far more saver and does some internal stuff
        """
        super().__init__()

        self.dimension = (
            shared.world.get_active_dimension()
            if dimension is None and shared.world is not None
            else dimension
        )
        self.unsafe_position = (0, 0, 0)  # todo: move to nbt
        self.rotation = (0, 0, 0)  # todo: move to nbt
        self.hearts = 0  # todo: move to nbt
        self.chunk = (
            None
            if self.dimension is None
            else self.dimension.get_chunk_for_position(self.unsafe_position)
        )
        self.uuid = uuid.uuid4()

        self.entity_height = (
            0  # the height of the entity, for positioning the child entity
        )

        self.parent = None  # the entity this is riding todo: move into nbt
        self.child = None  # the entity this is ridden by  todo: move into nbt

        # dict holding entity data, automatically saved & loaded, when loading, data is put ontop of the existing dict
        self.nbt_data = {
            "motion": (0, 0, 0),
            "invulnerable": False,
        }

        self.dead = False

    def get_collision_box(self):
        return EMPTY_BOUNDING_BOX

    async def read_from_network_buffer(self, buffer: ReadBuffer):
        version = buffer.read_uint()

        if version != self.VERSION:
            while version in self.DATA_FIXERS and version != self.VERSION:
                fixer = self.DATA_FIXERS[version]
                write = WriteBuffer()

                try:
                    if await fixer.apply2stream(self, buffer, write) is True:
                        break
                except:  # lgtm [py/catch-base-exception]
                    logger.print_exception(
                        f"during applying data fixer to block {self.NAME}; discarding data"
                    )
                    return

                buffer.stream = io.BytesIO(write.get_data())
                version = fixer.AFTER_VERSION

            # Our fixed stream belongs now here...

        await super(
            ICapabilityContainer, self
        ).read_from_network_buffer(  # lgtm [py/super-not-enclosing-class]
            buffer
        )
        dim_name = buffer.read_string()
        self.dimension = shared.world.get_dimension_by_name(
            dim_name if dim_name != "" else "overworld"
        )

        self.teleport(tuple((buffer.read_float() for _ in range(3))))
        self.rotation = list((buffer.read_float() for _ in range(3)))
        self.uuid = buffer.read_uuid()

        # todo: do something with this!
        if buffer.read_bool():
            parent_uuid = buffer.read_uuid()

        if buffer.read_bool():
            child_uuid = buffer.read_uuid()

        self.nbt_data["motion"] = tuple((buffer.read_float() for _ in range(3)))
        self.nbt_data["invulnerable"] = buffer.read_bool()

    async def write_to_network_buffer(self, buffer: WriteBuffer):
        buffer.write_uint(self.VERSION)

        await super(
            ICapabilityContainer, self
        ).write_to_network_buffer(  # lgtm [py/super-not-enclosing-class]
            buffer
        )
        buffer.write_string(
            self.dimension.get_name() if self.dimension is not None else ""
        )

        if len(self.unsafe_position) != 3 or len(self.rotation) != 3:
            raise RuntimeError("invalid player configuration")

        for e in self.unsafe_position:
            buffer.write_float(e)

        for e in self.rotation:
            buffer.write_float(e)

        buffer.write_uuid(self.uuid)

        buffer.write_bool(self.parent is not None)
        if self.parent is not None:
            buffer.write_uuid(self.parent.uuid)

        buffer.write_bool(self.child is not None)
        if self.child is not None:
            buffer.write_uuid(self.child.uuid)

        for e in self.nbt_data["motion"]:
            buffer.write_float(e)

        if len(self.nbt_data["motion"]) != 3:
            raise RuntimeError("invalid player configuration")

        buffer.write_bool(self.nbt_data["invulnerable"])

    def add_to_chunk(self):
        if self.dimension is not None:
            self.dimension.get_chunk_for_position(tuple(self.position)).entities.add(
                self
            )

    def remove_from_chunk(self):
        if (
            self.dimension is not None
            and self
            in self.dimension.get_chunk_for_position(tuple(self.position)).entities
        ):
            self.dimension.get_chunk_for_position(tuple(self.position)).entities.remove(
                self
            )

    def __del__(self):
        if not hasattr(self, "chunk"):
            return
        del self.chunk

    def __str__(self):
        return "{}(dim={},pos={},rot={})".format(
            type(self).__name__, self.dimension.id, self.position, self.rotation
        )

    # system for moving

    def get_position(self):
        return self.unsafe_position

    def set_position(self, position: tuple):
        if type(position) not in (tuple, list, set):
            logger.println(
                "[FATAL] invalid position for set_position() on {} '{}'".format(
                    self, position
                )
            )
            traceback.print_stack()
            return

        self.teleport(position)

    position = property(get_position, set_position)

    def get_motion(self):
        return self.nbt_data.setdefault("motion", (0, 0, 0))

    def set_motion(self, motion: tuple):
        self.nbt_data["motion"] = motion

    def get_dimension(self):
        return self.dimension

    movement = motion = property(get_motion, set_motion)

    # only for some small use-cases. WARNING: will  N O T  do any internal handling for updating the position
    def set_position_unsafe(self, position: tuple):
        self.unsafe_position = position

    def teleport(self, position, dimension=None, force_chunk_save_update=False):
        """
        Called when the entity should be teleported
        :param position: the position to teleport to
        :param dimension: to which dimension-id to teleport to, if None, no dimension change is used
        :param force_chunk_save_update: if the system should force updating were player data is stored
        """
        if self.chunk is None:
            sector_before = mcpython.util.math.position_to_chunk(self.position)
        else:
            sector_before = self.chunk.position

        if self.chunk is None:
            before_dim = None
        else:
            before_dim = self.chunk.get_dimension().get_dimension_id()

        if dimension is None:
            dimension_id = before_dim if before_dim is not None else 0
        else:
            dimension_id = dimension

        sector_after = mcpython.util.math.position_to_chunk(position)

        if (
            sector_before != sector_after
            or before_dim != dimension_id
            or force_chunk_save_update
        ):
            self.remove_from_chunk()
            self.unsafe_position = position
            self.add_to_chunk()

        else:
            self.unsafe_position = position

    # interaction functions

    def tell(self, msg: str):
        """
        Tells the entity an message. Not intended to inter-mod com
        Should be used by say-commands
        :param msg: the msg to tell
        """

    async def kill(
        self,
        drop_items=True,
        kill_animation=True,
        damage_source: mcpython.common.entity.DamageSource.DamageSource = None,
        force=False,
        internal=False,
    ):
        """
        Called to kill the entity [remove the entity from world]
        THIS IS THE FINAL REMOVAL METHOD. THIS DOES NOT HAVE MUCH CHECKS IF IT SHOULD BE ABLE TO BE KILLED!

        Is not affected by nbt-tag "invulnerable". Must be handled separately.
        :param drop_items: if items should be dropped
        :param kill_animation: if the kill animation should be played
        :param damage_source: the source of the damage
        :param force: if it should be forced or not
        :param internal: when this is set, this is a normal de-spawn / unload call
        todo: drop items if selected
        todo: play kill animation if selected
        """
        self.remove_from_chunk()

        if (
            shared.entity_manager is not None
            and self.uuid in shared.entity_manager.entity_map
        ):
            del shared.entity_manager.entity_map[self.uuid]

        self.dead = True

    async def pick_up_item(
        self, itemstack: mcpython.common.container.ResourceStack.ItemStack
    ) -> bool:
        """
        Let the entity pick up a item and insert it into its inventory
        :param itemstack: the itemstack to use
        :return: if it was successful or not

        for moder: see world/player.py as an example how this could work
        Subclasses should implement this when they have an inventory for it
        """
        return False

    def damage(
        self, damage, reason: mcpython.common.entity.DamageSource.DamageSource = None
    ):
        """
        Applies damage to the entity
        FOR MODER:
            This function is a default implementation. For a working example, see the player entity
            - you may want to apply armor calculation code
            - you may want to override this method for a custom implementation
        :param damage: the damage to apply
        :param reason: the reason for the damage, as a DamageSource-instance, or None
        """
        self.hearts -= damage
        if self.hearts <= 0:
            shared.tick_handler.schedule_once(self.kill())

    def on_interact(self, player, button: int, modifiers: int, itemstack) -> bool:
        """
        Called when the player tries to interact with the entity by clicking on it
        Damage should not be calculated here
        :param player: the player doing so, WARNING: only type-hinted for entity, not world/player.py:Player
        :param button: the button used
        :param modifiers: the modifiers used
        :param itemstack: the itemstack held in hand
        :return: if the normal behaviour should be canceled or not

        todo: make called
        """
        return False

    def get_inventories(self) -> typing.Iterable:
        """
        Will return an list of all currently arrival inventories for this entity
        """
        return tuple()

    def on_inventory_cleared(self):
        """
        Called when the entity inventory should be cleared
        Defaults to clearing all inventories from get_inventories()
        """
        for inv in self.get_inventories():
            inv.clear()

    # system events

    def draw(self):
        """
        Called to draw the entity in the world
        Invoked in the correct rendering phase
        """

    async def tick(self, dt: float):
        """
        Called every tick to update the entity
        Can be used to update animations, movement, do path finding stuff, damage other entities, ...
        """
        x, y, z = self.position
        dx, dy, dz = self.nbt_data["motion"]
        self.teleport((x + dx, y + dy, z + dz))

    # data serialisation

    def dump(self):
        """
        Dumps the entity into an save-able version
        :return: an pickle-able version, excluding position, rotation and harts, should include inventory serializer
            calls to make sure that everything works
        The nbt data is auto-saved
        Only extra stuff should be saved!
        """

    def load(self, data):
        """
        Loads data into the entity, previous saved
        For Moder:
            you CAN include a version entry to make sure you can fix the data version
        :param data: the data to load from
        The nbt data is auto-loaded before this event is called
        WARNING: data may be None when dump() was at some point not implemented
        """
