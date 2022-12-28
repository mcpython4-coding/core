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
import pyglet.gl as _gl
from pyglet.math import Mat4
from pyglet.math import Vec3

from mcpython.util.annotation import onlyInClient


@onlyInClient()
class MatrixStack:
    """
    Class handling an configuration of transformations for applying
    todo: optimise
    todo: use pyglet.matrix instead [pyglet 2 needed]
    """

    def __init__(self):
        self.operation_stack = []  # operator stack for which stuff to apply
        self.template_stack = []  # you can store an state and reset to it when needed

    def addTranslate3d(self, dx: float, dy: float, dz: float) -> int:
        """
        will add an glTranslated()-call
        :return: the operation id
        """
        self.operation_stack.append((0, dx, dy, dz))
        return len(self.operation_stack) - 1

    def addRotate3d(self, v: float, rx: float, ry: float, rz: float) -> int:
        """
        will add an glRotated()-call
        :return: the operation id
        """
        self.operation_stack.append((1, v, rx, ry, rz))
        return len(self.operation_stack) - 1

    def addScale3d(self, sx: float, sy: float, sz: float) -> int:
        """
        will add an glScaled()-call
        :return: the operation id
        """
        self.operation_stack.append((2, sx, sy, sz))
        return len(self.operation_stack) - 1

    def addViewport(self, *args):
        self.operation_stack.append((3,) + args)
        return len(self.operation_stack) - 1

    def addMatrixMode(self, mode):
        self.operation_stack.append((4, mode))
        return len(self.operation_stack) - 1

    def addLoadIdentity(self):
        self.operation_stack.append((5,))

    def addGluPerspective(self, *args):
        self.operation_stack.append((6,) + args)
        return len(self.operation_stack) - 1

    def modifyOperation(self, operation_id: int, *data):
        """
        will modify data from an operation on the stack
        :param operation_id: the id of the operation
        :param data: the data to use
        """
        self.operation_stack[operation_id] = (
            self.operation_stack[operation_id][0],
        ) + data

    def copy(self, include_template_stack=True):
        """
        will copy the MatrixStack object
        :param include_template_stack: if the template stack should be copied or not
        :return: the copied one
        """
        obj = MatrixStack()
        obj.operation_stack = self.operation_stack.copy()
        if include_template_stack:
            obj.template_stack = self.template_stack.copy()
        return obj

    def store(self):
        """
        will store the current status in the template stack
        """
        self.template_stack.append(self.copy())

    def pop(self):
        """
        will restore the latest stored status and remove it from the template stack
        """
        self.operation_stack = self.template_stack.pop(0).operation_stack.copy()

    def get_matrix(self) -> Mat4:
        matrix = Mat4()

        for opcode, *d in self.operation_stack:
            if opcode == 0:  # translate
                matrix @= Mat4.from_translation(d)
            elif opcode == 1:
                matrix @= Mat4.from_rotation(d[0], d[1:])
            elif opcode == 2:
                matrix @= Mat4.from_scale(d)
            elif opcode == 3:
                pass  # todo: what to do here?
            elif opcode == 4:
                pass  # todo: what to do here?
            elif opcode == 5:
                matrix = Mat4()
            elif opcode == 6:
                matrix @= Mat4.perspective_projection(*d[0])

        return matrix

    def apply(self):
        raise RuntimeError("pyglet 2.0 does NOT support this anymore, use get_matrix() instead")
        # _gl.glLoadIdentity()
        # for opcode, *d in self.operation_stack:
        #     if opcode == 0:
        #         _gl.glTranslated(*d)
        #     elif opcode == 1:
        #         _gl.glRotated(*d)
        #     elif opcode == 2:
        #         _gl.glScaled(*d)
        #     elif opcode == 3:
        #         _gl.glViewport(*d[0])
        #     elif opcode == 4:
        #         _gl.glMatrixMode(d[0])
        #     elif opcode == 5:
        #         _gl.glLoadIdentity()
        #     elif opcode == 6:
        #         _gl.gluPerspective(*d[0])


@onlyInClient()
class LinkedMatrixStack(MatrixStack):
    """
    Matrix stack for dynamically generated values
    """

    def addTranslate3d(self, *args) -> int:
        self.operation_stack.append((0,) + args)
        return len(self.operation_stack) - 1

    def addRotate3d(self, *args) -> int:
        assert len(args) == 1 or len(args) == 3
        self.operation_stack.append((1,) + args)
        return len(self.operation_stack) - 1

    def addScale3d(self, *args) -> int:
        self.operation_stack.append((2,) + args)
        return len(self.operation_stack) - 1

    def get_matrix(self) -> Mat4:
        matrix = Mat4()

        for opcode, *d in self.operation_stack:
            if opcode == 0:  # translate
                matrix @= Mat4.from_translation((
                    [e if not callable(e) else e() for e in d]
                    if not callable(d[0]) or len(d) != 1
                    else d[0]()
                ))
            elif opcode == 1:
                d = (
                    [e if not callable(e) else e() for e in d]
                    if not callable(d[0]) or len(d) != 1
                    else d[0]()
                )
                matrix @= Mat4.from_rotation(d[0], d[1:])
            elif opcode == 2:
                matrix @= Mat4.from_scale(Vec3(*[e if not callable(e) else e() for e in d]))
            elif opcode == 3:
                pass  # todo: what to do here?
            elif opcode == 4:
                pass  # todo: what to do here?
            elif opcode == 5:
                matrix = Mat4()
            elif opcode == 6:
                matrix @= Mat4.perspective_projection(*(
                    [e if not callable(e) else e() for e in d]
                    if not callable(d[0]) or len(d) != 1
                    else d[0]()
                ))

        return matrix

    def apply(self):
        raise RuntimeError("pyglet 2.0 does NOT support this anymore, use get_matrix() instead")
        # _gl.glLoadIdentity()
        # for opcode, *d in self.operation_stack:
        #     if opcode == 0:
        #         _gl.glTranslated(
        #             *(
        #                 [e if not callable(e) else e() for e in d]
        #                 if not callable(d[0]) or len(d) != 1
        #                 else d[0]()
        #             )
        #         )
        #
        #     elif opcode == 1:
        #         _gl.glRotated(
        #             *(
        #                 [e if not callable(e) else e() for e in d]
        #                 if not callable(d[0]) or len(d) != 1
        #                 else d[0]()
        #             )
        #         )
        #
        #     elif opcode == 2:
        #         _gl.glScaled(*[e if not callable(e) else e() for e in d])
        #
        #     elif opcode == 3:
        #         _gl.glViewport(
        #             *(
        #                 [e if not callable(e) else e() for e in d]
        #                 if not callable(d[0]) or len(d) != 1
        #                 else d[0]()
        #             )
        #         )
        #
        #     elif opcode == 4:
        #         _gl.glMatrixMode(d[0] if not callable(d[0]) else d[0]())
        #
        #     elif opcode == 5:
        #         _gl.glLoadIdentity()
        #
        #     elif opcode == 6:
        #         _gl.gluPerspective(
        #             *(
        #                 [e if not callable(e) else e() for e in d]
        #                 if not callable(d[0]) or len(d) != 1
        #                 else d[0]()
        #             )
        #         )
