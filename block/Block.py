"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import gui.ItemStack


class Block:
    """
    base class for all blocks
    """

    def __init__(self, position, setted_to=None):
        """
        creates new Block
        :param position: the position to create the block on
        :param setted_to: when the block is setted to an block, these parameter contains where
        """
        self.position = position
        self.setted_to = setted_to
        self.on_create()

    @staticmethod
    def get_name() -> str:
        """
        :return: the name of the block
        """
        return "minecraft:missing_name"

    @staticmethod
    def on_register(registry):
        """
        callen when the block is registered to any registry
        :param registry: the registry it registered to
        """
        pass

    def on_create(self):
        """
        callen when the block is created
        """

    def on_delete(self):
        """
        callen when the block is removed
        """

    def is_brakeable(self) -> bool:
        """
        :return: if the block is brakeable in gamemode 0
        """
        return True

    def on_random_update(self):
        """
        callen on random update
        todo: re-activate
        """

    def on_block_update(self):
        """
        callen when an near-by blockposition is updated by setting/removing an block
        """

    def get_brake_time(self, item: gui.ItemStack) -> int:
        """
        :param item: the item that is used
        :return: how long it takes to brake the block
        """
        return 2

    def is_solid_side(self, side) -> bool:
        """
        :param side: the side that is asked for
        :return: if the side is solid or not
        """
        return True

    def get_model_state(self) -> dict: return {}
