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
import copy
import typing

import mcpython.client.rendering.blocks.ICustomBlockRenderer
import mcpython.engine.event.EventHandler
import mcpython.util.enums
from mcpython import shared
from mcpython.engine.rendering.RenderingLayerManager import NORMAL_WORLD


class FaceInfo:
    """
    Class for face state of the block
    todo: merge data into AbstractBlock & make this a static class
    """

    DEFAULT_FACE_STATE = {
        x.normal_name: False for x in mcpython.util.enums.EnumSide.iterate()
    }
    DEFAULT_FACE_DATA = {
        x.normal_name: [] for x in mcpython.util.enums.EnumSide.iterate()
    }

    def __init__(self, block):
        """
        Block face state
        """
        self.block = block
        self.faces: typing.Optional[
            mcpython.util.enums.EnumSide, bool
        ] = self.DEFAULT_FACE_STATE.copy()
        self.face_data: typing.Optional[
            mcpython.util.enums.EnumSide, list
        ] = None  # self.DEFAULT_FACE_DATA.copy()
        self.custom_renderer = None  # holds a custom block renderer
        self.subscribed_renderer: bool = False

    def is_shown(self) -> bool:
        return any(self.faces.values())

    def show_face(self, face: mcpython.util.enums.EnumSide):
        """
        Shows an face
        :param face: the face of the block
        """
        if self.faces[face.normal_name]:
            return

        if self.face_data is None:
            self.face_data = copy.deepcopy(self.DEFAULT_FACE_DATA)

        self.faces[face.normal_name] = True

        if self.custom_renderer is not None:
            if issubclass(
                type(self.custom_renderer),
                mcpython.client.rendering.blocks.ICustomBlockRenderer.ICustomBatchBlockRenderer,
            ):
                self.face_data[face.normal_name] = self.custom_renderer.add(
                    self.block.position,
                    self.block,
                    face,
                    shared.world.get_dimension_by_name(self.block.dimension).batches,
                )
            elif issubclass(
                type(self.custom_renderer),
                mcpython.client.rendering.blocks.ICustomBlockRenderer.ICustomDrawMethodRenderer,
            ):
                if not self.subscribed_renderer:
                    mcpython.engine.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
                        NORMAL_WORLD.getRenderingEvent(), self._draw_custom_render
                    )
                    self.subscribed_renderer = True

        else:
            if self.face_data[face.normal_name] is None:
                self.face_data[face.normal_name] = []

            self.face_data[face.normal_name].extend(
                shared.model_handler.add_face_to_batch(
                    self.block,
                    face,
                    shared.world.get_dimension_by_name(self.block.dimension).batches,
                )
            )

    def hide_face(self, face: mcpython.util.enums.EnumSide):
        """
        Will hide an face
        :param face: the face to hide
        """
        if not self.faces[face.normal_name]:
            return

        self.faces[face.normal_name] = False

        if self.face_data is None:
            return

        if self.custom_renderer is not None:
            if issubclass(
                type(self.custom_renderer),
                mcpython.client.rendering.blocks.ICustomBlockRenderer.ICustomBatchBlockRenderer,
            ):
                self.custom_renderer.remove(
                    self.block.position,
                    self.block,
                    self.face_data[face.normal_name],
                    face,
                )
            elif issubclass(
                type(self.custom_renderer),
                mcpython.client.rendering.blocks.ICustomBlockRenderer.ICustomDrawMethodRenderer,
            ):
                if self.subscribed_renderer and not any(self.faces.values()):
                    mcpython.engine.event.EventHandler.PUBLIC_EVENT_BUS.unsubscribe(
                        NORMAL_WORLD.getRenderingEvent(), self._draw_custom_render
                    )
                    self.subscribed_renderer = False
        else:
            for x in self.face_data[face.normal_name]:
                try:
                    x.delete()
                except AssertionError:
                    pass

        self.face_data[face.normal_name] = None
        if all(value is None or len(value) == 0 for value in self.face_data.values()):
            self.face_data = None

    def _draw_custom_render(self):
        """
        Will inherit the custom renderer
        """
        if not self.subscribed_renderer:
            mcpython.engine.event.EventHandler.PUBLIC_EVENT_BUS.unsubscribe(
                NORMAL_WORLD.getRenderingEvent(), self._draw_custom_render
            )
            return
        self.custom_renderer.draw(self.block.position, self.block)

    def update(self, redraw_complete=True):
        """
        Updates the block face state
        :param redraw_complete: if all sides should be re-drawn
        """

        dimension = shared.world.get_dimension_by_name(self.block.dimension)
        chunk = dimension.get_chunk_for_position(self.block.position)
        state = chunk.exposed_faces(self.block.position)

        if state == self.faces and not redraw_complete:
            return

        chunk.mark_position_dirty(self.block.position)

        self.hide_all()

        for key in state.keys():
            if state[key]:
                face = (
                    key
                    if not isinstance(key, str)
                    else mcpython.util.enums.EnumSide[key.upper()]
                )
                self.show_face(face)

    def hide_all(self):
        """
        Will hide all faces
        todo: can we optimize it
        """
        if (
            any(self.faces.values())
            and issubclass(
                type(self.custom_renderer),
                mcpython.client.rendering.blocks.ICustomBlockRenderer.ICustomDrawMethodRenderer,
            )
            and self.subscribed_renderer
        ):
            mcpython.engine.event.EventHandler.PUBLIC_EVENT_BUS.unsubscribe(
                NORMAL_WORLD.getRenderingEvent(), self._draw_custom_render
            )
            self.subscribed_renderer = False

        [self.hide_face(face) for face in mcpython.util.enums.EnumSide.iterate()]
