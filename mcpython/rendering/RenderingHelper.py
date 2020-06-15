"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import pyglet.gl as _gl
import pyglet.gl.glu as _glu
import collections
import pyglet.graphics


class RenderingHelper:
    """
    class for helping storing an gl status and exchanging it, rolling back, ...
    todo: add setup functions for various systems
    """

    def __init__(self):
        """
        creates an new rendering helper.
        WARNING: multiple instances may work NOT well together as they are based on the same gl backend
        """
        self.status_table = {}
        self.saved = collections.deque()

    def save_status(self, add_to_stack=True):
        """
        will save the current status to later revert back to it
        :param add_to_stack: if the current status should be added to the internal collections.deque for using
            pop_status with these element
        :return: the copy of the status, injectable into apply()
        """
        status = self.status_table.copy()
        if add_to_stack: self.saved.append(status)
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
        if status: self.glEnable(flag)
        else: self.glDisable(flag)

    def apply(self, data=None):
        """
        will apply an status
        :param data: the data to apply or None to use the active one (to make sure everything is set correctly)
        """
        if data is None: data = self.status_table
        for key in data:
            self.set_flag(key, data[key])

