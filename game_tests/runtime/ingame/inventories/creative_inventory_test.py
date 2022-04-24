from game_tests.runtime.api import Stages
from mcpython.common.entity.PlayerEntity import PlayerEntity
from mcpython.engine.world.AbstractInterface import IDimension
from mcpython import shared


@Stages.bind_for_stage("loading_binds")
async def prepare_loading_bindings(mod_name: str):
    from mcpython import shared

    @shared.mod_loader(mod_name, "stage:item_groups:load")
    async def load_creative_tab():
        from mcpython.client.gui.InventoryCreativeTab import CreativeItemTab, CT_MANAGER
        from mcpython.common.container.ResourceStack import ItemStack

        tab = CreativeItemTab("Test", ItemStack("minecraft:barrier"))
        CT_MANAGER.add_tab(tab)


@Stages.bind_for_stage("ingame_setup")
async def setup_ingame(dimension: IDimension, player: PlayerEntity):
    player.set_gamemode(1)


@Stages.bind_for_stage("ingame_test")
async def run(dimension: IDimension, player: PlayerEntity):
    from mcpython.client.gui.InventoryCreativeTab import CT_MANAGER
    CT_MANAGER.activate()

