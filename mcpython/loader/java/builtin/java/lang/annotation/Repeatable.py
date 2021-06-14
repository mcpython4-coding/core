from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


class Repeatable(NativeClass):
    NAME = "java/lang/annotation/Repeatable"

    def on_annotate(self, cls, args):
        pass

