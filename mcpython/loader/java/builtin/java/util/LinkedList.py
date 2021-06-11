from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


class LinkedList(NativeClass):
    NAME = "java/util/LinkedList"

    @native("<init>", "()V")
    def init(self, instance):
        pass

