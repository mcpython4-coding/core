from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


class CopyOnWriteArrayList(NativeClass):
    NAME = "java/util/concurrent/CopyOnWriteArrayList"

    def create_instance(self):
        return []

    @native("<init>", "()V")
    def init(self, instance):
        pass

