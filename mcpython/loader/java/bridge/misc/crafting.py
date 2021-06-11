from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


class IRecipeType(NativeClass):
    NAME = "net/minecraft/item/crafting/IRecipeType"

    @native("func_222147_a", "(Ljava/lang/String;)Lnet/minecraft/item/crafting/IRecipeType;")
    def func_222147_a(self, *_):
        return self.create_instance()

