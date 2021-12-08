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
import mcpython.common.event.TickHandler
from mcpython.engine import logger
from mcpython.util.enums import LogAxis


class ILog(mcpython.common.block.AbstractBlock.AbstractBlock):
    """
    Base class for log-like blocks
    """

    def __init__(self):
        super().__init__()
        self.axis = LogAxis.Y

    async def on_block_added(self):
        if self.set_to:
            dx, dy, dz = (
                abs(self.set_to[0] - self.position[0]),
                abs(self.set_to[1] - self.position[0]),
                abs(self.set_to[2] - self.position[2]),
            )
            if dx:
                self.axis = LogAxis.X
            elif dz:
                self.axis = LogAxis.Z

            self.face_info.update(True)
            self.schedule_network_update()

    def get_model_state(self):
        return {"axis": self.axis.name.lower()}

    def set_model_state(self, state: dict):
        if "axis" in state:
            axis: str = state["axis"]

            try:
                self.axis = LogAxis[axis.upper()]
            except KeyError:
                logger.println(
                    f"[WARN] invalid log axis: {axis}; This indicates a world-save error!"
                )

    DEBUG_WORLD_BLOCK_STATES = [{"axis": "x"}, {"axis": "y"}, {"axis": "z"}]
