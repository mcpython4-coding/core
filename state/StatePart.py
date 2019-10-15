"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G


class StatePart:
    def __init__(self):
        self.parts = self.get_sub_parts()
        self.master = None

    def activate(self):
        for statepart in self.parts:
            statepart.activate()

    def deactivate(self):
        for statepart in self.parts:
            statepart.deactivate()

    def get_sub_parts(self) -> list:
        return []

    def bind_to_eventbus(self):
        for statepart in self.parts:
            statepart.master = self.master + [self]
            statepart.bind_to_eventbus()

