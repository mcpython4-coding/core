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


class CoreLogger(NativeClass):
    NAME = "org/apache/logging/log4j/core/Logger"

    def create_instance(self):
        instance = super().create_instance()
        instance.level = self.vm.get_class(
            "org/apache/logging/log4j/Level", version=self.internal_version
        ).get_static_attribute("OFF")
        return instance

    @native("getLevel", "()Lorg/apache/logging/log4j/Level;")
    def getLevel(self, instance):
        return instance.level

    @native("setLevel", "(Lorg/apache/logging/log4j/Level;)V")
    def setLevel(self, instance, level):
        instance.level = level


class LoggingLevel(NativeClass):
    NAME = "org/apache/logging/log4j/Level"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update({"OFF": "level:off"})


class Logger(CoreLogger):
    NAME = "org/apache/logging/log4j/Logger"


class LogManager(NativeClass):
    NAME = "org/apache/logging/log4j/LogManager"

    @native("getLogger", "(Ljava/lang/Class;)Lorg/apache/logging/log4j/Logger;")
    def getLogger(self, cls):
        return self.vm.get_class(
            "org/apache/logging/log4j/Logger", version=self.internal_version
        ).create_instance()

    @native("getLogger", "()Lorg/apache/logging/log4j/Logger;")
    def getLogger2(self):
        return self.vm.get_class(
            "org/apache/logging/log4j/Logger", version=self.internal_version
        ).create_instance()

    @native("getLogger", "(Ljava/lang/String;)Lorg/apache/logging/log4j/Logger;")
    def getLoggerFromString(self, string: str):
        return self.vm.get_class(
            "org/apache/logging/log4j/Logger", version=self.internal_version
        ).create_instance()
