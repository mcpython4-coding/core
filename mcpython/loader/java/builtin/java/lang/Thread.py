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
import threading

from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


class Thread(NativeClass):
    NAME = "java/lang/Thread"

    @native("currentThread", "()Ljava/lang/Thread;", static=True)
    def currentThread(self):
        return threading.currentThread()

    @native("getThreadGroup", "()Ljava/lang/ThreadGroup;")
    def getThreadGroup(self, instance: threading.Thread):
        pass
