"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import mcpython.common.world.AbstractInterface
import time
from mcpython import logger
import multiprocessing


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

    def get_task_count_for_chunk(
        self, chunk: mcpython.common.world.AbstractInterface.IChunk
    ) -> int:
        """
        gets the total count of tasks for an given chunk as an int
        :param chunk:
        :return:
        """
        dim = chunk.get_dimension().get_id()
        p = chunk.get_position()
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
        self,
        chunk: mcpython.common.world.AbstractInterface.IChunk,
        method,
        *args,
        **kwargs
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
        self.data_maps[0].setdefault(chunk.get_dimension().get_id(), {}).setdefault(
            chunk.get_position(), []
        ).append((method, args, kwargs))

    def schedule_block_add(
        self,
        chunk: mcpython.common.world.AbstractInterface.IChunk,
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
        self.data_maps[1].setdefault(chunk.get_dimension().get_id(), {}).setdefault(
            chunk.get_position(), {}
        )[position] = (name, args, kwargs, on_add)
        self.chunks.add(chunk)

    def schedule_block_remove(
        self,
        chunk: mcpython.common.world.AbstractInterface.IChunk,
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
        self.data_maps[1].setdefault(chunk.get_dimension().get_id(), {}).setdefault(
            chunk.get_position(), {}
        )[position] = (None, args, kwargs, on_remove)
        self.chunks.add(chunk)

    def schedule_block_show(
        self, chunk: mcpython.common.world.AbstractInterface.IChunk, position: tuple
    ):
        """
        schedules an show of an block
        :param chunk: the chunk
        :param position: the position of the block
        """
        self.data_maps[2].setdefault(chunk.get_dimension().get_id(), {}).setdefault(
            chunk.get_position(), {}
        )[position] = 1
        self.chunks.add(chunk)

    def schedule_block_hide(
        self, chunk: mcpython.common.world.AbstractInterface.IChunk, position: tuple
    ):
        """
        schedules an hide of an block
        :param chunk: the chunk
        :param position: the position of the block
        """
        self.data_maps[2].setdefault(chunk.get_dimension().get_id(), {}).setdefault(
            chunk.get_position(), {}
        )[position] = 0
        self.chunks.add(chunk)

    def schedule_visual_update(
        self, chunk: mcpython.common.world.AbstractInterface.IChunk, position: tuple
    ):
        """
        schedules an visual update of an block (-> show/hide as needed)
        :param chunk: the chunk
        :param position: the position of the block
        """
        self.data_maps[2].setdefault(chunk.get_dimension().get_id(), {}).setdefault(
            chunk.get_position(), {}
        )[position] = 2
        self.chunks.add(chunk)

    def process_one_task(self, chunk=None, log_msg=False) -> int:
        """
        processes one task from an semi-random chunk or an given one
        :param chunk: the chunk or None to select one
        :param log_msg: if messages for extra info should be logged
        """
        start = time.time()
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

    def _process_0_array(
        self, chunk: mcpython.common.world.AbstractInterface.IChunk
    ) -> bool:
        if chunk.get_dimension().get_id() in self.data_maps[0]:
            dim_map = self.data_maps[0][chunk.get_dimension().get_id()]
            if chunk.get_position() in dim_map:
                m: list = dim_map[chunk.get_position()]
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

    def _process_1_array(
        self, chunk: mcpython.common.world.AbstractInterface.IChunk
    ) -> bool:
        if chunk.get_dimension().get_id() in self.data_maps[1]:
            dim_map = self.data_maps[1][chunk.get_dimension().get_id()]
            if chunk.get_position() in dim_map:
                m: dict = dim_map[chunk.get_position()]
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

    def _process_2_array(
        self, chunk: mcpython.common.world.AbstractInterface.IChunk
    ) -> bool:
        if chunk.get_dimension().get_id() in self.data_maps[2]:
            dim_map = self.data_maps[2][chunk.get_dimension().get_id()]
            if chunk.get_position() in dim_map:
                m: dict = dim_map[chunk.get_position()]
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
                elif not isinstance(block, str):
                    block.face_state.update(redraw_complete=True)
                return True
        return False

    def get_block(
        self, position: tuple, chunk: mcpython.common.world.AbstractInterface.IChunk
    ):
        """
        gets an generated block from the array
        :param position: the position of the block
        :param chunk: if the chunk is known
        """
        dimension = chunk.get_dimension()
        try:
            return self.data_maps[1][dimension.get_id()][chunk.get_position()][
                position
            ][0]
        except (KeyError, AttributeError):
            pass

    def clear_chunk(self, chunk: mcpython.common.world.AbstractInterface.IChunk):
        """
        will remove all scheduled tasks from an given chunk
        :param chunk: the chunk
        """
        dim = chunk.get_dimension().get_id()
        p = chunk.get_position()
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


class IWorldGenerationTaskHandlerReference:
    def schedule_invoke(self, method, *args, **kwargs):
        raise NotImplementedError()

    def schedule_block_add(self, position, name, *args, on_add=None, **kwargs):
        raise NotImplementedError()

    def schedule_block_remove(self, position, *args, on_remove=None, **kwargs):
        raise NotImplementedError()

    def schedule_block_show(self, position):
        raise NotImplementedError()

    def schedule_block_hide(self, position):
        raise NotImplementedError()

    def schedule_visual_update(self, position):
        raise NotImplementedError()

    def get_block(self, position, chunk=None):
        raise NotImplementedError()


class WorldGenerationTaskHandlerReference(IWorldGenerationTaskHandlerReference):
    """
    reference class to an WorldGenerationTaskHandler for setting the chunk globally
    all scheduling functions are the same of WorldGenerationTaskHandler exept the chunk-parameter is missing.
    It is set on construction
    """

    def __init__(
        self,
        handler: WorldGenerationTaskHandler,
        chunk: mcpython.common.world.AbstractInterface.IChunk,
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

    def get_block(self, position, chunk=None):
        return self.handler.get_block(position, chunk)


class OffProcessTaskHelper:
    class OffProcessTaskHelperShared:
        def __init__(self):
            self.running = True

            self.task_queue = multiprocessing.Queue()
            self.task_data_out = multiprocessing.Queue()

        def run(self):
            while self.running:
                if not self.task_queue.empty():
                    layer, reference, config = self.task_queue.get()
                    layer.add_generate_functions_to_chunk(config, reference)
                    reference.execute_tasks()

    def __init__(self):
        self.shared = OffProcessTaskHelper.OffProcessTaskHelperShared()
        self.process = multiprocessing.Process(target=self.shared.run)
        self.process.start()

    def stop(self):
        self.shared.running = False

    def tick(self):
        pass

    def run_layer_generation(
        self, chunk: mcpython.common.world.AbstractInterface.IChunk, layer, config
    ):
        reference = ProcessSeparatedWorldGenerationTaskHandlerReference(
            self.shared, chunk.as_shareable()
        )
        self.shared.task_queue.put((layer, reference, config))


class ProcessSeparatedWorldGenerationTaskHandlerReference(
    IWorldGenerationTaskHandlerReference
):
    """
    reference class to an WorldGenerationTaskHandler for setting the chunk globally
    all scheduling functions are the same of WorldGenerationTaskHandler exept the chunk-parameter is missing.
    It is set on construction
    """

    def __init__(
        self,
        shared_helper: OffProcessTaskHelper.OffProcessTaskHelperShared,
        chunk: mcpython.common.world.AbstractInterface.IChunk,
    ):
        self.shared_helper = shared_helper
        self.chunk = chunk
        self.tasks = []

    def schedule_invoke(self, method, *args, **kwargs):
        pass

    def schedule_block_add(self, position, name, *args, on_add=None, **kwargs):
        pass

    def schedule_block_remove(self, position, *args, on_remove=None, **kwargs):
        pass

    def schedule_block_show(self, position):
        pass

    def schedule_block_hide(self, position):
        pass

    def schedule_visual_update(self, position):
        pass

    def get_block(self, position, chunk=None):
        pass

    def execute_tasks(self):
        pass
