"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
from . import State, StatePartGame
from .ui import UIPartButton, UIPartLable
import event.EventInfo
import globals as G
from pyglet.window import key
import util.math
import world.gen.WorldGenerationHandler


class StateWorldGenerationConfig(State.State):
    @staticmethod
    def get_name():
        return "minecraft:world_generation_config"

    def __init__(self):
        State.State.__init__(self)

    def get_parts(self) -> list:
        return [UIPartLable.UIPartLable("World Generation Selection", (0, 200), anchor_lable="MM", anchor_window="MM",
                                        color=(0, 0, 0, 255)),
                UIPartButton.UIPartToggleButton((300, 20), [0, 1, 2, 3], text_constructor="gamemode {}",
                                                position=(0, 0), anchor_window="MM", anchor_button="MM"),
                UIPartButton.UIPartButton((300, 20), "create world", (0, -50), anchor_button="MM", anchor_window="MM",
                                          on_press=self.on_new_world_press),
                UIPartButton.UIPartToggleButton((300, 20), list(G.worldgenerationhandler.configs.keys()),
                                                text_constructor="world generator {}", position=(0, 50),
                                                anchor_window="MM", anchor_button="MM")]

    def on_new_world_press(self, *args):
        G.world.cleanup(remove_dims=True)
        G.world.add_dimension(0, {"configname": self.parts[3].textpages[self.parts[3].index]})
        print("generating world")
        G.worldgenerationhandler.enable_generation = True
        for x in range(-1, 2):
            for z in range(-1, 2):
                chunk = G.world.dimensions[0].get_chunk(x, z, generate=False)
                chunk.is_ready = False
                G.worldgenerationhandler.generate_chunk(chunk)
        G.world.process_entire_queue()
        G.worldgenerationhandler.enable_generation = False
        # todo: remove disable for auto-gen
        print("finished")
        G.statehandler.switch_to("minecraft:gameinfo")
        G.world.change_sectors(None, util.math.sectorize(G.window.position), immediate=True)
        G.window.position = 0, util.math.get_max_y((0, 0, 0)), 0
        G.player.set_gamemode(self.parts[1].index)

    def get_event_functions(self) -> list:
        return [(self.on_key_press, "user:keyboard:press")]

    def on_activate(self, old):
        pass

    def on_deactivate(self, new):
        pass

    @G.eventhandler("user:keyboard:press", callactive=False)
    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            G.statehandler.switch_to("minecraft:startmenu")


escape = StateWorldGenerationConfig()

