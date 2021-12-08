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
import typing

import mcpython.client.gui.ContainerRenderer
import mcpython.client.rendering.gui.RecipeViewRenderer


class InventorySingleRecipeView(
    mcpython.client.gui.ContainerRenderer.ContainerRenderer
):
    """
    Inventory class for single inventory recipe view
    todo: add custom name attribute setter from renderer if needed
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

    async def on_activate(self):
        await super().on_activate()
        assert self.renderer is not None

    def draw(self, hovering_slot=None):
        self.bg_image_size = self.renderer.get_rendering_size()
        self.bg_anchor = "MM"
        self.window_anchor = "MM"
        self.renderer.draw(self.get_position(), hovering_slot=hovering_slot)

    # todo: move to container
    def get_interaction_slots(self):
        return self.renderer.get_slots()

    def tick(self, dt: float):
        self.renderer.tick(dt)


class InventoryMultiRecipeView(mcpython.client.gui.ContainerRenderer.ContainerRenderer):
    """
    Inventory class for multi inventory recipe view
    todo: add custom name attribute setter from renderer if needed
    """

    def __init__(self):
        super().__init__()
        self.renderers: typing.List[
            mcpython.client.rendering.gui.RecipeViewRenderer.AbstractRecipeViewRenderer
        ] = []

        self.page = 0
        self.recipes_per_page = 3

    def add_recipe_renderer(
        self,
        renderer: mcpython.client.rendering.gui.RecipeViewRenderer.AbstractRecipeViewRenderer,
    ):
        self.renderers.append(renderer)
        return self

    async def on_activate(self):
        await super().on_activate()
        assert self.renderers
        self.bg_anchor = "MM"
        self.window_anchor = "MM"

    def draw(self, hovering_slot=None):
        renderers = self.renderers[
            self.page * self.recipes_per_page : (self.page + 1) * self.recipes_per_page
        ]

        width = max(renderer.get_rendering_size()[0] for renderer in renderers)
        height = sum(
            renderer.get_rendering_size()[1] for renderer in renderers
        ) + 10 * (len(renderers) - 1)

        self.bg_image_size = width, height

        x, y = self.get_position()

        for renderer in reversed(renderers):
            renderer.draw((x, y), hovering_slot=hovering_slot)
            y += renderer.get_rendering_size()[1] + 10

    def get_interaction_slots(self):
        # todo: fix slot positions not matching up their local offset
        renderers = self.renderers[
            self.page * self.recipes_per_page : (self.page + 1) * self.recipes_per_page
        ]
        slots = sum([renderer.get_slots() for renderer in renderers], [])
        return slots

    def tick(self, dt: float):
        for renderer in self.renderers[
            self.page * self.recipes_per_page : (self.page + 1) * self.recipes_per_page
        ]:
            renderer.tick(dt)
