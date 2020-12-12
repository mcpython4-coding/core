"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import datetime
import typing

import mcpython.common.block.AbstractBlock as Block
import mcpython.util.enums
import mcpython.util.math
from mcpython.util.math import *  # todo: remove
import mcpython.common.world.AbstractInterface


class Chunk(mcpython.common.world.AbstractInterface.IChunk):
    """
    representation of an chunk in the world
    """

    now = datetime.datetime.now()  # when is now?

    attributes = {}  # an dict representing the default attributes of an chunk

    @staticmethod
    def add_default_attribute(name: str, reference: typing.Any, default: typing.Any):
        """
        will add an config entry into every new chunk instance
        :param name: the name of the attribute
        :param reference: the reference to use; unused internally
        :param default: the default value
        WARNING: content must be saved by owner, not auto-saved
        todo: make class based
        """
        Chunk.attributes[name] = (reference, default, None)

    def __init__(
        self,
        dimension: mcpython.common.world.AbstractInterface.IDimension,
        position: typing.Tuple[int, int],
    ):
        """
        Will create an new chunk instance
        :param dimension: the world.Dimension.Dimension object used to store this chunk
        :param position: the position of the chunk
        WARNING: use Dimension.get_chunk() where possible [saver variant, will do some work in the background]
        """
        self.dimension = dimension
        self.position = position
        self.world = {}
        self.is_ready = (
            False  # used when the chunks gets invalid or is loaded at the moment
        )
        self.visible = False  # used when the chunk should be visible
        self.loaded = False  # used if load success
        self.generated = False  # used if generation success
        self.attr = {}  # todo: rewrite!
        for attr in self.attributes.keys():
            v = self.attributes[attr][1]
            if hasattr(v, "copy") and callable(v.copy):
                v = v.copy()
            self.attr[attr] = v
        self.positions_updated_since_last_save = set()
        self.entities = set()

    def get_dimension(self):
        return self.dimension

    def get_position(self):
        return self.position

    def get_maximum_y_coordinate_from_generation(self, x: int, z: int) -> int:
        """
        Helper function for getting the y height at the given xz generation based on the generation code
        :param x: the x coord
        :param z: the y coord
        :return: the y value at that position
        """
        height_map = self.get_value("heightmap")
        y = height_map[x, z][0][1] if (x, z) in height_map else 0
        return y

    def set_value(self, name: str, value):
        """
        Will set an attribute of the chunk
        :param name: the name to use
        :param value: the value to use
        """
        self.attr[name] = value

    def get_value(self, name: str):
        """
        Will get the value of the given name
        :param name: the name to get
        :return: the data stored
        """
        return self.attr[name]

    def draw(self):
        """
        Will draw the chunk with the content for it
        """
        if not self.is_ready:
            return
        if not self.visible:
            return
        if not self.loaded:
            G.tick_handler.schedule_once(
                G.world.save_file.read,
                "minecraft:chunk",
                dimension=self.dimension.get_id(),
                chunk=self.position,
            )
        for entity in self.entities:
            entity.draw()

    def exposed_faces(
        self, position: typing.Tuple[int, int, int]
    ) -> typing.Dict[mcpython.util.enums.EnumSide, bool]:
        """
        returns an dict of the exposed status of every face of the given block
        :param position: the position to check
        :return: the dict for the status
        """
        x, y, z = position
        faces = {}
        blockinst = self.get_block(position)
        if blockinst is None or type(blockinst) == str:
            return {x: True for x in mcpython.util.enums.EnumSide.iterate()}
        for face in mcpython.util.enums.EnumSide.iterate():
            dx, dy, dz = face.relative
            pos = (x + dx, y + dy, z + dz)
            chunk = self.dimension.get_chunk_for_position(pos, generate=False)
            if chunk is None:
                continue
            if not chunk.is_loaded() and G.world.hide_faces_to_not_generated_chunks:
                faces[face] = False
            else:
                block = self.dimension.get_block(pos)
                if block is None:
                    faces[face] = True
                elif type(block) == str:
                    faces[face] = False  # todo: add an callback when the block is ready
                elif not block.face_solid[face.invert()]:
                    faces[face] = True
                elif not blockinst.face_solid[face]:
                    faces[face] = True
                else:
                    faces[face] = False
        return faces

    def is_position_blocked(self, position: typing.Tuple[float, float, float]) -> bool:
        """
        will return if at an given position is an block or an block is scheduled
        :param position: the position to check
        :return: if there is an block
        """
        return (
            position in self.world
            or G.world_generation_handler.task_handler.get_block(position, self)
            is not None
        )

    def add_block(
        self,
        position: tuple,
        block_name: typing.Union[str, Block.AbstractBlock],
        immediate=True,
        block_update=True,
        block_update_self=True,
        lazy_setup: typing.Callable[[Block.AbstractBlock], None] = None,
    ):
        """
        adds an block to the given position
        :param position: the position to add
        :param block_name: the name of the block or an instance of it
        :param immediate: if the block should be shown if needed
        :param block_update: if an block-update should be send to neighbors blocks
        :param block_update_self: if the block should get an block-update
        :param lazy_setup: an callable for setting up the block instance
        :return: the block instance or None if it could not be created
        """
        if position[1] < 0 or position[1] > 255:
            return
        if position != mcpython.util.math.normalize(position):
            raise ValueError(
                "position '{}' is no valid block position".format(position)
            )
        # logger.println("adding", block_name, "at", position)
        if position in self.world:
            self.remove_block(position, immediate=immediate, block_update=block_update)
        if block_name in [None, "air", "minecraft:air"]:
            return
        if issubclass(type(block_name), Block.AbstractBlock):
            block = block_name
            block.position = position
            if lazy_setup is not None:
                lazy_setup(block)
            block.face_state.update()
        else:
            table = G.registry.get_by_name("block").full_table
            if block_name not in table:
                logger.println(
                    "[CHUNK][ERROR] can't add block named '{}'. Block class not found!".format(
                        block_name
                    )
                )
                return
            block = table[block_name]()
            block.position = position
            if lazy_setup is not None:
                lazy_setup(block)
        block.on_block_added()
        if self.now.day == 13 and self.now.month == 1 and "diorite" in block.NAME:
            logger.println(
                "[WARNING][CLEANUP] you are not allowed to set block '{}' as it contains diorite!".format(
                    block.NAME
                )
            )
            # for developers: easter egg! [DO NOT REMOVE, UUK'S EASTER EGG]
            return self.add_block(position, "minecraft:stone")
        self.world[position] = block
        if immediate:
            if self.exposed(position):
                self.show_block(position)
            if block_update:
                self.on_block_updated(position, include_itself=block_update_self)
            self.check_neighbors(position)
        self.positions_updated_since_last_save.add(position)
        return block

    def on_block_updated(
        self, position: typing.Tuple[int, int, int], include_itself=True
    ):
        """
        will call to the neighbor blocks an block update
        :param position: the position in the center
        :param include_itself: if the block itself should be updated
        """
        x, y, z = position
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                for dz in range(-1, 2):
                    if [dx, dy, dz].count(0) >= 2 and not (
                        not include_itself and dx == dy == dz == 0
                    ):
                        b: Block.AbstractBlock = self.dimension.get_block(
                            (x + dx, y + dy, z + dz)
                        )
                        if b and type(b) != str:
                            try:
                                b.on_block_update()
                            except:
                                logger.print_exception(
                                    "during block-updating block {}".format(b)
                                )

    def remove_block(
        self,
        position: typing.Union[typing.Tuple[int, int, int], Block.AbstractBlock],
        immediate: bool = True,
        block_update: bool = True,
        block_update_self: bool = True,
        reason=Block.BlockRemovalReason.UNKNOWN,
    ):
        """
        Remove the block at the given `position`.
        :param position: The (x, y, z) position of the block to remove.
        :param immediate: Whether or not to immediately remove block from canvas.
        :param block_update: Whether an block-update should be called or not
        :param block_update_self: Whether the block to remove should get an block-update or not
        :param reason: the reason why the block was removed
        """
        if position not in self.world:
            return
        if issubclass(type(position), Block.AbstractBlock):
            position = position.position
        self.world[position].on_block_remove(reason)
        self.world[position].face_state.hide_all()
        del self.world[position]
        if block_update:
            self.on_block_updated(position, include_itself=block_update_self)
        if immediate:
            self.check_neighbors(position)
        self.positions_updated_since_last_save.add(position)

    def check_neighbors(self, position: typing.Tuple[int, int, int]):
        """
        Check all blocks surrounding `position` and ensure their visual
        state is current. This means hiding blocks that are not exposed and
        ensuring that all exposed blocks are shown. Usually used after a block
        is added or removed.
        :param position: the position as the center
        """
        x, y, z = position
        for face in mcpython.util.enums.EnumSide.iterate():
            dx, dy, dz = face.relative
            key = (x + dx, y + dy, z + dz)
            b = self.dimension.get_block(key)
            if b is None or type(b) == str:
                continue
            b.face_state.update(redraw_complete=True)

    def show_block(
        self,
        position: typing.Union[typing.Tuple[int, int, int], Block.AbstractBlock],
        immediate: bool = True,
    ):
        """
        Show the block at the given `position`. This method assumes the
        block has already been added with add_block()
        :param position: The (x, y, z) position of the block to show.
        :param immediate: Whether or not to show the block immediately.
        """
        if issubclass(type(position), Block.AbstractBlock):
            position = position.position
        if position not in self.world:
            return
        if immediate:
            self.world[position].face_state.update(redraw_complete=True)
        else:
            G.world_generation_handler.task_handler.schedule_visual_update(
                self, position
            )

    def hide_block(
        self,
        position: typing.Union[typing.Tuple[int, int, int], Block.AbstractBlock],
        immediate=True,
    ):
        """
        Hide the block at the given `position`. Hiding does not remove the
        block from the world.
        :param position: The (x, y, z) position of the block to hide.
        :param immediate: Whether or not to immediately remove the block from the canvas.

        """
        if issubclass(type(position), Block.AbstractBlock):
            position = position.position
        if immediate:
            if position not in self.world:
                return
            self.world[position].face_state.hide_all()
        else:
            G.world_generation_handler.task_handler.schedule_visual_update(
                self, position
            )

    def show(self, force=False):
        """
        will show the chunk
        :param force: if the chunk show should be forced or not
        """
        if self.visible and not force:
            return
        self.visible = True
        self.update_visible()

    def hide(self, force=False):
        """
        will hide the chunk
        :param force: if the chunk hide should be forced or not
        """
        if not self.visible and not force:
            return
        self.visible = False
        self.hide_all()

    def update_visible_block(self, position: typing.Tuple[int, int, int], hide=True):
        self.positions_updated_since_last_save.add(position)
        if not self.exposed(position):
            self.hide_block(position)
        elif hide:
            self.show_block(position)

    def exposed(self, position: typing.Tuple[int, int, int]) -> bool:
        return any(self.exposed_faces(position).values())

    def update_visible(self, hide=True, immediate=False):
        """
        will update all visible of all blocks of the chunk
        :param hide: if blocks should be hidden if needed
        :param immediate: if immediate call or not
        """
        for position in self.world.keys():
            if immediate:
                G.world_generation_handler.task_handler.schedule_visual_update(
                    self, position
                )
            else:
                self.update_visible_block(position, hide=hide)

    def hide_all(self, immediate=True):
        """
        will hide all blocks in the chunk
        :param immediate: if immediate or not
        """
        for position in self.world:
            self.hide_block(position, immediate=immediate)

    def get_block(
        self, position: typing.Tuple[int, int, int]
    ) -> typing.Union[Block.AbstractBlock, str, None]:
        """
        will get the block at an given position
        :param position: the position to check for
        :return: None if no block, str if scheduled and Block.Block if created
        todo: split up into get_block_generated and get_block_un_generated
        """
        position = mcpython.util.math.normalize(position)
        return (
            self.world[position]
            if position in self.world
            else G.world_generation_handler.task_handler.get_block(position, chunk=self)
        )

    def __del__(self):
        G.world_generation_handler.task_handler.clear_chunk(self)
        for block in self.world.values():
            del block
        self.world.clear()
        self.attr.clear()
        for entity in self.entities:
            del entity
        self.entities.clear()
        del self.dimension

    def __str__(self):
        return "Chunk(dimension={},position={})".format(
            self.dimension.get_id(), self.position
        )

    def is_loaded(self) -> bool:
        return self.loaded

    def is_generated(self) -> bool:
        return self.generated
