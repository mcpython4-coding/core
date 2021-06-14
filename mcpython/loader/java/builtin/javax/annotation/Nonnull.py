from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


class Nonnull(NativeClass):
    NAME = "javax/annotation/Nonnull"

    def on_annotate(self, cls, args):
        pass

