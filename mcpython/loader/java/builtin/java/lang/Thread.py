from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native
import threading


class Thread(NativeClass):
    NAME = "java/lang/Thread"

    @native("currentThread", "()Ljava/lang/Thread;", static=True)
    def currentThread(self):
        return threading.currentThread()

    @native("getThreadGroup", "()Ljava/lang/ThreadGroup;")
    def getThreadGroup(self, instance: threading.Thread):
        pass

