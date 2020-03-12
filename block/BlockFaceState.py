"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import util.enums
import globals as G
import rendering.ICustomBlockRenderer
import event.EventHandler


class BlockFaceState:
    def __init__(self, block):
        self.block = block
        self.faces = {x: False for x in util.enums.EnumSide.iterate()}
        self.face_data = {x: [] for x in util.enums.EnumSide.iterate()}
        self.custom_renderer = None  # holds an custom block renderer
        self.subscribed_renderer = False

    def show_face(self, face: util.enums.EnumSide):
        if self.faces[face]: return
        self.faces[face] = True
        if self.custom_renderer is not None:
            if issubclass(type(self.custom_renderer), rendering.ICustomBlockRenderer.ICustomBatchBlockRenderer):
                self.face_data[face] = self.custom_renderer.add(self.block.position, self.block, face)
            elif issubclass(type(self.custom_renderer), rendering.ICustomBlockRenderer.ICustomDrawMethodRenderer):
                if not self.subscribed_renderer:
                    event.EventHandler.PUBLIC_EVENT_BUS.subscribe("render:draw:3d", self.custom_renderer.draw)
                    self.subscribed_renderer = True
        else:
            self.face_data[face].extend(
                G.modelhandler.add_face_to_batch(self.block, face, G.world.get_active_dimension().batches))

    def hide_face(self, face: util.enums.EnumSide):
        if not self.faces[face]: return
        self.faces[face] = False
        if self.custom_renderer is not None:
            if issubclass(type(self.custom_renderer), rendering.ICustomBlockRenderer.ICustomBatchBlockRenderer):
                self.custom_renderer.remove(self.block.position, self.block, self.face_data[face], face)
            elif issubclass(type(self.custom_renderer), rendering.ICustomBlockRenderer.ICustomDrawMethodRenderer):
                if self.subscribed_renderer and not any(self.faces.values()):
                    event.EventHandler.PUBLIC_EVENT_BUS.unsubscribe("render:draw:3d", self.custom_renderer.draw)
        else:
            [x.delete() for x in self.face_data[face]]
        self.face_data[face].clear()

    def update(self, redraw_complete=False):
        state = G.world.get_active_dimension().get_chunk_for_position(self.block.position).exposed_faces(
            self.block.position)
        if state == self.faces and not redraw_complete: return
        G.world.get_active_dimension().get_chunk_for_position(
            self.block.position).positions_updated_since_last_save.add(self.block.position)
        self.hide_all()
        for key in state.keys():
            if state[key]: self.show_face(key)
            else: self.hide_face(key)

    def hide_all(self): [self.hide_face(face) for face in util.enums.EnumSide.iterate()]

