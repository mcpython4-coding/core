from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


class FileInputStream(NativeClass):
    NAME = "java/io/FileInputStream"

    @native("<init>", "(Ljava/io/File;)V")
    def init(self, instance, file):
        instance.underlying = open(file.path, mode="rb")

