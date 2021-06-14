from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


class Inherited(NativeClass):
    NAME = "java/lang/annotation/Inherited"

    def on_annotate(self, cls, args):
        pass

