from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


class Consumer(NativeClass):
    NAME = "java/util/function/Consumer"

    @native("accept", "(Ljava/lang/Object;)V")
    def accept(self, instance, arg):
        if instance is None: return

        instance(arg)

