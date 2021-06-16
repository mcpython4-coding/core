from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


class ArrayDeque(NativeClass):
    NAME = "java/util/ArrayDeque"

    def create_instance(self):
        return []

    @native("<init>", "()V")
    def init(self, *_):
        pass

