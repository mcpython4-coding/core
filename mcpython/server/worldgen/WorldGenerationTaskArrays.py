"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import mcpython.common.world.Chunk
import mcpython.common.world.AbstractInterface
import time
from mcpython import shared
from mcpython import logger


class WorldGenerationTaskHandler:
    """
    handler for generating tasks off-call
    todo: make task work more efficient!!!
    """

    def __init__(self):
        self.chunks = set()
        self.data_maps = [{}, {}, {}]  # invoke, world_changes, shown_updates

    def get_total_task_stats(self) -> list:
        """
        will return the sum of all tasks of the whole system, in invoke, world_changes and shown_updates separated
        """
        stats = []
        for d in self.data_maps:
            count = 0
            for dim in d.values():
                for chunk in dim.values():
                    count += len(chunk)
            stats.append(count)
        return stats

    def get_task_count_for_chunk(self, chunk: mcpython.common.world.AbstractInterface.IChunk) -> int:
        """
        gets the total count of tasks for an given chunk as an int
        :param chunk:
        :return:
        """
        dim = chunk.dimension.id
        p = chunk.position
        count = 0
        try:
            count += len(self.data_maps[0][dim][p])
        except (IndexError, KeyError):
            pass
        try:
            count += len(self.data_maps[1][dim][p])
        except (IndexError, KeyError):
            pass
        try:
            count += len(self.data_maps[2][dim][p])
        except (IndexError, KeyError):
            pass
        return count

    def schedule_invoke(
        self, chunk: mcpython.common.world.AbstractInterface.IChunk, method, *args, **kwargs
    ):
        """
        schedules an callable-invoke for the future
        :param chunk: the chunk to link to
        :param method: the method to call
        :param args: the args to call with
        :param kwargs: the kwargs to call with
        """
        if not issubclass(type(chunk), mcpython.common.world.AbstractInterface.IChunk):
            raise ValueError("chunk must be sub-class of Chunk, not {}".format(chunk))
        if not callable(method):
            raise ValueError(
                "method must be callable in order to be invoked by WorldGenerationTaskHandler"
            )
        self.chunks.add(chunk)
        self.data_maps[0].setdefault(chunk.dimension.id, {}).setdefault(
            chunk.position, []
        ).append((method, args, kwargs))

    def schedule_block_add(
        self,
        chunk: mcpython.common.world.Chunk.Chunk,
        position: tuple,
        name: str,
        *args,
        on_add=None,
        **kwargs
    ):
        """
        schedules an addition of an block
        :param chunk: the chunk the block is linked to
        :param position: the position of the block
        :param name: the name of the block
        :param args: the args to send to the add_block-method
        :param on_add: an callable called together with the block instance when the block is added
        :param kwargs: the kwargs send to the add_block-method
        """
        if "immediate" not in kwargs or kwargs["immediate"]:
            self.schedule_visual_update(chunk, position)
        kwargs["immediate"] = False
        self.data_maps[1].setdefault(chunk.dimension.id, {}).setdefault(
            chunk.position, {}
        )[position] = (name, args, kwargs, on_add)
        self.chunks.add(chunk)

    def schedule_block_remove(
        self,
        chunk: mcpython.common.world.Chunk.Chunk,
        position: tuple,
        *args,
        on_remove=None,
        **kwargs
    ):
        """
        schedules an removal of an block
        :param chunk: the chunk the block is linked to
        :param position: the position of the block
        :param args: the args to call the remove_block-function with
        :param on_remove: an callable to call when the block gets removed, with None as an parameter
        :param kwargs: the kwargs to call the remove_block-function with
        """
        self.data_maps[1].setdefault(chunk.dimension.id, {}).setdefault(
            chunk.position, {}
        )[position] = (None, args, kwargs, on_remove)
        self.chunks.add(chunk)

    def schedule_block_show(
        self, chunk: mcpython.common.world.Chunk.Chunk, position: tuple
    ):
        """
        schedules an show of an block
        :param chunk: the chunk
        :param position: the position of the block
        """
        self.data_maps[2].setdefault(chunk.dimension.id, {}).setdefault(
            chunk.position, {}
        )[position] = 1
        self.chunks.add(chunk)

    def schedule_block_hide(
        self, chunk: mcpython.common.world.Chunk.Chunk, position: tuple
    ):
        """
        schedules an hide of an block
        :param chunk: the chunk
        :param position: the position of the block
        """
        self.data_maps[2].setdefault(chunk.dimension.id, {}).setdefault(
            chunk.position, {}
        )[position] = 0
        self.chunks.add(chunk)

    def schedule_visual_update(
        self, chunk: mcpython.common.world.Chunk.Chunk, position: tuple
    ):
        """
        schedules an visual update of an block (-> show/hide as needed)
        :param chunk: the chunk
        :param position: the position of the block
        """
        self.data_maps[2].setdefault(chunk.dimension.id, {}).setdefault(
            chunk.position, {}
        )[position] = 2
        self.chunks.add(chunk)

    def process_one_task(self, chunk=None, log_msg=False) -> int:
        """
        processes one task from an semi-random chunk or an given one
        :param chunk: the chunk or None to select one
        :param log_msg: if messages for extra info should be logged
        """
        start = time.time()
        if not shared.worldgenerationhandler.enable_generation:
            return 0
        if chunk is None:
            if len(self.chunks) == 0:
                return 1
            chunk = self.chunks.pop()
            self.chunks.add(chunk)
        if log_msg:
            logger.println("[WORLD][HANDLER] processing chunk {}".format(chunk))
        if (
            self._process_0_array(chunk)
            or self._process_1_array(chunk)
            or self._process_2_array(chunk)
        ):
            if log_msg:
                logger.println(
                    "executing took {}s in chunk {}".format(time.time() - start, chunk)
                )
            return 2
        if self.get_task_count_for_chunk(chunk) == 0:
            self.chunks.remove(chunk)
            chunk.generated = True
            chunk.finished = True
            chunk.loaded = True
        return 3

    def process_tasks(self, chunks=None, timer=None):
        """
        process tasks
        :param chunks: if given, an iterable of chunks to generate
        :param timer: if given, an float in seconds to determine how far to generate
        """
        start = time.time()
        if chunks is None:
            chunks = list(self.chunks)
        chunks.sort(key=lambda chunk: abs(chunk.position[0] * chunk.position[1]))
        for chunk in chunks:
            flag = True
            while flag:
                flag = (
                    self._process_0_array(chunk)
                    or self._process_1_array(chunk)
                    or self._process_2_array(chunk)
                )
                if timer is not None and time.time() - start >= timer:
                    return
            if chunk in self.chunks:
                self.chunks.remove(chunk)
                chunk.generated = True
                chunk.finished = True
                chunk.loaded = True
                shared.eventhandler.call("worldgen:chunk:finished", chunk)

    def _process_0_array(self, chunk: mcpython.common.world.Chunk.Chunk) -> bool:
        if chunk.dimension.id in self.data_maps[0]:
            dim_map = self.data_maps[0][chunk.dimension.id]
            if chunk.position in dim_map:
                m: list = dim_map[chunk.position]
                if len(m) == 0:
                    return False
                data = m.pop(0)
                try:
                    data[0](*data[1], **data[2])
                except:
                    logger.print_exception(
                        "during invoking '{}' with *{} and **{}".format(*data)
                    )
                return True
        return False

    def _process_1_array(self, chunk: mcpython.common.world.Chunk.Chunk) -> bool:
        if chunk.dimension.id in self.data_maps[1]:
            dim_map = self.data_maps[1][chunk.dimension.id]
            if chunk.position in dim_map:
                m: dict = dim_map[chunk.position]
                if len(m) == 0:
                    return False
                position, data = m.popitem()
                if data[0] is None:
                    chunk.remove_block(position, **data[2])
                    if data[3] is not None:
                        data[3](None)
                else:
                    block = chunk.add_block(position, data[0], **data[2])
                    if data[3] is not None:
                        data[3](block)
                return True
        return False

    def _process_2_array(self, chunk: mcpython.common.world.Chunk.Chunk) -> bool:
        if chunk.dimension.id in self.data_maps[2]:
            dim_map = self.data_maps[2][chunk.dimension.id]
            if chunk.position in dim_map:
                m: dict = dim_map[chunk.position]
                if len(m) == 0:
                    return False
                position, data = m.popitem()
                block = chunk.get_block(position)
                if type(block) == str or block is None:
                    return True
                if data == 0:
                    chunk.hide_block(position)
                elif data == 1:
                    chunk.show_block(position)
                else:
                    block.face_state.update(redraw_complete=True)
                return True
        return False

    def get_block(self, position: tuple, chunk=None, dimension=None):
        """
        gets an generated block from the array
        :param position: the position of the block
        :param chunk: if the chunk is known
        :param dimension: if the dimension is known
        """
        if chunk is None:
            if dimension is None:
                dimension = shared.world.get_active_dimension()
            chunk = dimension.get_chunk_for_position(position)
        try:
            return self.data_maps[1][dimension.id][chunk.position][position][0]
        except (KeyError, AttributeError):
            pass

    def clear_chunk(self, chunk: mcpython.common.world.Chunk.Chunk):
        """
        will remove all scheduled tasks from an given chunk
        :param chunk: the chunk
        """
        dim = chunk.dimension.id
        p = chunk.position
        if dim in self.data_maps[0] and p in self.data_maps[0][dim]:
            del self.data_maps[0][dim][p]
        if dim in self.data_maps[1] and p in self.data_maps[1][dim]:
            del self.data_maps[1][dim][p]
        if dim in self.data_maps[2] and p in self.data_maps[2][dim]:
            del self.data_maps[2][dim][p]
        if chunk in self.chunks:
            self.chunks.remove(chunk)

    def clear(self):
        """
        will remove all scheduled tasks [chunk-wise]
        """
        for chunk in self.chunks.copy():
            self.clear_chunk(chunk)


class WorldGenerationTaskHandlerReference:
    """
    reference class to an WorldGenerationTaskHandler for setting the chunk globally
    all scheduling functions are the same of WorldGenerationTaskHandler exept the chunk-parameter is missing.
    It is set on construction
    """

    def __init__(
        self,
        handler: WorldGenerationTaskHandler,
        chunk: mcpython.common.world.Chunk.Chunk,
    ):
        self.handler = handler
        self.chunk = chunk

    def schedule_invoke(self, method, *args, **kwargs):
        self.handler.schedule_invoke(self.chunk, method, *args, **kwargs)

    def schedule_block_add(self, position, name, *args, on_add=None, **kwargs):
        self.handler.schedule_block_add(
            self.chunk, position, name, *args, on_add=on_add, **kwargs
        )

    def schedule_block_remove(self, position, *args, on_remove=None, **kwargs):
        self.handler.schedule_block_remove(
            self.chunk, position, *args, on_remove=on_remove, **kwargs
        )

    def schedule_block_show(self, position):
        self.handler.schedule_block_show(self.chunk, position)

    def schedule_block_hide(self, position):
        self.handler.schedule_block_hide(self.chunk, position)

    def schedule_visual_update(self, position):
        self.handler.schedule_visual_update(self.chunk, position)

    def process_one_task(self, chunk=None, reorder=True, log_msg=True):
        self.handler.process_one_task(chunk, reorder, log_msg)

    def get_block(self, position, chunk=None, dimension=None):
        return self.handler.get_block(position, chunk, dimension)
