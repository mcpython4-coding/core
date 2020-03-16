"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import entity.Entity
import rendering.EntityRenderer
import globals as G
import cProfile


class IEntityPlayer(entity.Entity.Entity):
    RENDERER = rendering.EntityRenderer.EntityRenderer("minecraft:player")

    def tick(self):
        pass

    def draw(self):
        rx, ry, rz = self.rotation
        rotation_head = (0, 0, 0)  # (ry, rx, 0)  # todo: implement
        self.RENDERER.draw(self, "inner" if self == G.world.get_active_player() else "outer",
                           part_rotation={"head": rotation_head})


