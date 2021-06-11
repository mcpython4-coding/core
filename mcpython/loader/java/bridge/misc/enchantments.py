from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


class EnchantmentType(NativeClass):
    NAME = "net/minecraft/enchantment/EnchantmentType"

    @native("create", "(Ljava/lang/String;Ljava/util/function/Predicate;)Lnet/minecraft/enchantment/EnchantmentType;")
    def create(self, *_):
        return self.create_instance()

