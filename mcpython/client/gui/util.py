import math
import typing

from pyglet.window import key
from pyglet.window import mouse

import mcpython.engine
from mcpython import shared
from mcpython.util import texture as texture_util
import mcpython.engine.ResourceLoader
import mcpython.engine.event.EventBus


TAB_TEXTURE = (
    None
    if shared.IS_TEST_ENV
    else mcpython.engine.ResourceLoader.read_pyglet_image(
        "minecraft:gui/container/creative_inventory/tabs"
    )
)


class CreativeTabScrollbar:
    """
    Creative tab scrollbar
    Feel free to re-use for other stuff

    todo: use batches
    """

    SCROLLBAR_SIZE = 24, 30

    NON_SELECTED_SCROLLBAR = None
    SELECTED_SCROLLBAR = None

    # todo: bind to reload handler
    @classmethod
    def reload(cls):
        cls.NON_SELECTED_SCROLLBAR = texture_util.resize_image_pyglet(
            TAB_TEXTURE.get_region(232, 241, 12, 15), cls.SCROLLBAR_SIZE
        )
        cls.SELECTED_SCROLLBAR = texture_util.resize_image_pyglet(
            TAB_TEXTURE.get_region(244, 241, 12, 15), cls.SCROLLBAR_SIZE
        )

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

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if buttons & mouse.LEFT:
            cx, cy = self.get_scrollbar_position()
            if self.is_hovered:
                # todo: something better here!
                self.on_mouse_scroll(0, 0, 0, -dy)

        self.on_mouse_move(x, y, dx, dy)

    def on_mouse_move(self, x, y, dx, dy):
        cx, cy = self.get_scrollbar_position()
        if (
            0 <= x - cx <= self.SCROLLBAR_SIZE[0]
            and 0 <= y - cy <= self.SCROLLBAR_SIZE[1]
        ):
            self.is_hovered = True
        else:
            self.is_hovered = False

    def on_mouse_scroll(self, x, y, sx, sy):
        self.currently_scrolling = max(
            1, min(self.currently_scrolling + math.copysign(1, sy), self.scroll_until)
        )
        self.callback(self.currently_scrolling)

    def on_key_press(self, symbol, modifiers):
        if shared.state_handler.global_key_bind_toggle:
            return

        if symbol == key.UP:
            self.on_mouse_scroll(0, 0, 0, -1)

        elif symbol == key.DOWN:
            self.on_mouse_scroll(0, 0, 0, 1)

        elif symbol == key.PAGEUP:
            for _ in range(5):
                self.on_mouse_scroll(0, 0, 0, -1)

        elif symbol == key.PAGEDOWN:
            for _ in range(5):
                self.on_mouse_scroll(0, 0, 0, 1)

    def get_scrollbar_position(self):
        x, y = self.position
        sx, sy = self.SCROLLBAR_SIZE
        y += self.height - sy
        if self.scroll_until != 1:
            y -= (self.height - sy) * (
                (self.currently_scrolling - 1) / (self.scroll_until - 1)
            )
        # print(self.position, self.SCROLLBAR_SIZE, self.height, self.currently_scrolling, self.scroll_until, x, y)
        return x, y

    def draw_at(self, lower_left: typing.Tuple[int, int], height: int):
        self.position = lower_left
        self.height = height

        (
            self.NON_SELECTED_SCROLLBAR if self.is_hovered else self.SELECTED_SCROLLBAR
        ).blit(*self.get_scrollbar_position())

        # This is here for debugging where the bar is drawn
        # draw_line_rectangle(lower_left, (self.SCROLLBAR_SIZE[0], height), (1, 0, 0))

    def activate(self):
        self.underlying_event_bus.activate()

    def deactivate(self):
        self.underlying_event_bus.deactivate()
        self.is_hovered = False

    def set_max_value(self, value: int):
        assert value >= 1, "value must be positive"

        self.scroll_until = value
        self.currently_scrolling = min(self.currently_scrolling, value)


if not shared.IS_TEST_ENV:
    CreativeTabScrollbar.reload()

