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
import math
import typing
from abc import ABC

import mcpython.client.gui.ContainerRenderer
import mcpython.client.gui.Slot
import mcpython.client.rendering.ui.Buttons
import mcpython.common.event.EventBus
import mcpython.common.event.TickHandler
import mcpython.ResourceLoader
import mcpython.util.texture as texture_util
import PIL.Image
import pyglet
from mcpython import shared
from mcpython.common.container.ItemGroup import ItemGroup
from mcpython.common.container.ResourceStack import ItemStack
from mcpython.util.opengl import draw_line_rectangle
from pyglet.window import key, mouse

TAB_TEXTURE = mcpython.ResourceLoader.read_pyglet_image(
    "minecraft:gui/container/creative_inventory/tabs"
)


class CreativeTabScrollbar:
    """
    Creative tab scrollbar
    Feel free to re-use for other stuff

    todo: use batches
    """

    SCROLLBAR_SIZE = 24, 30

    NON_SELECTED_SCROLLBAR = texture_util.resize_image_pyglet(
        TAB_TEXTURE.get_region(232, 241, 12, 15), SCROLLBAR_SIZE
    )
    SELECTED_SCROLLBAR = texture_util.resize_image_pyglet(
        TAB_TEXTURE.get_region(244, 241, 12, 15), SCROLLBAR_SIZE
    )

    def __init__(self, callback: typing.Callable[[int], None], scroll_until: int = 1):
        self.callback = callback
        self.scroll_until = scroll_until
        self.currently_scrolling = 1
        self.underlying_event_bus: mcpython.common.event.EventBus.EventBus = (
            shared.event_handler.create_bus(active=False)
        )

        self.underlying_event_bus.subscribe("user:mouse:drag", self.on_mouse_drag)
        self.underlying_event_bus.subscribe("user:mouse:motion", self.on_mouse_move)
        self.underlying_event_bus.subscribe("user:mouse:scroll", self.on_mouse_scroll)
        self.underlying_event_bus.subscribe("user:keyboard:press", self.on_key_press)

        self.position = (0, 0)
        self.height = 1

        self.is_hovered = False

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if buttons & mouse.LEFT:
            cx, cy = self.get_scrollbar_position()
            if self.is_hovered:
                # todo: something better here!
                self.on_mouse_scroll(0, 0, 0, -dy)

        self.on_mouse_move(x, y, dx, dy)

    def on_mouse_move(self, x, y, dx, dy):
        cx, cy = self.get_scrollbar_position()
        if (
            0 <= x - cx <= self.SCROLLBAR_SIZE[0]
            and 0 <= y - cy <= self.SCROLLBAR_SIZE[1]
        ):
            self.is_hovered = True
        else:
            self.is_hovered = False

    def on_mouse_scroll(self, x, y, sx, sy):
        self.currently_scrolling = max(
            1, min(self.currently_scrolling + math.copysign(1, sy), self.scroll_until)
        )
        self.callback(self.currently_scrolling)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.UP:
            self.on_mouse_scroll(0, 0, 0, -1)

        elif symbol == key.DOWN:
            self.on_mouse_scroll(0, 0, 0, 1)

        elif symbol == key.PAGEUP:
            for _ in range(5):
                self.on_mouse_scroll(0, 0, 0, -1)

        elif symbol == key.PAGEDOWN:
            for _ in range(5):
                self.on_mouse_scroll(0, 0, 0, 1)

    def get_scrollbar_position(self):
        x, y = self.position
        sx, sy = self.SCROLLBAR_SIZE
        y += self.height - sy
        if self.scroll_until != 1:
            y -= (self.height - sy) * (
                (self.currently_scrolling - 1) / (self.scroll_until - 1)
            )
        # print(self.position, self.SCROLLBAR_SIZE, self.height, self.currently_scrolling, self.scroll_until, x, y)
        return x, y

    def draw_at(self, lower_left: typing.Tuple[int, int], height: int):
        self.position = lower_left
        self.height = height

        (
            self.NON_SELECTED_SCROLLBAR if self.is_hovered else self.SELECTED_SCROLLBAR
        ).blit(*self.get_scrollbar_position())

        # This is here for debugging where the bar is drawn
        # draw_line_rectangle(lower_left, (self.SCROLLBAR_SIZE[0], height), (1, 0, 0))

    def activate(self):
        self.underlying_event_bus.activate()

    def deactivate(self):
        self.underlying_event_bus.deactivate()
        self.is_hovered = False

    def set_max_value(self, value: int):
        assert value >= 1, "value must be positive"

        self.scroll_until = value
        self.currently_scrolling = min(self.currently_scrolling, value)


class ICreativeView(mcpython.client.gui.ContainerRenderer.ContainerRenderer, ABC):
    """
    Base class for a creative tab
    Comes with some helper code
    """

    def __init__(self):
        super().__init__()
        self.tab_icon = None
        self.tab_icon_selected = None
        self.is_selected = False
        self.tab_slot = mcpython.client.gui.Slot.Slot()
        self.icon_position = 0, 0

    def update_rendering(self):
        pass

    def get_icon_stack(self) -> ItemStack:
        raise NotImplementedError

    def get_view_size(self) -> typing.Tuple[int, int]:
        raise NotImplementedError

    def draw_at(self, position: typing.Tuple[int, int], hovering_slot=None):
        pass

    def draw(self, hovering_slot=None):
        self.bg_anchor = "MM"
        self.window_anchor = "MM"
        self.bg_image_size = self.get_view_size()

        x, y = self.get_position()

        self.draw_at((x, y), hovering_slot=hovering_slot)

        CT_MANAGER.draw_tabs((x, y), self.bg_image_size)

        for slot in self.get_draw_slots():
            slot.draw(x, y, hovering=slot == hovering_slot)

        for slot in self.get_draw_slots():
            slot.draw_label()

        if self.custom_name is not None:
            if self.custom_name_label.text != self.custom_name:
                self.custom_name_label.text = self.custom_name

            self.custom_name_label.x = x + 15
            self.custom_name_label.y = y + self.bg_image_size[1] - 10
            self.custom_name_label.draw()

    def on_activate(self):
        super().on_activate()
        CT_MANAGER.activate()

    def on_deactivate(self):
        super().on_deactivate()
        shared.state_handler.active_state.parts[0].activate_mouse = True
        CT_MANAGER.deactivate()


class CreativeItemTab(ICreativeView):
    bg_texture: pyglet.image.AbstractImage = texture_util.to_pyglet_image(
        mcpython.util.texture.to_pillow_image(
            mcpython.ResourceLoader.read_pyglet_image(
                "minecraft:gui/container/creative_inventory/tab_items"
            ).get_region(0, 120, 194, 255 - 120)
        ).resize((2 * 195, 2 * 136), PIL.Image.NEAREST)
    )

    def __init__(
        self, name: str, icon: ItemStack, group: ItemGroup = None, linked_tag=None
    ):
        super().__init__()
        self.icon = icon
        self.group = group if group is not None else ItemGroup()
        self.scroll_offset = 0
        self.old_scroll_offset = 0
        self.linked_tag = linked_tag
        self.custom_name = self.name = name

        if linked_tag is not None:
            # If there is a tag linked to this tab, subscribe to the reload event

            import mcpython.common.data.ResourcePipe

            mcpython.common.data.ResourcePipe.handler.register_data_processor(
                self.load_from_tag
            )

        self.scroll_bar = CreativeTabScrollbar(self.set_scrolling)

    def set_scrolling(self, progress: int):
        self.scroll_offset = round(progress - 1)
        self.update_rendering()

    def load_from_tag(self):
        """
        Helper method for reloading the content from the underlying tag
        Use only when self.linked_tag is set, otherwise, this will crash
        """
        assert (
            self.linked_tag is not None
        ), "linked tag shouldn't be None when calling this method..."

        tag = shared.tag_handler.get_entries_for(self.linked_tag, "items")
        self.group.entries.clear()
        self.group.entries += (ItemStack(e) for e in tag)
        self.scroll_bar.set_max_value(
            max(1, (math.ceil(len(self.group.entries) / 9) - 4))
        )

        self.update_rendering(force=True)

    def update_rendering(self, force=False):
        """
        Updates the slot content of the rendering system
        :param force: force update, also when nothing changed
        """
        if self.old_scroll_offset == self.scroll_offset and not force:
            return
        self.old_scroll_offset = self.scroll_offset

        for i, slot in enumerate(self.slots[9:]):
            i += self.scroll_offset * 9

            if i < len(self.group.entries):
                slot.set_itemstack_force(self.group.entries[i].copy())
            else:
                slot.set_itemstack_force(ItemStack.create_empty())

        for slot in self.slots[:9]:
            slot.invalidate()

    def create_slot_renderers(self):
        """
        Creates the slots
        """

        def work(i):
            return lambda: shared.world.get_active_player().inventory_main.slots[i]

        slots = [
            [
                mcpython.client.gui.Slot.SlotInfiniteStack(
                    ItemStack.create_empty(), position=(18 + x * 36, 61 + y * 36)
                )
                for x in range(9)
            ]
            for y in range(4, -1, -1)
        ]
        # some black magic...
        return [
            mcpython.client.gui.Slot.SlotCopyWithDynamicTarget(
                work(j),
                position=(
                    20 + j * 36,
                    16,
                ),
            )
            for j in range(9)
        ] + sum(slots, [])

    def add_item(self, item: typing.Union[ItemStack, str]):
        """
        Adds an item to the underlying item group
        :param item: the item stack or the item name
        """

        self.group.add(item if not isinstance(item, str) else ItemStack(item))
        return self

    def get_icon_stack(self) -> ItemStack:
        return self.icon

    def get_view_size(self) -> typing.Tuple[int, int]:
        return 2 * 195, 2 * 136

    def draw_at(self, position: typing.Tuple[int, int], hovering_slot=None):
        self.bg_texture.blit(*position)
        self.scroll_bar.draw_at(
            (position[0] + 176 * 2, position[1] + 8 * 2), self.get_view_size()[1] - 50
        )

    def draw(self, hovering_slot=None):
        super().draw(hovering_slot)

    def clear(self):
        pass

    def on_deactivate(self):
        super().on_deactivate()
        self.scroll_bar.deactivate()

    def on_activate(self):
        super().on_activate()
        self.scroll_bar.activate()
        self.update_rendering(True)


class CreativePlayerInventory(ICreativeView):
    TEXTURE_SIZE = 195 * 2, 136 * 2

    TEXTURE = texture_util.resize_image_pyglet(
        mcpython.ResourceLoader.read_pyglet_image(
            "minecraft:gui/container/creative_inventory/tab_inventory"
        ).get_region(0, 120, 195, 136),
        TEXTURE_SIZE,
    )

    def __init__(self):
        super().__init__()
        self.stack = ItemStack("minecraft:chest")
        self.tab_icon = CreativeTabManager.LOWER_TAB
        self.tab_icon_selected = CreativeTabManager.LOWER_TAB_SELECTED

    def get_icon_stack(self) -> ItemStack:
        return self.stack

    def get_view_size(self) -> typing.Tuple[int, int]:
        return self.TEXTURE_SIZE

    def draw_at(self, position: typing.Tuple[int, int], hovering_slot=None):
        self.TEXTURE.blit(*position)

    def create_slot_renderers(self):
        """
        Creates the slots
        """

        def work(i):
            return lambda: shared.world.get_active_player().inventory_main.slots[i]

        # some black magic...
        return [
            mcpython.client.gui.Slot.SlotCopyWithDynamicTarget(
                work(j),
            )
            for j in range(40)
        ] + [
            mcpython.client.gui.Slot.SlotCopyWithDynamicTarget(
                work(45),
            ),
            mcpython.client.gui.Slot.SlotTrashCan()
        ]

    @staticmethod
    def get_config_file() -> str or None:
        return "assets/config/inventory/player_inventory_main_creative.json"


class CreativeTabManager:

    TAB_SIZE = 28 * 2, 30 * 2

    # todo: make this reload-able!
    UPPER_TAB = texture_util.resize_image_pyglet(
        TAB_TEXTURE.get_region(0, 224, 28, 30), TAB_SIZE
    )
    UPPER_TAB_SELECTED = texture_util.resize_image_pyglet(
        TAB_TEXTURE.get_region(0, 224 - 30, 28, 30), TAB_SIZE
    )
    LOWER_TAB = texture_util.resize_image_pyglet(
        TAB_TEXTURE.get_region(0, 164, 28, 30), TAB_SIZE
    )
    LOWER_TAB_SELECTED = texture_util.resize_image_pyglet(
        TAB_TEXTURE.get_region(0, 128, 28, 30), TAB_SIZE
    )

    def __init__(self):
        self.pages: typing.List[typing.List[ICreativeView]] = [[]]
        self.inventory_instance = None
        self.search_instance = None
        self.saved_hotbars = None
        self.current_page = 0

        self.underlying_event_bus: mcpython.common.event.EventBus.EventBus = (
            shared.event_handler.create_bus(active=False)
        )
        self.underlying_event_bus.subscribe("user:mouse:press", self.on_mouse_press)
        self.underlying_event_bus.subscribe("user:mouse:drag", self.on_mouse_move)
        self.underlying_event_bus.subscribe("user:mouse:motion", self.on_mouse_move)
        self.underlying_event_bus.subscribe("user:keyboard:press", self.on_key_press)

        self.hovering_tab = None

        self.page_left = mcpython.client.rendering.ui.Buttons.arrow_button_left(
            (0, 0), lambda: self.increase_page(-1)
        )
        self.page_right = mcpython.client.rendering.ui.Buttons.arrow_button_right(
            (0, 0), lambda: self.increase_page(1)
        )
        self.page_label = pyglet.text.Label(anchor_x="center", anchor_y="center")

        self.lower_left_position = 0, 0
        self.container_size = 1, 1

        self.current_tab: typing.Optional[ICreativeView] = None

    def is_multi_page(self):
        return len(self.pages) > 1

    def on_key_press(self, button, mod):
        if button == key.E:
            shared.inventory_handler.hide(self.current_tab)
        elif button == key.N and self.is_multi_page():
            self.current_page = max(self.current_page - 1, 0)
        elif button == key.M and self.is_multi_page():
            self.current_page = min(self.current_page + 1, len(self.pages) - 1)

    def on_mouse_move(self, x, y, dx, dy, *_):
        tab = self.get_tab_at(x, y)
        self.hovering_tab = tab

    def init_tabs_if_needed(self):
        if self.inventory_instance is None:
            self.inventory_instance = CreativePlayerInventory()

    def activate(self):
        mcpython.common.event.TickHandler.handler.bind(
            self.underlying_event_bus.activate, 1
        )

        if self.is_multi_page():
            self.page_left.activate()
            self.page_right.activate()

    def deactivate(self):
        self.underlying_event_bus.deactivate()
        self.page_left.deactivate()
        self.page_right.deactivate()

    def on_mouse_press(self, mx, my, button, modifiers):
        if not button & mouse.LEFT:
            return

        tab = self.get_tab_at(mx, my)
        if tab is not None:
            self.switch_to_tab(tab)

    def get_tab_at(self, mx, my) -> typing.Optional[ICreativeView]:
        tx, ty = self.TAB_SIZE

        tabs = self.pages[self.current_page]
        x, y = self.lower_left_position
        for tab in tabs[4:]:
            # y is here not a mistake as tabs are going down, instead of up
            if 0 <= mx - x <= tx and 0 <= y - my <= ty:
                return tab
            x += self.TAB_SIZE[0]

        x = self.lower_left_position[0]
        y += self.container_size[1]
        for tab in tabs[:4]:
            if 0 <= mx - x <= tx and 0 <= my - y <= ty:
                return tab
            x += self.TAB_SIZE[0]

        # todo: add extension point here
        for tab in (self.inventory_instance, self.search_instance, self.saved_hotbars):
            # print(mx, my, tab.icon_position if tab is not None else None)
            if (
                tab is not None
                and 0 <= mx - tab.icon_position[0] <= tx
                and 0 <= my - tab.icon_position[1] <= ty
            ):
                return tab

    def add_tab(self, tab: ICreativeView):
        tab.update_rendering()
        if len(self.pages[-1]) < 9:
            self.pages[-1].append(tab)
            tab.tab_icon = (
                self.UPPER_TAB if len(self.pages[-1]) <= 4 else self.LOWER_TAB
            )
            tab.tab_icon_selected = (
                self.UPPER_TAB_SELECTED
                if len(self.pages[-1]) <= 4
                else self.LOWER_TAB_SELECTED
            )
            tab.tab_slot.set_itemstack(tab.get_icon_stack())
        else:
            self.pages.append([tab])
            tab.tab_icon = self.UPPER_TAB
            tab.tab_icon_selected = self.UPPER_TAB_SELECTED
            tab.tab_slot.set_itemstack(tab.get_icon_stack())
        return self

    def draw_tab(self, tab: ICreativeView, x: int, y: int):
        icon = (
            tab.tab_icon
            if not tab.is_selected and tab != self.hovering_tab
            else tab.tab_icon_selected
        )
        icon.blit(x, y)
        tab.tab_slot.draw(x + 10, y + 10)
        tab.icon_position = x, y

    def draw_tabs(
        self,
        lower_left_position: typing.Tuple[int, int],
        container_size: typing.Tuple[int, int],
    ):
        self.lower_left_position = lower_left_position
        self.container_size = container_size

        tabs = self.pages[self.current_page]
        x, y = lower_left_position
        for tab in tabs[4:]:
            self.draw_tab(tab, x, y - self.TAB_SIZE[1])
            x += self.TAB_SIZE[0]

        x = lower_left_position[0]
        y += container_size[1]
        for tab in tabs[:4]:
            self.draw_tab(tab, x, y)
            x += self.TAB_SIZE[0]

        x, y = lower_left_position

        self.draw_tab(
            self.inventory_instance,
            x + container_size[0] - self.TAB_SIZE[0],
            y - self.TAB_SIZE[1],
        )

        if self.is_multi_page():
            self.page_left.active = self.current_page != 0
            self.page_left.position = (
                lower_left_position[0] - 10,
                lower_left_position[1] + container_size[1] + self.TAB_SIZE[1] + 10,
            )
            self.page_left.draw()

            self.page_right.active = self.current_page != len(self.pages) - 1
            self.page_right.position = (
                lower_left_position[0] + container_size[0] + 10,
                lower_left_position[1] + container_size[1] + self.TAB_SIZE[1] + 10,
            )
            self.page_right.draw()

            self.page_label.text = f"{self.current_page + 1} / {len(self.pages)}"
            self.page_label.position = (
                lower_left_position[0] + container_size[0] // 2 + 10,
                lower_left_position[1] + container_size[1] + self.TAB_SIZE[1] + 19,
            )
            self.page_label.draw()

    def open(self):
        if self.current_tab is None:
            self.init_tabs_if_needed()

            self.switch_to_tab(self.inventory_instance)
        else:
            shared.inventory_handler.show(self.current_tab)

    def increase_page(self, count: int):
        previous = self.current_page
        self.current_page = max(0, min(self.current_page + count, len(self.pages) - 1))
        if previous != self.current_page:
            self.switch_to_tab(self.pages[self.current_page][0])

    def switch_to_tab(self, tab: ICreativeView):
        if self.current_tab is not None:
            shared.inventory_handler.hide(self.current_tab)
            self.current_tab.is_selected = False

        self.current_tab = tab

        tab.is_selected = True
        shared.inventory_handler.show(tab)


CT_MANAGER = CreativeTabManager()

BuildingBlocks = None
Decoration = None
Redstone = None
Transportation = None
Miscellaneous = None
Food = None
Tools = None
Weapons = None
Brewing = None
Test = None


def init():
    global BuildingBlocks, Decoration, Redstone, Transportation, Miscellaneous, Food, Tools, Weapons, Brewing, Test
    BuildingBlocks = CreativeItemTab(
        "Building Blocks",
        ItemStack("minecraft:bricks"),
        linked_tag="#minecraft:tab_building_blocks",
    )
    Decoration = CreativeItemTab(
        "Decoration",
        ItemStack("minecraft:barrier"),
        linked_tag="#minecraft:tab_decoration",
    )
    Redstone = CreativeItemTab(
        "Redstone",
        ItemStack("minecraft:redstone_block"),
        linked_tag="#minecraft:tab_redstone",
    )
    Transportation = CreativeItemTab(
        "Transportation",
        ItemStack("minecraft:barrier"),
        linked_tag="#minecraft:tab_transportation",
    )
    Miscellaneous = CreativeItemTab(
        "Miscellaneous",
        ItemStack("minecraft:stick"),
        linked_tag="#minecraft:tab_miscellaneous",
    )
    Food = CreativeItemTab(
        "Food", ItemStack("minecraft:potato"), linked_tag="#minecraft:tab_food"
    )
    Tools = CreativeItemTab(
        "Tools", ItemStack("minecraft:iron_axe"), linked_tag="#minecraft:tab_tools"
    )
    Weapons = CreativeItemTab(
        "Weapons",
        ItemStack("minecraft:iron_sword"),
        linked_tag="#minecraft:tab_weapons",
    )
    Brewing = CreativeItemTab(
        "Brewing", ItemStack("minecraft:barrier"), linked_tag="#minecraft:tab_brewing"
    )
    Test = CreativeItemTab("Testing", ItemStack("minecraft:diamond_block")).add_item(
        "minecraft:obsidian"
    )

    CT_MANAGER.add_tab(BuildingBlocks).add_tab(Decoration).add_tab(Redstone).add_tab(
        Transportation
    ).add_tab(Miscellaneous).add_tab(Food).add_tab(Tools).add_tab(Weapons).add_tab(
        Brewing
    )
    # CT_MANAGER.add_tab(Test)
