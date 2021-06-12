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
import os

from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


class File(NativeClass):
    NAME = "java/io/File"

    @native("<init>", "(Ljava/io/File;Ljava/lang/String;)V")
    def init(self, instance, d, path: str):
        instance.path = d.path + "/" + path.replace("\\", "/")

    @native("getParentFile", "()Ljava/io/File;")
    def getParentFile(self, instance):
        obj = self.create_instance()
        obj.path = "/".join(instance.path.split("/")[:-1])
        return obj

    @native("exists", "()Z")
    def exists(self, instance):
        return os.path.exists(instance.path)

    @native("canRead", "()Z")
    def canRead(self, instance):
        return int(os.path.isfile(instance.path))

    @native("canWrite", "()Z")
    def canWrite(self, instance):
        return self.canRead(instance)

    @native("mkdirs", "()Z")
    def mkdirs(self, instance):
        os.makedirs(instance.path, exist_ok=True)
        return 1

    @native("createNewFile", "()Z")
    def createNewFile(self, instance):
        pass
