from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


class IllegalArgumentException(NativeClass):
    NAME = "java/lang/IllegalArgumentException"

    @native("<init>", "(Ljava/lang/String;)V")
    def init(self, instance, text):
        pass

