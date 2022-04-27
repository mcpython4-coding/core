import sys
import typing

import asyncio
import pyglet
from mcpython import shared


GENERAL_BOUND = {"loading_binds"}


class StageManager:
    def __init__(self):
        self.bound = {}
        self.test_bound = {}
        self.pending_tests = set()
        self.halting = False

    async def run_stage_for_mod(self, mod_name: str = None):
        if mod_name is None:
            if not self.pending_tests:
                shared.window.close()
                pyglet.app.exit()
                sys.exit(0)

            mod_name = self.pending_tests.pop()

        await self._invoke_stage(mod_name, "ingame_setup")
        await self._invoke_stage(mod_name, "ingame_test")
        await self._invoke_stage(mod_name, "ingame_cleanup")

        if not self.halting:
            shared.tick_handler.schedule_once(self.run_stage_for_mod())

    async def _invoke_stage(self, mod_name: str, stage: str):
        player = await shared.world.get_active_player_async()
        dimension = shared.world.get_active_dimension()

        await asyncio.gather(*filter(lambda e: e is not None, [e(dimension, player) for e in self.test_bound.setdefault(mod_name, {}).setdefault(stage, [])]))

    def pause_test(self):
        self.halting = True

    def continue_test(self):
        if self.halting:
            self.halting = False

            shared.tick_handler.schedule_once(self.run_stage_for_mod())

    async def auto_run(self):
        shared.tick_handler.schedule_once(self.run_stage_for_mod())


MANAGER = StageManager()


def bind_for_stage(stage_name: str, mod_name: str = None) -> typing.Callable[[typing.Callable], typing.Callable]:
    def annotate(func):
        if stage_name in GENERAL_BOUND:
            MANAGER.bound.setdefault(stage_name, []).append(func)
        else:
            MANAGER.test_bound.setdefault(mod_name, {}).setdefault(stage_name, []).append(func)
        return func
    
    return annotate


async def init_tests():
    from mcpython import shared
    from mcpython.common.mod import ModLoader
    
    for i, e in enumerate(MANAGER.bound.setdefault("loading_binds", [])):
        mod_name = "test_mod_"+str(i+1)
        shared.mod_loader.create_mod(mod_name)
        MANAGER.pending_tests.add(mod_name)

    for i, e in enumerate(MANAGER.bound.setdefault("loading_binds", [])):
        mod_name = "test_mod_" + str(i + 1)
        await e(mod_name)


class Asserts:
    @classmethod
    def equal(cls, *args):
        x = args[0]
        for e in args[1:]:
            if x != e:
                raise AssertionError("Not Equal: %s != %s" % (x, e))

    @classmethod
    def not_equal(cls, a, b):
        if a == b:
            raise AssertionError("Equal, but should not: %s = %s" % (a, b))
