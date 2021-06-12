from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


class Math(NativeClass):
    NAME = "java/lang/Math"

    @native("max", "(DD)D")
    def max(self, a, b):
        return max(a, b)

    @native("min", "(DD)D")
    def min(self, a, b):
        return min(a, b)

