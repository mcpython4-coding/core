"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import gui.ItemStack
import item.ItemTool
import block.BoundingBox


class Block:
    """
    base class for all blocks
    """

    def __init__(self, position, set_to=None, state=None, real_hit=None):
        """
        creates new Block
        :param position: the position to create the block on
        :param set_to: when the block is setted to an block, these parameter contains where
        :param real_hit: were the block the user set to was hit on
        """
        self.position = position
        self.set_to = set_to
        self.real_hit = real_hit
        self.on_create()  # todo: remove
        if state is not None:
            self.set_model_state(state)

    @staticmethod
    def get_name() -> str:  # todo: change it to constant
        """
        :return: the name of the block
        """
        return "minecraft:missing_name"

    @staticmethod
    def on_register(registry):
        """
        called when the block is registered to any registry
        :param registry: the registry it registered to
        """
        pass

    def on_create(self):  # todo: remove
        """
        called when the block is created
        """

    def on_delete(self): pass  # todo: remove

    def on_remove(self):
        """
        called when the block is removed
        """
        self.on_delete()

    def get_inventories(self):
        """
        called to get an list of inventories
        """
        return []

    def is_breakable(self) -> bool:  # todo: make to constant
        """
        :return: if the block is breakable in gamemode 0
        """
        return True

    def on_random_update(self):
        """
        called on random update
        todo: re-activate
        """

    def on_block_update(self):
        """
        called when an near-by block-position is updated by setting/removing an block
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
    def get_all_model_states() -> list: return [{}]  # todo: make attribute

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

    def get_custom_block_renderer(self): return None

    def on_request_item_for_block(self, itemstack):
        pass

    @classmethod
    def modify_block_item(cls, itemconstructor): pass

