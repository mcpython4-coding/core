"""
mcpython - a minecraft clone written in python licenced under the MIT-licence 
(https://github.com/mcpython4-coding/core)

Contributors: uuk, xkcdjerry (inactive)

Based on the game of fogleman (https://github.com/fogleman/Minecraft), licenced under the MIT-licence
Original game "minecraft" by Mojang Studios (www.minecraft.net), licenced under the EULA
(https://account.mojang.com/documents/minecraft_eula)
Mod loader inspired by "Minecraft Forge" (https://github.com/MinecraftForge/MinecraftForge) and similar

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native
from mcpython.loader.java.JavaExceptionStack import StackCollectingException


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
        instance = self.vm.get_class(
            "java/util/ArrayList", version=self.internal_version
        ).create_instance()
        return instance

    @native("newArrayList", "([Ljava/lang/Object;)Ljava/util/ArrayList;")
    def newArrayList(self, array):
        return array

    @native("newLinkedList", "()Ljava/util/LinkedList;")
    def newLinkedList(self):
        return []


class Maps(NativeClass):
    NAME = "com/google/common/collect/Maps"

    @native("newHashMap", "()Ljava/util/HashMap;")
    def create(self):
        instance = self.vm.get_class(
            "java/util/HashMap", version=self.internal_version
        ).create_instance()
        return instance

    @native("newHashMap", "(Ljava/util/Map;)Ljava/util/HashMap;")
    def copyHashMap(self, instance):
        return instance.copy()

    @native("newEnumMap", "(Ljava/util/Map;)Ljava/util/EnumMap;")
    def newEnumMap(self, base_map):
        return base_map

    @native("newTreeMap", "()Ljava/util/TreeMap;")
    def newTreeMap(self):
        return {}

    @native("newIdentityHashMap", "()Ljava/util/IdentityHashMap;")
    def newIdentityHashMap(self, *_):
        return {}


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


class ImmutableMap(NativeClass):
    NAME = "com/google/common/collect/ImmutableMap"

    @native("builder", "()Lcom/google/common/collect/ImmutableMap$Builder;")
    def builder(self):
        return self.vm.get_class(
            "com/google/common/collect/ImmutableMap$Builder",
            version=self.internal_version,
        ).create_instance()

    @native(
        "of",
        "(Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;)Lcom/google/common/collect/ImmutableMap;",
    )
    def of(self, *stuff):
        return self.create_instance()


class ImmutableMap__Builder(NativeClass):
    NAME = "com/google/common/collect/ImmutableMap$Builder"

    def create_instance(self):
        return {}

    @native(
        "putAll", "(Ljava/util/Map;)Lcom/google/common/collect/ImmutableMap$Builder;"
    )
    def putAll(self, instance, data):
        instance.update(data)
        return instance

    @native(
        "put",
        "(Ljava/lang/Object;Ljava/lang/Object;)Lcom/google/common/collect/ImmutableMap$Builder;",
    )
    def put(self, instance, key, value):
        instance[key] = value
        return instance

    @native("build", "()Lcom/google/common/collect/ImmutableMap;")
    def build(self, instance):
        return instance  # todo: make immutable


class ImmutableMultimap(NativeClass):
    NAME = "com/google/common/collect/ImmutableMultimap"

    @native("builder", "()Lcom/google/common/collect/ImmutableMultimap$Builder;")
    def builder(self):
        return self.vm.get_class(
            "com/google/common/collect/ImmutableMultimap$Builder",
            version=self.internal_version,
        ).create_instance()


class ImmutableMultimap__Builder(NativeClass):
    NAME = "com/google/common/collect/ImmutableMultimap$Builder"

    @native(
        "put",
        "(Ljava/lang/Object;Ljava/lang/Object;)Lcom/google/common/collect/ImmutableMultimap$Builder;",
    )
    def put(self, instance, key, value):
        return instance

    @native("build", "()Lcom/google/common/collect/ImmutableMultimap;")
    def build(self, instance):
        return self.vm.get_class(
            "com/google/common/collect/ImmutableMultimap", version=self.internal_version
        ).create_instance()


class MutableClassToInstanceMap(NativeClass):
    NAME = "com/google/common/collect/MutableClassToInstanceMap"

    @native("create", "()Lcom/google/common/collect/MutableClassToInstanceMap;")
    def create(self):
        return self.create_instance()

    @native("containsKey", "(Ljava/lang/Object;)Z")
    def containsKey(self, instance, key):
        return False

    @native("putInstance", "(Ljava/lang/Class;Ljava/lang/Object;)Ljava/lang/Object;")
    def putInstance(self, instance, cls, obj):
        return obj


class Preconditions(NativeClass):
    NAME = "com/google/common/base/Preconditions"

    @native("checkNotNull", "(Ljava/lang/Object;)Ljava/lang/Object;")
    def checkNotNull(self, obj):
        if obj is None:
            raise StackCollectingException("expected non-null, got null")
        return obj

    @native("checkArgument", "(Z)V")
    def checkArgument(self, value):
        if not value:
            raise StackCollectingException("expected true, got false")

    @native("checkArgument", "(ZLjava/lang/Object;)V")
    def checkArgument2(self, value, obj):
        if not value:
            raise StackCollectingException(f"expected true, got false, message: {obj}")


class ClassToInstanceMap(NativeClass):
    NAME = "com/google/common/collect/ClassToInstanceMap"

    @native("containsKey", "(Ljava/lang/Object;)Z")
    def containsKey(self, instance, key):
        return False

    @native("putInstance", "(Ljava/lang/Class;Ljava/lang/Object;)Ljava/lang/Object;")
    def putInstance(self, instance, cls, obj):
        return obj


class CharMatcher(NativeClass):
    NAME = "com/google/common/base/CharMatcher"

    @native(
        "forPredicate",
        "(Lcom/google/common/base/Predicate;)Lcom/google/common/base/CharMatcher;",
    )
    def forPredicate(self, *_):
        pass

    @native("anyOf", "(Ljava/lang/CharSequence;)Lcom/google/common/base/CharMatcher;")
    def anyOf(self, *_):
        pass

    @native(
        "or",
        "(Lcom/google/common/base/CharMatcher;)Lcom/google/common/base/CharMatcher;",
    )
    def or_(self, *_):
        pass


class Strings(NativeClass):
    NAME = "com/google/common/base/Strings"

    @native("isNullOrEmpty", "(Ljava/lang/String;)Z")
    def isNullOrEmpty(self, string: str):
        return int(string is None or len(string) == 0)


class ImmutableSet(NativeClass):
    NAME = "com/google/common/collect/ImmutableSet"

    @native(
        "copyOf", "(Ljava/util/Collection;)Lcom/google/common/collect/ImmutableSet;"
    )
    def copyOf(self, collection):
        obj = self.create_instance()

        try:
            obj.underlying = (
                set(collection)
                if not hasattr(collection, "get_class")
                or not hasattr(collection.get_class(), "iter_over_instance")
                else set(collection.get_class().iter_over_instance(collection))
            )
        except TypeError:
            raise NotImplementedError(f"object {collection} seems not iterable!")

        return obj

    @native(
        "of",
        "(Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;)Lcom/google/common/collect/ImmutableSet;",
    )
    def of(self, *elements):
        return set(elements)

    @native("builder", "()Lcom/google/common/collect/ImmutableSet$Builder;")
    def builder(self):
        return set()


class ImmutableSet__Builder(NativeClass):
    NAME = "com/google/common/collect/ImmutableSet$Builder"

    @native(
        "add", "(Ljava/lang/Object;)Lcom/google/common/collect/ImmutableSet$Builder;"
    )
    def add(self, instance, obj):
        instance.add(obj)
        return instance

    @native("build", "()Lcom/google/common/collect/ImmutableSet;")
    def build(self, instance):
        return instance  # todo: make immutable


class BiMap(NativeClass):
    NAME = "com/google/common/collect/BiMap"

    @native("put", "(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;")
    def put(self, instance, key, value):
        instance[key] = value
        return value


class Joiner(NativeClass):
    NAME = "com/google/common/base/Joiner"

    @native("on", "(Ljava/lang/String;)Lcom/google/common/base/Joiner;")
    def on(self, string: str):
        return self.create_instance()


class ArrayListMultimap(NativeClass):
    NAME = "com/google/common/collect/ArrayListMultimap"

    @native("create", "()Lcom/google/common/collect/ArrayListMultimap;")
    def create(self):
        return self.create_instance()


class Sets(NativeClass):
    NAME = "com/google/common/collect/Sets"

    @native("newHashSet", "()Ljava/util/HashSet;")
    def newHashSet(self, *_):
        return set()


class Multimaps(NativeClass):
    NAME = "com/google/common/collect/Multimaps"

    @native("newListMultimap",
            "(Ljava/util/Map;Lcom/google/common/base/Supplier;)Lcom/google/common/collect/ListMultimap;")
    def newListMultimap(self, *_):
        return {}


class ImmutableBiMap(NativeClass):
    NAME = "com/google/common/collect/ImmutableBiMap"

    def create_instance(self):
        return {}

    @native("of", "()Lcom/google/common/collect/ImmutableBiMap;")
    def of(self, *_):
        return {}

