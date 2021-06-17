from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


class Type(NativeClass):
    NAME = "org/objectweb/asm/Type"

    @native("getType", "(Ljava/lang/Class;)Lorg/objectweb/asm/Type;")
    def getType(self, cls):
        return self.create_instance()

