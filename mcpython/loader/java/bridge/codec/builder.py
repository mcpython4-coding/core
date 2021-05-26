from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


class RecordCodecBuilder(NativeClass):
    NAME = "com/mojang/serialization/codecs/RecordCodecBuilder"

    @native("create", "(Ljava/util/function/Function;)Lcom/mojang/serialization/Codec;")
    def create(self, method):
        pass
