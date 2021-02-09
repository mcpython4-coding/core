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
import mcpython.common.container.ItemStack
from mcpython import shared, logger
import mcpython.common.event.Registry
import mcpython.common.entity.EntityHandler
import uuid
import mcpython.util.math
import traceback
import mcpython.common.entity.DamageSource


class AbstractEntity(mcpython.common.event.Registry.IRegistryContent):
    """
    Dummy class for every entity,
    only used by the player at the moment (as no more entities are implemented)
    feel free to use, general functions for cross-mod work
    """

    TYPE = "minecraft:entity"

    SUMMON_ABLE = True  # if the entity can be used in /summom-command

    @classmethod
    def create_new(cls, position, *args, **kwargs):
        """
        creates an new entity and set up it correctly for later use
        :param position: the position to create at
        :param args: args to send to the constructor
        :param kwargs: kwargs to send to the constructor
        :return: the created entity
        todo: make added to world
        for moder: use this rather than raw constructor as it is the more "safe" way of doing it
        """
        entity = cls(*args, **kwargs)
        entity.position = position
        return entity

    @classmethod
    def init_renderers(cls):
        pass

    def __init__(self, dimension=None):
        """
        creates an new entity for the world
        for moder: you SHOULD implement an custom constructor which set the bellow values to an "good" value
        """
        self.dimension = (
            shared.world.get_active_dimension() if dimension is None else dimension
        )
        self.unsafe_position = (0, 0, 0)  # todo: move to nbt
        self.rotation = (0, 0, 0)  # todo: move to nbt
        self.harts = 0  # todo: move to nbt
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

        self.nbt_data = {
            "motion": (0, 0, 0),
            "invulnerable": False,
        }  # dict holding entity data, automatically saved & loaded, when loading, data is put ontop of the existing dict

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
            traceback.print_exc()
            return
        self.teleport(position)

    position = property(get_position, set_position)

    def get_motion(self):
        return self.nbt_data.setdefault("motion", (0, 0, 0))

    def set_motion(self, motion: tuple):
        self.nbt_data["motion"] = motion

    movement = motion = property(get_motion, set_motion)

    # only for some small use-cases. WARNING: will  N O T  do any internal handling for updating the position
    def set_position_unsafe(self, position: tuple):
        self.unsafe_position = position

    def teleport(self, position, dimension=None, force_chunk_save_update=False):
        """
        called when the entity should be teleported
        :param position: the position to teleport to
        :param dimension: to which dimension-id to teleport to, if None, no dimension change is used
        :param force_chunk_save_update: if the system should force to update were player data is stored
        """
        if not shared.event_handler.call_cancelable(
            "world:entity:teleport", self, dimension, force_chunk_save_update
        ):
            return
        if self.chunk is None:
            sector_before = mcpython.util.math.position_to_chunk(self.position)
        else:
            sector_before = self.chunk.position
        if self.chunk is None:
            before_dim = None
        else:
            before_dim = self.chunk.dimension.id
        if dimension is None:
            dimension_id = before_dim if before_dim is not None else 0
        else:
            dimension_id = dimension
        dimension = shared.world.get_dimension(dimension_id)
        self.unsafe_position = position
        if dimension is None:
            return
        sector_after = mcpython.util.math.position_to_chunk(self.position)
        if (
            sector_before != sector_after
            or before_dim != dimension_id
            or force_chunk_save_update
        ):
            if self.chunk and self in self.chunk.entities:
                self.chunk.entities.remove(self)
            self.chunk = dimension.get_chunk_for_position(self.position)
            self.chunk.entities.add(self)
        shared.event_handler.call("world:entity:teleport:post", self)

    # interaction functions

    def tell(self, msg: str):
        """
        tells the entity an message. Not intended to inter-mod com
        Should be used by say-commands
        :param msg: the msg to tell
        """

    def kill(
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
        :param internal: when this is set, this is a normal despawn / unload call
        todo: drop items if selected
        todo: play kill animation if selected
        """
        if self.chunk is not None and self in self.chunk.entities:
            self.chunk.entities.remove(self)

        if self.uuid in shared.entity_handler.entity_map:
            del shared.entity_handler.entity_map[self.uuid]

    def pick_up_item(
        self, itemstack: mcpython.common.container.ItemStack.ItemStack
    ) -> bool:
        """
        Let the entity pick up an item and insert it into its inventory
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
        applies damage to the entity
        FOR MODER:
            this function is an default implementation. for an working example, see the player entity
            - you may want to apply armor calculation code
            - you may want to override this method for an custom implementation
        :param damage: the damage to apply
        :param reason: the reason for the damage, as an DamageSource-instance
        """
        self.harts -= damage
        if self.harts <= 0:
            self.kill()

    def on_interact(self, player, button, modifiers, itemstack):
        """
        called when the player tries to interact with the entity
        :param player: the player doing so, WARNING: only type-hinted for entity, not world/player.py:Player
        :param button: the button used
        :param modifiers: the modifiers used
        :param itemstack: the itemstack held in hand
        todo: make called
        todo: damage entity when needed
        for moder: should damage entity if needed
        """

    def get_inventories(self) -> list:
        """
        Will return an list of all currently arrival inventories for this entity
        """
        return []

    def on_inventory_cleared(self):
        """
        Called by /clear when the inventory of the entity should be cleared
        """

    # system events

    def draw(self):
        """
        Called to draw the entity
        """

    def tick(self, dt: float):
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
        dumps the entity into an save-able version
        :return: an pickle-able version, excluding position, rotation and harts, should include inventory serializer
            calls to make sure that everything works
        The nbt data is auto-saved
        Only extra stuff should be saved!
        """

    def load(self, data):
        """
        loads data into the entity, previous saved
        For Moder:
            you CAN include an version entry to make sure you can fix the data version
        :param data: the data to load from
        The nbt data is auto-loaded before this event is called
        """
