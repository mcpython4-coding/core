"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import gui.ItemStack
import item.ItemTool
import block.BoundingBox


class Block:
    """
    base class for all blocks
    """

    def __init__(self, position, setted_to=None, state=None, real_hit=None):
        """
        creates new Block
        :param position: the position to create the block on
        :param setted_to: when the block is setted to an block, these parameter contains where
        :param real_hit: were the block the user set to was hit on
        """
        self.position = position
        self.setted_to = setted_to
        self.real_hit = real_hit
        self.on_create()
        if state is not None:
            self.set_model_state(state)

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

    def get_inventories(self):
        """
        callen to get an list of inventories
        """
        return []

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

    def is_solid_side(self, side) -> bool:
        """
        :param side: the side that is asked for
        :return: if the side is solid or not
        """
        return True

    def get_model_state(self) -> dict: return {}

    def set_model_state(self, state: dict): pass

    @staticmethod
    def get_all_model_states() -> list: return [{}]

    def on_player_interact(self, itemstack, button, modifiers, exact_hit) -> bool:
        return False

    def get_hardness(self):
        return 1

    def get_minimum_tool_level(self):
        return 0

    def get_best_tools(self):
        return []

    def get_provided_slots(self, side):
        return []

    def get_view_bbox(self):
        return block.BoundingBox.FULL_BLOCK_BOUNDING_BOX

