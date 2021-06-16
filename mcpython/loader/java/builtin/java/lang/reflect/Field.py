from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


class Field(NativeClass):
    NAME = "java/lang/reflect/Field"

    @native("getAnnotation", "(Ljava/lang/Class;)Ljava/lang/annotation/Annotation;")
    def getAnnotation(self, instance, cls):
        pass

