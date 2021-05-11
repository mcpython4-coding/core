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

    def load_from_tag(self):
        """
        Helper method for reloading the content from the underlying tag
        Use only when self.linked_tag is set, otherwise, this will crash
        """
        assert self.linked_tag is not None, "linked tag cannot be None"

        tag = shared.tag_handler.get_entries_for(self.linked_tag, "items")
        self.group.entries.clear()
        self.group.entries += (ItemStack(e) for e in tag)

        self.update_rendering(force=True)

    def update_rendering(self, force=False):
        """
        Updates the slot content of the rendering system
        :param force: force update, also when nothing changed
        """
        if self.old_scroll_offset != self.scroll_offset: return
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

    def draw(self, hovering_slot=None):
        super().draw(hovering_slot)

    def clear(self):
        pass


class CreativeTabManager:
    TABS = mcpython.ResourceLoader.read_pyglet_image("minecraft:gui/container/creative_inventory/tabs")

    TAB_SIZE = 28*2, 30*2

    UPPER_TAB = texture_util.resize_image_pyglet(TABS.get_region(0, 224, 28, 30), TAB_SIZE)
    LOWER_TAB = texture_util.resize_image_pyglet(TABS.get_region(0, 128, 28, 30), TAB_SIZE)

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

