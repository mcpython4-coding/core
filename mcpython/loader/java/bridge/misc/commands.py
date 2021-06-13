"""
mcpython - a minecraft clone written in python licenced under the MIT-licence 
(https://github.com/mcpython4-coding/core)

Contributors: uuk, xkcdjerry (inactive)

Based on the game of fogleman (https://github.com/fogleman/Minecraft), licenced under the MIT-licence
Original game "minecraft" by Mojang Studios (www.minecraft.net), licenced under the EULA
(https://account.mojang.com/documents/minecraft_eula)
Mod loader inspired by "Minecraft Forge" (https://github.com/MinecraftForge/MinecraftForge) and similar

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


class Commands(NativeClass):
    NAME = "net/minecraft/command/Commands"

    @native(
        "func_197057_a",
        "(Ljava/lang/String;)Lcom/mojang/brigadier/builder/LiteralArgumentBuilder;",
    )
    def func_197057_a(self, v: str):
        pass

    @native(
        "func_197056_a",
        "(Ljava/lang/String;Lcom/mojang/brigadier/arguments/ArgumentType;)Lcom/mojang/brigadier/builder/RequiredArgumentBuilder;",
    )
    def func_197056_a(self, v: str, argument_type):
        return self.vm.get_class(
            "com/mojang/brigadier/builder/RequiredArgumentBuilder",
            version=self.internal_version,
        ).create_instance()


class RequiredArgumentBuilder(NativeClass):
    NAME = "com/mojang/brigadier/builder/RequiredArgumentBuilder"

    @native(
        "executes",
        "(Lcom/mojang/brigadier/Command;)Lcom/mojang/brigadier/builder/ArgumentBuilder;",
    )
    def executes(self, instance, command):
        return instance

    @native(
        "then",
        "(Lcom/mojang/brigadier/builder/ArgumentBuilder;)Lcom/mojang/brigadier/builder/ArgumentBuilder;",
    )
    def then(self, instance, other):
        return instance


class LiteralArgumentBuilder(NativeClass):
    NAME = "com/mojang/brigadier/builder/LiteralArgumentBuilder"

    @native(
        "then",
        "(Lcom/mojang/brigadier/builder/ArgumentBuilder;)Lcom/mojang/brigadier/builder/ArgumentBuilder;",
    )
    def then(self, instance, builder):
        return instance

    @native(
        "requires",
        "(Ljava/util/function/Predicate;)Lcom/mojang/brigadier/builder/ArgumentBuilder;",
    )
    def requires(self, instance, predicate):
        return instance


class StringArgumentType(NativeClass):
    NAME = "com/mojang/brigadier/arguments/StringArgumentType"

    @native("greedyString", "()Lcom/mojang/brigadier/arguments/StringArgumentType;")
    def greedyString(self):
        return self.create_instance()

    @native("string", "()Lcom/mojang/brigadier/arguments/StringArgumentType;")
    def string(self, *_):
        pass


class EntityArgument(NativeClass):
    NAME = "net/minecraft/command/arguments/EntityArgument"

    @native("func_197094_d", "()Lnet/minecraft/command/arguments/EntityArgument;")
    def func_197094_d(self):
        return self.create_instance()


class ArgumentSerializer(NativeClass):
    NAME = "net/minecraft/command/arguments/ArgumentSerializer"

    @native("<init>", "(Ljava/util/function/Supplier;)V")
    def init(self, instance, supplier):
        pass
