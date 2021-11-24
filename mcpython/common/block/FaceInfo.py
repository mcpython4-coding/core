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
import weakref

import mcpython.engine.event.EventHandler
import mcpython.util.enums
from mcpython import shared
from mcpython.client.rendering.blocks.ICustomBlockRenderer import (
    ICustomBatchBlockRenderer,
    ICustomBlockRenderer,
)
from mcpython.engine import logger
from mcpython.engine.rendering.RenderingLayerManager import NORMAL_WORLD
from mcpython.util.annotation import onlyInClient


@onlyInClient()
class FaceInfo:
    """
    Class for face state of the block
    """

    __slots__ = [
        "block",
        "faces",
        "custom_renderer",
        "subscribed_renderer",
        "bound_rendering_info",
        "multi_data",
    ]

    def __init__(self, block):
        """
        Block face state, client-sided container holding information for rendering
        """
        # A reference to the super block
        self.block = weakref.proxy(block)

        # Holds which faces are visible
        self.faces = 0

        # holds a custom block renderer
        self.custom_renderer: ICustomBlockRenderer | None = None

        # If the custom_renderer was bound to a rendering event or not
        self.subscribed_renderer: bool = False
        self.bound_rendering_info = None

        # The data from the normal add_to_batch() calls, should be a list of VertexList's
        self.multi_data = None

    def is_shown(self) -> bool:
        return bool(self.faces)

    def show_faces(self, faces: int):
        """
        Shows the faces indicating by the bit flag (See EnumSide.bitflag)
        """
        if not faces:
            return

        if self.faces:
            self.hide_all()

        if not isinstance(faces, int):
            raise ValueError(faces)

        # Remove faces in both lists
        self.faces |= faces

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

        else:
            self.multi_data = shared.model_handler.add_faces_to_batch(
                self.block,
                self.faces,
                shared.world.get_dimension_by_name(self.block.dimension).batches,
            )

    def _hide_data(self):
        if self.custom_renderer is not None and isinstance(
            self.custom_renderer,
            ICustomBatchBlockRenderer,
        ):
            self.custom_renderer.remove_multi(
                self.block.position, self.block, self.multi_data
            )

        elif self.multi_data:
            try:
                for e in self.multi_data:
                    e.delete()
            except AssertionError:
                # todo: what is the cause of this exception?
                # logger.println(f"De-allocation error @{self.block}")
                pass

        self.multi_data = None

    def hide_faces(self, faces: int):
        """
        Will hide the faces indicated by the face
        :param faces: the faces to hide

        Will hide all faces and re-render the still visible ones
        """
        if not self.faces & faces:
            return

        faces = faces & self.faces
        self.faces ^= faces

        if self.custom_renderer is not None:
            if self.subscribed_renderer and not self.faces:
                self.custom_renderer.on_block_fully_hidden(self.block)
                self.subscribed_renderer = False

        self._hide_data()

        self.faces ^= faces & self.faces

        if self.faces:
            self.show_faces(self.faces)

    def _draw_custom_render(self):
        """
        Will inherit the custom renderer
        """
        # todo: remove this for performance reasons
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
        state = chunk.exposed_faces_flag(self.block)

        if state == self.faces and not redraw_complete:
            return

        chunk.mark_position_dirty(self.block.position)
        self.hide_all()
        self.show_faces(state)

    def hide_all(self):
        """
        Will hide all faces
        """
        if self.faces and self.custom_renderer is not None and self.subscribed_renderer:
            self.custom_renderer.on_block_fully_hidden(self.block)
            self.subscribed_renderer = False

        self.hide_faces(self.faces)
        self.faces = 0
