from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


class File(NativeClass):
    NAME = "java/io/File"

    @native("<init>", "(Ljava/io/File;Ljava/lang/String;)V")
    def init(self, *_):
        pass

