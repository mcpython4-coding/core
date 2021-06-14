from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


class CheckForNull(NativeClass):
    NAME = "javax/annotation/CheckForNull"

    def on_annotate(self, cls, args):
        pass

