import state.StatePart
import pyglet
import PIL.Image
import ResourceLocator
import globals as G
import util.texture


class BackgroundHandler:
    batch = pyglet.graphics.Batch()
    objects = []
    background_raw: PIL.Image.Image = ResourceLocator.read(
        "assets/minecraft/textures/gui/options_background.png", "pil")
    background_size = (32, 32)
    background_image = util.texture.to_pyglet_image(background_raw.resize(background_size))

    old_win_size = None

    @classmethod
    def recreate(cls, wx, wy):
        if cls.old_win_size == (wx, wy): return
        cls.old_win_size = (wx, wy)
        [obj.delete() for obj in cls.objects]
        cls.objects.clear()
        for x in range(wx // cls.background_size[0] + 1):
            for y in range(wy // cls.background_size[1] + 1):
                obj = pyglet.sprite.Sprite(cls.background_image, batch=cls.batch)
                obj.position = (x * cls.background_size[0], y * cls.background_size[1])
                cls.objects.append(obj)


class StatePartConfigBackground(state.StatePart.StatePart):
    def activate(self):
        super().activate()
        BackgroundHandler.recreate(*G.window.get_size())

    def bind_to_eventbus(self):
        super().bind_to_eventbus()
        self.master[0].eventbus.subscribe("render:draw:2d:background", self.draw)
        self.master[0].eventbus.subscribe("user:window:resize", self.resize)

    def draw(self): BackgroundHandler.batch.draw()

    def resize(self, x, y): BackgroundHandler.recreate(x, y)

