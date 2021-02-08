"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
import itertools
from mcpython.util.enums import EnumSide, FACE_ORDER_HORIZONTAL


class PossibleBlockStateBuilder:
    def __init__(self):
        self.states = []
        self.combination_stack = {}

    def combinations(self):
        self.combination_stack.clear()
        return self

    def add_comby(self, key: str, *states):
        self.combination_stack[key] = states
        return self

    def add_comby_bool(self, key: str):
        return self.add_comby(key, "true", "false")

    def add_comby_side(self, key: str):
        return self.add_comby(key, *(face.normal_name for face in EnumSide.iterate()))

    def add_comby_side_horizontal(self, key: str):
        return self.add_comby(
            key, *(face.normal_name for face in FACE_ORDER_HORIZONTAL)
        )

    def build_combys(self):
        keys = list(self.combination_stack.keys())
        self.states.extend(
            (
                {key: e[i] for i, key in enumerate(keys)}
                for e in itertools.product(
                    *(self.combination_stack[key] for key in keys)
                )
            )
        )
        self.combination_stack.clear()
        return self

    def add_state(self, state):
        self.states.append(state)
        return self

    def build(self):
        if len(self.combination_stack) > 0:
            self.build_combys()

        return self.states
