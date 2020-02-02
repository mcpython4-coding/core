import util.enums
import globals as G


class BlockFaceState:
    def __init__(self, block):
        self.block = block
        self.faces = {x: False for x in util.enums.EnumSide.iterate()}
        self.face_data = {x: [] for x in util.enums.EnumSide.iterate()}

    def show_face(self, face: util.enums.EnumSide):
        if self.faces[face]: return
        self.faces[face] = True
        self.face_data[face].extend(
            G.modelhandler.add_face_to_batch(self.block, face, G.world.get_active_dimension().batches))

    def hide_face(self, face: util.enums.EnumSide):
        if not self.faces[face]: return
        self.faces[face] = False
        [x.delete() for x in self.face_data[face]]
        self.face_data[face].clear()

    def update(self):
        state = G.world.get_active_dimension().get_chunk_for_position(self.block.position).exposed_faces(
            self.block.position)
        for key in state.keys():
            if state[key]: self.show_face(key)
            else: self.hide_face(key)

    def hide_all(self): [self.hide_face(face) for face in util.enums.EnumSide.iterate()]

