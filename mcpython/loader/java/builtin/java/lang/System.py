from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


class System(NativeClass):
    NAME = "java/lang/System"

    @native("getProperty", "(Ljava/lang/String;)Ljava/lang/String;")
    def getProperty(self, *_):
        pass

