"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import event.Registry


class EntityHandler:
    def __init__(self):
        self.registry = event.Registry.Registry("registry", ["minecraft:entity"])
        self.entity_map = {}

    def add_entity(self, name, position, *args, dimension=None, uuid=None, **kwargs):
        if dimension is None: dimension = G.world.get_active_dimension()
        if name not in self.registry.registered_object_map:
            raise ValueError("unknown entity type name: '{}'".format(name))
        entity = self.registry.registered_object_map[name].create_new(position, *args, dimension=dimension, **kwargs)
        if uuid is not None: entity.uuid = uuid
        self.entity_map[entity.uuid] = entity
        return entity

    def tick(self):
        for entity in self.entity_map.values():
            entity.tick()


G.entityhandler = EntityHandler()

