import math
import typing
from abc import ABC

import PIL.Image
import pyglet

import mcpython.client.gui.ContainerRenderer
import mcpython.client.gui.Slot
from mcpython.common.container.ResourceStack import ItemStack
from mcpython.common.container.ItemGroup import ItemGroup
import mcpython.ResourceLoader
from mcpython import shared
import mcpython.util.texture as texture_util
from mcpython.util.opengl import draw_line_rectangle
import mcpython.common.event.EventBus
from pyglet.window import mouse, key


TAB_TEXTURE = mcpython.ResourceLoader.read_pyglet_image("minecraft:gui/container/creative_inventory/tabs")


class CreativeTabScrollbar:
    """
    Creative tab scrollbar
    Feel free to re-use for other stuff

    todo: use batches
    """

    SCROLLBAR_SIZE = 24, 30

    NON_SELECTED_SCROLLBAR = texture_util.resize_image_pyglet(TAB_TEXTURE.get_region(232, 241, 12, 15), SCROLLBAR_SIZE)
    SELECTED_SCROLLBAR = texture_util.resize_image_pyglet(TAB_TEXTURE.get_region(244, 241, 12, 15), SCROLLBAR_SIZE)

    def __init__(self, callback: typing.Callable[[int], None], scroll_until: int = 1):
        self.callback = callback
        self.scroll_until = scroll_until
        self.currently_scrolling = 1
        self.underlying_event_bus: mcpython.common.event.EventBus.EventBus = shared.event_handler.create_bus(active=False)

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
        if 0 <= x - cx <= self.SCROLLBAR_SIZE[0] and 0 <= y - cy <= self.SCROLLBAR_SIZE[1]:
            self.is_hovered = True
        else:
            self.is_hovered = False

    def on_mouse_scroll(self, x, y, sx, sy):
        self.currently_scrolling = max(1, min(self.currently_scrolling+math.copysign(1, sy), self.scroll_until))
        self.callback(self.currently_scrolling)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.UP:
            self.on_mouse_scroll(0, 0, 0, -1)
        elif symbol == key.DOWN:
            self.on_mouse_scroll(0, 0, 0, 1)

    def get_scrollbar_position(self):
        x, y = self.position
        sx, sy = self.SCROLLBAR_SIZE
        y += self.height - sy
        if self.scroll_until != 1:
            y -= (self.height - sy) * ((self.currently_scrolling - 1) / (self.scroll_until - 1))
        # print(self.position, self.SCROLLBAR_SIZE, self.height, self.currently_scrolling, self.scroll_until, x, y)
        return x, y

    def draw_at(self, lower_left: typing.Tuple[int, int], height: int):
        self.position = lower_left
        self.height = height

        (self.NON_SELECTED_SCROLLBAR if self.is_hovered else self.SELECTED_SCROLLBAR).blit(*self.get_scrollbar_position())

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
        self.tab_slot = mcpython.client.gui.Slot.Slot()

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

    def on_deactivate(self):
        super().on_deactivate()
        shared.state_handler.active_state.parts[0].activate_mouse = True


class CreativeItemTab(ICreativeView):
    bg_texture: pyglet.image.AbstractImage = texture_util.to_pyglet_image(mcpython.util.texture.to_pillow_image(mcpython.ResourceLoader.read_pyglet_image("minecraft:gui/container/creative_inventory/tab_items").get_region(0, 120, 194, 255-120)).resize((2*195, 2*136), PIL.Image.NEAREST))

    def __init__(self, icon: ItemStack, group: ItemGroup = None, linked_tag=None):
        super().__init__()
        self.icon = icon
        self.group = group if group is not None else ItemGroup()
        self.scroll_offset = 0
        self.old_scroll_offset = 0
        self.linked_tag = linked_tag

        if linked_tag is not None:
            # If there is a tag linked to this tab, subscribe to the reload event

            import mcpython.common.data.ResourcePipe
            mcpython.common.data.ResourcePipe.handler.register_data_processor(self.load_from_tag)

        self.scroll_bar = CreativeTabScrollbar(self.set_scrolling)

    def set_scrolling(self, progress: int):
        self.scroll_offset = round(progress - 1)
        self.update_rendering()

    def load_from_tag(self):
        """
        Helper method for reloading the content from the underlying tag
        Use only when self.linked_tag is set, otherwise, this will crash
        """
        assert self.linked_tag is not None, "linked tag shouldn't be None when calling this method..."

        tag = shared.tag_handler.get_entries_for(self.linked_tag, "items")
        self.group.entries.clear()
        self.group.entries += (ItemStack(e) for e in tag)
        self.scroll_bar.set_max_value(max(1, (math.ceil(len(self.group.entries) / 9)-4)))

        self.update_rendering(force=True)

    def update_rendering(self, force=False):
        """
        Updates the slot content of the rendering system
        :param force: force update, also when nothing changed
        """
        if self.old_scroll_offset == self.scroll_offset and not force: return
        self.old_scroll_offset = self.scroll_offset

        for i, slot in enumerate(self.slots[9:]):
            i += self.scroll_offset * 9

            if i < len(self.group.entries):
                slot.set_itemstack_force(self.group.entries[i].copy())
            else:
                slot.set_itemstack_force(ItemStack.create_empty())

    def create_slot_renderers(self):
        """
        Creates the slots
        """

        slots = [
            [
                mcpython.client.gui.Slot.SlotInfiniteStack(ItemStack.create_empty(), position=(18+x*36, 61+y*36)) for x in range(9)
            ]
            for y in range(4, -1, -1)
        ]
        # some black magic...
        return [slot.copy((18+i*36, slot.position[1]-2)) for i, slot in enumerate(shared.world.get_active_player().inventory_main.slots[:9])] + sum(slots, [])

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
        return 2*195, 2*136

    def draw_at(self, position: typing.Tuple[int, int], hovering_slot=None):
        self.bg_texture.blit(*position)
        self.scroll_bar.draw_at((position[0]+176*2, position[1]+8*2), self.get_view_size()[1]-50)

    def draw(self, hovering_slot=None):
        super().draw(hovering_slot)

    def clear(self):
        pass

    def on_deactivate(self):
        super().on_deactivate()
        self.scroll_bar.deactivate()

    def on_activate(self):
        super().on_deactivate()
        self.scroll_bar.activate()
        self.update_rendering(True)


class CreativeTabManager:

    TAB_SIZE = 28*2, 30*2

    UPPER_TAB = texture_util.resize_image_pyglet(TAB_TEXTURE.get_region(0, 224, 28, 30), TAB_SIZE)
    LOWER_TAB = texture_util.resize_image_pyglet(TAB_TEXTURE.get_region(0, 128, 28, 30), TAB_SIZE)

    def __init__(self):
        self.pages: typing.List[typing.List[ICreativeView]] = [[]]
        self.inventory_instance = None
        self.search_instance = None
        self.current_page = 0

    def add_tab(self, tab: ICreativeView):
        tab.update_rendering()
        if len(self.pages[-1]) < 10:
            self.pages[-1].append(tab)
            tab.tab_icon = self.UPPER_TAB if len(self.pages[-1]) <= 5 else self.LOWER_TAB
            tab.tab_slot.set_itemstack(tab.get_icon_stack())
        else:
            self.pages.append([tab])
            tab.tab_icon = self.UPPER_TAB
            tab.tab_slot.set_itemstack(tab.get_icon_stack())
        return self

    def draw_tabs(self, lower_left_position: typing.Tuple[int, int], container_size: typing.Tuple[int, int]):
        tabs = self.pages[self.current_page]
        x, y = lower_left_position
        for tab in tabs[5:]:
            tab.tab_icon.blit(x, y-self.TAB_SIZE[1])
            tab.tab_slot.draw(x + 10, y - self.TAB_SIZE[1] + 10)
            x += self.TAB_SIZE[0]

        x = lower_left_position[0]
        y += container_size[1]
        for tab in tabs[:5]:
            tab.tab_icon.blit(x, y)
            tab.tab_slot.draw(x + 10, y + 10)
            x += self.TAB_SIZE[0]

    def open(self):
        shared.inventory_handler.show(self.pages[0][0])


CT_MANAGER = CreativeTabManager()

BuildingBlocks = None


def init():
    global BuildingBlocks
    BuildingBlocks = CreativeItemTab(ItemStack("minecraft:bricks"), linked_tag="#minecraft:tab_building_blocks")

    CT_MANAGER.add_tab(BuildingBlocks)

