import typing


class StageManager:
    def __init__(self):
        self.bound = {}


MANAGER = StageManager()


def bind_for_stage(stage_name: str) -> typing.Callable[[typing.Callable], typing.Callable]:
    def annotate(func):
        MANAGER.bound.setdefault(stage_name, []).append(func)
        return func
    
    return annotate


async def init_tests():
    from mcpython import shared
    from mcpython.common.mod import ModLoader
    
    for i, e in enumerate(MANAGER.bound.setdefault("loading_binds", [])):
        mod_name = "test_mod_"+str(i+1)
        shared.mod_loader.create_mod(mod_name)

    for i, e in enumerate(MANAGER.bound.setdefault("loading_binds", [])):
        mod_name = "test_mod_" + str(i + 1)
        await e(mod_name)
