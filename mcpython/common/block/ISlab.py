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
import mcpython.common.block.AbstractBlock
import mcpython.engine.physics.BoundingBox
import mcpython.util.enums
from mcpython.util.enums import SlabModes

BBOX_DICT = {
    SlabModes.TOP: mcpython.engine.physics.BoundingBox.BoundingBox(
        (1, 0.5, 1), (0, 0.5, 0)
    ),
    SlabModes.BOTTOM: mcpython.engine.physics.BoundingBox.BoundingBox((1, 0.5, 1)),
    SlabModes.DOUBLE: mcpython.engine.physics.BoundingBox.FULL_BLOCK_BOUNDING_BOX,
}


class ISlab(mcpython.common.block.AbstractBlock.AbstractBlock):
    """
    Base class for slabs
    """

    IS_SOLID = False
    DEFAULT_FACE_SOLID = 0

    def __init__(self):
        super().__init__()
        self.type = SlabModes.TOP

    def on_block_added(self):
        if self.real_hit and self.real_hit[1] - self.position[1] > 0:
            self.type = SlabModes.TOP
        else:
            self.type = SlabModes.BOTTOM
        self.schedule_network_update()

    def get_model_state(self):
        return {"type": self.type.name.lower()}

    def set_model_state(self, state: dict):
        if "type" in state:
            self.type = SlabModes[state["type"].upper()]

    DEBUG_WORLD_BLOCK_STATES = [{"type": x.name.upper()} for x in SlabModes]

    def on_player_interact(
        self, player, itemstack, button, modifiers, exact_hit
    ) -> bool:
        # todo: add half -> double convert
        return False

    def get_view_bbox(self):
        return BBOX_DICT[self.type]
