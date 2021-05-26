from mcpython.loader.java.Java import native, NativeClass
from mcpython import shared


class HashMultiMap(NativeClass):
    NAME = "com/google/common/collect/HashMultimap"

    @native("create", "()Lcom/google/common/collect/HashMultimap;")
    def create(self):
        instance = self.create_instance()
        return instance


class Lists(NativeClass):
    NAME = "com/google/common/collect/Lists"

    @native("newArrayList", "()Ljava/util/ArrayList;")
    def create(self):
        instance = self.vm.get_class("java/util/ArrayList").create_instance()
        return instance


class Maps(NativeClass):
    NAME = "com/google/common/collect/Maps"

    @native("newHashMap", "()Ljava/util/HashMap;")
    def create(self):
        instance = self.vm.get_class("java/util/HashMap").create_instance()
        return instance

