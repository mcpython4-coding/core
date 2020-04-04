"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import gui.ItemStack
import globals as G
import event.Registry
import entity.EntityHandler
import uuid
import util.math


class Entity(event.Registry.IRegistryContent):
    """
    dummy class for every entity,
    only used by the player at the moment
    """

    TYPE = "minecraft:entity"

    SUMMON_ABLE = True

    @classmethod
    def create_new(cls, position, *args, **kwargs):
        """
        creates an new entity and set up it correctly for later use
        :param position: the position to create at
        :param args: args to send to the constructor
        :param kwargs: kwargs to send to the constructor
        :return: the created entity
        todo: make added to world
        for moder: use this rather than raw constructor
        """
        entity = cls(*args, **kwargs)
        entity.position = position
        return entity

    def __init__(self, dimension=None):
        """
        creates an new entity for the world
        for moder: you SHOULD implement an custom constructor which set the bellow values to an good value
        """
        self.dimension = G.world.get_active_dimension() if dimension is None else dimension
        self.__position = (0, 0, 0)
        self.rotation = (0, 0, 0)
        self.inventories = {}
        self.harts = 0
        self.chunk = None if self.dimension is None else self.dimension.get_chunk_for_position(self.position)
        self.uuid = uuid.uuid4()

    def get_position(self): return self.__position

    def set_position(self, position: tuple): self.teleport(position)

    # only for some small use-cases. WARNING: will  N O T  do any internal handling for updating the position
    def set_position_unsafe(self, position: tuple): self.__position = position

    position = property(get_position, set_position)

    def tell(self, msg: str):
        """
        tells the entity an message. Not intended to inter-mod com
        Should be used by say-commands
        :param msg: the msg to tell
        """

    def kill(self, drop_items=True, kill_animation=True):
        """
        called to kill the entity [remove the entity from world]
        :param drop_items: if items should be dropped
        :param kill_animation: if the kill animation should be played
        todo: drop items
        """
        if self.chunk is not None and self in self.chunk.entities:
            self.chunk.entities.remove(self)
        if self.uuid in G.entityhandler.entity_map:
            del G.entityhandler.entity_map[self.uuid]

    def pick_up(self, itemstack: gui.ItemStack.ItemStack) -> bool:
        """
        let the entity pick up an item and insert it into its inventory
        :param itemstack: the itemstack to use
        :return: if it was successful or not
        for moder: see world/player.py as an example how this could work
        """

    def damage(self, damage, reason=None):
        """
        applies damage to the entity
        FOR MODER:
            this function is an default implementation. for an working example, see the player entity
            - you may want to apply armor calculation code
            - you may want to override this method for an custom implementation
        :param damage: the damage to apply
        :param reason: the reason for the damage, may be entity or str [something like DamageSource in mc]
        """
        self.harts -= damage
        if self.harts <= 0:
            self.kill()

    def draw(self):
        """
        called to draw the entity
        """

    def tick(self):
        """
        called every tick to update the entity
        can be used to update animations, movement, do path finding stuff, damage other entities, ...
        """

    def dump(self):
        """
        dumps the entity into an save-able version
        :return: an pickle-able version, excluding position, rotation and harts, should include inventory serializer
            calls to make sure that everything works
        """

    def load(self, data):
        """
        loads data into the entity, previous saved
        For Moder:
            you CAN include an version entry to make sure you can fix the data version
        :param data: the data to load from
        """

    def teleport(self, position, dimension=None, force_chunk_save_update=False):
        """
        called when the entity should be teleported
        :param position: the position to teleport to
        :param dimension: to which dimension-id to teleport to, if None, no dimension change is used
        :param force_chunk_save_update: if the system should force to update were player data is stored
        """
        if self.chunk is None: sector_before = util.math.sectorize(self.position)
        else: sector_before = self.chunk.position
        if self.chunk is None: before_dim = None
        else: before_dim = self.chunk.dimension.id
        if dimension is None: dimension_id = before_dim if before_dim is not None else 0
        else: dimension_id = dimension
        self.__position = position
        sector_after = util.math.sectorize(self.position)
        if sector_before != sector_after or before_dim != dimension_id or force_chunk_save_update:
            if self.chunk and self in self.chunk.entities:
                self.chunk.entities.remove(self)
            self.chunk = G.world.dimensions[dimension_id].get_chunk_for_position(self.position)
            self.chunk.entities.add(self)

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

