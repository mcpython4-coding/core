from mcpython.loader.java.Java import NativeClass, native


class Object(NativeClass):
    NAME = "java/lang/Object"

    @native("<init>", "()V")
    def init(self, instance):
        pass
