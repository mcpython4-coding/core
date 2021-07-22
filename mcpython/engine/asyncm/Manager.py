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
import multiprocessing
import sys
import typing

import mcpython.engine.asyncm.serializer


class SpawnedProcessInfo:
    def __init__(self, name: str):
        self.name = name

        self.main2off = multiprocessing.Queue()
        self.main2off_data = multiprocessing.Queue()
        self.off2main = multiprocessing.Queue()
        self.off2main_data = multiprocessing.Queue()

        self.sided_task_manager: typing.Optional[TaskManager] = None

        self.call_regular = None

    def spawn_main_task_manager(self):
        return TaskManager(
            self, self.off2main, self.off2main_data, self.main2off, self.main2off_data
        )

    def spawn_off_task_manager(self):
        return TaskManager(
            self, self.main2off, self.main2off_data, self.off2main, self.off2main_data
        )

    def off_work(self):
        asyncio.get_event_loop().create_task(self.off_work_async())
        asyncio.get_event_loop().run_forever()

    async def off_work_async(self):
        manager = self.spawn_off_task_manager()
        manager.router = lambda p: manager
        self.sided_task_manager = manager

        while True:
            await manager.fetch()

            if self.call_regular is not None:
                await self.call_regular(self)

            await asyncio.sleep(0)


class TaskManager:
    def __init__(
        self,
        info: "SpawnedProcessInfo",
        queue_in: multiprocessing.Queue,
        data_queue_in: multiprocessing.Queue,
        queue_out: multiprocessing.Queue,
        data_queue_out: multiprocessing.Queue,
    ):
        self.info = info
        self.queue_in = queue_in
        self.data_queue_in = data_queue_in
        self.queue_out = queue_out
        self.data_queue_out = data_queue_out

        self.next_id = 0
        self.waiting_awaits: typing.Dict[int, asyncio.Event] = {}
        self.result_cache: typing.Dict[int, typing.Any] = {}

        self.process: typing.Optional[multiprocessing.Process] = None

        self.router: typing.Optional[typing.Callable[[str], "TaskManager"]] = None
        self.is_on_main = False
        self.main_obj: typing.Optional["AsyncProcessManager"] = None

    async def execute_task(self, task_id, source, target, function, args, kwargs):
        # print(f"invoking {function} on {self.info.name}, task id {task_id}")

        try:
            result = await function(self.info, *args, **kwargs)
        except:
            # print("error @", self, function, args, kwargs)
            raise

        # print(f"invoked {function} on {self.info.name}, task id {task_id} - success; return to {source} - {result}")

        if task_id != -1:
            self.router(source).data_queue_out.put((source, target, result, task_id))

    async def fetch(self):
        # if not self.is_on_main: print(self.info.name, self.data_queue_out.qsize(), self.queue_in.qsize())

        while not self.queue_in.empty():
            target, source, task, task_id = d = self.queue_in.get_nowait()

            # print(f"@{self} fetched from {source} -> {target}: {task}@{task_id}")

            if target != self.info.name if not self.is_on_main else target != "main":
                if self.router is None:
                    raise RuntimeError(
                        f"{self} has no router set and so cannot re-route task {task} to process '{target}'"
                    )

                # print(f"routing from {self.info.name} to {target}")
                self.router(target).queue_out.put(d)
                continue

            (
                function,
                args,
                kwargs,
                meta,
            ) = mcpython.engine.asyncm.serializer.deserialize_task(task)

            asyncio.ensure_future(
                self.execute_task(task_id, source, target, function, args, kwargs)
            )

        while not self.data_queue_in.empty():
            target, source, result, task_id = d = self.data_queue_in.get()

            # print(f"got data from {source} to {target}: {result} (for task {task_id}) on {self}")

            if target != self.info.name:
                # print(f"routing data from {self.info.name} to {target}")

                manager = self.router(target)
                manager.data_queue_in.put(d)

                continue

            if self.is_on_main:
                # print(f"routing data internally in {target}")

                self.data_queue_out.put(d)

                continue

            # todo: clean up this somehow... (maybe weakref?)
            self.result_cache[task_id] = result

            if task_id in self.waiting_awaits:
                self.waiting_awaits.pop(task_id).set()
            # else:
            # print("warn: result was not waited for!", self.waiting_awaits)

    async def invokeOnMain(self, function, *args, ignore_result=False, **kwargs):
        if not ignore_result:
            internal_id = self.next_id
            self.next_id += 1
        else:
            internal_id = -1
        self.queue_out.put(
            (
                "main",
                self.info.name,
                mcpython.engine.asyncm.serializer.serialize_task(
                    function, args, kwargs
                ),
                internal_id,
            )
        )

        event = asyncio.Event()

        self.waiting_awaits[internal_id] = event

        await event.wait()

        return self.result_cache.pop(internal_id, None)

    def invokeOnMainNoWait(self, function, *args, **kwargs):
        self.queue_out.put(
            (
                "main",
                self.info.name,
                mcpython.engine.asyncm.serializer.serialize_task(
                    function, args, kwargs
                ),
                -1,
            )
        )

    async def invokeOn(
        self, process: str, function, *args, ignore_result=False, **kwargs
    ):
        if not ignore_result:
            internal_id = self.next_id
            self.next_id += 1
        else:
            internal_id = -1
        self.queue_out.put(
            (
                process,
                self.info.name,
                mcpython.engine.asyncm.serializer.serialize_task(
                    function, args, kwargs
                ),
                internal_id,
            )
        )

        event = asyncio.Event()

        self.waiting_awaits[internal_id] = event

        await event.wait()

        return self.result_cache.pop(internal_id, None)

    def invokeOnNoWait(self, process: str, function, *args, **kwargs):
        self.queue_out.put(
            (
                process,
                self.info.name,
                mcpython.engine.asyncm.serializer.serialize_task(
                    function, args, kwargs
                ),
                -1,
            )
        )

    def __repr__(self):
        return f"TaskManager(of='{self.info.name}',router={self.router},on_main={self.is_on_main})"


class AsyncProcessManager:
    """
    This is the class managing everything
    Call main() in order to get things going
    [The inter-process-com is not active before]
    Tasks may run before calling main()
    """

    def __init__(self):
        self.spawned_processes: typing.List[SpawnedProcessInfo] = []
        self.lookup_processes: typing.Dict[str, SpawnedProcessInfo] = {}
        self.callbacks = []

        self.running = False

    def add_regular_async_callback(
        self, callback: typing.Callable[[SpawnedProcessInfo], typing.Awaitable]
    ):
        self.callbacks.append(callback)

    def run_regular_on_process(self, process: str, task, *args, **kwargs):
        self.lookup_processes[process].sided_task_manager.invokeOnNoWait(
            process, task, *args, **kwargs
        )

    def add_process(self, name: str) -> SpawnedProcessInfo:
        if name == "main":
            raise ValueError("<name> cannot be 'main'")

        info = SpawnedProcessInfo(name)
        self.spawned_processes.append(info)
        self.lookup_processes[name] = info

        process = multiprocessing.Process(target=info.off_work)
        process.start()

        info.sided_task_manager = info.spawn_main_task_manager()
        info.sided_task_manager.process = process
        info.sided_task_manager.router = lambda p: self.lookup_processes[
            p
        ].sided_task_manager
        info.sided_task_manager.is_on_main = True
        info.sided_task_manager.main_obj = self

        return info

    def main(self):
        asyncio.get_event_loop().create_task(self.main_async())
        asyncio.get_event_loop().run_forever()

    async def main_async(self):
        self.running = True

        while self.running:
            for p in self.spawned_processes:
                await p.sided_task_manager.fetch()

            for c in self.callbacks:
                await c(self)

            await asyncio.sleep(0)

    def stop(self):
        self.running = False
        for p in self.spawned_processes:
            p.sided_task_manager.process.terminate()
        asyncio.get_event_loop().stop()
