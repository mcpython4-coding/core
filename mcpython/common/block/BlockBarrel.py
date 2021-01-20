"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft, representing snapshot 20w51a
(https://www.minecraft.net/en-us/article/minecraft-snapshot-20w51a)

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared
from . import AbstractBlock
from pyglet.window import mouse, key
import mcpython.util.enums
import pyglet
import mcpython.client.gui.InventoryBarrel


class BlockBarrel(AbstractBlock.AbstractBlock):
    """
    class for the Barrel-Block
    """

    NAME: str = "minecraft:barrel"  # the name of the block

    DEBUG_WORLD_BLOCK_STATES = []
    for face in ["north", "east", "south", "west", "up", "down"]:
        DEBUG_WORLD_BLOCK_STATES.append({"open": "false", "facing": face})
        DEBUG_WORLD_BLOCK_STATES.append({"open": "true", "facing": face})

    HARDNESS = 2.5
    ASSIGNED_TOOLS = [mcpython.util.enums.ToolType.AXE]

    def __init__(self):
        """
        Creates an new BlockBarrel-class
        """
        super().__init__()

        self.opened: bool = False  # if the barrel is open
        self.inventory = mcpython.client.gui.InventoryBarrel.InventoryBarrel(self)
        self.facing: str = "up"  # the direction the block faces to

    def on_block_added(self):
        # only if this is set, decode it
        if self.set_to is not None:
            dx, dy, dz = tuple([self.position[i] - self.set_to[i] for i in range(3)])
            if dx > 0:
                self.facing = "west"
            elif dz > 0:
                self.facing = "north"
            elif dx < 0:
                self.facing = "east"
            elif dz < 0:
                self.facing = "south"
            elif dy > 0:
                self.facing = "down"
            elif dy < 0:
                self.facing = "up"
            if shared.IS_CLIENT:
                self.face_state.update()

    def on_player_interaction(
        self, player, button: int, modifiers: int, hit_position: tuple
    ):
        if button == mouse.RIGHT and not modifiers & (
            key.MOD_SHIFT | key.MOD_ALT | key.MOD_CTRL
        ):  # open the inv when needed
            shared.inventory_handler.show(self.inventory)
            return True
        else:
            return False

    def get_inventories(self):
        return [self.inventory]

    def get_provided_slot_lists(self, side):
        return self.inventory.slots, self.inventory.slots

    def set_model_state(self, state: dict):
        if "side" in state:
            face = state["side"]
            if type(face) == str:
                self.facing = mcpython.util.enums.EnumSide[state["side"]]
            else:
                self.facing = face

    def get_model_state(self) -> dict:
        return {"facing": self.facing, "open": str(self.opened).lower()}

    @classmethod
    def set_block_data(cls, item, block):
        if hasattr(item, "inventory"):
            block.inventory = item.inventory.copy()

    def on_request_item_for_block(self, itemstack):
        if (
            shared.window.keys[pyglet.window.key.LCTRL]
            and shared.world.get_active_player().gamemode == 1
            and shared.window.mouse_pressing[pyglet.window.mouse.MIDDLE]
        ):
            itemstack.item.inventory = self.inventory.copy()

    def on_block_remove(self, reason):
        if shared.world.gamerule_handler.table["doTileDrops"].status.status:
            for slot in self.inventory.slots:
                shared.world.get_active_player().pick_up_item(slot.itemstack.copy())
                slot.itemstack.clean()

        shared.inventory_handler.hide(self.inventory)
        del self.inventory


@shared.mod_loader("minecraft", "stage:block:load")
def load():
    shared.registry.register(BlockBarrel)
