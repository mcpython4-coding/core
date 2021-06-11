from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


class TreeMap(NativeClass):
    NAME = "java/util/TreeMap"

    def create_instance(self):
        return {}

    @native("<init>", "()V")
    def init(self, instance):
        pass

    @native("values", "()Ljava/util/Collection;")
    def values(self, instance):
        return list(instance.keys())

    @native("clear", "()V")
    def clear(self, instance):
        instance.clear()

    @native("get", "(Ljava/lang/Object;)Ljava/lang/Object;")
    def get(self, instance, key):
        return instance[key] if key in instance else None

    @native("containsKey", "(Ljava/lang/Object;)Z")
    def containsKey(self, instance, obj):
        return obj in instance

