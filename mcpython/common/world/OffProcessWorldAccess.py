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
import sys
import types
import typing

import mcpython.engine.world.AbstractInterface
import mcpython.util
import mcpython.util.enums
import mcpython.util.math
from mcpython.engine.world.AbstractInterface import IChunk


class OffProcessWorldHelper:
    """
    Some huge, complex system for asynchronous world-access-able multiprocessing.
    Use OffProcessWorldHelper.spawn_process(World) for creating a new process linke to the given world.
    You MUST call run_tasks() regular on your RemoteWorldHelperReference to process tasks to run on main!
    """

    class OffProcessWorldContext:
        def __init__(
            self, world: mcpython.engine.world.AbstractInterface.IWorld, helper
        ):
            self.world = world
            self.helper = helper

        def get_world(self) -> mcpython.engine.world.AbstractInterface.IWorld:
            return self.world

        def get_helper(self) -> "OffProcessWorldHelper":
            return self.helper

    class OffProcessWorldHelperReference:
        def __init__(
            self,
            instance: "OffProcessWorldHelper",
            process: multiprocessing.Process,
            world: mcpython.engine.world.AbstractInterface.IWorld,
        ):
            self.instance = instance
            self.process = process
            self.context = OffProcessWorldHelper.OffProcessWorldContext(world, instance)

        def stop(self, immediate=True):
            self.run_on_process(lambda context: context.get_helper().stop())

            if immediate:
                self.process.join()

        def run_tasks(self):
            while not self.instance.task_main_queue.empty():
                task = self.instance.task_main_queue.get()
                OffProcessWorldHelper.run_task(
                    task,
                    lambda task_id, result: self.instance.task_result_queue.put(
                        (task_id, result)
                    ),
                    self.context,
                )

        def run_on_process(self, func, *args, **kwargs):
            self.instance.task_off_process_queue.put(
                self.instance.encode_task(
                    func,
                    args,
                    kwargs,
                    (
                        -1,
                        False,
                    ),
                )
            )

        def get_worker_count(self):
            return self.instance.get_worker_count()

    @classmethod
    def spawn_process(
        cls, world: mcpython.engine.world.AbstractInterface.IWorld
    ) -> "OffProcessWorldHelper.OffProcessWorldHelperReference":
        instance = cls()
        process = multiprocessing.Process(target=instance.run)
        process.start()
        return OffProcessWorldHelper.OffProcessWorldHelperReference(
            instance, process, world
        )

    @classmethod
    def run_task(cls, task, result_helper, context):
        task, args, kwargs, (task_id, wait_for_result) = cls.decode_task(task)
        result = task(context, *args, **kwargs)
        if wait_for_result:
            result_helper(task_id, result)

    @classmethod
    def run_task_async(cls, task, context):
        task, args, kwargs, info = cls.decode_task(task)

        async def run():
            context.get_helper().worker_count.value += 1
            p = task(context, *args, **kwargs)

            if isinstance(p, typing.Coroutine):
                await p

            context.get_helper().worker_count.value -= 1

        asyncio.ensure_future(run())

    @classmethod
    def decode_task(cls, task) -> typing.Tuple[typing.Callable, list, dict, typing.Any]:
        data, args, kwargs, info = pickle.loads(task)
        return (
            types.FunctionType(marshal.loads(data), globals()),
            args,
            kwargs,
            info,
        )

    @classmethod
    def encode_task(cls, func, args, kwargs, info) -> bytes:
        return pickle.dumps((marshal.dumps(func.__code__), args, kwargs, info))

    def __init__(self):
        self.task_main_queue = multiprocessing.Queue()
        self.task_off_process_queue = multiprocessing.Queue()
        self.task_result_queue = multiprocessing.Queue()

        self.running = True
        self.inner_task_id = 0
        self.worker_count = multiprocessing.Value("i", 0)

        self.pending_result_waits = {}

    def get_worker_count(self) -> int:
        return self.worker_count.value

    def stop(self):
        self.running = False

    def run(self):
        try:
            asyncio.run(self.main())
        except (SystemExit, KeyboardInterrupt):
            self.run_on_main(lambda ctx: sys.exit(1))
            self.stop()

    async def main(self):
        context = OffProcessWorldHelper.OffProcessWorldContext(
            OffProcessWorld(self), self
        )

        while self.running:
            while not self.task_off_process_queue.empty():
                task = self.task_off_process_queue.get()
                self.run_task_async(task, context)

            while not self.task_result_queue.empty():
                task_id, result = self.task_result_queue.get()
                self.pending_result_waits[task_id] = result

            await asyncio.sleep(0.1)

    async def run_on_main_async(self, func, *args, **kwargs):
        task_id = self.inner_task_id
        self.inner_task_id += 1
        self.task_main_queue.put(
            self.encode_task(
                func,
                args,
                kwargs,
                (
                    task_id,
                    True,
                ),
            )
        )
        while task_id not in self.pending_result_waits:
            await asyncio.sleep(0.2)
        result = self.pending_result_waits[task_id]
        del self.pending_result_waits[task_id]
        return result

    def run_on_main(self, func, *args, **kwargs):
        self.task_main_queue.put(
            self.encode_task(
                func,
                args,
                kwargs,
                (
                    -1,
                    False,
                ),
            )
        )

    def run_on_process(self, func, *args, **kwargs):
        self.task_off_process_queue.put(
            self.encode_task(
                func,
                args,
                kwargs,
                (
                    -1,
                    False,
                ),
            )
        )


class OffProcessWorld(mcpython.engine.world.AbstractInterface.IWorld):
    def __init__(self, helper: OffProcessWorldHelper):
        self.helper = helper
        self.chunk_dimension_cache = {}

    async def get_dimension_names(self) -> typing.Iterable[str]:
        return await self.helper.run_on_main_async(
            lambda context: context.get_world().get_dimension_names()
        )

    async def add_player(
        self, name: str, add_inventories: bool = True, override: bool = True
    ):
        # todo: await remote entity instance
        self.helper.run_on_main(
            lambda context: asyncio.get_event_loop().run_until_complete(context.get_world().add_player(
                name, add_inventories=add_inventories, override=override
            ))
        )

    async def get_active_player(self, create: bool = True) -> typing.Optional:
        raise NotImplementedError  # todo: implement

    async def reset_config(self):
        self.helper.run_on_main(lambda context: context.get_world().reset_config())

    async def get_active_dimension(self) -> typing.Union["OffProcessDimension", None]:
        dim_id = await self.helper.run_on_main_async(
            lambda context: context.get_world()
            .get_active_dimension()
            .get_dimension_id()
        )
        if dim_id in self.chunk_dimension_cache:
            return self.chunk_dimension_cache[dim_id]
        dim = self.chunk_dimension_cache.setdefault(
            dim_id, OffProcessDimension(self.helper, dim_id, self)
        )
        await dim.setup()
        return dim

    async def add_dimension(
        self, dim_id: int, name: str, dim_config=None
    ) -> "OffProcessDimension":
        await self.helper.run_on_main_async(
            lambda context: context.get_world()
            .add_dimension(dim_id, name, dim_config)
            .get_dimension_id()
        )
        dim = self.chunk_dimension_cache.setdefault(
            name, OffProcessDimension(self.helper, dim_id, self)
        )
        await dim.setup()
        return dim

    async def join_dimension(self, dim_id: int):
        await self.helper.run_on_main_async(
            lambda context: context.get_world().join_dimension(dim_id)
        )

    async def get_dimension(self, dim_id: int) -> "OffProcessDimension":
        dim = self.chunk_dimension_cache.setdefault(
            dim_id, OffProcessDimension(self.helper, dim_id, self)
        )
        await dim.setup()
        return dim

    async def hit_test(
        self,
        position: typing.Tuple[float, float, float],
        vector: typing.Tuple[float, float, float],
        max_distance: int = 8,
    ) -> typing.Union[
        typing.Tuple[
            typing.Tuple[int, int, int],
            typing.Tuple[int, int, int],
            typing.Tuple[float, float, float],
        ],
        typing.Tuple[None, None, None],
    ]:
        return await self.helper.run_on_main_async(
            lambda context: context.get_world().hit_test(position, vector, max_distance)
        )

    async def show_chunk(self, chunk: typing.Union[typing.Tuple[int, int], IChunk]):
        raise NotImplementedError

    async def hide_chunk(self, chunk: typing.Union[typing.Tuple[int, int], IChunk]):
        raise NotImplementedError

    async def change_chunks(
        self,
        before: typing.Union[typing.Tuple[int, int], None],
        after: typing.Union[typing.Tuple[int, int], None],
        generate_chunks=True,
        load_immediate=True,
    ):
        raise NotImplementedError

    async def cleanup(self, remove_dims=False, filename=None):
        await self.helper.run_on_main_async(
            lambda context: context.get_world().cleanup(
                remove_dims=remove_dims, filename=filename
            )
        )

    async def setup_by_filename(self, filename: str):
        await self.helper.run_on_main_async(
            lambda context: context.get_world().setup_by_filename(filename)
        )


class OffProcessDimension(mcpython.engine.world.AbstractInterface.IDimension):
    def __init__(
        self, helper: OffProcessWorldHelper, dimension_id: int, world: OffProcessWorld
    ):
        super().__init__()
        self.helper = helper
        self.dimension_id = dimension_id
        self.dimension_range = None
        self.dimension_name = None
        self.world = world

        self.chunk_cache = {}

    async def setup(self):
        self.dimension_range, self.dimension_name = await self.helper.run_on_main_async(
            lambda context: (
                context.get_world()
                .get_dimension(self.dimension_id)
                .get_world_height_range(),
                context.get_world().get_dimension(self.dimension_id).get_name(),
            )
        )

    def get_world_height_range(self) -> typing.Tuple[int, int]:
        return self.dimension_range

    def get_dimension_id(self):
        return self.dimension_id

    def get_name(self) -> str:
        return self.dimension_name

    async def get_chunk(
        self,
        cx: typing.Union[int, typing.Tuple[int, int]],
        cz: int = None,
        generate: bool = True,
        create: bool = True,
    ) -> "OffProcessChunk":

        if cz is None:
            assert type(cx) == tuple
            cx, cz = cx

        if (cx, cz) in self.chunk_cache:
            return self.chunk_cache[(cx, cz)]

        chunk = self.chunk_cache.setdefault(
            (cx, cz), OffProcessChunk(self.helper, (cx, cz), self)
        )
        await chunk.setup()
        return chunk

    async def get_chunk_for_position(
        self,
        position: typing.Union[
            typing.Tuple[float, float, float],
            typing.Any,
        ],
        **kwargs
    ) -> typing.Optional["OffProcessChunk"]:
        if hasattr(position, "position"):
            position = position.position
        pos = mcpython.util.math.position_to_chunk(position)
        return await self.get_chunk(*pos)

    async def get_block(
        self, position: typing.Tuple[int, int, int], none_if_str=False
    ) -> typing.Union[typing.Any, str, None]:
        # todo: some form of remote block / only the block name?
        return await self.helper.run_on_main_async(
            lambda context: context.get_world()
            .get_dimension(self.dimension_id)
            .get_block(position, none_if_str=none_if_str)
        )

    async def add_block(self, *args, **kwargs):
        # todo: some form of remote block / only the block name?
        return await self.helper.run_on_main_async(
            lambda context: context.get_world()
            .get_dimension(self.dimension_id)
            .add_block(*args, **kwargs)
        )

    async def remove_block(self, *args, **kwargs):
        await self.helper.run_on_main_async(
            lambda context: context.get_world()
            .get_dimension(self.dimension_id)
            .remove_block(*args, **kwargs)
        )

    async def check_neighbors(self, position: typing.Tuple[int, int, int]):
        self.helper.run_on_main(
            lambda context: context.get_world()
            .get_dimension(self.dimension_id)
            .check_neighbors(position)
        )

    async def hide_block(self, position, immediate=True):
        self.helper.run_on_main(
            lambda context: context.get_world()
            .get_dimension(self.dimension_id)
            .hide_block(position, immediate=immediate)
        )

    async def get_world_generation_config_for_layer(self, layer_name: str):
        # todo: can we cache it?
        return await self.helper.run_on_main_async(
            lambda context: context.get_world()
            .get_dimension(self.dimension_id)
            .get_world_generation_config_for_layer(layer_name)
        )

    async def set_world_generation_config_for_layer(self, layer_name, layer_config):
        # todo: can we cache it?
        await self.helper.run_on_main_async(
            lambda context: context.get_world()
            .get_dimension(self.dimension_id)
            .set_world_generation_config_for_layer(layer_name, layer_config)
        )

    async def get_world_generation_config_entry(self, name: str, default=None):
        # todo: can we cache it?
        return await self.helper.run_on_main_async(
            lambda context: context.get_world()
            .get_dimension(self.dimension_id)
            .get_world_generation_config_entry(name, default=default)
        )

    async def set_world_generation_config_entry(self, name: str, value):
        await self.helper.run_on_main_async(
            lambda context: context.get_world()
            .get_dimension(self.dimension_id)
            .set_world_generation_config_entry(name, value)
        )

    async def unload_chunk(self, chunk: IChunk):
        await self.helper.run_on_main_async(
            lambda context: context.get_world()
            .get_dimension(self.dimension_id)
            .unload_chunk(chunk)
        )


class OffProcessChunk(mcpython.engine.world.AbstractInterface.IChunk):
    def __init__(
        self, helper: OffProcessWorldHelper, position, dimension: OffProcessDimension
    ):
        super().__init__()
        self.helper = helper
        self.position = position
        self.dimension = dimension
        self.block_cache = {}

    async def setup(self):
        pass

    async def is_loaded(self) -> bool:
        # todo: cache and get informed by chunk
        return await self.helper.run_on_main_async(
            lambda context: context.get_world()
            .get_dimension(self.dimension.get_dimension_id())
            .get_chunk(*self.position)
            .is_loaded()
        )

    async def is_generated(self) -> bool:
        # todo: cache and get informed by chunk
        return await self.helper.run_on_main_async(
            lambda context: context.get_world()
            .get_dimension(self.dimension.get_dimension_id())
            .get_chunk(*self.position)
            .is_generated()
        )

    async def is_visible(self) -> bool:
        # todo: cache and get informed by chunk
        return await self.helper.run_on_main_async(
            lambda context: context.get_world()
            .get_dimension(self.dimension.get_dimension_id())
            .get_chunk(*self.position)
            .is_visible()
        )

    def get_dimension(self) -> "OffProcessDimension":
        return self.dimension

    def get_position(self) -> typing.Tuple[int, int]:
        return self.position

    async def get_maximum_y_coordinate_from_generation(self, x: int, z: int) -> int:
        return await self.helper.run_on_main_async(
            lambda context: context.get_world()
            .get_dimension(self.dimension.get_dimension_id())
            .get_chunk(*self.position)
            .get_maximum_y_coordinate_from_generation(x, z)
        )

    async def exposed_faces(
        self, position: typing.Tuple[int, int, int]
    ) -> typing.Dict[mcpython.util.enums.EnumSide, bool]:
        return await self.helper.run_on_main_async(
            lambda context: context.get_world()
            .get_dimension(self.dimension.get_dimension_id())
            .get_chunk(*self.position)
            .exposed_faces(position)
        )

    async def is_position_blocked(
        self, position: typing.Tuple[float, float, float]
    ) -> bool:
        return await self.helper.run_on_main_async(
            lambda context: context.get_world()
            .get_dimension(self.dimension.get_dimension_id())
            .get_chunk(*self.position)
            .is_position_blocked()
        )

    async def add_block(self, *args, **kwargs):
        # todo: cache & get informed by other side
        return await self.helper.run_on_main_async(
            lambda context: context.get_world()
            .get_dimension(self.dimension.get_dimension_id())
            .get_chunk(*self.position)
            .add_block(*args, **kwargs)
        )

    def on_block_updated(
        self, position: typing.Tuple[float, float, float], itself=True
    ):
        self.helper.run_on_main(
            lambda context: context.get_world()
            .get_dimension(self.dimension.get_dimension_id())
            .get_chunk(*self.position)
            .on_block_updated(position)
        )

    async def remove_block(self, *args, **kwargs):
        # todo: cache & get informed by other side
        return await self.helper.run_on_main_async(
            lambda context: context.get_world()
            .get_dimension(self.dimension.get_dimension_id())
            .get_chunk(*self.position)
            .remove_block(*args, **kwargs)
        )

    def check_neighbors(self, position: typing.Tuple[int, int, int]):
        self.helper.run_on_main(
            lambda context: context.get_world()
            .get_dimension(self.dimension.get_dimension_id())
            .get_chunk(*self.position)
            .check_neighbors(position)
        )

    async def show_block(
        self,
        position: typing.Union[
            typing.Tuple[int, int, int],
            typing.Any,
        ],
        immediate: bool = True,
    ):
        await self.helper.run_on_main_async(
            lambda context: context.get_world()
            .get_dimension(self.dimension.get_dimension_id())
            .get_chunk(*self.position)
            .show_block(position, immediate=immediate)
        )

    async def hide_block(
        self,
        position: typing.Union[
            typing.Tuple[int, int, int],
            typing.Any,
        ],
        immediate=True,
    ):
        await self.helper.run_on_main_async(
            lambda context: context.get_world()
            .get_dimension(self.dimension.get_dimension_id())
            .get_chunk(*self.position)
            .hide_block(position, immediate=immediate)
        )

    async def show(self, force=False):
        await self.helper.run_on_main_async(
            lambda context: context.get_world()
            .get_dimension(self.dimension.get_dimension_id())
            .get_chunk(*self.position)
            .show(force=force)
        )

    async def hide(self, force=False):
        await self.helper.run_on_main_async(
            lambda context: context.get_world()
            .get_dimension(self.dimension.get_dimension_id())
            .get_chunk(*self.position)
            .hide(force=force)
        )

    async def update_visible_block(
        self, position: typing.Tuple[int, int, int], hide=True
    ):
        await self.helper.run_on_main_async(
            lambda context: context.get_world()
            .get_dimension(self.dimension.get_dimension_id())
            .get_chunk(*self.position)
            .update_visible_block(position, hide=hide)
        )

    async def exposed(self, position: typing.Tuple[int, int, int]):
        return await self.helper.run_on_main_async(
            lambda context: context.get_world()
            .get_dimension(self.dimension.get_dimension_id())
            .get_chunk(*self.position)
            .exposed(position)
        )

    async def update_visible(self, hide=True, immediate=False):
        await self.helper.run_on_main_async(
            lambda context: context.get_world()
            .get_dimension(self.dimension.get_dimension_id())
            .get_chunk(*self.position)
            .update_visible(hide=hide, immediate=immediate)
        )

    async def hide_all(self, immediate=True):
        await self.helper.run_on_main_async(
            lambda context: context.get_world()
            .get_dimension(self.dimension.get_dimension_id())
            .get_chunk(*self.position)
            .hide_all(immediate=immediate)
        )

    async def get_block(
        self, position: typing.Tuple[int, int, int], none_if_str=False
    ) -> typing.Union[typing.Any, str, None]:
        # todo: cache
        return await self.helper.run_on_main_async(
            lambda context: context.get_world()
            .get_dimension(self.dimension.get_dimension_id())
            .get_chunk(*self.position)
            .get_block(position, none_if_str=none_if_str)
        )

    def as_shareable(self) -> "OffProcessChunk":
        return self

    def mark_dirty(self):
        self.helper.run_on_main(
            lambda context: context.get_world()
            .get_dimension(self.dimension.get_dimension_id())
            .get_chunk(*self.position)
            .mark_dirty()
        )

    async def get_entities(self):
        # todo: cache & get informed by other side
        return await self.helper.run_on_main_async(
            lambda context: context.get_world()
            .get_dimension(self.dimension.get_dimension_id())
            .get_chunk(*self.position)
            .get_entities()
        )

    async def set_value(self, key: str, data):
        # todo: cache & get informed by other side
        return await self.helper.run_on_main_async(
            lambda context: context.get_world()
            .get_dimension(self.dimension.get_dimension_id())
            .get_chunk(*self.position)
            .set_value(key, data)
        )

    async def get_value(self, key: str):
        # todo: cache & get informed by other side
        return await self.helper.run_on_main_async(
            lambda context: context.get_world()
            .get_dimension(self.dimension.get_dimension_id())
            .get_chunk(*self.position)
            .get_value(key)
        )
