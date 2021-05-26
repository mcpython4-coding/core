from mcpython.loader.java.Java import native, NativeClass
from mcpython import shared


class Logger(NativeClass):
    NAME = "org/apache/logging/log4j/Logger"


class LogManager(NativeClass):
    NAME = "org/apache/logging/log4j/LogManager"

    @native("getLogger", "(Ljava/lang/Class;)Lorg/apache/logging/log4j/Logger;")
    def getLogger(self, cls):
        return self.vm.get_class("org/apache/logging/log4j/Logger").create_instance()

    @native("getLogger", "(Ljava/lang/String;)Lorg/apache/logging/log4j/Logger;")
    def getLoggerFromString(self, string: str):
        return self.vm.get_class("org/apache/logging/log4j/Logger").create_instance()

