"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import world.gen.layer.Layer
import world.gen.mode
import world.Dimension
import world.Chunk
import mod.ModMcpython
import logger
import util.math


class WorldGenerationHandler:
    def __init__(self):
        self.layers = {}
        self.features = {}
        self.configs = {}
        self.enable_generation = False
        self.enable_auto_gen = False
        self.runtimegenerationcache = [[], {}, {}]  # chunk order, chunk state, chunk gen data
        self.tasks_to_generate = []

    def add_chunk_to_generation_list(self, chunk, dimension=None, prior=False, force_generate=False, generate_add=True):
        if not self.enable_auto_gen and not force_generate: return
        if type(chunk) == tuple:
            if dimension is None:
                chunk = G.world.get_active_dimension().get_chunk(*chunk, generate=False)
            else:
                chunk = G.world.dimensions[dimension].get_chunk(*chunk, generate=False)
        if prior:
            if chunk in self.runtimegenerationcache[0]:
                self.runtimegenerationcache[0].remove(chunk)
            self.runtimegenerationcache[0].insert(0, chunk)
        elif chunk not in self.runtimegenerationcache[0]:
            self.tasks_to_generate.append(chunk)
            if len(self.runtimegenerationcache[0]) == 0 and generate_add:
                self.process_one_generation_task()
        chunk.loaded = True

    def process_one_generation_task(self, chunk=None, reorder=True, log_msg=True):
        if not self.enable_generation: return
        if type(chunk) in (tuple, list, set): chunk = G.world.get_active_dimension().get_chunk(chunk)
        if chunk is None:
            if len(self.runtimegenerationcache[0]) == 0:
                cx, cz = util.math.sectorize(G.player.position)
                for _ in range(min(len(self.tasks_to_generate), 4)):
                    chunk = min(self.tasks_to_generate,
                                key=lambda c: ((c.position[0] - cx) ** 2 + (c.position[1] - cz) ** 2) ** 0.5)
                    self.tasks_to_generate.remove(chunk)
                    self.runtimegenerationcache[0].insert(-1, chunk)
                    self.runtimegenerationcache[1][chunk.position] = -1
                    self.runtimegenerationcache[2][chunk.position] = None
                    return
                if len(self.runtimegenerationcache[0]) == 0:
                    return False
            chunk = self.runtimegenerationcache[0][0]
        if chunk.position not in self.runtimegenerationcache[1]:
            self.runtimegenerationcache[1][chunk.position] = -1
            self.runtimegenerationcache[2][chunk.position] = None
        step = self.runtimegenerationcache[1][chunk.position]
        if step == -1:  # nothing done, so add layers and set to 0
            self.runtimegenerationcache[1][chunk.position] = 0
            dimension = chunk.dimension
            configname = dimension.worldgenerationconfig["configname"]
            config = self.configs[configname]
            if "on_chunk_generate_pre" in config:
                config["on_chunk_generate_pre"](chunk.position[0], chunk.position[1], chunk)
            self.runtimegenerationcache[2][chunk.position] = [self.layers[layername] for layername in config["layers"]]
            if reorder:
                self.runtimegenerationcache[0].remove(chunk)
                self.runtimegenerationcache[0].insert(-1, chunk)
        elif step == 0:  # process layers
            if len(self.runtimegenerationcache[2][chunk.position]) == 0:
                self.runtimegenerationcache[1][chunk.position] = 1
                return
            layer = self.runtimegenerationcache[2][chunk.position].pop(0)
            layer.add_generate_functions_to_chunk(chunk.dimension.worldgenerationconfigobjects[layer.NAME], chunk)
        elif step == 1:  # process chunk gen tasks
            if len(chunk.chunkgenerationtasks) == 0:
                self.runtimegenerationcache[1][chunk.position] = 2
                chunk.generated = True
                return
            task = chunk.chunkgenerationtasks.pop(0)
            task[0](*task[1], **task[2])
            if reorder:
                self.runtimegenerationcache[0].remove(chunk)
                self.runtimegenerationcache[0].insert(min(len(self.runtimegenerationcache[0])-1, 4), chunk)
        elif step == 2:  # process block additions to the chunk
            if len(chunk.blockmap) == 0:
                self.runtimegenerationcache[1][chunk.position] = 3
                return
            position = list(chunk.blockmap.keys())[0]
            args, kwargs, on_add = chunk.blockmap[position]
            del chunk.blockmap[position]
            blockinstance = chunk.add_block(*args, **kwargs)
            if on_add is not None:
                on_add(blockinstance)
            if reorder:
                self.runtimegenerationcache[0].remove(chunk)
                self.runtimegenerationcache[0].insert(min(len(self.runtimegenerationcache[0])-1, 4), chunk)
        elif step == 3:  # process show tasks
            if len(chunk.show_tasks) == 0:
                self.runtimegenerationcache[1][chunk.position] = 4
                return
            position = max(chunk.show_task, key=lambda x: x[1])
            chunk.show_task.remove(position)
            chunk.show_block(position)
        elif step == 4:  # process hide tasks
            if len(chunk.hide_tasks) == 0:
                self.runtimegenerationcache[0].remove(chunk)
                del self.runtimegenerationcache[1][chunk.position]
                del self.runtimegenerationcache[2][chunk.position]
                if log_msg:
                    logger.println("finished generation of chunk {}/{}".format(*chunk.position))
                G.eventhandler.call("worldgen:chunk:finished", chunk)
                chunk.generated = True
                # G.tickhandler.schedule_once(G.world.savefile.dump, None, "minecraft:chunk",
                #                             dimension=chunk.dimension.id, chunk=chunk.position)
                return
            position = chunk.hide_tasks.pop(0)
            chunk.hide_block(position)

    def setup_dimension(self, dimension, config=None):
        configname = dimension.worldgenerationconfig["configname"]
        if configname is None: return  # empty dimension
        for layername in self.configs[configname]["layers"]:
            layer = self.layers[layername]
            if config is None or layername not in config:
                cconfig = world.gen.layer.Layer.LayerConfig(**(
                    dimension.worldgenerationconfig[layername] if layername in dimension.worldgenerationconfig else {}))
                cconfig.dimension = dimension.id
            else:
                cconfig = config[layername]
            layer.normalize_config(cconfig)
            dimension.worldgenerationconfigobjects[layername] = cconfig
            cconfig.layer = layer

    def generate_chunk(self, chunk: world.Chunk.Chunk, dimension=None, check_chunk=True):
        if not self.enable_generation: return
        if check_chunk and chunk.generated: return
        if type(chunk) == tuple:
            if dimension is None:
                chunk = G.world.get_active_dimension().get_chunk(*chunk, generate=False)
            else:
                chunk = G.world.dimensions[dimension].get_chunk(*chunk, generate=False)
        chunk.loaded = True
        logger.println("generating", chunk.position)
        dimension = chunk.dimension
        configname = dimension.worldgenerationconfig["configname"]
        config = self.configs[configname]
        if "on_chunk_generate_pre" in config:
            config["on_chunk_generate_pre"](chunk.position[0], chunk.position[1], chunk)
        m = len(config["layers"])
        for i, layername in enumerate(config["layers"]):
            logger.println("\rgenerating layer {} ({}/{})".format(layername, i+1, m), end="")
            layer = self.layers[layername]
            layer.add_generate_functions_to_chunk(dimension.worldgenerationconfigobjects[layername], chunk)
            G.world.process_entire_queue()
        logger.println("\r", end="")
        G.eventhandler.call("worldgen:chunk:finished", chunk)
        chunk.generated = True
        chunk.loaded = True
        # G.tickhandler.schedule_once(G.world.savefile.dump, None, "minecraft:chunk",
        #                             dimension=chunk.dimension.id, chunk=chunk.position)

    def register_layer(self, layer: world.gen.layer.Layer.Layer):
        # logger.println(layer, layer.get_name())
        self.layers[layer.NAME] = layer

    def register_feature(self, decorator):
        pass

    def register_world_gen_config(self, name: str, layerconfig: dict):
        self.configs[name] = layerconfig

    def __call__(self, data: str or world.gen.layer.Layer, config=None):
        if type(data) == dict:
            self.register_world_gen_config(data, config)
        elif issubclass(data, world.gen.layer.Layer.Layer):
            self.register_layer(data)
        elif issubclass(data, object):
            self.register_feature(data)
        else:
            raise TypeError("unknown data type")
        return data


G.worldgenerationhandler = WorldGenerationHandler()


def load_layers():
    from world.gen.layer import (DefaultBedrockLayer, DefaultLandMassLayer, DefaultTemperatureLayer, DefaultBiomeLayer,
                                 DefaultHeightMapLayer, DefaultStonePlacementLayer, DefaultTopLayerLayer, DefaultTreeLayer)


def load_modes():
    from world.gen.mode import DefaultOverWorldGenerator, DebugOverWorldGenerator


mod.ModMcpython.mcpython.eventbus.subscribe("stage:worldgen:layer", load_layers, info="loading generation layers")
mod.ModMcpython.mcpython.eventbus.subscribe("stage:worldgen:mode", load_modes, info="loading generation modes")
