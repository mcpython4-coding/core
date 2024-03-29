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
import os
import shutil
import time
import typing

import mcpython.common.data.DataPacks
import mcpython.common.mod.ModMcpython
import mcpython.common.state.ConfigBackgroundPart
import mcpython.common.state.WorldGenerationProgressState
import mcpython.common.state.WorldLoadingProgressState
import mcpython.common.world.SaveFile
import mcpython.engine.rendering.RenderingGroups
import mcpython.engine.ResourceLoader
import mcpython.util.math
from mcpython import shared
from mcpython.engine.network.util import ReadBuffer

from . import AbstractState
from .ui import UIPartButton, UIPartScrollBar

if shared.IS_CLIENT:
    import mcpython.util.opengl
    import mcpython.util.texture
    import PIL.Image
    import pyglet
    from pyglet.window import key, mouse

    MISSING_TEXTURE = mcpython.util.texture.to_pyglet_image(
        asyncio.run(
            mcpython.engine.ResourceLoader.read_image("assets/missing_texture.png")
        )
        .resize((50, 50), PIL.Image.NEAREST)
    )
    WORLD_SELECTION = asyncio.run(
        mcpython.engine.ResourceLoader.read_image("minecraft:gui/world_selection")
    )
    WORLD_SELECTION_SELECT = mcpython.util.texture.to_pyglet_image(
        WORLD_SELECTION.crop((0, 0, 32, 32))
    )


class WorldList(AbstractState.AbstractState):
    NAME = "minecraft:world_selection"

    def __init__(self):
        super().__init__()
        # the data representing the world list; first goes in list from above
        self.world_data = []
        self.selected_world = None

        if shared.IS_CLIENT:
            self.selection_sprite = pyglet.sprite.Sprite(WORLD_SELECTION_SELECT)

            self.scissor_group = mcpython.engine.rendering.RenderingGroups.ScissorGroup(
                0, 0, 10, 10
            )

    def create_state_renderer(self) -> typing.Any:
        from mcpython.client.state.WorldListRenderer import WorldListRenderer

        return WorldListRenderer()

    def bind_to_eventbus(self):
        self.eventbus.subscribe("user:mouse:press", self.on_mouse_press)
        self.eventbus.subscribe("user:keyboard:press", self.on_key_press)
        self.eventbus.subscribe("user:window:resize", self.on_resize)
        self.eventbus.subscribe("user:mouse:scroll", self.on_mouse_scroll)

    def on_resize(self, wx, wy):
        self.parts[-1].set_size_respective((wx - 80, 105), wy - 195)
        self.recalculate_sprite_position()
        self.scissor_group.area = (45, 100, wx - 90, wy - 160)

    def create_state_parts(self) -> list:
        if not shared.IS_CLIENT:
            return []

        wx, wy = shared.window.get_size()
        return [
            mcpython.common.state.ConfigBackgroundPart.ConfigBackground(),
            UIPartButton.UIPartButton(
                (150, 20),
                "generate new",
                (105, 60),
                anchor_button="MM",
                anchor_window="MD",
                on_press=self.on_new_world_press,
            ),
            UIPartButton.UIPartButton(
                (150, 20),
                "play!",
                (-105, 60),
                anchor_button="MM",
                anchor_window="MD",
                on_press=self.on_world_load_press,
            ),
            UIPartButton.UIPartButton(
                (150, 20),
                "back",
                (-105, 20),
                anchor_window="MD",
                anchor_button="MD",
                on_press=self.on_back_press,
            ),
            UIPartButton.UIPartButton(
                (150, 20),
                "delete",
                (105, 20),
                anchor_window="MD",
                anchor_button="MD",
                on_press=self.on_delete_press,
            ),
            UIPartScrollBar.UIScrollBar(
                (wx - 80, 105), wy - 195, on_scroll=self.on_scroll
            ),
        ]

    async def on_mouse_press(self, x, y, button, modifiers):
        if not button == mouse.LEFT:
            return

        wx, _ = shared.window.get_size()
        wx -= 120
        for i, (_, icon, _, _) in enumerate(self.world_data):
            px, py = icon.position
            if 0 <= x - px <= wx - 130 and 0 <= y - py <= 50:
                if 0 <= x - px <= 50:
                    await self.enter_world(i)
                else:
                    if self.selected_world != i:
                        self.selected_world = i
                    else:
                        await self.enter_world(i)
                return

        self.selected_world = None

    async def on_scroll(self, x, y, dx, dy, button, mod, status):
        self.recalculate_sprite_position()

    async def on_mouse_scroll(self, x, y, dx, dy):
        self.parts[-1].move(dy * 4)

    def recalculate_sprite_position(self):
        wx, wy = shared.window.get_size()
        status = (
            (1 - self.parts[-1].get_status())
            * (len(self.world_data) - (wy - 140) // 60)
            * 60
            if (wy - 140) / 60 < len(self.world_data)
            else 0
        )
        ay = wy - 130 + status
        for i, (_, sprite, labels, _) in enumerate(self.world_data):
            sprite.x = 50
            sprite.y = ay
            dy = ay
            for label in labels:
                label.x = 120
                label.y = dy + 36
                dy -= 15
            ay -= 60

        if (wy - 140) / 60 > len(self.world_data):
            self.parts[-1].active = False

    async def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            await self.on_back_press(0, 0)
        elif symbol == key.R:  # "R" will reload the world list
            await self.reload_world_icons()
        elif (
            symbol == key.ENTER and self.selected_world is not None
        ):  # selecting world & pressing enter will launch it
            await self.enter_world(self.selected_world)
        elif (
            symbol == key.UP
            and self.selected_world is not None
            and self.selected_world > 0
        ):
            self.selected_world -= 1
            self.parts[-1].move(60)
        elif (
            symbol == key.DOWN
            and self.selected_world is not None
            and self.selected_world < len(self.world_data) - 1
        ):
            self.selected_world += 1
            self.parts[-1].move(-60)

    async def activate(self):
        await super().activate()

        await self.reload_world_icons()
        self.parts[-1].set_status(1)

    async def reload_world_icons(self):
        if not os.path.exists(mcpython.common.world.SaveFile.SAVE_DIRECTORY):
            os.makedirs(mcpython.common.world.SaveFile.SAVE_DIRECTORY)
        wx, wy = shared.window.get_size()
        self.world_data.clear()

        for directory in os.listdir(mcpython.common.world.SaveFile.SAVE_DIRECTORY):
            path = os.path.join(
                mcpython.common.world.SaveFile.SAVE_DIRECTORY, directory
            ).replace("\\", "/")
            if os.path.isdir(path) and os.path.isfile(path + "/level.dat"):
                if os.path.isfile(path + "/icon.png"):
                    icon = pyglet.image.load(path + "/icon.png")
                else:
                    icon = MISSING_TEXTURE

                sprite = pyglet.sprite.Sprite(icon)
                delta = os.path.getmtime(path + "/level.dat")
                date = time.localtime(delta)
                modification_time = time.strftime("%d/%m/%Y", date)
                edit = "last edited: " + modification_time

                with open(path + "/level.dat", mode="rb") as f:
                    data = f.read()

                read_buffer = ReadBuffer(data)
                read_buffer.read_ulong()  # save version
                version_id = read_buffer.read_ulong()
                read_buffer.read_string()  # player name
                mods = await read_buffer.read_dict(
                    read_buffer.read_string, read_buffer.read_any
                )

                labels = [
                    pyglet.text.Label(directory),
                    pyglet.text.Label(
                        "last played in version '{}' {}".format(version_id, edit)
                    ),
                    pyglet.text.Label(
                        "last loaded with {} mod{}".format(
                            len(mods), "" if len(mods) <= 1 else "s"
                        )
                    ),
                ]
                self.world_data.append((delta, sprite, labels, path))

        self.world_data.sort(key=lambda d: -d[0])
        self.recalculate_sprite_position()
        self.parts[-1].active = (wy - 140) / 60 < len(self.world_data)

    async def on_back_press(self, *_):
        await shared.state_handler.change_state("minecraft:start_menu")

    async def on_new_world_press(self, *_):
        await shared.state_handler.change_state("minecraft:world_generation_config")

    async def on_delete_press(self, *_):
        if self.selected_world is None:
            return

        shutil.rmtree(self.world_data[self.selected_world][3])
        await self.reload_world_icons()

    async def on_world_load_press(self, *_):
        if self.selected_world is None:
            return

        await self.enter_world(self.selected_world)

    async def enter_world(self, number: int):
        await shared.state_handler.states["minecraft:world_loading"].load_world_from(
            self.world_data[number][2][0].text
        )


world_selection = None


async def create():
    global world_selection
    world_selection = WorldList()


mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe("stage:states", create())
