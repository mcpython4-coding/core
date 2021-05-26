from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


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


class ImmutableList(NativeClass):
    NAME = "com/google/common/collect/ImmutableList"

    def create_instance(self):
        instance = super().create_instance()
        instance.underlying_tuple = None
        return instance

    @native(
        "of",
        "(Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;[Ljava/lang/Object;)Lcom/google/common/collect/ImmutableList;",
    )
    def of(self, *stuff):
        instance = self.create_instance()
        instance.underlying_tuple = stuff[:-1] + tuple(stuff[-1])
        return instance

    @native(
        "of",
        "(Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;)Lcom/google/common/collect/ImmutableList;",
    )
    def of_2(self, *stuff):
        instance = self.create_instance()
        instance.underlying_tuple = stuff
        return instance
