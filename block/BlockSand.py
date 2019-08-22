"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
from . import Block
import event.TickHandler


@G.blockhandler
class BlockSand(Block.Block):
    @staticmethod
    def get_name() -> str:
        return "minecraft:sand"

    def get_model_name(self):
        return "block/sand"

    def on_block_update(self):
        x, y, z = self.position
        block = G.world.get_active_dimension().get_block((x, y-1, z))
        if not block:
            event.TickHandler.handler.bind(self.fall, 10)

    def fall(self):
        x, y, z = self.position
        block = G.world.get_active_dimension().get_block((x, y - 1, z))
        if not block:
            G.world.get_active_dimension().remove_block(self)
            G.world.get_active_dimension().add_block((x, y - 1, z), self)
