"""
mcpython - a minecraft clone written in python licenced under the MIT-licence 
(https://github.com/mcpython4-coding/core)

Contributors: uuk, xkcdjerry (inactive)

Based on the game of fogleman (https://github.com/fogleman/Minecraft), licenced under the MIT-licence
Original game "minecraft" by Mojang Studios (www.minecraft.net), licenced under the EULA
(https://account.mojang.com/documents/minecraft_eula)
Mod loader inspired by "Minecraft Forge" (https://github.com/MinecraftForge/MinecraftForge) and similar

This project is not official by mojang and does not relate to it.
"""
import asyncio
import marshal
import multiprocessing
import pickle
import time
import typing
import weakref

import mcpython.engine.world.AbstractInterface
from mcpython import shared
from mcpython.engine import logger


class WorldGenerationTaskHandler:
    """
    Handler for generating tasks in preparation for off-thread [like MC] & off-process generation
    [even more efficient when correctly implemented]
    todo: make task work more efficient, even without
    """

    def __init__(self):
        self.chunks: weakref.WeakSet[
            mcpython.engine.world.AbstractInterface.IChunk
        ] = weakref.WeakSet()
        self.data_maps = [{}, {}, {}]  # invoke, world_changes, shown_updates

    def get_total_task_stats(self) -> list:
        """
        Will return the sum of all tasks of the whole system, in invoke, world_changes and shown_updates separated
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
        self, chunk: mcpython.engine.world.AbstractInterface.IChunk
    ) -> int:
        """
        Gets the total count of tasks for an given chunk as an int
        :param chunk:
        :return:
        """
        dim = chunk.get_dimension().get_dimension_id()
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
        chunk: mcpython.engine.world.AbstractInterface.IChunk,
        method: typing.Callable | typing.Awaitable,
        *args,
        **kwargs,
    ):
        """
        Schedules a callable-invoke for the future or an await on such a task
        :param chunk: the chunk to link to
        :param method: the method to call
        :param args: the args to call with
        :param kwargs: the kwargs to call with
        """
        if not issubclass(type(chunk), mcpython.engine.world.AbstractInterface.IChunk):
            raise ValueError("chunk must be sub-class of Chunk, not {}".format(chunk))

        if not callable(method) and not asyncio.iscoroutine(method):
            raise ValueError(
                "method must be callable or awaitable in order to be invoked by WorldGenerationTaskHandler"
            )

        self.chunks.add(chunk)
        self.data_maps[0].setdefault(
            chunk.get_dimension().get_dimension_id(), {}
        ).setdefault(chunk.get_position(), []).append((method, args, kwargs))

    def schedule_block_add(
        self,
        chunk: mcpython.engine.world.AbstractInterface.IChunk,
        position: tuple,
        name: str,
        *args,
        on_add=None,
        **kwargs,
    ):
        """
        Schedules an addition of an block
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
        self.data_maps[1].setdefault(
            chunk.get_dimension().get_dimension_id(), {}
        ).setdefault(chunk.get_position(), {})[position] = (name, args, kwargs, on_add)
        self.chunks.add(chunk)

    def schedule_block_remove(
        self,
        chunk: mcpython.engine.world.AbstractInterface.IChunk,
        position: tuple,
        *args,
        on_remove=None,
        **kwargs,
    ):
        """
        Schedules an removal of an block
        :param chunk: the chunk the block is linked to
        :param position: the position of the block
        :param args: the args to call the remove_block-function with
        :param on_remove: an callable to call when the block gets removed, with None as an parameter
        :param kwargs: the kwargs to call the remove_block-function with
        """
        self.data_maps[1].setdefault(
            chunk.get_dimension().get_dimension_id(), {}
        ).setdefault(chunk.get_position(), {})[position] = (
            None,
            args,
            kwargs,
            on_remove,
        )
        self.chunks.add(chunk)

    def schedule_block_show(
        self, chunk: mcpython.engine.world.AbstractInterface.IChunk, position: tuple
    ):
        """
        schedules an show of an block
        :param chunk: the chunk
        :param position: the position of the block
        """
        self.data_maps[2].setdefault(
            chunk.get_dimension().get_dimension_id(), {}
        ).setdefault(chunk.get_position(), {})[position] = 1
        self.chunks.add(chunk)

    def schedule_block_hide(
        self, chunk: mcpython.engine.world.AbstractInterface.IChunk, position: tuple
    ):
        """
        Schedules hiding a block
        :param chunk: the chunk
        :param position: the position of the block
        """
        self.data_maps[2].setdefault(
            chunk.get_dimension().get_dimension_id(), {}
        ).setdefault(chunk.get_position(), {})[position] = 0
        self.chunks.add(chunk)

    def schedule_visual_update(
        self, chunk: mcpython.engine.world.AbstractInterface.IChunk, position: tuple
    ):
        """
        Schedules a visual update of a block (-> show/hide as needed)
        :param chunk: the chunk
        :param position: the position of the block
        """
        self.data_maps[2].setdefault(
            chunk.get_dimension().get_dimension_id(), {}
        ).setdefault(chunk.get_position(), {})[position] = 2
        self.chunks.add(chunk)

    def process_one_task(self, chunk=None, log_msg=False) -> int:
        """
        Processes one task from a semi-random chunk or a given one
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
            self.unsafe_process_0_array(chunk)
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
        Process tasks in chunks [default to all scheduled chunks] until more time than timer is left behind
            [Defaults to no limit]
        :param chunks: if given, an iterable of chunks to generate
        :param timer: if given, an float in seconds to determine how far to generate
        todo: add some better sorting function!
        """
        start = time.time()
        if chunks is None:
            # todo: optimize this!
            chunks = list(self.chunks)

        chunks.sort(key=lambda c: abs(c.position[0] * c.position[1]))

        if timer is not None:
            for chunk in chunks:
                self.process_chunk(chunk, timer=timer)
                timer -= time.time() - start
                if timer < 0:
                    return
                start = time.time()
        else:
            for chunk in chunks:
                self.process_chunk(chunk)

    def process_chunk(
        self, chunk: mcpython.engine.world.AbstractInterface.IChunk, timer=None
    ):
        start = time.time()
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
            if not chunk.generated:
                shared.world_generation_handler.mark_finished(chunk)

            self.chunks.remove(chunk)
            chunk.generated = True
            chunk.finished = True
            chunk.loaded = True

    def _process_0_array(
        self, chunk: mcpython.engine.world.AbstractInterface.IChunk
    ) -> bool:
        dimension = chunk.get_dimension().get_dimension_id()
        if dimension in self.data_maps[0]:
            dim_map = self.data_maps[0][dimension]
            if chunk.get_position() in dim_map:
                return self.unsafe_process_0_array(chunk, dim_map=dim_map)
        return False

    def unsafe_process_0_array(self, chunk, dim_map: dict = None) -> bool:
        if dim_map is None:
            dim_map = self.data_maps[0][chunk.get_dimension().get_dimension_id()]

        m: list = dim_map[chunk.get_position()]
        if len(m) == 0:
            return False

        data = m.pop(0)
        try:
            if asyncio.iscoroutine(data[0]):
                task = asyncio.get_event_loop().create_task(data[0])
                asyncio.get_event_loop().run_until_complete(task)

                if task.exception():
                    raise task.exception()
            else:
                data[0](*data[1], **data[2])
        except (SystemExit, KeyboardInterrupt, OSError):
            raise
        except:
            logger.print_exception(
                "during invoking '{}' with *{} and **{} during world generation".format(
                    *data
                )
            )
        return True

    def _process_1_array(
        self, chunk: mcpython.engine.world.AbstractInterface.IChunk
    ) -> bool:
        # todo: can we optimize this?
        if chunk.get_dimension().get_dimension_id() in self.data_maps[1]:
            dim_map = self.data_maps[1][chunk.get_dimension().get_dimension_id()]
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
                    if data[3] is not None and block is not None:
                        data[3](block)
                return True

        return False

    def _process_2_array(
        self, chunk: mcpython.engine.world.AbstractInterface.IChunk
    ) -> bool:
        # todo: can we optimize this?
        if chunk.get_dimension().get_dimension_id() in self.data_maps[2]:
            dim_map = self.data_maps[2][chunk.get_dimension().get_dimension_id()]
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

                elif not isinstance(block, str) and shared.IS_CLIENT:
                    try:
                        block.face_info.update(redraw_complete=True)
                    except:
                        logger.print_exception(f"during showing block {block}")

                return True

        return False

    def get_block(
        self, position: tuple, chunk: mcpython.engine.world.AbstractInterface.IChunk
    ):
        """
        Gets an generated block from the array
        :param position: the position of the block
        :param chunk: if the chunk is known
        todo: make thread-safe
        """
        dimension = chunk.get_dimension()
        try:
            return self.data_maps[1][dimension.get_dimension_id()][
                chunk.get_position()
            ][position][0]
        except (KeyError, AttributeError):
            pass

    def clear_chunk(self, chunk: mcpython.engine.world.AbstractInterface.IChunk):
        """
        Will remove all scheduled tasks from an given chunk
        :param chunk: the chunk
        """
        dim = chunk.get_dimension().get_dimension_id()
        p = chunk.get_position()
        if dim in self.data_maps[0] and p in self.data_maps[0][dim]:
            del self.data_maps[0][dim][p]
        if dim in self.data_maps[1] and p in self.data_maps[1][dim]:
            del self.data_maps[1][dim][p]
        if dim in self.data_maps[2] and p in self.data_maps[2][dim]:
            del self.data_maps[2][dim][p]
        if chunk.get_position() in self.chunks:
            self.chunks.remove(chunk)

    def clear(self):
        """
        Will remove all scheduled tasks [chunk-wise]
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

    def get_block_name(self, position, chunk=None):
        block = self.get_block(position, chunk)
        if hasattr(block, "NAME"):
            return block.NAME
        return block

    def fill_area(
        self,
        start: typing.Tuple[int, int, int],
        end: typing.Tuple[int, int, int],
        block,
        only_non_air=False,
        **kwargs,
    ):
        for y in range(start[1], end[1] + 1):
            for x in range(start[0], end[0] + 1):
                for z in range(start[2], end[2] + 1):
                    if not only_non_air or self.get_block((x, y, z)) is not None:
                        self.schedule_block_add((x, y, z), block, **kwargs)

    def fill_area_inner_outer(
        self,
        start: typing.Tuple[int, int, int],
        end: typing.Tuple[int, int, int],
        inner_block,
        outer_block,
        only_non_air=False,
        inner_config=None,
        outer_config=None,
    ):
        for y in range(start[1], end[1] + 1):
            for x in range(start[0], end[0] + 1):
                for z in range(start[2], end[2] + 1):
                    if not only_non_air or self.get_block((x, y, z)) is not None:
                        if (
                            y not in (start[1], end[1])
                            and x not in (start[0], end[0])
                            and z not in (start[2], end[2])
                        ):
                            if inner_config is None:
                                self.schedule_block_add((x, y, z), inner_block)
                            else:
                                self.schedule_block_add(
                                    (x, y, z), inner_block, **inner_config
                                )
                        else:
                            if outer_config is None:
                                self.schedule_block_add((x, y, z), outer_block)
                            else:
                                self.schedule_block_add(
                                    (x, y, z), outer_block, **outer_config
                                )

    def replace_air_and_liquid_downwards(self, block, x, y, z, delta, liquids):
        for dy in range(delta, 0, -1):
            b = self.get_block((x, y - dy, z))
            if b is None or b in liquids:
                self.schedule_block_add((x, y - dy, z), block)
            else:
                return

    def get_biome_at(self, x, z) -> str:
        raise NotImplementedError()


class WorldGenerationTaskHandlerReference(IWorldGenerationTaskHandlerReference):
    """
    reference class to an WorldGenerationTaskHandler for setting the chunk globally
    all scheduling functions are the same of WorldGenerationTaskHandler except the chunk-parameter is missing.
    It is set on construction
    """

    def __init__(
        self,
        handler: WorldGenerationTaskHandler,
        chunk: mcpython.engine.world.AbstractInterface.IChunk,
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
        return self.handler.get_block(
            position, chunk if chunk is not None else self.chunk
        )

    def get_biome_at(self, x, z) -> str:
        return self.chunk.get_value("minecraft:biome_map")[x, z]


class OffProcessTaskHelper:
    class OffProcessTaskHelperShared:
        def __init__(
            self, reference: "ProcessSeparatedWorldGenerationTaskHandlerReference"
        ):
            self.running = True
            self.reference = reference

            self.task_queue = multiprocessing.Queue()
            self.task_data_out = multiprocessing.Queue()

        def run(self):
            while self.running:
                self.reference.execute_tasks()

    def __init__(self, chunk):
        self.chunk = chunk
        self.shared = OffProcessTaskHelper.OffProcessTaskHelperShared()
        self.process = multiprocessing.Process(target=self.shared.run)
        self.process.start()
        self.reference: typing.Optional[
            "ProcessSeparatedWorldGenerationTaskHandlerReference"
        ] = None

    def stop(self):
        self.shared.running = False

    def run_main(
        self,
        manager: "RemoteTaskHandlerManager",
        default: WorldGenerationTaskHandlerReference,
    ):
        while not self.shared.task_data_out.empty():
            task, *data = self.shared.task_data_out.get()
            if task == 1:
                method, *args = marshal.loads(data[0]), pickle.loads(data[1])
                if args[2]:
                    method(default, *args[0], **args[2])
                else:
                    self.shared.task_queue.put((method,) + data)

            elif task == 2:
                position, name, args, kwargs = pickle.loads(data[0])
                on_add = None if data[1] is None else marshal.loads(data[1])

                # todo: can we use an lambda to move post-execution off-process?
                default.schedule_block_add(
                    position, name, *args, on_add=on_add, **kwargs
                )

            elif task == 3:
                position, args, kwargs = pickle.loads(data[0])
                on_remove = None if data[1] is None else marshal.loads(data[1])
                default.schedule_block_remove(
                    position, *args, on_remove=on_remove, **kwargs
                )

            else:
                position = data[0]

                if task == 4:
                    default.schedule_block_show(position)
                elif task == 5:
                    default.schedule_block_hide(position)
                elif task == 6:
                    default.schedule_visual_update(position)

    def run_layer_generation(self, layer, config):
        self.shared.task_queue.put(
            (
                1,
                marshal.dumps(layer.add_generate_functions_to_chunk),
                pickle.dumps(([config, self.reference], {})),
            )
        )


class RemoteTaskHandlerManager:
    def __init__(self):
        self.references: typing.List[
            typing.Tuple[
                OffProcessTaskHelper,
                "ProcessSeparatedWorldGenerationTaskHandlerReference",
                WorldGenerationTaskHandlerReference,
            ]
        ] = []

    def create(
        self,
        chunk: mcpython.engine.world.AbstractInterface.IChunk,
        default: WorldGenerationTaskHandlerReference,
    ) -> typing.Tuple[
        "ProcessSeparatedWorldGenerationTaskHandlerReference", OffProcessTaskHelper
    ]:
        helper_instance = OffProcessTaskHelper(chunk)
        array_instance = ProcessSeparatedWorldGenerationTaskHandlerReference(
            helper_instance.shared, chunk.as_shareable()
        )
        helper_instance.reference = array_instance
        self.references.append((helper_instance, array_instance, default))
        return array_instance, helper_instance

    def tick(self):
        for helper, array, default in self.references:
            helper.run_main(self, default)


class ProcessSeparatedWorldGenerationTaskHandlerReference(
    IWorldGenerationTaskHandlerReference
):
    """
    Reference class to an WorldGenerationTaskHandler for setting the chunk globally
    all scheduling functions are the same of WorldGenerationTaskHandler except the chunk-parameter is missing.
    It is set on construction
    WARNING: does need an assigned group of RemoteTaskHandlerReference and OffProcessTaskHelper to work correctly.
    Use RemoteTaskHandlerManager.create(<chunk>, <reference>) returning this object and an assigned OffProcessTaskHelper instance
    ready to go
    """

    def __init__(
        self,
        shared_helper: OffProcessTaskHelper.OffProcessTaskHelperShared,
        chunk: mcpython.engine.world.AbstractInterface.IChunk,
    ):
        self.shared_helper = shared_helper
        self.chunk = chunk
        self.tasks = []

    def schedule_invoke(self, method, *args, force_main=False, **kwargs):
        self.shared_helper.task_data_out.put(
            (1, marshal.dumps(method), pickle.dumps((args, kwargs)), force_main)
        )

    def schedule_block_add(self, position, name, *args, on_add=None, **kwargs):
        self.shared_helper.task_data_out.put(
            (
                2,
                pickle.dumps((position, name, args, kwargs)),
                None if on_add is None else marshal.dumps(on_add),
            )
        )

    def schedule_block_remove(self, position, *args, on_remove=None, **kwargs):
        self.shared_helper.task_data_out.put(
            (
                3,
                pickle.dumps((position, args, kwargs)),
                None if on_remove is None else marshal.dumps(on_remove),
            )
        )

    def schedule_block_show(self, position):
        self.shared_helper.task_data_out.put((4, position))

    def schedule_block_hide(self, position):
        self.shared_helper.task_data_out.put((5, position))

    def schedule_visual_update(self, position):
        self.shared_helper.task_data_out.put((6, position))

    def get_block(self, position: tuple, chunk=None):
        pass  # todo: implement!

    def execute_tasks(self):
        while not self.shared_helper.task_queue.empty():
            task, *data = self.shared_helper.task_queue.get()
            if task == 1:
                method, *args = marshal.loads(data[0]), pickle.loads(data[1])
                if args[2]:
                    self.schedule_invoke(method, *args[1], force_main=True, **args[2])
                else:
                    method(self, *args[0], **args[1])
            else:
                # todo: implement shared logger
                print(
                    "[WARN] failed to run task {}: {} from off-process handler!".format(
                        task, data
                    )
                )

    def get_biome_at(self, x, z) -> str:
        pass  # todo: implement!
