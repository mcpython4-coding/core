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
from mcpython import shared
from mcpython.engine import logger
from mcpython.mixin.PyBytecodeManipulator import FunctionPatcher


def applyPillowPatches():
    try:
        import PIL.Image
    except (ImportError, ModuleNotFoundError):
        logger.println(
            "[MIXIN][INFO] failed to apply mixin to default resize() value of PIL.Image.Image.resize(), PIL not found!"
        )
        return

    logger.println(
        "[MIXIN][INFO] applying mixin to default resize() value of PIL.Image.Image.resize()..."
    )
    method = FunctionPatcher(PIL.Image.Image.resize)

    # Security checks so mixin does only apply where it should
    assert method.code_string[26] == 116
    assert method.code_string[27] == 2

    method.code_string[27] = 1  # LOAD_GLOBAL BICUBIC -> NEAREST
    method.applyPatches()


def patchAsyncSystem():
    import asyncio.proactor_events

    method = FunctionPatcher(asyncio.proactor_events.BaseProactorEventLoop.close)


def removeLaunchWrapperPyVersionCheck():
    """
    Util method to be invoked by the launcher to disable the python version checker on launch.
    This is needed as the launcher may decide to use a newer python version than we have support for.
    """

    logger.println("[MIXIN][INFO] applying mixin to python version checker")
    import mcpython.LaunchWrapper

    method = FunctionPatcher(mcpython.LaunchWrapper.LaunchWrapper.check_py_version)

    method.code_string[0] = 100  # LOAD_CONST
    method.code_string[1] = 0  # None
    method.code_string[2] = 83  # return value
    method.code_string[3] = 0

    method.applyPatches()


patchAsyncSystem()


if shared.IS_CLIENT:

    def replacement_update_draw_list(self):
        import pyglet

        def visit(group):
            draw_list = []

            if group not in self.group_map:
                self._add_group(group)

            # Draw domains using this group
            domain_map = self.group_map[group]
            for (formats, mode, indexed), domain in list(domain_map.items()):
                # Remove unused domains from batch
                if domain._is_empty():
                    del domain_map[(formats, mode, indexed)]
                    continue
                draw_list.append((lambda d, m: lambda: d.draw(m))(domain, mode))

            # Sort and visit child groups of this group
            children = self.group_children.get(group)
            if children:
                children.sort()
                for child in list(children):
                    if child.visible:
                        draw_list.extend(visit(child))

            if children or domain_map:
                return [group.set_state] + draw_list + [group.unset_state]
            else:
                # Remove unused group from batch
                del self.group_map[group]
                group._assigned_batches.remove(self)
                if group.parent:
                    self.group_children[group.parent].remove(group)
                try:
                    del self.group_children[group]
                except KeyError:
                    pass
                try:
                    self.top_groups.remove(group)
                except ValueError:
                    pass

                return []

        self._draw_list = []

        self.top_groups.sort()
        for group in list(self.top_groups):
            if group.visible:
                self._draw_list.extend(visit(group))

        self._draw_list_dirty = False

        if pyglet.graphics._debug_graphics_batch:
            self._dump_draw_list()

    def patchPygletRendering():
        logger.println("[MIXIN][PYGLET] applying pyglet mixins")
        import pyglet

        method = FunctionPatcher(pyglet.graphics.Batch._update_draw_list)

        method.overrideFrom(FunctionPatcher(replacement_update_draw_list))
        method.applyPatches()

    applyPillowPatches()
    patchPygletRendering()
