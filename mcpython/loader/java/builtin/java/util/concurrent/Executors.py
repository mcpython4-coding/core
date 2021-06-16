from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


class Executors(NativeClass):
    NAME = "java/util/concurrent/Executors"

    @native("newCachedThreadPool", "(Ljava/util/concurrent/ThreadFactory;)Ljava/util/concurrent/ExecutorService;")
    def newCachedThreadPool(self, factory):
        pass

