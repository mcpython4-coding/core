import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from mcpython.LaunchWrapper import LaunchWrapper

launch = LaunchWrapper()
launch.set_client()


import mcpython.common.mod.ModLoader
import mcpython.common.mod.Mod
from mcpython import shared


test_mod = mcpython.common.mod.Mod.Mod("structure_test_system", (1, 0, 0)).add_dependency(mcpython.common.mod.Mod.ModDependency("minecraft"))


class StructureTest:
    def decode_from_data(self, data: dict):
        pass


def intercept_loading(handler):
    handler.cancel()

    world_config_state = shared.state_handler.states["minecraft:world_generation"]
    world_config_state.generate_world({
        "world_config_name": "minecraft:default_overworld",  # todo: empty world
        "world_size": (1, 1),
        "seed_source": "minecraft:open_simplex_noise",
        "seed": 0,
        "player_name": "test_system_player",
        "auto_gen_enabled": False,
        "world_barrier_enabled": False,
    })

    shared.state_handler.change_state("minecraft:world_generation")


@shared.mod_loader("structure_test_system", "stage:mod:init")
def init():
    from mcpython.engine.event.EventHandler import PUBLIC_EVENT_BUS

    PUBLIC_EVENT_BUS.subscribe("stage_handler:loading2main_menu", intercept_loading)


if __name__ == "__main__":
    launch.full_launch()

