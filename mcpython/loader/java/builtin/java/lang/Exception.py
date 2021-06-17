from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


class Exception(NativeClass):
    NAME = "java/lang/Exception"

    @native("<init>", "(Ljava/lang/String;)V")
    def init(self, instance, text):
        pass

