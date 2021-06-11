from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


class FileOutputStream(NativeClass):
    NAME = "java/io/FileOutputStream"

    @native("<init>", "(Ljava/io/File;)V")
    def init(self, *_):
        pass

