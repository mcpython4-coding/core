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
import mcpython.common.Language
import mcpython.engine.event.EventInfo
import mcpython.engine.ResourceLoader
import mcpython.util.opengl
import pyglet
from mcpython.util.annotation import onlyInClient
from mcpython.util.enums import ButtonMode
from pyglet.window import mouse

from . import UIPart

image = mcpython.engine.ResourceLoader.read_pyglet_image("gui/widgets")
disabled = image.get_region(2, 256 - 46 - 17, 196, 14)
enabled = image.get_region(2, 256 - 66 - 17, 196, 14)
hovering = image.get_region(2, 256 - 86 - 17, 196, 14)
# enabled.save(shared.local+"/tmp/minecraft.png")  # only for debugging reasons


IMAGES = {
    ButtonMode.DISABLED: disabled,
    ButtonMode.ENABLED: enabled,
    ButtonMode.HOVERING: hovering,
}


@onlyInClient()
def draw_button(position, size, mode):
    if mode not in IMAGES:
        mode = ButtonMode.DISABLED
    sourceimage: pyglet.image.AbstractImage = IMAGES[mode]
    w = size[0] // sourceimage.width
    h = size[1] // sourceimage.height
    pyglet.gl.glColor3d(255, 255, 255)
    for x in range(w + 1):
        i = (
            sourceimage
            if x != w
            else sourceimage.get_region(
                0, 0, size[0] % sourceimage.width, sourceimage.height
            )
        )
        for y in range(h + 1):
            ii = (
                i
                if y != h
                else i.get_region(0, 0, i.width, size[1] % sourceimage.height)
            )
            try:
                ii.blit(
                    x * sourceimage.width + position[0],
                    y * sourceimage.height + position[1],
                )
            except ZeroDivisionError:
                pass
            except TypeError:
                pass
    mcpython.util.opengl.draw_line_rectangle(
        position, size, (0, 0, 0) if mode != ButtonMode.HOVERING else (255, 255, 255)
    )


@onlyInClient()
class UIPartButton(UIPart.UIPart):
    def __init__(
        self,
        size,
        text,
        position,
        press=mcpython.engine.event.EventInfo.MousePressEventInfo(
            pyglet.window.mouse.LEFT
        ),
        anchor_button="WS",
        anchor_window="WS",
        on_press=None,
        on_hover=None,
        on_try_press=None,
        enabled=True,
        has_hovering_state=True,
    ):
        """
        Creates a new UIPartButton
        :param size: the size of the button
        :param text: the text of the button
        :param position: the position of the button
        :param press: the EventInfo for mouse buttons and mods, no area
        :param anchor_button: the anchor on the button
        :param anchor_window: the anchor on the window
        :param on_press: called together with x and y on press on the button  todo: change to include button
        :param on_hover: called on every mouse move on the button with the mouse x and y
        :param on_try_press: called when the button is pressed during an in-active phase of the button with x and y
        :param enabled: if the button should be enabled from the start
        :param has_hovering_state: if the button has an state different from normal when the mouse is over it
        """
        super().__init__(
            position, size, anchor_element=anchor_button, anchor_window=anchor_window
        )
        self.text = text
        self.press: mcpython.engine.event.EventInfo.MousePressEventInfo = press

        self.on_press = on_press
        self.on_hover = on_hover
        self.on_try_press = on_try_press

        self.enabled = enabled
        self.has_hovering_state = has_hovering_state
        self.hovering = False

        self.lable = pyglet.text.Label(text=text)
        self.active = False

    def bind_to_eventbus(self):
        self.master[0].eventbus.subscribe("user:mouse:press", self.on_mouse_press)
        self.master[0].eventbus.subscribe("user:mouse:motion", self.on_mouse_motion)
        self.master[0].eventbus.subscribe("render:draw:2d", self.on_draw_2d)

    def deactivate(self):
        super().deactivate()
        self.hovering = False

    def on_mouse_press(self, x, y, button, modifiers):
        mx, my = self.get_real_position()
        sx, sy = self.bboxsize
        self.press.area = ((mx, my), (mx + sx, my + sy))
        if self.press.equals(x, y, button, modifiers):
            if self.on_press:
                self.on_press(x, y)
        else:
            if self.on_try_press:
                self.on_try_press(x, y)

    def on_mouse_motion(self, x, y, dx, dy):
        mx, my = self.get_real_position()
        sx, sy = self.bboxsize
        if 0 <= x - mx <= sx and 0 <= y - my <= sy:
            if self.on_hover:
                self.on_hover(x, y)
            self.hovering = True
        else:
            self.hovering = False

    def on_draw_2d(self):
        mode = (
            ButtonMode.DISABLED
            if not self.enabled
            else (
                ButtonMode.HOVERING
                if self.hovering and self.has_hovering_state
                else ButtonMode.ENABLED
            )
        )
        x, y = self.get_real_position()
        draw_button((x, y), self.bboxsize, mode)
        self.lable.text = mcpython.common.Language.translate(self.text)
        wx, wy = self.lable.content_width, self.lable.content_height
        self.lable.x = x + self.bboxsize[0] // 2 - wx // 2
        self.lable.y = y + self.bboxsize[1] // 2 - wy // 3
        self.lable.font_size = self.bboxsize[1] // 2.0
        self.lable.draw()


@onlyInClient()
class UIPartToggleButton(UIPartButton):
    def __init__(
        self,
        size,
        text_possibilities,
        position,
        toggle=mcpython.engine.event.EventInfo.MousePressEventInfo(
            pyglet.window.mouse.LEFT
        ),
        retoggle=mcpython.engine.event.EventInfo.MousePressEventInfo(
            pyglet.window.mouse.RIGHT
        ),
        anchor_button="WS",
        anchor_window="WS",
        on_toggle=None,
        on_hover=None,
        on_try_press=None,
        enabled=True,
        has_hovering_state=True,
        text_constructor="{}",
        start=0,
    ):
        """
        creates an new UIPartButton
        :param size: the size of the button
        :param text_possibilities: the texts of the button
        :param position: the position of the button
        :param toggle: the EventInfo for mouse buttons and mods, no area to define, toggle forward
        :param retoggle: the EventInfo for mouse buttons and mods, no area to define, toggle backwards
        :param anchor_button: the anchor on the button
        :param anchor_window: the anchor on the window
        :param on_toggle: called when the button toggles, parameters: (from: str, to: str, direction: int, position:tuple)
        :param on_hover: called when the mouse is over the button
        :param on_try_press: called when button is disabled and the user presses the button
        :param enabled: button should be clickable?
        :param has_hovering_state: if the button gets blue when mouse is over it
        :param text_constructor: an string.format(item) or an function(item: str) -> str entry
        :param start: where in the array to start from
        """
        UIPart.UIPart.__init__(
            self,
            position,
            size,
            anchor_element=anchor_button,
            anchor_window=anchor_window,
        )
        self.text_pages = text_possibilities
        self.text_constructor = text_constructor
        self.index = start
        self.text = ""
        self.toggle: mcpython.engine.event.EventInfo.MousePressEventInfo = toggle
        self.retoggle: mcpython.engine.event.EventInfo.MousePressEventInfo = retoggle

        self.on_toggle = on_toggle
        self.on_hover = on_hover
        self.on_try_press = on_try_press

        self.event_functions = [
            ("user:mouse:press", self.on_mouse_press),
            ("user:mouse:motion", self.on_mouse_motion),
            ("render:draw:2d", self.on_draw_2d),
        ]

        self.enabled = enabled
        self.has_hovering_state = has_hovering_state
        self.hovering = False

        self.lable = pyglet.text.Label(text=self.text)
        self.active = False

    def update_text(self):
        text = self.text_pages[self.index]
        if type(self.text_constructor) == str:
            self.text = mcpython.common.Language.translate(
                self.text_constructor.format(text)
            )
        elif callable(self.text_constructor):
            self.text = mcpython.common.Language.translate(self.text_constructor(text))
        else:
            self.text = mcpython.common.Language.translate(text)

    def on_mouse_press(self, x, y, button, modifiers):
        mx, my = self.get_real_position()
        sx, sy = self.bboxsize
        self.toggle.area = self.retoggle.area = ((mx, my), (mx + sx, my + sy))
        if self.toggle.equals(x, y, button, modifiers):
            self.index += 1
            if self.index >= len(self.text_pages):
                self.index = 0
            new = self.text_pages[self.index]
            if self.on_toggle:
                self.on_toggle(self.text, new, 1, (x, y))
            self.update_text()
        elif self.retoggle.equals(x, y, button, modifiers):
            self.index -= 1
            if self.index < 0:
                self.index = len(self.text_pages) - 1
            new = self.text_pages[self.index]
            if self.on_toggle:
                self.on_toggle(self.text, new, -1, (x, y))
            self.update_text()
        else:
            if self.on_try_press:
                self.on_try_press(x, y)

    def on_draw_2d(self):
        if self.text == "":
            self.update_text()
        super().on_draw_2d()
