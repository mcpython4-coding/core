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
import asyncio
import itertools
import math
import typing
from abc import ABC

import mcpython.client.gui.ContainerRenderer
import mcpython.client.gui.Slot
import mcpython.client.rendering.ui.Buttons
import mcpython.client.rendering.ui.SearchBar
import mcpython.common.event.TickHandler
import mcpython.engine.event.EventBus
import mcpython.engine.ResourceLoader
import mcpython.util.texture as texture_util
import PIL.Image
import pyglet
from mcpython import shared
from mcpython.client.gui.util import CreativeTabScrollbar, getTabTexture
from mcpython.common.container.ItemGroup import FilteredItemGroup, ItemGroup
from mcpython.common.container.ResourceStack import ItemStack, LazyClassLoadItemstack
from mcpython.engine import logger
from pyglet.window import key, mouse


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

    async def on_activate(self):
        await super().on_activate()
        await CT_MANAGER.activate()

    async def on_deactivate(self):
        await super().on_deactivate()
        shared.state_handler.active_state.parts[0].activate_mouse = True
        await CT_MANAGER.deactivate()


class CreativeItemTab(ICreativeView):
    bg_texture: pyglet.image.AbstractImage = None

    @classmethod
    async def reload(cls):
        cls.bg_texture = texture_util.to_pyglet_image(
            mcpython.util.texture.to_pillow_image(
                (
                    await mcpython.engine.ResourceLoader.read_pyglet_image(
                        "minecraft:gui/container/creative_inventory/tab_items"
                    )
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
        if self.linked_tag is None:
            raise RuntimeError("tag must be set for reloading")

        tag = shared.tag_handler.get_entries_for(self.linked_tag, "items")
        self.group.entries.clear()
        self.group.entries += filter(
            lambda stack: not stack.is_empty(),
            (ItemStack(e, warn_if_unarrival=False) for e in tag),
        )
        self.scroll_bar.set_max_value(
            max(1, (math.ceil(len(self.group.entries) / 9) - 4))
        )

        self.update_rendering(force=True)

    def update_rendering(self, force=False):
        """
        Updates the slot content of the rendering system
        :param force: force update, also when nothing changed
        """
        self.group.load_lazy()

        if self.old_scroll_offset == self.scroll_offset and not force:
            return
        self.old_scroll_offset = self.scroll_offset

        entries = list(self.group.view())  # todo: cache value!
        self.scroll_bar.set_max_value(max(math.ceil(len(entries) / 9) - 4, 1))

        # print("cycling at", self.name, "entries:", entries)

        entries = iter(entries)

        if self.scroll_offset != 0:
            for _ in range(9 * self.scroll_offset):
                next(entries)

        for i, slot in enumerate(self.slots[9:]):
            try:
                entry = next(entries)
            except StopIteration:
                # todo: can we simply clean the itemstack?
                slot.set_itemstack_force(ItemStack.create_empty())
            else:
                # print("writing at", i, "stack", entry)
                # todo: can we change the item in the stack?
                slot.set_itemstack_force(entry)

        for slot in self.slots[:9]:
            slot.invalidate()

    async def create_slot_renderers(self):
        """
        Creates the slots
        """

        def work(i):
            return (
                lambda: shared.world.get_active_player().inventory_main.slots[i]
                if shared.world.world_loaded
                else None
            )

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

    def add_item(self, item: typing.Union[ItemStack, LazyClassLoadItemstack, str]):
        """
        Adds an item to the underlying item group
        :param item: the item stack or the item name
        """

        if isinstance(item, str):
            item = LazyClassLoadItemstack(item)

        self.group.add(item)
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

    def clear(self):
        pass

    async def on_deactivate(self):
        await super().on_deactivate()
        self.scroll_bar.deactivate()

    async def on_activate(self):
        await super().on_activate()
        self.scroll_bar.activate()
        self.update_rendering(True)

    def on_mouse_button_press(
        self,
        relative_x: int,
        relative_y: int,
        button: int,
        modifiers: int,
        item_stack,
        slot,
    ) -> bool:
        if (
            2 * 16 <= relative_x <= 2 * 170
            and 24 * 2 <= relative_y <= 119 * 2
            and not item_stack.is_empty()
            and (
                slot is None
                or not slot.get_itemstack().contains_same_resource(item_stack)
            )
        ):
            item_stack.clean()
            return True

        return False

    def __repr__(self):
        return f"CreateItemTab({self.name}, entry_count={len(self.group.entries)})"

    def update_shift_container(self):
        shared.inventory_handler.shift_container_handler.container_A = self.slots[:9]
        shared.inventory_handler.shift_container_handler.container_B = self.slots[9:]


if not shared.IS_TEST_ENV:
    shared.tick_handler.schedule_once(CreativeItemTab.reload())


class CreativeTabSearchBar(CreativeItemTab):
    @classmethod
    async def reload(cls):
        cls.bg_texture = texture_util.to_pyglet_image(
            mcpython.util.texture.to_pillow_image(
                (
                    await mcpython.engine.ResourceLoader.read_pyglet_image(
                        "minecraft:gui/container/creative_inventory/tab_item_search"
                    )
                ).get_region(0, 120, 194, 255 - 120)
            ).resize((2 * 195, 2 * 136), PIL.Image.NEAREST)
        )

    def __init__(
        self, name: str, icon: ItemStack, group: ItemGroup = None, linked_tag=None
    ):
        super().__init__(name, icon, group, linked_tag)
        self.group: FilteredItemGroup = self.group.filtered()
        self.search_bar = mcpython.client.rendering.ui.SearchBar.SearchBar(
            change_callback=lambda text: self.group.apply_raw_filter(f"(.*){text}(.*)"),
            enter_callback=lambda: self.search_bar.disable(),
            exit_callback=lambda: self.search_bar.disable(),
            enable_mouse_to_enter=True,
        )
        self.tab_icon = CreativeTabManager.UPPER_TAB
        self.tab_icon_selected = CreativeTabManager.UPPER_TAB_SELECTED

        self.need_reload = True

        def setNeedReload():
            self.need_reload = True

        import mcpython.common.data.ResourcePipe as ResourcePipe

        ResourcePipe.handler.register_data_processor(setNeedReload)

    async def on_deactivate(self):
        await super().on_deactivate()
        self.search_bar.disable()

    async def on_activate(self):
        await super().on_activate()
        self.group.apply_raw_filter("(.*)")

        if self.need_reload:
            self.need_reload = False

            self.group.entries.clear()

            for page in CT_MANAGER.pages:
                for tab in page:
                    if isinstance(tab, CreativeItemTab):
                        self.group.entries += tab.group.entries

            self.group.sort_after_item_name()
            self.update_rendering(True)


class CreativePlayerInventory(ICreativeView):
    TEXTURE_SIZE = 195 * 2, 136 * 2

    TEXTURE = None

    @classmethod
    async def reload(cls):
        cls.TEXTURE = texture_util.resize_image_pyglet(
            (
                await mcpython.engine.ResourceLoader.read_pyglet_image(
                    "minecraft:gui/container/creative_inventory/tab_inventory"
                )
            ).get_region(0, 120, 195, 136),
            cls.TEXTURE_SIZE,
        )

    def __init__(self):
        super().__init__()
        self.stack = ItemStack("minecraft:chest")
        self.tab_icon = CreativeTabManager.LOWER_TAB
        self.tab_icon_selected = CreativeTabManager.LOWER_TAB_SELECTED

    async def on_activate(self):
        await super().on_activate()
        shared.tick_handler.schedule_once(self.reload_config())

    def get_icon_stack(self) -> ItemStack:
        return self.stack

    def get_view_size(self) -> typing.Tuple[int, int]:
        return self.TEXTURE_SIZE

    def draw_at(self, position: typing.Tuple[int, int], hovering_slot=None):
        self.TEXTURE.blit(*position)

    async def create_slot_renderers(self):
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
            mcpython.client.gui.Slot.SlotTrashCan(),
        ]

    @staticmethod
    def get_config_file() -> str or None:
        return "assets/config/inventory/player_inventory_main_creative.json"


if not shared.IS_TEST_ENV:
    shared.tick_handler.schedule_once(CreativePlayerInventory.reload())


class CreativeTabManager:

    TAB_SIZE = 28 * 2, 30 * 2

    # todo: make this reload-able!
    UPPER_TAB = None
    UPPER_TAB_SELECTED = None
    LOWER_TAB = None
    LOWER_TAB_SELECTED = None

    @classmethod
    async def reload(cls):
        cls.UPPER_TAB = texture_util.resize_image_pyglet(
            getTabTexture().get_region(0, 224, 28, 30), cls.TAB_SIZE
        )
        cls.UPPER_TAB_SELECTED = texture_util.resize_image_pyglet(
            getTabTexture().get_region(0, 224 - 30, 28, 30), cls.TAB_SIZE
        )
        cls.LOWER_TAB = texture_util.resize_image_pyglet(
            getTabTexture().get_region(0, 164, 28, 30), cls.TAB_SIZE
        )
        cls.LOWER_TAB_SELECTED = texture_util.resize_image_pyglet(
            getTabTexture().get_region(0, 128, 28, 30), cls.TAB_SIZE
        )

    def __init__(self):
        self.pages: typing.List[typing.List[ICreativeView]] = [[]]
        self.inventory_instance = None
        self.search_instance = None
        self.saved_hotbars = None
        self.current_page = 0

        self.underlying_event_bus: mcpython.engine.event.EventBus.EventBus = (
            shared.event_handler.create_bus(active=False)
        )
        self.underlying_event_bus.subscribe("user:mouse:press", self.on_mouse_press)
        self.underlying_event_bus.subscribe("user:mouse:drag", self.on_mouse_move)
        self.underlying_event_bus.subscribe("user:mouse:motion", self.on_mouse_move)
        self.underlying_event_bus.subscribe("user:keyboard:press", self.on_key_press)

        self.hovering_tab = None

        self.page_left = (
            mcpython.client.rendering.ui.Buttons.arrow_button_left(
                (0, 0), lambda: self.increase_page(-1)
            )
            if not shared.IS_TEST_ENV
            else None
        )
        self.page_right = (
            mcpython.client.rendering.ui.Buttons.arrow_button_right(
                (0, 0), lambda: self.increase_page(1)
            )
            if not shared.IS_TEST_ENV
            else None
        )
        self.page_label = pyglet.text.Label(anchor_x="center", anchor_y="center")

        self.lower_left_position = 0, 0
        self.container_size = 1, 1

        self.current_tab: typing.Optional[ICreativeView] = None

    def is_multi_page(self):
        return len(self.pages) > 1

    async def on_key_press(self, button, mod):
        if shared.state_handler.global_key_bind_toggle:
            return

        if button == key.E:
            await shared.inventory_handler.hide(self.current_tab)
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

        if self.search_instance is None:
            self.search_instance = CreativeTabSearchBar(
                "Search", ItemStack("minecraft:paper")
            )

    async def activate(self):
        mcpython.common.event.TickHandler.handler.bind(
            self.underlying_event_bus.activate, 1
        )

        if self.is_multi_page():
            await self.page_left.activate()
            await self.page_right.activate()

    async def deactivate(self):
        self.underlying_event_bus.deactivate()
        await self.page_left.deactivate()
        await self.page_right.deactivate()

    async def on_mouse_press(self, mx, my, button, modifiers):
        if not button & mouse.LEFT:
            return

        tab = self.get_tab_at(mx, my)
        if tab is not None:
            await self.switch_to_tab(tab)

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

        self.draw_tab(
            self.search_instance,
            x + container_size[0] - self.TAB_SIZE[0],
            y + container_size[1],
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

    async def open(self):
        if self.current_tab is None:
            self.init_tabs_if_needed()

            await self.switch_to_tab(self.inventory_instance)
        else:
            await shared.inventory_handler.show(self.current_tab)

    def increase_page(self, count: int):
        previous = self.current_page
        self.current_page = max(0, min(self.current_page + count, len(self.pages) - 1))
        if previous != self.current_page:
            asyncio.get_event_loop().run_until_complete(
                self.switch_to_tab(self.pages[self.current_page][0])
            )

    async def switch_to_tab(self, tab: ICreativeView):
        if self.current_tab is not None:
            await shared.inventory_handler.hide(self.current_tab)
            self.current_tab.is_selected = False

        self.current_tab = tab

        tab.is_selected = True
        await shared.inventory_handler.show(tab)

    def print_missing(self):
        for page in self.pages:
            for tab in page:
                if isinstance(tab, CreativeItemTab):

                    entries = []

                    for itemstack in tab.group.entries:
                        if (
                            isinstance(itemstack, LazyClassLoadItemstack)
                            and itemstack.is_empty()
                        ):
                            entries.append("- " + itemstack.lazy_item_name)

                    if entries:
                        logger.write_into_container(
                            entries, header=f"Missing items in {tab.name}"
                        )


if not shared.IS_TEST_ENV:
    shared.tick_handler.schedule_once(CreativeTabManager.reload())


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


async def init():
    global BuildingBlocks, Decoration, Redstone, Transportation, Miscellaneous, Food, Tools, Weapons, Brewing, Test
    BuildingBlocks = CreativeItemTab(
        "Building Blocks",
        ItemStack("minecraft:bricks"),
        linked_tag="#minecraft:tab_building_blocks",
    )
    Decoration = CreativeItemTab(
        "Decoration",
        ItemStack("minecraft:peony"),
        linked_tag="#minecraft:tab_decoration",
    )
    Redstone = CreativeItemTab(
        "Redstone",
        ItemStack("minecraft:redstone"),
        linked_tag="#minecraft:tab_redstone",
    )
    Transportation = CreativeItemTab(
        "Transportation",
        ItemStack("minecraft:powered_rail"),
        linked_tag="#minecraft:tab_transportation",
    )
    Miscellaneous = CreativeItemTab(
        "Miscellaneous",
        ItemStack("minecraft:lava_bucket"),
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
        ItemStack("minecraft:golden_sword"),
        linked_tag="#minecraft:tab_weapons",
    )
    Brewing = CreativeItemTab(
        "Brewing", ItemStack("minecraft:barrier"), linked_tag="#minecraft:tab_brewing"
    )

    CT_MANAGER.add_tab(BuildingBlocks).add_tab(Decoration).add_tab(Redstone).add_tab(
        Transportation
    ).add_tab(Miscellaneous).add_tab(Food).add_tab(Tools).add_tab(Weapons).add_tab(
        Brewing
    )


if not shared.IS_TEST_ENV:
    shared.mod_loader("minecraft", "stage:item_groups:load")(init())
