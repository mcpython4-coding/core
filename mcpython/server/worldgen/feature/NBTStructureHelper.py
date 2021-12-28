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
import mcpython.engine.ResourceLoader
import mcpython.server.worldgen.WorldGenerationTaskArrays
import python_nbt.nbt as nbt
from mcpython import shared


class StructureNBTHelper:
    @classmethod
    async def from_file(cls, file: str):
        data = await mcpython.engine.ResourceLoader.read_raw(file)
        with open(shared.tmp.name + "/tmp.nbt", mode="wb") as f:
            f.write(data)
        return cls(nbt.read_from_nbt_file(shared.tmp.name + "/tmp.nbt").json_obj())

    def __init__(self, data: dict):
        data = data["value"]

        self.entities = data["entities"]["value"]

        self.blocks = {}

        for block_data in data["palette"]["value"][:]:
            if "Properties" in block_data:
                state = block_data["Properties"]["value"]
                state = {
                    key: value["value"]
                    if isinstance(value["value"], dict)
                    else value["value"]
                    for key, value in state.items()
                }
                block_data["Properties"] = state
            else:
                block_data["Properties"] = {}

        for block in data["blocks"]["value"]:
            pos = tuple(block["pos"]["value"])
            index = block["state"]["value"]

            block_data = data["palette"]["value"][index]
            name = block_data["Name"]["value"]
            state = block_data["Properties"]

            self.blocks[pos] = name, state

    async def place(self, dimension, x: int, y: int, z: int, config):
        for pos, (name, state) in self.blocks.items():
            dx, dy, dz = pos
            block = await dimension.add_block((x + dx, y + dy, z + dz), name)

            if block is not None:
                block.set_model_state(state)
                block.face_info.update(True)

    def place_array(
        self,
        array: mcpython.server.worldgen.WorldGenerationTaskArrays.IWorldGenerationTaskHandlerReference,
        x: int,
        y: int,
        z: int,
        config,
    ):
        def callback(s):
            def setup(block):
                block.set_model_state(s)
                block.face_info.update(True)

            return setup

        for pos, (name, state) in self.blocks.items():
            dx, dy, dz = pos
            array.schedule_block_add(
                (x + dx, y + dy, z + dz), name, on_add=callback(state)
            )
