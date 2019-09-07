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
                G.worldgenerationhandler.generate_chunk(self.chunks[(cx, cz)])
        return self.chunks[(cx, cz)]

    def get_chunk_for_position(self, position, **kwargs) -> world.Chunk.Chunk or None:
        if issubclass(type(position), block.Block.Block):
            position = position.position
        return self.get_chunk(*util.math.sectorize(position), **kwargs)

    def get_block(self, position):
        chunk = self.get_chunk_for_position(position, generate=False)
        return chunk.get_block(position)

    def add_block(self, position: tuple, blockname: str, immediate=True, block_update=True, args=[], kwargs={}):
        self.get_chunk_for_position(position).add_block(position, blockname, immediate=immediate,
                                                        block_update=block_update, args=args, kwargs=kwargs)

    def remove_block(self, position: tuple, immediate=True, block_update=True):
        self.get_chunk_for_position(position).remove_block(position, immediate=immediate, block_update=block_update)

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

