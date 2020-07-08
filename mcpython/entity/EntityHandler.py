"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
import globals as G
import mcpython.event.Registry
import mcpython.mod.ModMcpython
import logger


class EntityHandler:
    def __init__(self):
        self.registry = mcpython.event.Registry.Registry("registry", ["minecraft:entity"])
        self.entity_map = {}

    def add_entity(self, name, position, *args, dimension=None, uuid=None, check_summon=False, **kwargs):
        if dimension is None: dimension = G.world.get_active_dimension()
        if type(dimension) == int: dimension = G.world.dimensions[dimension]
        if name not in self.registry.registered_object_map:
            raise ValueError("unknown entity type name: '{}'".format(name))
        entity = self.registry.registered_object_map[name]
        if not entity.SUMMON_ABLE and check_summon:
            logger.println("[WARN] tried to summon an not-summon-able entity named '{}' at '{}'".format(name, position))
            return
        entity = entity.create_new(position, *args, dimension=dimension, **kwargs)
        if uuid is not None: entity.uuid = uuid
        self.entity_map[entity.uuid] = entity
        entity.teleport(entity.position, force_chunk_save_update=True)
        return entity

    def tick(self):
        for entity in self.entity_map.values():
            entity.tick()


G.entityhandler = EntityHandler()


def load():
    from mcpython.entity import (Entity)


mcpython.mod.ModMcpython.mcpython.eventbus.subscribe("stage:entities", load)

