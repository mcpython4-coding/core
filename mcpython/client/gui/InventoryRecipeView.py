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
import typing

import mcpython.client.gui.Inventory
import mcpython.client.rendering.gui.RecipeViewRenderer


class InventorySingleRecipeView(mcpython.client.gui.Inventory.Inventory):
    """
    Inventory class for single inventory recipe view
    """

    def __init__(self):
        super().__init__()
        self.renderer: typing.Optional[
            mcpython.client.rendering.gui.RecipeViewRenderer.AbstractRecipeViewRenderer
        ] = None

    def set_renderer(
        self,
        renderer: mcpython.client.rendering.gui.RecipeViewRenderer.AbstractRecipeViewRenderer,
    ):
        self.renderer = renderer
        return self

    def on_activate(self):
        super().on_activate()
        assert self.renderer is not None

    def draw(self, hovering_slot=None):
        self.bg_image_size = self.renderer.get_rendering_size()
        self.bg_anchor = "MM"
        self.window_anchor = "MM"
        self.renderer.draw(self.get_position(), hovering_slot=hovering_slot)

    def get_interaction_slots(self):
        return self.renderer.get_slots()
