"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import pyglet
import block.Block as Block
from util.math import *
import config
from typing import Dict, List
import util.math
import util.enums
import datetime


class Chunk:
    now = datetime.datetime.now()

    attributes = {}

    @staticmethod
    def add_default_attribute(name, reference, default, authcode=None) -> int:
        if authcode is None: authcode = hash(name)
        Chunk.attributes[name] = (reference, default, authcode)
        return authcode

    def __init__(self, dimension, position):
        self.dimension = dimension
        self.position = position
        self.world = {}
        self.is_ready = False  # used when the chunks gets invalid or is loaded at the moment
        self.visible = False  # used when the chunk should be visible
        self.loaded = False  # used if load success
        self.generated = False  # used if generation success
        self.attr = {}  # todo: rewrite!
        for attr in self.attributes.keys():
            self.attr[attr] = self.attributes[attr][1]
        self.positions_updated_since_last_save = set()
        self.entities = set()

    def set_value(self, name, value):
        self.attr[name] = value

    def get_value(self, name):
        return self.attr[name]

    def draw(self):
        # if len(self.entities) > 0:
        #     print([(entity.position, entity.NAME, entity.name) for entity in self.entities])
        #     print(self.position, self.is_ready, len(self.chunkgenerationtasks), self.visible, self.loaded)
        if not self.is_ready: return
        if not self.visible: return
        if not self.loaded:
            G.tickhandler.schedule_once(G.world.savefile.read, "minecraft:chunk", dimension=self.dimension.id,
                                        chunk=self.position)
        for entity in self.entities:
            entity.draw()

    def exposed(self, position):
        """ Returns False is given `position` should be hidden, True otherwise.

        """
        x, y, z = position
        for face in util.enums.EnumSide.iterate():
            dx, dy, dz = face.relative
            pos = (x + dx, y + dy, z + dz)
            chunk = self.dimension.get_chunk_for_position(pos, generate=False)
            if chunk.loaded:
                block = self.dimension.get_block(pos)
                if not (block and (block.face_solid[face] if type(block) != str else True)):
                    return True
        return False

    def exposed_faces(self, position):
        x, y, z = position
        faces = {}
        blockinst = self.get_block(position)
        if blockinst is None or type(blockinst) == str: return {x: True for x in util.enums.EnumSide.iterate()}
        for face in util.enums.EnumSide.iterate():
            dx, dy, dz = face.relative
            pos = (x + dx, y + dy, z + dz)
            chunk = self.dimension.get_chunk_for_position(pos, generate=False)
            if not chunk.loaded and G.world.hide_faces_to_ungenerated_chunks:
                faces[face] = False
            else:
                block = self.dimension.get_block(pos)
                if block is None: faces[face] = True
                elif type(block) == str: faces[face] = False  # todo: add an callback when the block is ready
                elif not block.face_solid[face.invert()]: faces[face] = True
                elif not blockinst.face_solid[face]: faces[face] = True
                else: faces[face] = False
        return faces

    def is_position_blocked(self, position):
        return position in self.world or G.worldgenerationhandler.task_handler.get_block(position) is not None

    def add_block(self, position: tuple, block_name: str, immediate=True, block_update=True, blockupdateself=True,
                  args=[], kwargs={}):
        """
        adds an block to the given position
        :param position: the position to add
        :param block_name: the name of the block or an instance of it
        :param immediate: if the block should be shown if needed
        :param block_update: if an block-update should be send to neighbors blocks
        :param blockupdateself: if the block should get an block-update
        :param args: the args to create the block with
        :param kwargs: the kwargs to create the block with
        :return: the block instance or None if it could not be created
        """
        if position[1] < 0 or position[1] > 255: return
        if position != util.math.normalize(position):
            raise ValueError("position '{}' is no valid block position".format(position))
        # logger.println("adding", block_name, "at", position)
        if position in self.world:
            self.remove_block(position, immediate=immediate, block_update=block_update)
        if block_name in [None, "air", "minecraft:air"]: return
        if issubclass(type(block_name), Block.Block):
            blockobj = block_name
            blockobj.position = position
        else:
            table = G.registry.get_by_name("block").full_table
            if block_name not in table:
                logger.println("[CHUNK][ERROR] can't add block named '{}'. Block class not found!".format(block_name))
                return
            blockobj = table[block_name](position, *args, **kwargs)
        if self.now.day == 13 and self.now.month == 1 and "diorite" in blockobj.NAME:
            print("[WARNING][CLEANUP] you are not allowed to set block '{}' as it contains diorite!".format(
                blockobj.NAME))
            # for developers: easter egg! [DO NOT REMOVE, UUK'S EASTER EGG]
            return self.add_block(position, "minecraft:stone")
        self.world[position] = blockobj
        if immediate:
            if self.exposed(position):
                self.show_block(position)
            if block_update:
                self.on_block_updated(position, itself=blockupdateself)
            self.check_neighbors(position)
        self.positions_updated_since_last_save.add(position)
        return blockobj

    def on_block_updated(self, position, itself=True):
        x, y, z = position
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                for dz in range(-1, 2):
                    if [dx, dy, dz].count(0) >= 2 and not (not itself and dx == dy == dz == 0):
                        b: Block.Block = self.dimension.get_block((x+dx, y+dy, z+dz))
                        if b and type(b) != str:
                            b.on_block_update()

    def remove_block(self, position, immediate=True, block_update=True, blockupdateself=True):
        """ Remove the block at the given `position`.

        Parameters
        :param position: tuple of len 3
            The (x, y, z) position of the block to remove.
        :param immediate: bool
            Whether or not to immediately remove block from canvas.
        :param block_update: bool
            Whether an block-update should be called or not
        :param blockupdateself:
            Whether the block to remove should get an block-update or not
        """
        if position not in self.world: return
        if issubclass(type(position), Block.Block):
            position = position.position
        self.world[position].on_remove()
        if block_update and blockupdateself:
            self.world[position].on_block_update()
        self.world[position].face_state.hide_all()
        del self.world[position]
        if immediate:
            if block_update:
                self.on_block_updated(position)
            self.check_neighbors(position)
        self.positions_updated_since_last_save.add(position)

    def check_neighbors(self, position):
        """ Check all blocks surrounding `position` and ensure their visual
        state is current. This means hiding blocks that are not exposed and
        ensuring that all exposed blocks are shown. Usually used after a block
        is added or removed.

        """
        x, y, z = position
        for face in util.enums.EnumSide.iterate():
            dx, dy, dz = face.relative
            key = (x + dx, y + dy, z + dz)
            b = self.dimension.get_block(key)
            # chunk = self.dimension.get_chunk_for_position(key, generate=False)
            if b is None or type(b) == str: continue
            b.face_state.update()

    def show_block(self, position, immediate=True):
        """ Show the block at the given `position`. This method assumes the
        block has already been added with add_block()

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to show.
        immediate : bool
            Whether or not to show the block immediately.

        """
        if type(position) == Block.Block:
            position = position.position
        if position not in self.world: return
        if immediate:
            self._show_block(position, self.world[position])
        else:
            G.worldgenerationhandler.task_handler.schedule_visual_update(self, position)

    def _show_block(self, position, block):
        """ Private implementation of the `show_block()` method.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to show.
        block: the blockinstance to show

        """
        self.world[position].face_state.update()

    def hide_block(self, position, immediate=True):
        """ Hide the block at the given `position`. Hiding does not remove the
        block from the world.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to hide.
        immediate : bool
            Whether or not to immediately remove the block from the canvas.

        """
        if type(position) == Block.Block:
            position = position.position
        if immediate:
            self._hide_block(position)
        else:
            G.worldgenerationhandler.task_handler.schedule_visual_update(self, position)

    def _hide_block(self, position):
        """ Private implementation of the 'hide_block()` method.

        """
        if position not in self.world: return
        self.world[position].face_state.hide_all()

    def show(self):
        self.visible = True
        self.update_visable(hide=False)

    def hide(self):
        self.visible = False
        self.hide_all()

    def update_visable_block(self, position, hide=True):
        self.positions_updated_since_last_save.add(position)
        if not self.exposed(position):
            self.hide_block(position)
        elif hide:
            self.show_block(position)

    def update_visable(self, hide=True, immediate=False):
        for position in self.world.keys():
            if immediate:
                G.worldgenerationhandler.task_handler.schedule_visual_update(self, position)
            else:
                self.update_visable_block(position, hide=hide)

    def hide_all(self, immediate=True):
        for position in self.world:
            self.hide_block(position, immediate=immediate)

    def get_block(self, position):
        position = util.math.normalize(position)
        return self.world[position] if position in self.world else G.worldgenerationhandler.task_handler.get_block(
            position, chunk=self)

    def __del__(self):
        G.worldgenerationhandler.task_handler.clear_chunk(self)
        for block in self.world.values():
            del block
        self.world.clear()
        self.attr.clear()
        for entity in self.entities:
            del entity
        self.entities.clear()
        del self.dimension

    def __str__(self):
        return "Chunk(dimension={},position={})".format(self.dimension.id, self.position)

