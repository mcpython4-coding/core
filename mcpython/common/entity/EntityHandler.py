"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared, logger
import mcpython.common.event.Registry
import mcpython.common.mod.ModMcpython


class EntityHandler:
    """
    Handler for entities in the current world
    """

    def __init__(self):
        self.registry = mcpython.common.event.Registry.Registry(
            "minecraft:entities",
            ["minecraft:entity"],
            "stage:entities",
            injection_function=self.add_entity_cls,
        )
        self.entity_map = {}

    def add_entity_cls(self, registry, entity_cls):
        if shared.IS_CLIENT:
            entity_cls.init_renderers()

    def spawn_entity(
        self,
        name,
        position,
        *args,
        dimension=None,
        uuid=None,
        check_summon=False,
        **kwargs
    ):
        if name not in self.registry.entries:
            raise ValueError("unknown entity type name: '{}'".format(name))

        if dimension is None:
            dimension = shared.world.get_active_dimension()

        if type(dimension) in (str, int):
            dimension = shared.world.get_dimension(dimension)

        entity_cls = self.registry.entries[name]

        if not entity_cls.SUMMON_ABLE and check_summon:
            logger.println(
                "[WARN] tried to summon an not-summon-able entity named '{}' at '{}'".format(
                    name, position
                )
            )
            return

        entity = entity_cls.create_new(position, *args, dimension=dimension, **kwargs)
        if uuid is not None:
            entity.uuid = uuid
        self.entity_map[entity.uuid] = entity
        entity.teleport(entity.position, force_chunk_save_update=True)

        return entity

    def tick(self, dt: float):
        # todo: move to dimensions

        for entity in list(self.entity_map.values()):
            entity.tick(dt)
            if (
                entity.parent is None and entity.child is not None
            ):  # update the positions of the children
                x, y, z = entity.position
                y += entity.entity_height
                child = entity.child

                while child is not None:
                    child.position = (x, y, z)
                    y += child.entity_height
                    child = child.child

            if not entity.nbt_data["invulnerable"] and entity.position[1] < -1000 + (
                entity.dimension.get_dimension_range()[0]
                if entity.dimension is not None
                else 0
            ):  # check if it has fallen to far down so it should be killed
                entity.kill()

            # todo: add collision & falling system
            # todo: add max entities standing in one space handler

    def clear(self):
        for entity in list(self.entity_map.values()):
            try:
                entity.kill(internal=True, force=True)
            except:
                logger.print_exception(
                    "during unloading entity {} with uuid {}".format(
                        entity, entity.uuid
                    )
                )

        self.entity_map.clear()


shared.entity_handler = EntityHandler()


def load():
    from mcpython.common.entity import AbstractEntity, FallingBlockEntity


mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe("stage:entities", load)
