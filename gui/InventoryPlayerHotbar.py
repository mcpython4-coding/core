"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import gui.Inventory
import gui.InventoryHandler
import gui.Slot
import pyglet
import ResourceLocator
import time
import util.opengl


class InventoryPlayerHotbar(gui.Inventory.Inventory):
    """
    main inventory for the hotbar
    """

    def __init__(self):
        gui.Inventory.Inventory.__init__(self)
        self.selected_sprite = pyglet.sprite.Sprite(ResourceLocator.read("build/texture/gui/selected_slot.png",
                                                                         "pyglet"))
        self.lable = pyglet.text.Label(color=(255, 255, 255, 255))
        self.last_index = 0
        self.last_item = None
        self.time_since_last_change = 0

        self.xp_level_lable = pyglet.text.Label(color=(92, 133, 59), anchor_x="center")

    @staticmethod
    def get_config_file():
        return "assets/config/inventory/playerinventoryhotbar.json"

    def is_blocking_interactions(self) -> bool:
        return False

    def create_slots(self) -> list:
        return [gui.Slot.Slot() for _ in range(9)]

    def on_activate(self):
        pass

    def on_deactivate(self):
        pass

    def draw(self, hoveringslot=None):
        self.on_draw_background()
        x, y = self._get_position()
        if self.bgsprite:
            self.bgsprite.position = (x + self.bg_image_pos[0], y + self.bg_image_pos[1])
            self.bgsprite.draw()
        self.on_draw_over_backgroundimage()
        for slot in self.slots:
            slot.draw(x, y)  # change to default implementation: do NOT render hovering entry
        self.on_draw_over_image()
        for slot in self.slots:
            slot.draw_lable(x, y)
        self.on_draw_overlay()

    def on_draw_over_image(self):
        slot = G.world.get_active_player().get_active_inventory_slot()
        x, y = slot.position
        dx, dy = tuple(self.config["selected_delta"]) if "selected_delta" in self.config else (8, 8)
        x -= dx
        y -= dy
        dx, dy = self._get_position()
        x += dx
        y += dy
        self.selected_sprite.position = (x, y)
        self.selected_sprite.draw()

        selected_slot = G.world.get_active_player().get_active_inventory_slot()

        if self.last_index != G.world.get_active_player().active_inventory_slot or \
                selected_slot.get_itemstack().get_item_name() != self.last_item:
            self.time_since_last_change = time.time()
            self.last_index = G.world.get_active_player().active_inventory_slot
            self.last_item = selected_slot.get_itemstack().get_item_name()

        pyglet.gl.glColor3d(1., 1., 1.)
        if G.world.get_active_player().gamemode in (0, 2):
            self.draw_hearts(x, y)
            self.draw_hunger(x, y)
            self.draw_xp_level(x, y)
            if G.world.get_active_player().armor_level > 0:
                self.draw_armor(x, y)

        if selected_slot.get_itemstack().get_item_name() and time.time() - self.time_since_last_change <= 5.:
            self.lable.text = str(selected_slot.get_itemstack().get_item_name())
            self.lable.x = round(G.window.get_size()[0] // 2 - self.lable.content_width // 2)
            self.lable.y = 90
            self.lable.draw()

    def draw_hearts(self, hx, hy):
        wx, _ = G.window.get_size()
        x = wx // 2 - 10 * 16 - 22
        y = hy + 75
        hearts = round(G.world.get_active_player().hearts)
        for _ in range(10):
            G.world.get_active_player().iconparts[0][2].blit(x-1, y-1)
            if hearts > 0:
                G.world.get_active_player().iconparts[0][int(hearts == 1)].blit(x, y)
                hearts -= 2
            x += 16

    def draw_hunger(self, hx, hy):
        wx, _ = G.window.get_size()
        x = wx // 2 + 22 + 10 * 16
        y = hy + 75
        hunger = round(G.world.get_active_player().hunger)
        for _ in range(10):
            G.world.get_active_player().iconparts[1][2].blit(x+1, y)
            if hunger > 0:
                G.world.get_active_player().iconparts[1][int(hunger == 1)].blit(x, y)
                hunger -= 2
            x -= 16

    def draw_xp_level(self, hx, hy):
        wx, _ = G.window.get_size()
        x = wx // 2 - 182
        y = hy + 55
        G.world.get_active_player().iconparts[3][0].blit(x, y)
        active_progress = G.world.get_active_player().xp / G.world.get_active_player().get_needed_xp_for_next_level()
        G.world.get_active_player().iconparts[3][1].get_region(x=0, y=0, height=10, width=round(362*active_progress)+1).blit(x, y)
        if G.world.get_active_player().xp_level != 0:
            self.lable.x = wx // 2
            self.lable.y = hy + 65
            self.lable.text = str(G.world.get_active_player().xp_level)
            self.lable.draw()

    def draw_armor(self, hx, hy):
        wx, _ = G.window.get_size()
        x = wx // 2 - 10 * 16 - 22
        y = hy + 95
        armor = round(G.world.get_active_player().armor_level)
        for _ in range(10):
            G.world.get_active_player().iconparts[2][2].blit(x, y)
            if armor > 0:
                G.world.get_active_player().iconparts[2][int(armor == 1)].blit(x, y)
                armor -= 2
            x += 16

    def is_closable_by_escape(self) -> bool: return False

    def is_always_open(self) -> bool: return True

