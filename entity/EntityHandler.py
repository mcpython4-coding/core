import globals as G
import event.Registry


class EntityHandler:
    def __init__(self):
        self.registry = event.Registry.Registry("registry", ["minecraft:entity"])
        self.entity_map = {}

    def add_entity(self, name, position, *args, dimension=None, **kwargs):
        if dimension is None: dimension = G.world.get_active_dimension()
        if name not in self.registry.registered_object_map:
            raise ValueError("unknown entity type name: '{}'".format(name))
        entity = self.registry.registered_object_map[name].create_new(position, *args, dimension=dimension, **kwargs)
        self.entity_map[entity.uuid] = entity
        return entity

    def tick(self):
        for entity in self.entity_map.values():
            entity.tick()


G.entityhandler = EntityHandler()

