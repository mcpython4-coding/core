"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import gui.ItemStack
import globals as G
import event.Registry


class Entity(event.Registry.IRegistryContent):
    """
    dummy class for every entity,
    only used by the player at the moment
    """

    TYPE = "minecraft:entity"

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
        self.position = (0, 0, 0)
        self.rotation = (0, 0, 0)
        self.inventory_slots = []
        self.harts = 0

    def tell(self, msg: str):
        """
        tells the entity an message. Not intended to inter-mod com
        Should be used by say-commands
        :param msg: the msg to tell
        """

    def kill(self):
        """
        called to kill [remove the entity from world] the entity
        todo: invalidate uuid
        todo: drop items
        todo: remove from world
        """

    def add_to_free_place(self, itemstack: gui.ItemStack.ItemStack) -> bool:
        """
        let the entity pick up an item and insert it into its inventory
        :param itemstack: the itemstack to use
        :return: if it was successful or not
        for moder: see world/player.py as an example how this could work
        """

    def damage(self, damage):
        """
        applies damage to the entity
        FOR MODER:
            - you may want to apply armor calculation code
            - you may want to override this method for an custom implementation
        :param damage: the damage to apply
        """
        self.harts -= damage
        if self.harts <= 0:
            self.kill()

    def draw(self):
        """
        called to draw the entity
        todo: make called
        """

    def tick(self):
        """
        called every tick to update the entity
        todo: make called
        """

    def dump(self):
        """
        dumps the entity into an save-able version
        :return: an pickle-able version, excluding position, rotation and harts, should include inventory serializer
            calls to make sure that everything works
        """

    def load(self, data):
        """
        loads data into the entity
        :param data: the data to load from
        """

    def teleport(self, position):
        """
        called when the entity should be teleported
        :param position: the position to teleport to
        todo: make called
        """
        self.position = position

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

