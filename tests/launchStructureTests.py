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
import importlib
import os
import sys
import typing
from abc import ABC

import pyglet.clock

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


class AbstractStructureTestAction(ABC):
    TYPE_NAME: str = None

    def setup(self, test: "StructureTest"):
        pass

    def get_comparable_identifier(self):
        raise NotImplementedError


class AbstractStructureTestValidator(ABC):
    TYPE_NAME: str = None

    def validate(self, test: "StructureTest") -> bool:
        raise NotImplementedError


class EndOfTestAction(AbstractStructureTestValidator):
    def validate(self, test: "StructureTest") -> bool:

        for stage in test.stages:
            stage.clean()

        manager.next_test()

        return True


class StructureTest:
    class StructureTestStage:
        def __init__(self, test: "StructureTest"):
            self.test = test
            self.actions = []
            self.validators = []
            self.delay_after = 0

        def clean(self):
            pass

        def run_actions(self):
            pass

        def validate(self):
            pass

        def add_action(self, action: AbstractStructureTestAction):
            pass

        def add_validator(self, validator: AbstractStructureTestValidator):
            pass

    def __init__(self):
        self.env_variables = {}
        self.stages: typing.List["StructureTest.StructureTestStage"] = []
        self.current_stage = -1
        self.requirements = []

    def set_env_variable(self, variable: str, value):
        self.env_variables[variable] = value
        return value

    def get_env_variable(self, variable: str):
        return self.env_variables[variable] if variable in self.env_variables else None

    def decode_from_data(self, data: dict):
        self.requirements = data.setdefault("requirements", [])

    def begin(self):
        self.current_stage = -1

        for req in self.requirements:
            manager.enforce_requirement(self, req)

        setup = StructureTest.StructureTestStage(self)
        self.stages.append(setup)

        end = StructureTest.StructureTestStage(self)
        self.stages.append(end)

        end.add_validator(EndOfTestAction())

        self.next_stage()

    def next_stage(self, dt=None):
        self.current_stage += 1
        if self.current_stage >= len(self.stages) + 1:
            return

        stage = self.stages[self.current_stage]
        stage.run_actions()
        stage.validate()

        pyglet.clock.schedule_once(self.next_stage, stage.delay_after)


class StructureTestManager:
    def __init__(self):
        self.tests: typing.List[StructureTest] = []
        self.current_test = -1

        self.requirements: typing.Dict[str, typing.Callable[[StructureTest], None]] = {}
        self.actions: typing.Dict[str, typing.Type[AbstractStructureTestAction]] = {}
        self.validators: typing.Dict[
            str, typing.Type[AbstractStructureTestValidator]
        ] = {}

    def register_requirement_loader(
        self, name: str, loader: typing.Callable[[StructureTest], None]
    ):
        self.requirements[name] = loader

    def register_test_action(self, part: typing.Type[AbstractStructureTestAction]):
        self.actions[part.TYPE_NAME] = part

    def register_test_validator(
        self, validator: typing.Type[AbstractStructureTestValidator]
    ):
        self.validators[validator.TYPE_NAME] = validator

    def register_test(self, test: StructureTest):
        self.tests.append(test)

    def start_tests(self):
        self.current_test = -1
        self.next_test()

    def next_test(self):
        self.current_test += 1
        if self.current_test >= len(self.tests) - 1:
            return

        self.tests[self.current_test].begin()

    def look_for_empty_chunk(self) -> typing.Tuple[int, int]:
        return 0, 0

    def get_free_player(self) -> str:
        return "test:player"

    def enforce_requirement(self, test: StructureTest, req: str):
        self.requirements[req](test)


class PlayerController:
    def __init__(self, test: StructureTest):
        self.test = test

    def prepareInventory(self):
        pass


manager = StructureTestManager()
manager.register_requirement_loader(
    "chunk",
    lambda test: test.set_env_variable(
        "operating_chunk", manager.look_for_empty_chunk()
    ),
)
manager.register_requirement_loader(
    "chunk:blocks",
    lambda test: importlib.import_module("mcpython.common.block.BlockManager").load(),
)
manager.register_requirement_loader(
    "player",
    lambda test: test.set_env_variable("operating_player", manager.get_free_player()),
)
manager.register_requirement_loader(
    "player:controller",
    lambda test: test.set_env_variable("player_controller", PlayerController(test)),
)
manager.register_requirement_loader(
    "player:inventory",
    lambda test: test.get_env_variable("player_controller").prepareInventory(),
)


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

    asyncio.get_event_loop().run_until_complete(
        shared.state_handler.change_state("minecraft:world_generation")
    )

    from mcpython.engine.event.EventHandler import PUBLIC_EVENT_BUS

    @PUBLIC_EVENT_BUS.subscribe("on_game_enter")
    def on_game_enter():
        player = shared.world.get_active_player()
        player.position = (0, 0, 0)
        player.set_gamemode(3)

        manager.start_tests()


@shared.mod_loader("structure_test_system", "stage:mod:init")
async def init():
    from mcpython.engine.event.EventHandler import PUBLIC_EVENT_BUS

    PUBLIC_EVENT_BUS.subscribe("stage_handler:loading2main_menu", intercept_loading)


if __name__ == "__main__":
    launch.full_launch()
