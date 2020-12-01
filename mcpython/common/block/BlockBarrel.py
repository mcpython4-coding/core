"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared as G
from . import Block
from pyglet.window import mouse, key
import mcpython.util.enums
import pyglet
import mcpython.client.gui.InventoryBarrel


class BlockBarrel(Block.Block):
    """
    class for the Barrel-Block
    """

    NAME: str = "minecraft:barrel"  # the name of the block

    def __init__(self, *args, **kwargs):
        """
        Creates an new BlockBarrel-class
        """
        super().__init__(*args, **kwargs)
        self.facing: str = "up"  # the direction the block faces to
        self.opened: bool = False  # if the barrel is open
        self.inventory = mcpython.client.gui.InventoryBarrel.InventoryBarrel(self)
        if self.set_to is not None:  # check for direction from setting
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

    def on_player_interaction(
        self, player, button: int, modifiers: int, hit_position: tuple
    ):
        if (
            button == mouse.RIGHT and not modifiers & key.MOD_SHIFT
        ):  # open the inv when needed
            G.inventoryhandler.show(self.inventory)
            return True
        else:
            return False

    def get_inventories(self):
        return [self.inventory]

    HARDNESS = 2.5
    BEST_TOOLS_TO_BREAK = [mcpython.util.enums.ToolType.AXE]

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

    @staticmethod
    def get_all_model_states() -> list:
        facing = [
            {"facing": "north"},
            {"facing": "east"},
            {"facing": "south"},
            {"facing": "west"},
            {"facing": "up"},
            {"facing": "down"},
        ]
        return [{"open": "false", **e} for e in facing] + [
            {"open": "true", **e} for e in facing
        ]

    @classmethod
    def set_block_data(cls, iteminst, block):
        if hasattr(iteminst, "inventory"):
            block.inventory = iteminst.inventory.copy()

    def on_request_item_for_block(self, itemstack):
        if (
            G.window.keys[pyglet.window.key.LCTRL]
            and G.world.get_active_player().gamemode == 1
            and G.window.mouse_pressing[pyglet.window.mouse.MIDDLE]
        ):
            itemstack.item.inventory = self.inventory.copy()

    def on_remove(self):
        if not G.world.gamerulehandler.table["doTileDrops"].status.status:
            return
        for slot in self.inventory.slots:
            G.world.get_active_player().pick_up(slot.itemstack.copy())
            slot.itemstack.clean()
        G.inventoryhandler.hide(self.inventory)
        del self.inventory

    @classmethod
    def modify_block_item(cls, itemfactory):
        itemfactory.setFuelLevel(15)


@G.modloader("minecraft", "stage:block:load")
def load():
    G.registry.register(BlockBarrel)
