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

import mcpython.common.data.Language
import pyglet
from mcpython import shared
from mcpython.common.container.ResourceStack import ItemStack


class IHoveringItemBoxDefinitionPlugin:
    """
    Abstract class for manipulating an existing HoveringDefinition text.
    Use addPlugin(<instance>) on the final class to register your plugin.
    Saver than replacing the entry for the item.
    Multiple plugins can co-exists. They are applied in order of registration.
    Please make sure that you look for changes before applying your changes (as you might interfere with stuff from another plugin)
    """

    def manipulateShownText(self, slot: ItemStack, text: list):
        raise NotImplementedError()


class IHoveringItemBoxDefinition:
    """
    Base class for an ToolTip text provider. Should generate out of an ItemStack an html-string-list
    """

    PLUGINS = []

    @classmethod
    def setup(cls):
        """
        Call this method on every child to set up
        """
        cls.PLUGINS = []

    def getHoveringText(self, itemstack: ItemStack) -> list:
        raise NotImplementedError()

    @classmethod
    def addPlugin(cls, plugin: IHoveringItemBoxDefinitionPlugin):
        cls.PLUGINS.append(plugin)


class DefaultHoveringItemBoxDefinition(IHoveringItemBoxDefinition):
    """
    Class representing an normal translate-able-configure-able tooltip with an given default style and layout
    Uses the default Item-class-methods to render certain stuff

    Subclasses can safely override getAdditionalText() to insert informal text, without breaking
    mods mixin into the getHoveringText() method
    """

    def __init__(
        self,
        default_style="<font color='{color}'>{text}</font>",
        localize_builder="item.{}.{}",
    ):
        self.localize_builder = localize_builder
        self.default_style = default_style

    def getAdditionalText(self, itemstack: ItemStack) -> typing.List[str]:
        return []

    def getHoveringText(self, itemstack: ItemStack) -> typing.List[str]:
        if itemstack.is_empty():
            return []

        item_name = itemstack.get_item_name()

        try:
            raw = self.localize_builder.format(*item_name.split(":"))
        except IndexError:
            raw = item_name

        localized_name = mcpython.common.data.Language.get(raw)
        if raw == localized_name:
            localized_name = itemstack.item.NAME
        if localized_name == "ConstructedItem":
            localized_name = "<MissingName:{{{};{}x}}>".format(
                item_name, itemstack.amount
            )

        tags = itemstack.item.TAGS
        if item_name in shared.registry.get_by_name("minecraft:block"):
            block_cls = shared.registry.get_by_name("minecraft:block")[item_name]
            tags = tags + [tag for tag in block_cls.TAGS if tag not in tags]

        stuff = (
            # Display name
            [
                self.default_style.format(
                    color=itemstack.item.ITEM_NAME_COLOR, text=localized_name
                )
            ]
            + self.getAdditionalText(itemstack)
            # Namespaced name
            + [
                self.default_style.format(
                    color="gray", text=mcpython.common.data.Language.translate(line)
                )
                for line in itemstack.item.get_additional_tooltip_text(itemstack, self)
            ]
            # Tags
            + (
                [self.default_style.format(color="gray", text=tag) for tag in tags]
                if not itemstack.is_empty()
                else []
            )
            # Namespace
            + [
                self.default_style.format(color="gray", text=item_name),
                self.default_style.format(
                    color="blue", text="<b><i>" + item_name.split(":")[0] + "</i></b>"
                ),
            ]
        )

        return stuff


DefaultHoveringItemBoxDefinition.setup()

# Both of these are the default renderers for items and block-item respectively.
# Feel free to override, but use IHoveringItemBoxDefinitionPlugin were possible instead
# Everything here MUST extend IHoveringItemBoxDefinition.
DEFAULT_ITEM_TOOLTIP = DefaultHoveringItemBoxDefinition()
DEFAULT_BLOCK_ITEM_TOOLTIP = DefaultHoveringItemBoxDefinition(
    localize_builder="block.{}.{}"
)


class HoveringItemBoxProvider:
    """
    Class for generating these tool-tips like in mc
    Uses above IHoveringItemBoxDefinition class to generate for itemstacks
    Create a new instance for rendering 2 or more at the same time
    """

    def __init__(self):
        self.last_slot = None
        self.cached_text = None
        self.cached_provider = None

        self.labels = []
        self.label_batch = pyglet.graphics.Batch()
        self.bg_rectangle = pyglet.shapes.Rectangle(0, 0, 0, 0, (0, 0, 0))

    def renderFor(self, itemstack: ItemStack, position):
        """
        Will render the ItemBoxProvider for a given slot
        :param itemstack: the slot to render over
        :param position: the position to render at, or None if calculated from slot
        """
        if itemstack != self.last_slot:
            self.last_slot = itemstack
            self.cached_provider = itemstack.item.get_tooltip_provider()
            self.cached_text = self.cached_provider.getHoveringText(itemstack)

            for plugin in self.cached_provider.PLUGINS:
                plugin.manipulateShownText(itemstack, self.cached_text)

            if len(self.labels) > len(self.cached_text):
                [label.delete() for label in self.labels[len(self.cached_text) :]]
                self.labels = self.labels[: len(self.cached_text)]

            if len(self.labels) < len(self.cached_text):
                self.labels += [
                    pyglet.text.HTMLLabel(batch=self.label_batch)
                    for _ in range(len(self.cached_text) - len(self.labels))
                ]

            for i, line in enumerate(self.cached_text):
                text = pyglet.text.decode_html(line)
                self.labels[i].document = text
                self.labels[i].anchor_y = "top"

            self.bg_rectangle.width = (
                max([label.content_width for label in self.labels]) + 10
            )
            self.bg_rectangle.height = (
                sum([label.content_height // 2 for label in self.labels]) + 10
            )

        self.bg_rectangle.position = position
        self.bg_rectangle.draw()

        y = position[1] + self.bg_rectangle.height
        for label in self.labels:
            label.begin_update()
            label.x = position[0] + 5
            label.y = y - 4
            y -= label.content_height // 2
            label.end_update()

        self.label_batch.draw()

    def eraseCache(self):
        """
        Can be used to re-calculate the text of the tool tip
        """
        self.last_slot = None
        self.cached_text = None
        self.cached_provider = None
