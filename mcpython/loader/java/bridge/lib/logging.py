from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


class CoreLogger(NativeClass):
    NAME = "org/apache/logging/log4j/core/Logger"

    def create_instance(self):
        instance = super().create_instance()
        instance.level = self.vm.get_class(
            "org/apache/logging/log4j/Level"
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
        return self.vm.get_class("org/apache/logging/log4j/Logger").create_instance()

    @native("getLogger", "(Ljava/lang/String;)Lorg/apache/logging/log4j/Logger;")
    def getLoggerFromString(self, string: str):
        return self.vm.get_class("org/apache/logging/log4j/Logger").create_instance()
