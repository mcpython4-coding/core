from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


class LinkedHashSet(NativeClass):
    NAME = "java/util/LinkedHashSet"

    def create_instance(self):
        return set()

    @native("<init>", "()V")
    def init(self, *_):
        pass

