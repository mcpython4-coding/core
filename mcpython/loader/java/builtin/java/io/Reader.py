from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


class Reader(NativeClass):
    NAME = "java/io/Reader"

    @native("<init>", "()V")
    def init(self, *_):
        pass

