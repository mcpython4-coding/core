from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


class DecimalFormat(NativeClass):
    NAME = "java/text/DecimalFormat"

    @native("<init>", "(Ljava/lang/String;)V")
    def init(self, instance, v: str):
        pass

