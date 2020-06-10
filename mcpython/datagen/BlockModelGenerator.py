"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import typing
import mcpython.util.enums


class ModelRepresentation:
    """
    class for representing an model
    """

    def __init__(self, model: str, r_x=0, r_y=0, uvlock=False, weight=1):
        pass

    def wrap(self) -> str:
        pass


class OrBlockStateCondition:
    def __init__(self, *parts):
        pass

    def wrap(self) -> list:
        pass


class SingleFaceConfiguration:
    def __init__(self, face: mcpython.util.enums.EnumSide, texture: str, uv=(0, 0, 1, 1), cullface=None,
                 rotation=0, tintindex=None):
        pass

    def wrap(self) -> str:
        pass


class BlockStateGenerator:
    def __init__(self, name: str):
        pass

    def add_state(self, state: typing.Any[str, dict, list], *models: typing.List[typing.Any[str, ModelRepresentation]]):
        pass


class MultiPartBlockStateGenerator:
    def __init__(self, name: str):
        pass

    def add_state(self, state: typing.Any[str, dict, list, OrBlockStateCondition],
                  *models: typing.List[typing.Any[str, ModelRepresentation]]):
        pass


class ModelDisplay:
    def __init__(self, rotation: tuple = None, translation: tuple = None, scale: tuple = None):
        pass

    def wrap(self) -> dict:
        pass


class BlockModelGenerator:
    def __init__(self, name: str, parent: str = None, ambientocclusion=True):
        pass

    def set_texture_variable(self, name: str, texture: str):
        pass

    def add_element(self, f: tuple, t: tuple, *faces: typing.List[SingleFaceConfiguration], rotation_center=None,
                    rotation_axis=None, rotation_angle=None, rotation_rescale=False, shade=True):
        assert len(faces) == 6, "faces must be 6"

    def set_display_mode(self, key: str, config: ModelDisplay):
        pass

