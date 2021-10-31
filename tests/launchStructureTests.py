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
import os
import sys
import typing

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from mcpython.LaunchWrapper import LaunchWrapper

launch = LaunchWrapper()
launch.set_client()


import mcpython.common.mod.Mod
import mcpython.common.mod.ModLoader
from mcpython import shared

test_mod = mcpython.common.mod.Mod.Mod(
    "structure_test_system", (1, 0, 0)
).add_dependency(mcpython.common.mod.Mod.ModDependency("minecraft"))


class AbstractStructureTestEnvironmentPart:
    TYPE_NAME: str = None

    def setup(self):
        pass

    def clean(self):
        pass

    def get_comparable_identifier(self):
        raise NotImplementedError


class StructureTest:
    def decode_from_data(self, data: dict):
        pass


class StructureTestManager:
    def register_requirement_loader(self, name: str, loader: typing.Callable):
        pass

    def register_test_env_part(self, part: typing.Type[AbstractStructureTestEnvironmentPart]):
        pass

    def register_test_validator(self, validator):
        pass

    def start_tests(self):
        pass


manager = StructureTestManager()


def intercept_loading(handler):
    handler.cancel()

    world_config_state = shared.state_handler.states["minecraft:world_generation"]
    world_config_state.generate_world(
        {
            "world_config_name": "minecraft:void_world_generator",
            "world_size": (1, 1),
            "seed_source": "minecraft:open_simplex_noise",
            "seed": 0,
            "player_name": "test_system_player",
            "auto_gen_enabled": False,
            "world_barrier_enabled": False,
        }
    )

    shared.state_handler.change_state("minecraft:world_generation")

    from mcpython.engine.event.EventHandler import PUBLIC_EVENT_BUS

    @PUBLIC_EVENT_BUS.subscribe("on_game_enter")
    def on_game_enter():
        player = shared.world.get_active_player()
        player.position = (0, 0, 0)
        player.set_gamemode(3)

        manager.start_tests()


@shared.mod_loader("structure_test_system", "stage:mod:init")
def init():
    from mcpython.engine.event.EventHandler import PUBLIC_EVENT_BUS

    PUBLIC_EVENT_BUS.subscribe("stage_handler:loading2main_menu", intercept_loading)


if __name__ == "__main__":
    launch.full_launch()
