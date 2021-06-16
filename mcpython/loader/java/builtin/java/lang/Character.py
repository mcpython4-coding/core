from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


class Character(NativeClass):
    NAME = "java/lang/Character"

    @native("isLetterOrDigit", "(C)Z", static=True)
    def isLetterOrDigit(self, char: str):
        return char.isdigit() or char.isascii()

