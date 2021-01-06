"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import itertools
import typing


class Stream:
    # Input / Creation

    @classmethod
    def from_iterator(cls, iterator: typing.Iterator):
        return cls(iterator)

    @classmethod
    def from_iterable(cls, iterable: typing.Iterable):
        return cls((e for e in iterable))

    def __init__(self, source: typing.Iterator):
        self.source = source
        self.operations = []
        self.stream_able = True

    def copy(self):
        instance = Stream(self.source)
        instance.stream_able = self.stream_able
        instance.operations = self.operations.copy()
        return instance

    # Manipulation

    def for_each(self, function: typing.Callable[[int, typing.Any], None]):
        self.operations.append((1, function))
        return self

    def for_each_store(self, function: typing.Callable[[int, typing.Any], typing.Any]):
        self.operations.append((2, function))
        return self

    def filter(self, function: typing.Callable[[int, typing.Any], bool]):
        self.operations.append((3, function))
        return self

    def slice(self, start: int, end: int, step: int):
        self.filter(lambda i, obj: (start <= i < end and (i - start) % step == 0))
        return self

    def merge(self, stream: "Stream"):
        self.operations.append((4, stream))
        return self

    def sum(
        self, function: typing.Callable[[int, typing.Any], typing.Any] = lambda i, e: e
    ):
        return sum(self.copy().for_each_store(function).as_iterator())

    def mul(
        self,
        function: typing.Callable[[int, typing.Any], typing.Any] = lambda i, e: e,
        default=1,
    ):
        def step(i, element):
            step.count *= function(i, element)

        step.count = default

        self.copy().for_each(step).build()

        return step.count

    # Output

    def as_iterator(self) -> typing.Iterator:
        if not self.stream_able:
            return self.as_list()
        additional_sources = []
        for op, *args in self.operations:
            if op == 4:
                additional_sources.append(args[0])
        return itertools.chain(self.raw_iterator(), *additional_sources)

    def raw_iterator(self) -> typing.Iterator:
        for i, element in enumerate(self.source):
            for op, *args in self.operations:
                try:
                    element = self.execute_operation_on(element, i, op, args)
                except RuntimeError:
                    break
            else:
                yield element

    def execute_operation_on(self, element, i, op, args):
        if op == 1:
            args[0](i, element)
        elif op == 2:
            return args[0](i, element)
        elif op == 3:
            if not args[0](i, element):
                raise RuntimeError()
        return element

    def build(self):
        for i, element in enumerate(self.source):
            for op, *args in self.operations:
                if op == 1:
                    args[0](i, element)
                elif op == 2:
                    element = args[0](i, element)
                elif op == 3:
                    if not args[0](i, element):
                        break

    def as_list(self) -> typing.List:
        if self.stream_able:
            return list(self.as_iterator())
