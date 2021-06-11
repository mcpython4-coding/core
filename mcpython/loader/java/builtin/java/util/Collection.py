from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


class Collection(NativeClass):
    NAME = "java/util/Collection"

    @native("iterator", "()Ljava/util/Iterator;")
    def iterator(self, *_):
        return []

