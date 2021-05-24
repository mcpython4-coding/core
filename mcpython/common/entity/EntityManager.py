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
import typing

import mcpython.common.event.Registry
from mcpython import logger, shared


class EntityManager:
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
        if shared.IS_CLIENT and not shared.IS_TEST_ENV:
            entity_cls.init_renderers()

        return self

    def spawn_entity(
        self,
        name: typing.Union[str, typing.Any],
        position,
        *args,
        dimension=None,
        uuid=None,
        check_summon=False,
        **kwargs
    ):
        if isinstance(name, str):
            if name not in self.registry.entries:
                raise ValueError("unknown entity type name: '{}'".format(name))

            if dimension is None:
                dimension = shared.world.get_active_dimension()

            if type(dimension) in (str, int):
                dimension = shared.world.get_dimension(dimension)

            entity_cls = self.registry.entries[name]

            if not entity_cls.SUMMON_ABLE and check_summon:
                logger.println(
                    "[WARN] tried to summon a not-summon-able entity named '{}' at '{}'".format(
                        name, position
                    )
                )
                return

            entity = entity_cls.create_new(
                position, *args, dimension=dimension, **kwargs
            )

        else:
            entity = name

        if uuid is not None:
            entity.uuid = uuid

        self.entity_map[entity.uuid] = entity
        entity.teleport(entity.position, force_chunk_save_update=True)

        return entity

    def tick(self, dt: float):
        # todo: move to dimensions
        # todo: move most of this here to entity

        for entity in list(self.entity_map.values()):
            entity.tick(dt)

            # update the positions of the children
            if entity.parent is None and entity.child is not None:
                x, y, z = entity.position
                y += entity.entity_height
                child = entity.child

                while child is not None:
                    child.position = (x, y, z)
                    y += child.entity_height
                    child = child.child

            # check if it has fallen to far down so it should be killed
            if not entity.nbt_data["invulnerable"] and entity.position[1] < -1000 + (
                entity.dimension.get_dimension_range()[0]
                if entity.dimension is not None
                else 0
            ):
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

        # At the end, discard all entities here; Errors may arise when above handles an exception
        # and the entity is not removed
        # todo: add indicator at entity to not delete itself than!
        self.entity_map.clear()


def load():
    from mcpython.common.entity import AbstractEntity, FallingBlockEntity


# This check is here as test env don't want to import this stuff
if not shared.IS_TEST_ENV:
    shared.entity_manager = EntityManager()

    import mcpython.common.mod.ModMcpython
    mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe("stage:entities", load)
