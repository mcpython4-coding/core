"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft, representing snapshot 20w51a
(https://www.minecraft.net/en-us/article/minecraft-snapshot-20w51a)

This project is not official by mojang and does not relate to it.
"""
import collections
import math

import pyglet.gl as _gl

from mcpython import shared
import mcpython.client.rendering.MatrixStack
from mcpython.util.annotation import onlyInClient


@onlyInClient()
class RenderingHelper:
    """
    class for helping storing an gl status and exchanging it, rolling back, ...
    todo: add setup functions for various systems

    todo: add checks if this is the rendering process
    """

    def __init__(self):
        """
        creates an new rendering helper.
        WARNING: multiple instances may work NOT well together as they are based on the same gl backend
            -> todo: make shared
        """
        self.status_table = {}
        self.saved = collections.deque()
        self.default_3d_stack = None

    def save_status(self, add_to_stack=True):
        """
        will save the current status to later revert back to it
        :param add_to_stack: if the current status should be added to the internal collections.deque for using
            pop_status with these element
        :return: the copy of the status, injectable into apply()
        """
        status = self.status_table.copy()
        if add_to_stack:
            self.saved.append(status)
        return status

    def pop_status(self):
        """
        Will pop the current status and will revert it to the one before the save_status()-call
        WARNING: when no status found, an exception will be raised
        """
        status = self.saved.pop()
        for key in self.status_table.copy():
            if key in status:
                if self.status_table[key] != status[key]:
                    self.set_flag(key, status[key])
                del status[key]
        for key in status:
            self.set_flag(key, status[key])

    def deleteSavedStates(self):
        self.saved.clear()

    def glEnable(self, flag: int):
        """
        enables an gl flag via glEnable(flag) and will mark it in the status table as True
        :param flag: the flag to set
        """
        _gl.glEnable(flag)
        self.status_table[flag] = True

    def glDisable(self, flag: int):
        """
        disables an gl flag via glDisable(flag) and will mark it in the status table as False
        :param flag: the flag to set
        """
        _gl.glDisable(flag)
        self.status_table[flag] = False

    def set_flag(self, flag: int, status: bool):
        """
        will set the enabled status via an boolean
        :param flag: the gl-enum-int to use
        :param status: the status to set
        """
        if status:
            self.glEnable(flag)
        else:
            self.glDisable(flag)

    def apply(self, data=None):
        """
        will apply an status
        :param data: the data to apply or None to use the active one (to make sure everything is set correctly)
        """
        if data is None:
            data = self.status_table
        for key in data:
            if data[key]:
                _gl.glEnable(key)
            else:
                _gl.glDisable(key)
        return self

    def get_default_3d_matrix_stack(
        self, base=None
    ) -> mcpython.client.rendering.MatrixStack.MatrixStack:
        """
        will create an MatrixStack-instance with the active transformation for the active player
        Will set up perspective for 3d rendering with these stack
        :param base: the MatrixStack-instance to set into
        :return: the MatrixStack instance
        WARNING: all transformations will be applied ON TOP of the base-MatrixStack if its provided
        Use get_dynamic_3d_matrix_stack() where possible & reuse
        """
        if base is None:
            base = mcpython.client.rendering.MatrixStack.MatrixStack()
        width, height = shared.window.get_size()
        self.glEnable(_gl.GL_DEPTH_TEST)
        viewport = shared.window.get_viewport_size()
        base.addViewport(0, 0, max(1, viewport[0]), max(1, viewport[1]))
        base.addMatrixMode(_gl.GL_PROJECTION)
        base.addLoadIdentity()
        base.addGluPerspective(65.0, width / height, 0.1, 60.0)
        base.addMatrixMode(_gl.GL_MODELVIEW)
        base.addLoadIdentity()
        x, y, _ = shared.world.get_active_player().rotation
        base.addRotate3d(x, 0, 1, 0)
        base.addRotate3d(-y, math.cos(math.radians(x)), 0, math.sin(math.radians(x)))
        x, y, z = shared.world.get_active_player().position
        base.addTranslate3d(-x, -y, -z)
        return base

    def get_dynamic_3d_matrix_stack(
        self, base=None
    ) -> mcpython.client.rendering.MatrixStack.LinkedMatrixStack:
        """
        same as get_default_3d_matrix_stack, but the matrix stack is an LinkedMatrixStack with links to player position,
            etc. (so it dynamically updates itself when the player changes the parameters)
        [see above]
        """
        if base is None:
            base = mcpython.client.rendering.MatrixStack.LinkedMatrixStack()
        self.glEnable(_gl.GL_DEPTH_TEST)
        base.addViewport(
            lambda: (
                0,
                0,
                max(1, shared.window.get_viewport_size()[0]),
                max(1, shared.window.get_viewport_size()[1]),
            )
        )
        base.addMatrixMode(_gl.GL_PROJECTION)
        base.addLoadIdentity()
        base.addGluPerspective(
            lambda: (65.0, shared.window.get_size()[0] / shared.window.get_size()[1], 0.1, 60.0)
        )
        base.addMatrixMode(_gl.GL_MODELVIEW)
        base.addLoadIdentity()
        base.addRotate3d(lambda: (shared.world.get_active_player().rotation[0], 0, 1, 0))
        base.addRotate3d(
            lambda: (
                -shared.world.get_active_player().rotation[1],
                math.cos(math.radians(shared.world.get_active_player().rotation[0])),
                0,
                math.sin(math.radians(shared.world.get_active_player().rotation[0])),
            )
        )
        base.addTranslate3d(lambda: [-e for e in shared.world.get_active_player().position])
        return base

    def setup2d(self, anchor=(0, 0), z_buffer=0):
        """
        will setup an 2d environment
        :param anchor: the anchor in the window as an tuple of two floats representing an move as factors to the window size
        :param z_buffer: the layer in which to render
        """
        self.glDisable(_gl.GL_DEPTH_TEST)
        _gl.glViewport(0, 0, *[max(1, e) for e in shared.window.get_viewport_size()])
        _gl.glMatrixMode(_gl.GL_PROJECTION)
        _gl.glLoadIdentity()
        width, height = s = shared.window.get_size()
        _gl.glOrtho(0, max(1, width), 0, max(1, height), -1, 1)
        _gl.glMatrixMode(_gl.GL_MODELVIEW)
        _gl.glLoadIdentity()
        _gl.glTranslated(*[-s[i] * anchor[i] for i in range(2)], -z_buffer)
        self.apply()

    def enableAlpha(self):
        """
        will enable alpha blending
        """
        self.glDisable(_gl.GL_CULL_FACE)
        self.glEnable(_gl.GL_BLEND)
        _gl.glBlendFunc(_gl.GL_SRC_ALPHA, _gl.GL_ONE_MINUS_SRC_ALPHA)

    def disableAlpha(self):
        """
        will disable alpha rendering
        """
        _gl.glBlendFunc(_gl.GL_ONE, _gl.GL_ZERO)
        self.glEnable(_gl.GL_CULL_FACE)
