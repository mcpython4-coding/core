"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import pyglet
import ResourceLocator
import config
import math
import logger


FILES = {}


def execute_file_by_name(name, **kwargs):
    if name not in FILES:
        FILES[name] = OpenGLSetupFile.from_name(name)
    try:
        return FILES[name].execute(**kwargs)
    except:
        logger.println("[WARNING] can't parse name '{}'".format(name))
        raise


class OpenGLSetupFile:
    """
    Base class for an OpenGL-parse-able file
    """

    @classmethod
    def from_name(cls, name: str):
        mod = name.split(":")[0] if ":" in name else "minecraft"
        path = "assets/{}/rendering/opengl_setup/{}.gl".format(mod, name.split(":")[-1])
        if not ResourceLocator.exists(path):
            raise IOError("file for '{}' not found!".format(name))
        return cls.from_file(path)

    @classmethod
    def from_file(cls, file: str):
        return cls(ResourceLocator.read(file).decode("UTF-8"))

    def __init__(self, data: str):
        self.data = data.replace("\r", "").split("\n")

    def execute(self, **kwargs):
        for line in self.data:
            if line.startswith("//"): continue
            if line.count(" ") + line.count("   ") == len(line): continue
            if line.startswith("gl") and line[2] != line[2].lower():
                gl_command = line.split("(")[0]
                gl_function = getattr(pyglet.gl, gl_command)
                param_raw = line.split("(")[1].split(")")[0]
                if len(param_raw) > 0:
                    gl_function(*[self._transform_value(e, **kwargs) for e in param_raw.split(", ")])
                else:
                    gl_function()
            elif line.startswith("set"):
                self._set_value(line.split(" ")[1], self._transform_value(line.split("-> ")[1], **kwargs))
            elif line.startswith("subcall"):
                execute_file_by_name(line.split(" ")[1], **kwargs)
            elif line.startswith("glu") and line[3] != line[3].lower():
                glu_command = line.split("(")[0]
                glu_function = getattr(pyglet.gl, glu_command)
                param_raw = line.split("(")[1].split(")")[0]
                if len(param_raw) > 0:
                    glu_function(*[self._transform_value(e, **kwargs) for e in param_raw.split(", ")])
                else:
                    glu_function()
            elif line.startswith("invoke "):
                raw = " ".join(line.split(" ")[1:])
                invoke = raw.split("(")[0]
                if invoke.startswith("pyglet.graphics."):
                    getattr(pyglet.graphics, ".".join(invoke.split(".")[2:]))(
                        *[self._transform_value(e, **kwargs) for e in raw.split("(")[1][:-1].split(", ")])
                else:
                    raise ValueError("can't invoke function '{}'".format(invoke))
            else:
                raise ValueError("can't parse line '{}'".format(line))

    def _transform_value(self, name: str, **kwargs):
        if name.startswith("glEnum "):
            return getattr(pyglet.gl, name.split(" ")[-1])
        elif name.startswith("glParameter "):
            return kwargs[name.split(" ")[-1]]
        elif name.startswith("glFloatTuple "):
            t = name.split(" ")[1:]
            return (pyglet.gl.GLfloat * len(t))(*[float(e) for e in t])
        elif name.startswith("config "):
            return getattr(config, name.split(" ")[1])
        elif name.startswith("sum "):
            raw = " ".join(name.split(" ")[1:])
            return sum([self._transform_value(e[1:-1].replace(" //", " ")) for e in raw.split(" | ")])
        elif name.startswith("neg "):
            raw = " ".join(name.split(" ")[1:])
            return -self._transform_value(raw[1:-1], **kwargs)
        elif name.startswith("div "):
            raw = " ".join(name.split(" ")[1:]).split(" | ")
            return self._transform_value(raw[0][1:-1], **kwargs) / self._transform_value(raw[1][1:-1], **kwargs)
        elif name.startswith("glFloat"):
            return float(name.split(" ")[1])
        elif name.startswith("glInt "):
            return int(name.split(" ")[1])
        elif name.startswith("math_op "):
            _, operation, *raw = name.split(" ")
            return getattr(math, operation)([e[1:-1] for e in raw.split(" | ")])
        else:
            raise ValueError("unsupported value transform '{}'".format(name))

    def _set_value(self, address, value):
        if address.startswith("pyglet"):
            trace = pyglet
        else:
            raise ValueError("unable to locate write-object '{}'".format(address))
        for element in address.split(".")[1:-1]:
            trace = getattr(trace, element)
        setattr(trace, address.split(".")[-1], value)

