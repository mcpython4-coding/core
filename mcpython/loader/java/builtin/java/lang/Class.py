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
import mcpython.ResourceLoader
from mcpython import logger
from mcpython.loader.java.Java import AbstractJavaClass, NativeClass, native


class Class(NativeClass):
    NAME = "java/lang/Class"

    @native("isInstance", "(Ljava/lang/Object;)Z")
    def isInstance(self, instance, obj):
        return obj.get_class().is_subclass_of(instance.name)

    @native("getInterfaces", "()[Ljava/lang/Class;")
    def getInterfaces(self, instance):
        return [interface() for interface in instance.interfaces]

    @native("forName", "(Ljava/lang/String;)Ljava/lang/Class;")
    def forName(self, name: str):
        return self.vm.get_class(name, version=self.internal_version)

    @native("newInstance", "()Ljava/lang/Object;")
    def newInstance(self, cls):
        return cls.create_instance()

    @native("desiredAssertionStatus", "()Z")
    def desiredAssertionStatus(self, *_):
        return 0

    @native("getSimpleName", "()Ljava/lang/String;")
    def getSimpleName(self, instance):
        return instance.name

    @native("getResourceAsStream", "(Ljava/lang/String;)Ljava/io/InputStream;")
    def getResourceAsStream(self, instance, path: str):
        return mcpython.ResourceLoader.read_raw(path)

    @native("getDeclaredFields", "()[Ljava/lang/reflect/Field;")
    def getDeclaredFields(self, instance):
        if isinstance(instance, NativeClass):
            logger.println(
                f"[WARN] from NativeImplementation: NativeImplementation.getDeclaredFields on {instance} is unsafe"
            )
            return list(
                instance.get_dynamic_field_keys()
                | set(instance.exposed_attributes.keys())
            )

        return list(instance.fields.values())

    @native("getDeclaredMethods", "()[Ljava/lang/reflect/Method;")
    def getDeclaredMethods(self, instance):
        if isinstance(instance, NativeClass):
            logger.println(
                f"[WARN] from NativeImplementation: NativeImplementation.getDeclaredMethods on {instance} is unsafe"
            )
            return list(instance.exposed_methods.values())

        return list(instance.methods.values())

    @native("getSuperclass", "()Ljava/lang/Class;")
    def getSuperclass(self, instance: AbstractJavaClass):
        if isinstance(instance, NativeClass):
            logger.println(
                f"[WARN] from NativeImplementation: NativeImplementation.getSuperClass on {instance} is unsafe"
            )

        # If parent is None, parent is java/lang/Object, which is listed as None
        return instance.parent() if instance.parent is not None else None

    @native("getName", "()Ljava/lang/String;")
    def getName(self, instance):
        return instance.name
