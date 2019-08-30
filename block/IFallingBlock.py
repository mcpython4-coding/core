"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import block.IBlock
import event.TickHandler


@G.blockhandler
class IFallingBlock(block.IBlock.IBlock):
    @staticmethod
    def get_extension_name() -> str:
        return "falling_block"

    @classmethod
    def get_functions_to_inject(cls) -> dict:
        return {block.IBlock.InjectionMode.IF_NO_OTHER: [cls.get_functions_to_inject, cls.get_extension_name],
                block.IBlock.InjectionMode.PARALLEL: [cls.on_block_update, cls.fall]}

    @classmethod
    def on_block_update(cls, self):
        x, y, z = self.position
        block = G.world.get_active_dimension().get_block((x, y - 1, z))
        if not block:
            event.TickHandler.handler.bind(cls.fall, 10, args=[self])

    def fall(self):
        x, y, z = self.position
        block = G.world.get_active_dimension().get_block((x, y - 1, z))
        if not block:
            G.world.get_active_dimension().remove_block(self.position)
            G.world.get_active_dimension().add_block((x, y - 1, z), self)

