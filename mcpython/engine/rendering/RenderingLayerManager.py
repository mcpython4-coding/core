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
import typing

from mcpython import shared
from pyglet.gl import *

__all__ = [
    "RenderingLayer",
    "RenderingLayerManager",
    "manager",
    "REAL_BACKGROUND",
    "NORMAL_WORLD",
    "INTER_BACKGROUND",
    "MIDDLE_GROUND",
    "FOREGROUND",
]


class RenderingLayer:
    def __init__(self, rendering_manager: "RenderingLayerManager", name: str):
        self.manager = rendering_manager
        self.name = name

        self.event_name = None
        self.enabled = True
        self.rendering_mode = None

        self.invoke_after = set()
        self.invoke_before = set()

        self.draw_subscribers = []

    def activate(self):
        self.enabled = True

    def deactivate(self):
        self.enabled = False

    def renderAfter(self, layer: typing.Union[str, "RenderingLayer"]):
        self.invoke_after.add(layer if isinstance(layer, str) else layer.name)
        return self

    def renderBefore(self, layer: typing.Union[str, "RenderingLayer"]):
        self.invoke_before.add(layer if isinstance(layer, str) else layer.name)
        return self

    def setRenderingMode(self, mode: str):
        self.rendering_mode = mode
        return self

    def getRenderingEvent(self) -> str:
        if self.event_name is None:
            self.event_name = self.manager.create_rendering_event(self.name)
        return self.event_name

    def registerEventSub(self, sub: typing.Callable):
        self.draw_subscribers.append(sub)
        return sub

    def isEnvEqual(self, other: "RenderingLayer") -> bool:
        return (
            self.rendering_mode == other.rendering_mode
            and self.rendering_mode is not None
        )

    def setupEnv(self):
        if self.rendering_mode == "2d":
            shared.window.set_2d()
        elif self.rendering_mode == "3d":
            shared.window.set_3d()
        else:
            glLoadIdentity()

    def draw(self):
        if self.event_name is not None:
            shared.event_handler.call_ordered(self.event_name)

        for sub in self.draw_subscribers:
            sub()

    def resetEnv(self):
        glLoadIdentity()


class RenderingLayerManager:
    def __init__(self):
        self.layers: typing.Dict[str, RenderingLayer] = {}
        self.ordered_layers: typing.List[RenderingLayer] = []
        self.schedule_resort = False

    def register_rendering_stage(self, name: str):
        layer = RenderingLayer(self, name)
        self.layers[name] = layer
        self.schedule_resort = True

        return layer

    def create_rendering_event(self, name: str):
        return "minecraft:rendering:" + name  # todo: make more save

    def draw(self):
        if self.schedule_resort:
            self.sort_layers()

        prev_layer = None
        for layer in self.ordered_layers:
            if not layer.enabled:
                continue

            if prev_layer is None or not layer.isEnvEqual(prev_layer):
                if prev_layer is not None:
                    prev_layer.resetEnv()
                layer.setupEnv()

            layer.draw()

            prev_layer = layer

        if prev_layer is not None:
            prev_layer.resetEnv()

    def sort_layers(self):
        import graphlib

        layers = {layer.name: layer.invoke_after for layer in self.layers.values()}

        for layer in self.layers.values():
            for dep in layer.invoke_before:
                layers[dep].add(layer.name)

        graph = graphlib.TopologicalSorter(layers)

        self.ordered_layers = [self.layers[name] for name in graph.static_order()]


manager = RenderingLayerManager()
REAL_BACKGROUND = manager.register_rendering_stage("background_pre").setRenderingMode(
    "2d"
)
NORMAL_WORLD = (
    manager.register_rendering_stage("world")
    .setRenderingMode("3d")
    .renderAfter(REAL_BACKGROUND)
)
INTER_BACKGROUND = (
    manager.register_rendering_stage("inter_background")
    .setRenderingMode("2d")
    .renderAfter(NORMAL_WORLD)
)
MIDDLE_GROUND = (
    manager.register_rendering_stage("middle_ground")
    .setRenderingMode("2d")
    .renderAfter(INTER_BACKGROUND)
)
FOREGROUND = (
    manager.register_rendering_stage("foreground")
    .setRenderingMode("2d")
    .renderAfter(MIDDLE_GROUND)
)
