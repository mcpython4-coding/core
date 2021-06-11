from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


class OutputStreamWriter(NativeClass):
    NAME = "java/io/OutputStreamWriter"

    @native("<init>", "(Ljava/io/OutputStream;Ljava/lang/String;)V")
    def init(self, instance, stream, text):
        pass

