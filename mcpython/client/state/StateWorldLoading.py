"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from . import State
import mcpython.client.state.ui.UIPartLabel
from mcpython import shared as G, logger
import mcpython.util.math
from pyglet.window import key
import mcpython.common.mod.ModMcpython
import mcpython.client.state.StatePartConfigBackground
import mcpython.common.DataPack
import mcpython.util.opengl
import mcpython.common.config
from mcpython.util.annotation import onlyInClient


@onlyInClient()
class StateWorldLoading(State.State):
    NAME = "minecraft:world_loading"

    def __init__(self):
        State.State.__init__(self)
        self.status_table = {}
        self.world_size = ((0, 0), (0, 0, 0, 0), 0)
        self.finished_chunks = 0

    def get_parts(self) -> list:
        return [
            mcpython.client.state.StatePartConfigBackground.StatePartConfigBackground(),
            mcpython.client.state.ui.UIPartLabel.UIPartLabel(
                "0%",
                (0, 50),
                anchor_lable="MM",
                anchor_window="MD",
                color=(255, 255, 255, 255),
            ),
            mcpython.client.state.ui.UIPartLabel.UIPartLabel(
                "(0/0/0)",
                (0, 30),
                anchor_lable="MM",
                anchor_window="MD",
                color=(255, 255, 255, 255),
            ),
        ]

    def on_update(self, dt):
        G.world_generation_handler.task_handler.process_tasks(timer=0.8)
        for chunk in self.status_table:
            c = G.world_generation_handler.task_handler.get_task_count_for_chunk(
                G.world.get_active_dimension().get_chunk(*chunk)
            )
            self.status_table[chunk] = 1 / c if c > 0 else -1
        if len(G.world_generation_handler.task_handler.chunks) == 0:
            G.event_handler.call("data:reload:work")
            G.state_handler.switch_to("minecraft:game")
            G.world.world_loaded = True
            if (
                mcpython.common.config.SHUFFLE_DATA
                and mcpython.common.config.SHUFFLE_INTERVAL > 0
            ):
                G.event_handler.call("data:shuffle:all")
        self.parts[1].text = "{}%".format(
            round(sum(self.status_table.values()) / len(self.status_table) * 1000) / 10
        )

    def activate(self):
        super().activate()
        G.world_generation_handler.enable_generation = False
        self.status_table.clear()
        G.dimension_handler.init_dims()
        try:
            G.world.save_file.load_world()
        except IOError:  # todo: add own exception class as IOError may be raised somewhere else in the script
            logger.println(
                "failed to load world. data-fixer failed with NoDataFixerFoundException"
            )
            G.world.cleanup()
            G.state_handler.switch_to("minecraft:startmenu")
            return
        except:
            logger.print_exception("failed to load world")
            G.world.cleanup()
            G.state_handler.switch_to("minecraft:startmenu")
            return
        for cx in range(-3, 4):
            for cz in range(-3, 4):
                self.status_table[(cx, cz)] = 0
                # todo: fix bug: something is wrong here...
                # G.world.savefile.read("minecraft:chunk", dimension=G.world.get_active_player().dimension.id, chunk=(cx, cz),
                #                       immediate=False)
        G.world_generation_handler.enable_generation = True

    def deactivate(self):
        super().deactivate()
        player = G.world.get_active_player()
        player.teleport(player.position, force_chunk_save_update=True)
        import mcpython.common.data.ResourcePipe

        mcpython.common.data.ResourcePipe.handler.reload_content()

    def bind_to_eventbus(self):
        super().bind_to_eventbus()
        self.eventbus.subscribe("user:keyboard:press", self.on_key_press)
        self.eventbus.subscribe("render:draw:2d", self.on_draw_2d_post)
        self.eventbus.subscribe("gameloop:tick:end", self.on_update)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            G.state_handler.switch_to("minecraft:startmenu")
            G.tick_handler.schedule_once(G.world.cleanup)
            logger.println("interrupted world loading by user")

    def calculate_percentage_of_progress(self):
        k = list(self.status_table.values())
        return k.count(-1) / len(k)

    def on_draw_2d_post(self):
        wx, wy = G.window.get_size()
        mx, my = wx // 2, wy // 2
        if len(self.status_table) == 0:
            self.parts[1].text = "0%"
            self.parts[2].text = "0/0/0"
        else:
            self.parts[1].text = "{}%".format(
                round(self.calculate_percentage_of_progress() * 1000) / 10
            )
            self.parts[2].text = "{}/{}/{}".format(
                *G.world_generation_handler.task_handler.get_total_task_stats()
            )

        for cx, cz in self.status_table:
            status = self.status_table[(cx, cz)]
            if 0 <= status <= 1:
                factor = status * 255
                color = (factor, factor, factor)
            elif status == -1:
                color = (0, 255, 0)
            else:
                color = (136, 0, 255)
            mcpython.util.opengl.draw_rectangle(
                (mx + cx * 10, my + cz * 10), (10, 10), color
            )


world_loading = None


@onlyInClient()
def create():
    global world_loading
    world_loading = StateWorldLoading()


mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe("stage:states", create)
