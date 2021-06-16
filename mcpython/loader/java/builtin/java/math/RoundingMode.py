from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


class RoundingMode(NativeClass):
    NAME = "java/math/RoundingMode"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update({
            "DOWN": 0,
        })

