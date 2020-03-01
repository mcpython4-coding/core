"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import gui.ItemStack
import item.ItemTool
import block.BoundingBox
import block.BlockFaceState
import event.Registry


class Block(event.Registry.IRegistryContent):
    """
    base class for all blocks
    """

    CUSTOM_WALING_SPEED_MULTIPLIER = None  # used when the player walks in an different speed on this block
    TYPE = "minecraft:block_registry"

    BLOCK_ITEM_GENERATOR_STATE = None

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
        if state is not None: self.set_model_state(state)
        self.face_state = block.BlockFaceState.BlockFaceState(self)
        self.block_state = None

    def on_remove(self):
        """
        called when the block is removed
        """

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

    def get_hardness(self):  # todo: make attribute
        return 1

    def get_minimum_tool_level(self):  # todo: make attribute
        return 0

    def get_best_tools(self):  # todo: make attribute
        return []

    def get_provided_slots(self, side):
        return []

    def get_view_bbox(self):  # todo: make attribute
        return block.BoundingBox.FULL_BLOCK_BOUNDING_BOX

    def get_custom_block_renderer(self): return None  # todo: make attribute

    def on_request_item_for_block(self, itemstack):
        pass

    @classmethod
    def modify_block_item(cls, itemconstructor): pass  # todo: add an event for this

