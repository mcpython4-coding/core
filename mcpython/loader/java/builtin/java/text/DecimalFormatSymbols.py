from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


class DecimalFormatSymbols(NativeClass):
    NAME = "java/text/DecimalFormatSymbols"

    @native("<init>", "()V")
    def init(self, instance):
        pass

    @native("setDecimalSeparator", "(C)V")
    def setDecimalSeparator(self, instance, separator: int):
        pass

