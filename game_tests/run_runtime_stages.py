import json
import os
import importlib
import asyncio


local = os.path.dirname(__file__)
index_file = local+"/runtime/index.json"

with open(index_file, mode="r") as f:
    index = json.load(f)


import game_tests.runtime.api.Stages
import mcpython.engine.event.EventHandler
from mcpython import shared


async def cancel_start_menu(handle):
    # todo: generate empty world and run tests

    handle.cancel()


mcpython.engine.event.EventHandler.PUBLIC_EVENT_BUS.subscribe("stage_handler:loading2main_menu", cancel_start_menu)


for module in index:
    importlib.import_module("game_tests.runtime."+module)


asyncio.get_event_loop().run_until_complete(game_tests.runtime.api.Stages.init_tests())

import mcpython.LaunchWrapper
launch = mcpython.LaunchWrapper.LaunchWrapper()

if __name__ == "__main__":
    launch.full_launch()


