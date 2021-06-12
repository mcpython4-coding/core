from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


class Method(NativeClass):
    NAME = "java/lang/reflect/Method"

    @native("getClass", "()Ljava/lang/Class;")
    def getClass(self, instance):
        return self

    @native("accept", "(Ljava/lang/Object;)V")
    def accept(self, instance, obj):
        instance(obj)

    @native("apply", "(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;")
    def apply(self, instance, arg1, arg2):
        instance(arg1, arg2)

