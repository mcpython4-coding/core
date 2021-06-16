from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


class DecimalFormat(NativeClass):
    NAME = "java/text/DecimalFormat"

    @native("<init>", "(Ljava/lang/String;)V")
    def init(self, instance, v: str):
        pass

    @native("setDecimalFormatSymbols", "(Ljava/text/DecimalFormatSymbols;)V")
    def setDecimalFormatSymbols(self, instance, symbols):
        pass

    @native("setRoundingMode", "(Ljava/math/RoundingMode;)V")
    def setRoundingMode(self, instance, mode):
        pass

