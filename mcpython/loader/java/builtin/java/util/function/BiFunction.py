from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


class BiFunction(NativeClass):
    NAME = "java/util/function/BiFunction"

    @native("apply", "(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;")
    def apply(self, instance, arg1, arg2):
        instance(arg1, arg2)

