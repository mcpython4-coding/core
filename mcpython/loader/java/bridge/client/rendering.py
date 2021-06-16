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


class RenderType(NativeClass):
    NAME = "net/minecraft/client/renderer/RenderType"

    @native("func_228641_d_", "()Lnet/minecraft/client/renderer/RenderType;")
    def func_228641_d_(self):
        pass

    @native("func_228643_e_", "()Lnet/minecraft/client/renderer/RenderType;")
    def func_228643_e_(self):
        pass

    @native("func_228645_f_", "()Lnet/minecraft/client/renderer/RenderType;")
    def func_228645_f_(self):
        pass


class RenderTypeLookup(NativeClass):
    NAME = "net/minecraft/client/renderer/RenderTypeLookup"

    @native(
        "setRenderLayer",
        "(Lnet/minecraft/block/Block;Lnet/minecraft/client/renderer/RenderType;)V",
    )
    def setRenderLayer(self, block, render_type):
        pass


class ModelProperty(NativeClass):
    NAME = "net/minecraftforge/client/model/data/ModelProperty"

    @native("<init>", "()V")
    def init(self, *_):
        pass

    @native("<init>", "(Ljava/util/function/Predicate;)V")
    def init2(self, *_):
        pass


class ParticleType(NativeClass):
    NAME = "net/minecraft/particles/ParticleType"


class BlockColors(NativeClass):
    NAME = "net/minecraft/client/renderer/color/BlockColors"

    @native("func_186722_a", "(Lnet/minecraft/client/renderer/color/IBlockColor;[Lnet/minecraft/block/Block;)V")
    def func_186722_a(self, instance, color, blocks):
        pass
