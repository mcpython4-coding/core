from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


class BufferedWriter(NativeClass):
    NAME = "java/io/BufferedWriter"

    @native("<init>", "(Ljava/io/Writer;)V")
    def init(self, instance, writer):
        pass

