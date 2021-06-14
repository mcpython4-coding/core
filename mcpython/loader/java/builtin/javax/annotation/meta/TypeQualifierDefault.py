from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


class TypeQualifierDefault(NativeClass):
    NAME = "javax/annotation/meta/TypeQualifierDefault"

    def on_annotate(self, cls, args):
        pass

