from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


class TreeMap(NativeClass):
    NAME = "java/util/TreeMap"

    @native("<init>", "()V")
    def init(self, *_):
        pass

