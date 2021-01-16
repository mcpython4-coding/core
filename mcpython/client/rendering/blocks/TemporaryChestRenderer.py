import typing

import mcpython.client.rendering.blocks.ICustomBlockRenderer
from mcpython import shared


class TemporaryChestRenderer(mcpython.client.rendering.blocks.ICustomBlockRenderer.ICustomBatchBlockRenderer):
    def add(self, position: typing.Tuple[int, int, int], block, face, batches):
        return shared.model_handler.add_raw_face_to_batch(position, {}, None, batches, face)

