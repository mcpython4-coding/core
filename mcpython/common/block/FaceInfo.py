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
import itertools
import typing
import weakref

import mcpython.engine.event.EventHandler
import mcpython.util.enums
from mcpython import shared
from mcpython.client.rendering.blocks.ICustomBlockRenderer import (
    ICustomBatchBlockRenderer,
    ICustomBlockRenderer,
)
from mcpython.engine.rendering.RenderingLayerManager import NORMAL_WORLD
from mcpython.util.annotation import onlyInClient
from mcpython.util.enums import EnumSide


@onlyInClient()
class FaceInfo:
    """
    Class for face state of the block
    """

    DEFAULT_FACE_STATE = {x.normal_name: False for x in EnumSide.iterate()}
    DEFAULT_FACE_DATA = {x.normal_name: None for x in EnumSide.iterate()}

    def __init__(self, block):
        """
        Block face state, client-sided container holding information for rendering
        """
        self.block = weakref.proxy(block)
        self.faces: typing.Optional[EnumSide, bool] = self.DEFAULT_FACE_STATE.copy()
        self.face_data: typing.Optional[
            EnumSide, list
        ] = None  # self.DEFAULT_FACE_DATA.copy()
        self.custom_renderer = None  # holds a custom block renderer
        self.subscribed_renderer: bool = False
        self.bound_rendering_info = None

        self.multi_data = None
        self.multi_faces = set()

    def is_shown(self) -> bool:
        return any(self.faces.values())

    def show_face(self, face: EnumSide, force=False):
        """
        Shows a face
        :param face: the face of the block
        :param force: force the show, WARNING: internal only
        """
        if self.faces[face.normal_name] and not force:
            return

        if self.face_data is None:
            self.face_data = copy.deepcopy(self.DEFAULT_FACE_DATA)

        self.faces[face.normal_name] = True

        if self.custom_renderer is not None:
            if not self.subscribed_renderer:
                self.custom_renderer.on_block_exposed(self.block)
                self.subscribed_renderer = True

            if isinstance(
                self.custom_renderer,
                ICustomBatchBlockRenderer,
            ):
                self.face_data[face.normal_name] = self.custom_renderer.add(
                    self.block.position,
                    self.block,
                    face,
                    shared.world.get_dimension_by_name(self.block.dimension).batches,
                )

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

    def show_faces(self, faces: typing.List[str]):
        """
        Optimised show_face() for more than one face
        Will do only something optimal when more than one face is passed in
        """
        for face in faces[:]:
            if self.faces[face]:
                faces.remove(face)
            else:
                self.faces[face] = True

        if not faces:
            return

        if len(faces) == 1:
            # print("short-circuiting show face for face", EnumSide[faces[0].upper()], "@", self.block.position)
            self.show_face(EnumSide[faces[0].upper()], force=True)
            return

        if self.face_data is None:
            self.face_data = copy.deepcopy(self.DEFAULT_FACE_DATA)

        if self.multi_data:
            self.hide_multi_data()
            faces += self.multi_faces

        if self.custom_renderer is not None:
            if not self.subscribed_renderer:
                self.custom_renderer.on_block_exposed(self.block)
                self.subscribed_renderer = True

            if isinstance(
                self.custom_renderer,
                ICustomBatchBlockRenderer,
            ):
                self.multi_data = self.custom_renderer.add_multi(
                    self.block.position,
                    self.block,
                    faces,
                    shared.world.get_dimension_by_name(self.block.dimension).batches,
                )
                self.multi_faces.update(faces)

        else:
            self.multi_data = shared.model_handler.add_faces_to_batch(
                self.block,
                [EnumSide[face.upper()] for face in faces],
                shared.world.get_dimension_by_name(self.block.dimension).batches,
            )

    def hide_multi_data(self):
        if self.custom_renderer is not None and isinstance(
            self.custom_renderer,
            ICustomBatchBlockRenderer,
        ):
            self.custom_renderer.remove_multi(
                self.block.position, self.block, self.multi_data
            )
        else:
            [e.delete() for e in self.multi_data]

        self.multi_data = None

    def hide_face(self, face: EnumSide):
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
            if self.subscribed_renderer and not any(self.faces.values()):
                self.custom_renderer.on_block_fully_hidden(self.block)
                self.subscribed_renderer = False

        if face in self.multi_faces:
            self.hide_multi_data()

            self.multi_faces.remove(face)

            if self.multi_faces:
                self.show_faces(list(self.multi_faces))

        else:
            if self.custom_renderer is not None:
                if isinstance(
                    self.custom_renderer,
                    ICustomBatchBlockRenderer,
                ):
                    self.custom_renderer.remove(
                        self.block.position,
                        self.block,
                        self.face_data[face.normal_name],
                        face,
                    )
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

        self.show_faces(
            [
                (key if isinstance(key, str) else key.normal_name)
                for key, value in state.items()
                if value
            ]
        )

    def hide_all(self):
        """
        Will hide all faces
        """
        if (
            any(self.faces.values())
            and self.custom_renderer is not None
            and self.subscribed_renderer
        ):
            self.custom_renderer.on_block_fully_hidden(self.block)
            self.subscribed_renderer = False

        if self.multi_data:
            self.hide_multi_data()
            self.faces.update({key: False for key in self.multi_faces})
            self.multi_faces.clear()

        if self.custom_renderer:
            [
                self.hide_face(face)
                for face in EnumSide.iterate()
                if self.faces[face.normal_name]
            ]

        # Only when it is shown we need to hide something...
        elif self.face_data:
            for element in itertools.chain.from_iterable(
                e for e in self.face_data.values() if e is not None
            ):
                element.delete()

            for face in EnumSide.iterate():
                self.faces[face.normal_name] = False

            self.face_data = None
