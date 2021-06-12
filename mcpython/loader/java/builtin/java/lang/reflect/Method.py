from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


class Method(NativeClass):
    NAME = "java/lang/reflect/Method"

    @native("getClass", "()Ljava/lang/Class;")
    def getClass(self, instance):
        return self

