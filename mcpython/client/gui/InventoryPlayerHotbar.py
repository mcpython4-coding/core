"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared, logger
import mcpython.client.gui.Inventory
import mcpython.client.gui.InventoryHandler
import mcpython.client.gui.Slot
import pyglet
import mcpython.ResourceLoader
import time
import mcpython.util.opengl
import mcpython.common.event.EventHandler
import sys
import mcpython.ResourceLoader
import PIL.Image
import mcpython.util.texture


class _TEXTURES:
    hearts = []
    armor = []
    hunger = []
    bar = None
    bar_size = None
    selection = None

    xp_bars = []


TEXTURES = _TEXTURES


def reload():
    try:
        base: pyglet.image.AbstractImage = mcpython.ResourceLoader.read_pyglet_image(
            "gui/icons"
        )
    except:
        logger.print_exception("[FATAL] failed to load hotbar image")
        sys.exit(-1)

    def _get_tex_region(rx, ry, rex, rey):
        image = base.get_region(
            round(rx / 255 * base.width),
            round((1 - rey / 255) * base.height),
            round((rex - rx) / 255 * base.width),
            round(((rey - ry) / 255) * base.height),
        )
        return image

    class Textures:
        # todo: make %-based

        hearts = [
            [  # base, regenerate
                _get_tex_region(16, 0, 25, 9),
                _get_tex_region(25, 0, 34, 9),
                _get_tex_region(34, 0, 43, 9),
                _get_tex_region(43, 0, 52, 9),
            ],
            [  # normal, hit
                _get_tex_region(52, 0, 61, 9),
                _get_tex_region(61, 0, 70, 9),
                _get_tex_region(70, 0, 79, 9),
                _get_tex_region(79, 0, 88, 9),
            ],
            [  # poison, hit
                _get_tex_region(88, 0, 97, 9),
                _get_tex_region(97, 0, 106, 9),
                _get_tex_region(106, 0, 115, 9),
                _get_tex_region(115, 0, 124, 9),
            ],
            [  # wither, hit
                _get_tex_region(124, 0, 133, 9),
                _get_tex_region(133, 0, 142, 9),
                _get_tex_region(142, 0, 151, 9),
                _get_tex_region(151, 0, 160, 9),
            ],
            [  # absorption
                _get_tex_region(160, 0, 169, 9),
                _get_tex_region(169, 0, 178, 9),
            ],
        ]

        armor = [
            _get_tex_region(16, 9, 25, 18),
            _get_tex_region(25, 9, 34, 18),
            _get_tex_region(34, 9, 43, 18),
        ]

        hunger = [
            [  # background
                _get_tex_region(16, 27, 25, 36),
                _get_tex_region(25, 27, 34, 36),
                _get_tex_region(34, 27, 43, 36),
                _get_tex_region(43, 27, 52, 36),
            ],
            [  # normal, regen
                _get_tex_region(52, 27, 61, 36),
                _get_tex_region(61, 27, 70, 36),
                _get_tex_region(70, 27, 79, 36),
                _get_tex_region(79, 27, 88, 36),
            ],
            [  # hunger, regen
                _get_tex_region(88, 27, 97, 36),
                _get_tex_region(97, 27, 106, 36),
                _get_tex_region(106, 27, 115, 36),
                _get_tex_region(115, 27, 124, 36),
            ],
        ]

        base = mcpython.ResourceLoader.read_image("minecraft:gui/widgets")

        bar = mcpython.util.texture.to_pyglet_image(
            base.crop((0, 0, 182, 22)).resize((364, 44), PIL.Image.NEAREST)
        )
        bar_size = (364, 44)
        selection = mcpython.util.texture.to_pyglet_image(
            base.crop((0, 22, 24, 46)).resize((48, 48), PIL.Image.NEAREST)
        )

        base = mcpython.ResourceLoader.read_image("minecraft:gui/icons")
        xp_bars = [
            mcpython.util.texture.to_pyglet_image(
                base.crop((0, 69, 182, 74)).resize((364, 10), PIL.Image.NEAREST)
            ),
            mcpython.util.texture.to_pyglet_image(
                base.crop((0, 64, 182, 69)).resize((364, 10), PIL.Image.NEAREST)
            ),
        ]

    global TEXTURES
    TEXTURES = Textures


mcpython.common.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
    "data:reload:work", reload
)
reload()


class InventoryPlayerHotbar(mcpython.client.gui.Inventory.Inventory):
    """
    main inventory for the hotbar
    """

    def __init__(self, player):
        super().__init__()
        self.player = player
        self.lable = pyglet.text.Label(color=(255, 255, 255, 255))
        self.last_index = 0
        self.last_item = None
        self.time_since_last_change = 0

        self.xp_level_lable = pyglet.text.Label(color=(92, 133, 59), anchor_x="center")

    @staticmethod
    def get_config_file():
        return "assets/config/inventory/player_inventory_hotbar.json"

    def is_blocking_interactions(self) -> bool:
        return False

    def create_slots(self) -> list:
        return [mcpython.client.gui.Slot.Slot() for _ in range(9)]

    def on_activate(self):
        pass

    def on_deactivate(self):
        pass

    def draw(self, hovering_slot=None):
        self.bg_image_size = TEXTURES.bar_size
        x, y = self.get_position()
        y += 40
        TEXTURES.bar.blit(x, y)
        for slot in self.slots:
            slot.draw(
                x, y
            )  # change to default implementation: do NOT render hovering entry
        selected_slot = shared.world.get_active_player().get_active_inventory_slot()
        x, y = selected_slot.position
        dx, dy = (
            tuple(self.config["selected_delta"])
            if "selected_delta" in self.config
            else (8, 8)
        )
        x -= dx
        y -= dy
        dx, dy = self.get_position()
        x += dx
        y += dy

        TEXTURES.selection.blit(x, y + 39)

        if (
            self.last_index != shared.world.get_active_player().active_inventory_slot
            or selected_slot.get_itemstack().get_item_name() != self.last_item
        ):
            self.time_since_last_change = time.time()
            self.last_index = shared.world.get_active_player().active_inventory_slot
            self.last_item = selected_slot.get_itemstack().get_item_name()

        pyglet.gl.glColor3d(1.0, 1.0, 1.0)
        if shared.world.get_active_player().gamemode in (0, 2):
            x, y = self.get_position()
            y += 40
            self.draw_hearts(x, y)
            self.draw_hunger(x, y)
            self.draw_xp_level(x, y)
            if shared.world.get_active_player().armor_level > 0:
                self.draw_armor(x, y)

        if (
            selected_slot.get_itemstack().get_item_name()
            and time.time() - self.time_since_last_change <= 5.0
        ):
            self.lable.text = str(selected_slot.get_itemstack().get_item_name())
            self.lable.x = round(
                shared.window.get_size()[0] // 2 - self.lable.content_width // 2
            )
            self.lable.y = 90
            self.lable.draw()
        for slot in self.slots:
            slot.draw_label()

    def draw_hearts(self, hx, hy):
        wx, _ = shared.window.get_size()
        x = wx // 2 - 10 * 16 - 22
        y = hy + 75
        hearts = round(shared.world.get_active_player().hearts)
        for _ in range(10):
            TEXTURES.hearts[0][0].blit(x, y, width=18, height=18)
            if hearts > 0:
                TEXTURES.hearts[1][bool(hearts == 1)].blit(x, y, width=18, height=18)
                hearts -= 2
            x += 16

    def draw_hunger(self, hx, hy):
        wx, _ = shared.window.get_size()
        x = wx // 2 + 22 + 10 * 16
        y = hy + 75
        hunger = round(shared.world.get_active_player().hunger)
        for _ in range(10):
            TEXTURES.hunger[0][0].blit(x, y, width=18, height=18)
            if hunger > 0:
                TEXTURES.hunger[1][int(hunger == 1)].blit(x, y, width=18, height=18)
                hunger -= 2
            x -= 16

    def draw_xp_level(self, hx, hy):
        wx, _ = shared.window.get_size()
        x = wx // 2 - 182
        y = hy + 55
        TEXTURES.xp_bars[1].blit(x, y)
        active_progress = (
            shared.world.get_active_player().xp
            / shared.world.get_active_player().get_needed_xp_for_next_level()
        )
        TEXTURES.xp_bars[1].get_region(
            x=0, y=0, height=10, width=round(362 * active_progress) + 1
        ).blit(x, y)
        if shared.world.get_active_player().xp_level != 0:
            self.lable.x = wx // 2
            self.lable.y = hy + 65
            self.lable.text = str(shared.world.get_active_player().xp_level)
            self.lable.draw()

    def draw_armor(self, hx, hy):
        wx, _ = shared.window.get_size()
        x = wx // 2 - 10 * 16 - 22
        y = hy + 95
        armor = round(shared.world.get_active_player().armor_level)
        for _ in range(10):
            TEXTURES.armor[0].blit(x, y, width=18, height=18)
            if armor > 0:
                TEXTURES.armor[int(armor != 1) + 1].blit(x, y, width=18, height=18)
                armor -= 2
            x += 16

    def is_closable_by_escape(self) -> bool:
        return False

    def is_always_open(self) -> bool:
        return True
