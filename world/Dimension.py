"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import world.Chunk
import util.math
import pyglet
import block.Block
import mod.ModMcpython


class DimensionDefinition:
    def __init__(self, name: str, config: dict):
        self.name = name
        self.id = None
        self.config = config

    def setStaticId(self, dimid):
        self.id = dimid
        return self


class DimensionHandler:
    def __init__(self):
        self.dimensions = {}
        self.unfinisheddims = []
        mod.ModMcpython.mcpython.eventbus.subscribe("stage:post", self.finish)

    def finish(self):
        i = 0
        for dim in self.unfinisheddims:
            while i in self.unfinisheddims: i += 1
            dim.id = i
            self.add_dimension(dim)

    def add_default_dimensions(self):
        self.add_dimension(DimensionDefinition("overworld", {"configname": "default_overworld"}).setStaticId(0))

    def add_dimension(self, dim: DimensionDefinition):
        if dim.id is None:
            self.unfinisheddims.append(dim)
        else:
            self.dimensions[dim.id] = dim

    def init_dims(self):
        for dim in self.dimensions.values():
            G.world.add_dimension(dim.id, dim.config)


G.dimensionhandler = DimensionHandler()

mod.ModMcpython.mcpython.eventbus.subscribe("stage:dimension", G.dimensionhandler.add_default_dimensions)


class Dimension:
    def __init__(self, world, id, genconfig={}):
        self.id = id
        self.world = world
        self.chunks = {}
        self.worldgenerationconfig = genconfig
        self.worldgenerationconfigobjects = {}
        # normal batch
        self.batches = [pyglet.graphics.Batch() for _ in range(2)]  # normal, alpha

    def get_chunk(self, cx, cz, generate=True, create=True) -> world.Chunk.Chunk or None:
        if (cx, cz) not in self.chunks:
            if not create:
                return
            self.chunks[(cx, cz)] = world.Chunk.Chunk(self, (cx, cz))
            if generate:
                G.worldgenerationhandler.add_chunk_to_generation_list(self.chunks[(cx, cz)])
        return self.chunks[(cx, cz)]

    def get_chunk_for_position(self, position, **kwargs) -> world.Chunk.Chunk or None:
        if issubclass(type(position), block.Block.Block):
            position = position.position
        return self.get_chunk(*util.math.sectorize(position), **kwargs)

    def get_block(self, position):
        chunk = self.get_chunk_for_position(position, generate=False)
        return chunk.get_block(position)

    def add_block(self, position: tuple, blockname: str, immediate=True, block_update=True, blockupdateself=True,
                  args=[], kwargs={}):
        self.get_chunk_for_position(position).add_block(position, blockname, immediate=immediate,
                                                        block_update=block_update, args=args, kwargs=kwargs,
                                                        blockupdateself=blockupdateself)

    def remove_block(self, position: tuple, immediate=True, block_update=True, blockupdateself=True):
        self.get_chunk_for_position(position).remove_block(position, immediate=immediate, block_update=block_update,
                                                           blockupdateself=blockupdateself)

    def check_neighbors(self, position): self.get_chunk_for_position(position).check_neighbors(position)

    def show_block(self, position, immediate=True):
        self.get_chunk_for_position(position).show_block(position, immediate=immediate)

    def hide_block(self, position, immediate=True):
        self.get_chunk_for_position(position).hide_block(position, immediate=immediate)

    def draw(self):
        x, z = util.math.sectorize(G.window.position)
        pad = 4
        for dx in range(-pad, pad + 1):
            for dz in range(-pad, pad + 1):
                cx, cz = x + dx, z + dz
                chunk = self.get_chunk(cx, cz, create=False)
                if chunk:
                    chunk.draw()
        self.batches[0].draw()
        # draw with alpha
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
        self.batches[1].draw()

