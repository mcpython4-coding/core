from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native
import uuid


class UUID(NativeClass):
    NAME = "java/util/UUID"

    @native("fromString", "(Ljava/lang/String;)Ljava/util/UUID;")
    def fromString(self, string):
        return uuid.uuid3("loader", string)

