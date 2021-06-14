from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


class Color(NativeClass):
    NAME = "java/awt/Color"

    def __init__(self):
        super().__init__()
        self.exposed_attributes.update({
            "white": (255, 255, 255),
        })

