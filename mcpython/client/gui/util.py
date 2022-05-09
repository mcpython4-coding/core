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
import math
import typing

import mcpython.engine
import mcpython.engine.event.EventBus
import mcpython.engine.ResourceLoader
import pyglet
from mcpython import shared
from mcpython.common.state.WorldListState import MISSING_TEXTURE
from mcpython.util import texture as texture_util
from pyglet.window import key, mouse

TAB_TEXTURE: typing.Optional[pyglet.image.AbstractImage] = None


def getTabTexture():
    return TAB_TEXTURE


async def reload():
    global TAB_TEXTURE
    TAB_TEXTURE = await mcpython.engine.ResourceLoader.read_pyglet_image(
        "minecraft:gui/container/creative_inventory/tabs"
    )


if not shared.IS_TEST_ENV:
    shared.tick_handler.schedule_once(reload())


class CreativeTabScrollbar:
    """
    Creative tab scrollbar
    Feel free to re-use for other stuff

    todo: use batches
    """

    SCROLLBAR_SIZE = 24, 30
    SCROLLBAR_SCALE = 2

    NON_SELECTED_SCROLLBAR = None
    SELECTED_SCROLLBAR = None

    # todo: bind to reload handler
    @classmethod
    async def reload(cls):
        cls.NON_SELECTED_SCROLLBAR = TAB_TEXTURE.get_region(232, 241, 12, 15)
        cls.SELECTED_SCROLLBAR = TAB_TEXTURE.get_region(244, 241, 12, 15)

    def __init__(self, callback: typing.Callable[[int], None], scroll_until: int = 1):
        self.callback = callback
        self.scroll_until = scroll_until
        self.currently_scrolling = 1
        self.underlying_event_bus: mcpython.engine.event.EventBus.EventBus = (
            shared.event_handler.create_bus(active=False)
        )

        self.underlying_event_bus.subscribe("user:mouse:drag", self.on_mouse_drag)
        self.underlying_event_bus.subscribe("user:mouse:motion", self.on_mouse_move)
        self.underlying_event_bus.subscribe("user:mouse:scroll", self.on_mouse_scroll)
        self.underlying_event_bus.subscribe("user:keyboard:press", self.on_key_press)

        self.position = (0, 0)
        self.height = 1

        self.is_hovered = False

        self.scrollbar_sprite = pyglet.sprite.Sprite(MISSING_TEXTURE)
        self.scrollbar_sprite.scale = self.SCROLLBAR_SCALE

    async def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if buttons & mouse.LEFT:
            if self.is_hovered:
                # todo: something better here!
                await self.on_mouse_scroll(0, 0, 0, dy)

        await self.on_mouse_move(x, y, dx, dy)

    async def on_mouse_move(self, x, y, dx, dy):
        cx, cy = self.get_scrollbar_position()
        if (
            0 <= x - cx <= self.SCROLLBAR_SIZE[0]
            and 0 <= y - cy <= self.SCROLLBAR_SIZE[1]
        ):
            self.is_hovered = True
        else:
            self.is_hovered = False

    async def on_mouse_scroll(self, x, y, sx, sy):
        self.currently_scrolling = max(
            1, min(self.currently_scrolling - math.copysign(1, sy), self.scroll_until)
        )
        self.callback(self.currently_scrolling)

    async def on_key_press(self, symbol, modifiers):
        # todo: while pressing, scroll further

        if shared.state_handler.global_key_bind_toggle:
            return

        if symbol == key.UP:
            await self.on_mouse_scroll(0, 0, 0, -1)

        elif symbol == key.DOWN:
            await self.on_mouse_scroll(0, 0, 0, 1)

        elif symbol == key.PAGEUP:
            for _ in range(5):
                await self.on_mouse_scroll(0, 0, 0, -1)

        elif symbol == key.PAGEDOWN:
            for _ in range(5):
                await self.on_mouse_scroll(0, 0, 0, 1)

    def get_scrollbar_position(self):
        x, y = self.position
        sx, sy = self.SCROLLBAR_SIZE
        y += self.height - sy
        if self.scroll_until != 1:
            y -= (self.height - sy) * (
                (self.currently_scrolling - 1) / (self.scroll_until - 1)
            )

        return x, y

    def draw_at(self, lower_left: typing.Tuple[int, int], height: int):
        self.position = lower_left
        self.height = height

        # todo: don't update each draw call
        self.scrollbar_sprite.image = (
            self.NON_SELECTED_SCROLLBAR if self.is_hovered else self.SELECTED_SCROLLBAR
        )
        self.scrollbar_sprite.position = self.get_scrollbar_position()
        self.scrollbar_sprite.draw()

    async def activate(self):
        self.underlying_event_bus.activate()
        self.is_hovered = False
        await self.on_mouse_move(*shared.window.mouse_position, 0, 0)

    async def deactivate(self):
        self.underlying_event_bus.deactivate()
        self.is_hovered = False

    def set_max_value(self, value: int):
        if value < 1:
            raise ValueError("value must be positive")

        self.scroll_until = value
        self.currently_scrolling = min(self.currently_scrolling, value)


if not shared.IS_TEST_ENV:
    shared.tick_handler.schedule_once(CreativeTabScrollbar.reload())
