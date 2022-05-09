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
from game_tests.runtime.api import Stages
from mcpython import shared
from mcpython.engine.rendering import key
from mcpython.engine.world.AbstractInterface import IDimension


@Stages.bind_for_stage("loading_binds")
async def prepare_loading_bindings(mod_name: str):
    from mcpython import shared

    @shared.mod_loader(mod_name, "stage:item_groups:load")
    async def load_creative_tab():
        from mcpython.client.gui.InventoryCreativeTab import CT_MANAGER, CreativeItemTab
        from mcpython.common.container.ResourceStack import ItemStack

        tab = CreativeItemTab("Test", ItemStack("minecraft:barrier"))
        CT_MANAGER.add_tab(tab)

    @Stages.bind_for_stage("ingame_setup", mod_name)
    async def setup_ingame(dimension: IDimension, player):
        player.set_gamemode(1)

    @Stages.bind_for_stage("ingame_test", mod_name)
    async def run(dimension: IDimension, player):
        from mcpython.client.gui.InventoryCreativeTab import CT_MANAGER

        # Simulate an inventory open action
        await shared.event_handler.call_async("user:keyboard:press", key.E, 0)

        Stages.Asserts.equal(CT_MANAGER.pages[0][0].name, "Building Blocks")
        await CT_MANAGER.page_right.press_button()

        Stages.Asserts.equal(CT_MANAGER.current_page, 1)
        Stages.Asserts.equal(CT_MANAGER.pages[1][0].name, "Test")

        CT_MANAGER.switch_to_tab(CT_MANAGER.pages[1][0])
