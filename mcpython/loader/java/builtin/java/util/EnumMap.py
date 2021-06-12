from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


class EnumMap(NativeClass):
    NAME = "java/util/EnumMap"

    @native("<init>", "(Ljava/lang/Class;)V")
    def init(self, instance, cls):
        instance.underlying = {}

    @native("put", "(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;")
    def put(self, instance, key, obj):
        instance.underlying[key] = obj
        return obj

