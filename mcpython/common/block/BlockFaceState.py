"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import mcpython.common.event.EventHandler
from mcpython import globals as G
import mcpython.client.rendering.ICustomBlockRenderer
import mcpython.util.enums


class BlockFaceState:
    """
    class for face state of the block
    """

    def __init__(self, block):
        """
        block face state
        """
        self.block = block
        self.faces = {x: False for x in mcpython.util.enums.EnumSide.iterate()}
        self.face_data = {x: [] for x in mcpython.util.enums.EnumSide.iterate()}
        self.custom_renderer = None  # holds an custom block renderer
        self.subscribed_renderer: bool = False

    def show_face(self, face: mcpython.util.enums.EnumSide):
        """
        shows an face
        :param face: the face of the block
        """
        if self.faces[face]:
            return
        self.faces[face] = True
        if self.custom_renderer is not None:
            if issubclass(
                type(self.custom_renderer),
                mcpython.client.rendering.ICustomBlockRenderer.ICustomBatchBlockRenderer,
            ):
                self.face_data[face] = self.custom_renderer.add(
                    self.block.position, self.block, face
                )
            elif issubclass(
                type(self.custom_renderer),
                mcpython.client.rendering.ICustomBlockRenderer.ICustomDrawMethodRenderer,
            ):
                if not self.subscribed_renderer:
                    mcpython.common.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
                        "render:draw:3d", self._draw_custom_render
                    )
                    self.subscribed_renderer = True
        else:
            self.face_data[face].extend(
                G.modelhandler.add_face_to_batch(
                    self.block, face, G.world.get_active_dimension().batches
                )
            )

    def hide_face(self, face: mcpython.util.enums.EnumSide):
        """
        will hide an face
        :param face: the face to hide
        """
        if not self.faces[face]:
            return
        self.faces[face] = False
        if self.custom_renderer is not None:
            if issubclass(
                type(self.custom_renderer),
                mcpython.client.rendering.ICustomBlockRenderer.ICustomBatchBlockRenderer,
            ):
                self.custom_renderer.remove(
                    self.block.position, self.block, self.face_data[face], face
                )
            elif issubclass(
                type(self.custom_renderer),
                mcpython.client.rendering.ICustomBlockRenderer.ICustomDrawMethodRenderer,
            ):
                if self.subscribed_renderer and not any(self.faces.values()):
                    mcpython.common.event.EventHandler.PUBLIC_EVENT_BUS.unsubscribe(
                        "render:draw:3d", self._draw_custom_render
                    )
                    self.subscribed_renderer = False
        else:
            [x.delete() for x in self.face_data[face]]
        self.face_data[face].clear()

    def _draw_custom_render(self):
        """
        will inherit the custom renderer
        """
        if not self.subscribed_renderer:
            mcpython.common.event.EventHandler.PUBLIC_EVENT_BUS.unsubscribe(
                "render:draw:3d", self._draw_custom_render
            )
            return
        self.custom_renderer.draw(self.block.position, self.block)

    def update(self, redraw_complete=True):
        """
        updates the block face state
        :param redraw_complete: if all sides should be re-drawn
        """
        state = (
            G.world.get_active_dimension()
            .get_chunk_for_position(self.block.position)
            .exposed_faces(self.block.position)
        )
        if state == self.faces and not redraw_complete:
            return
        G.world.get_active_dimension().get_chunk_for_position(
            self.block.position
        ).positions_updated_since_last_save.add(self.block.position)
        self.hide_all()
        for key in state.keys():
            if state[key]:
                self.show_face(key)
            else:
                self.hide_face(key)

    def hide_all(self):
        """
        will hide all faces
        """
        if (
            any(self.faces.values())
            and issubclass(
                type(self.custom_renderer),
                mcpython.client.rendering.ICustomBlockRenderer.ICustomDrawMethodRenderer,
            )
            and self.subscribed_renderer
        ):
            mcpython.common.event.EventHandler.PUBLIC_EVENT_BUS.unsubscribe(
                "render:draw:3d", self._draw_custom_render
            )
            self.subscribed_renderer = False
        [self.hide_face(face) for face in mcpython.util.enums.EnumSide.iterate()]

    def __del__(self):
        """
        will delete references to various parts for gc
        """
        self.hide_all()
        del self.block
        del self.custom_renderer
