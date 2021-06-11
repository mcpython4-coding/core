from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


class PushbackInputStream(NativeClass):
    NAME = "java/io/PushbackInputStream"

    @native("<init>", "(Ljava/io/InputStream;I)V")
    def init(self, instance, stream, size):
        instance.data = stream.underlying.read()
        instance.size = size
        instance.offset = 0

    @native("read", "([BII)I")
    def read(self, instance, buffer, start, end):
        buffer[:] = instance.data[start+instance.offset:end+instance.offset]
        instance.offset += len(buffer)
        return len(buffer)

