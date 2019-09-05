"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import state.StatePart
import globals as G
import event.EventInfo
import enum
import pyglet
from pyglet.window import mouse
import util.texture
import ResourceLocator


class ButtonMode(enum.Enum):
    DISABLED = 0
    ENABLED = 1
    HOVERING = 2


IMAGE_DICT = {}  # ButtonMode -> [NW, NM, NE, MW, MM, ME, SW, SM, SE] as 10x10 images loaded in pyglet as corner

button_file = ResourceLocator.read("gui/widgets", "pil")

IMAGE_DICT[ButtonMode.ENABLED] = [
    util.texture.to_pyglet_sprite(button_file.crop((0, 66, 10, 76))),  # NW
    util.texture.to_pyglet_sprite(button_file.crop((0, 71, 10, 81))),  # NM
    util.texture.to_pyglet_sprite(button_file.crop((0, 76, 10, 86))),  # NE
    util.texture.to_pyglet_sprite(button_file.crop((10, 66, 20, 76))),  # MW
    util.texture.to_pyglet_sprite(button_file.crop((10, 71, 20, 81))),  # MM
    util.texture.to_pyglet_sprite(button_file.crop((10, 76, 20, 86))),  # ME
    util.texture.to_pyglet_sprite(button_file.crop((190, 66, 200, 76))),  # SW
    util.texture.to_pyglet_sprite(button_file.crop((190, 71, 200, 81))),  # SM
    util.texture.to_pyglet_sprite(button_file.crop((190, 76, 200, 86)))  # SE
]

IMAGE_DICT[ButtonMode.DISABLED] = [
    util.texture.to_pyglet_sprite(button_file.crop((0, 46, 10, 56))),  # NW
    util.texture.to_pyglet_sprite(button_file.crop((0, 51, 10, 61))),  # NM
    util.texture.to_pyglet_sprite(button_file.crop((0, 56, 10, 66))),  # NE
    util.texture.to_pyglet_sprite(button_file.crop((10, 46, 20, 56))),  # MW
    util.texture.to_pyglet_sprite(button_file.crop((10, 51, 20, 61))),  # MM
    util.texture.to_pyglet_sprite(button_file.crop((10, 56, 20, 66))),  # ME
    util.texture.to_pyglet_sprite(button_file.crop((190, 46, 200, 56))),  # SW
    util.texture.to_pyglet_sprite(button_file.crop((190, 51, 200, 61))),  # SM
    util.texture.to_pyglet_sprite(button_file.crop((190, 56, 200, 66)))  # SE
]

IMAGE_DICT[ButtonMode.HOVERING] = [
    util.texture.to_pyglet_sprite(button_file.crop((0, 86, 10, 96))),  # NW
    util.texture.to_pyglet_sprite(button_file.crop((0, 91, 10, 101))),  # NM
    util.texture.to_pyglet_sprite(button_file.crop((0, 96, 10, 106))),  # NE
    util.texture.to_pyglet_sprite(button_file.crop((10, 86, 20, 96))),  # MW
    util.texture.to_pyglet_sprite(button_file.crop((10, 91, 20, 101))),  # MM
    util.texture.to_pyglet_sprite(button_file.crop((10, 96, 20, 106))),  # ME
    util.texture.to_pyglet_sprite(button_file.crop((190, 86, 200, 96))),  # SW
    util.texture.to_pyglet_sprite(button_file.crop((190, 91, 200, 101))),  # SM
    util.texture.to_pyglet_sprite(button_file.crop((190, 96, 200, 106)))  # SE
]


def draw_button(position, size, mode):
    if mode not in IMAGE_DICT:
        mode = ButtonMode.DISABLED
    images = IMAGE_DICT[mode]
    x, y = position
    dx, dy = size

    # middle

    mx, my = size[0] % 10 // 2, size[1] % 10 // 2

    for rx in range(size[0] // 10):
        rx *= 10
        rx += mx
        for ry in range(size[1] // 10):
            ry *= 10
            ry += my
            images[4].position = (rx+x, ry+y)
            images[4].draw()

    for rx in range(size[0] // 10):
        rx *= 10
        images[5].position = (x+rx, y)
        images[5].draw()
        images[3].position = (x+rx, y+size[1]-10)
        images[3].draw()

    for ry in range(size[1] // 10):
        ry *= 10
        images[1].position = (x, y+ry)
        images[1].draw()
        images[7].position = (x+size[0]-10, y+ry)
        images[7].draw()

    # corners
    dx -= 10
    dy -= 10
    images[6].position = (x+dx, y+dy)
    images[6].draw()
    images[8].position = (x+dx, y)
    images[8].draw()
    images[0].position = (x, y+dy)
    images[0].draw()
    images[2].position = position
    images[2].draw()


class UIPartButton(state.StatePart.StatePart):
    def __init__(self, size, text, position, press=event.EventInfo.MousePressEventInfo(pyglet.window.mouse.LEFT),
                 anchor_button="WS", anchor_window="WS", on_press=None, on_hover=None, on_try_press=None,
                 enabled=True, has_hovering_state=True):
        """
        creates an new UIPartButton
        :param size: the size of the button
        :param text: the text of the button
        :param position: the position of the button
        :param press: the EventInfo for mouse buttons and mods, no area
        :param anchor_button: the anchor on the button
        :param anchor_window: the anchor on the window
        """
        self.size = size
        self.text = text
        self.position = position
        self.press: event.EventInfo.MousePressEventInfo = press
        self.anchor_button = anchor_button
        self.anchor_window = anchor_window

        self.on_press = on_press
        self.on_hover = on_hover
        self.on_try_press = on_try_press

        self.event_functions = [("user:mouse:press", self.on_mouse_press),
                                ("user:mouse:motion", self.on_mouse_motion),
                                ("render:draw:2d", self.on_draw_2d)]

        self.enabled = enabled
        self.has_hovering_state = has_hovering_state
        self.hovering = False

        self.lable = pyglet.text.Label(text=text)

    def activate(self):
        for eventname, function in self.event_functions:
            G.eventhandler.activate_to_callback(eventname, function)

    def deactivate(self):
        for eventname, function in self.event_functions:
            G.eventhandler.deactivate_from_callback(eventname, function)
        self.hovering = False

    def _get_button_base_positon(self):
        x, y = self.position
        wx, wy = G.window.get_size()
        bx, by = self.size
        if self.anchor_button[0] == "M":
            x -= bx // 2
        elif self.anchor_button[0] == "E":
            x = bx - abs(x)
        if self.anchor_button[1] == "M":
            y -= by // 2
        elif self.anchor_button[1] == "N":
            y = by - abs(y)
        if self.anchor_window[0] == "M":
            x += wx // 2
        elif self.anchor_window[0] == "E":
            x = wx - abs(x)
        if self.anchor_window[1] == "M":
            y += wy // 2
        elif self.anchor_window[1] == "N":
            y = wy - abs(y)
        return x, y

    @G.eventhandler("user:mouse:press", callactive=False)
    def on_mouse_press(self, x, y, button, modifiers):
        mx, my = self._get_button_base_positon()
        sx, sy = self.size
        self.press.area = ((mx, my), (mx+sx, my+sy))
        if self.press.equals(x, y, button, modifiers):
            if self.on_press:
                self.on_press(x, y)
        else:
            if self.on_try_press:
                self.on_try_press(x, y)

    @G.eventhandler("user:mouse:motion", callactive=False)
    def on_mouse_motion(self, x, y, dx, dy):
        mx, my = self._get_button_base_positon()
        sx, sy = self.size
        if 0 <= x - mx <= sx and 0 <= y - my <= sy:
            if self.on_hover:
                self.on_hover(x, y)
            self.hovering = True
        else:
            self.hovering = False

    @G.eventhandler("render:draw:2d", callactive=False)
    def on_draw_2d(self):
        mode = ButtonMode.DISABLED if not self.enabled else (
            ButtonMode.HOVERING if self.hovering and self.has_hovering_state else ButtonMode.ENABLED
        )
        x, y = self._get_button_base_positon()
        draw_button((x, y), self.size, mode)
        self.lable.text = self.text
        wx, wy = self.lable.content_width, self.lable.content_height
        self.lable.x = x + self.size[0] // 2 - wx // 2
        self.lable.y = y + self.size[1] // 2 - wy // 3
        self.lable.font_size = self.size[1] // 2.0
        self.lable.draw()


class UIPartToggleButton(UIPartButton):
    def __init__(self, size, textpossibilitys, position,
                 toggle=event.EventInfo.MousePressEventInfo(pyglet.window.mouse.LEFT),
                 retoggle=event.EventInfo.MousePressEventInfo(pyglet.window.mouse.RIGHT),
                 anchor_button="WS", anchor_window="WS", on_toggle=None, on_hover=None, on_try_press=None,
                 enabled=True, has_hovering_state=True, text_constructor="{}", start=0):
        """
        creates an new UIPartButton
        :param size: the size of the button
        :param textpossibilitys: the texts of the button
        :param position: the position of the button
        :param toggle: the EventInfo for mouse buttons and mods, no area to define, toggle forward
        :param retoggle: the EventInfo for mouse buttons and mods, no area to define, toggle backwards
        :param anchor_button: the anchor on the button
        :param anchor_window: the anchor on the window
        :param on_toggle: callen when the button toggles, parameters: (from: str, to: str, direction: int, position:tuple)
        :param on_hover: callen when the mouse is over the button
        :param on_try_press: callen when button is disabled and the user presses the button
        :param enabled: button should be clickable?
        :param has_hovering_state: if the button gets blue when mouse is over it
        :param text_constructor: an string.format(item) or an function(item: str) -> str entry
        :param start: where in the array to start from
        """
        self.size = size
        self.textpages = textpossibilitys
        self.textconstructor = text_constructor
        self.index = start
        self.text = ""
        self._generate_text()
        self.position = position
        self.toggle: event.EventInfo.MousePressEventInfo = toggle
        self.retoggle: event.EventInfo.MousePressEventInfo = retoggle
        self.anchor_button = anchor_button
        self.anchor_window = anchor_window

        self.on_toggle = on_toggle
        self.on_hover = on_hover
        self.on_try_press = on_try_press

        self.event_functions = [("user:mouse:press", self.on_mouse_press),
                                ("user:mouse:motion", self.on_mouse_motion),
                                ("render:draw:2d", self.on_draw_2d)]

        self.enabled = enabled
        self.has_hovering_state = has_hovering_state
        self.hovering = False

        self.lable = pyglet.text.Label(text=self.text)

    def _generate_text(self):
        text = self.textpages[self.index]
        if type(self.textconstructor) == str:
            self.text = self.textconstructor.format(text)
        elif callable(self.textconstructor):
            self.text = self.textconstructor(text)
        else:
            self.text = text

    @G.eventhandler("user:mouse:press", callactive=False)
    def on_mouse_press(self, x, y, button, modifiers):
        mx, my = self._get_button_base_positon()
        sx, sy = self.size
        self.toggle.area = self.retoggle.area = ((mx, my), (mx + sx, my + sy))
        if self.toggle.equals(x, y, button, modifiers):
            self.index += 1
            if self.index >= len(self.textpages): self.index = 0
            new = self.textpages[self.index]
            if self.on_toggle:
                self.on_toggle(self.text, new, 1, (x, y))
            self._generate_text()
        elif self.retoggle.equals(x, y, button, modifiers):
            self.index -= 1
            if self.index < 0: self.index = len(self.textpages) - 1
            new = self.textpages[self.index]
            if self.on_toggle:
                self.on_toggle(self.text, new, -1, (x, y))
            self._generate_text()
        else:
            if self.on_try_press:
                self.on_try_press(x, y)

