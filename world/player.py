"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4-pre6.jar"""
import globals as G
import gui.InventoryPlayerHotbar


class Player:
    GAMEMODE_DICT = {
        "survival": 0,
        "creative": 1,
        "adventure": 2,
        "spectator": 3
    }

    def __init__(self, name):
        self.name = name
        self.gamemode = None
        self.set_gamemode(1)
        self.harts = 20
        self.hunger = 20
        self.xp = 0
        self.xp_level = 0

        self.inventorys = {
            "hotbar": gui.InventoryPlayerHotbar.InventoryPlayerHotbar()
        }

        G.player = self

    def set_gamemode(self, gamemode: int or str):
        if gamemode in self.GAMEMODE_DICT:
            gamemode = self.GAMEMODE_DICT[gamemode]
        self.gamemode = gamemode
        if gamemode == 0:
            G.window.flying = False
        elif gamemode == 1:
            pass
        elif gamemode == 2:
            G.window.flying = False
        elif gamemode == 3:
            G.window.flying = True
        else:
            raise ValueError("can't cast {} to valid gamemode".format(gamemode))

    def _get_needed_xp_for_next_level(self) -> int:
        if self.xp_level < 16:
            return self.xp_level * 2 + 5
        elif self.xp_level < 30:
            return 37 + (self.xp_level - 15) * 5
        else:
            return 107 + (self.xp_level - 29) * 9

    def add_xp(self, xp: int):
        while xp > 0:
            if self.xp + xp < self._get_needed_xp_for_next_level():
                self.xp += xp
                return
            elif xp > self._get_needed_xp_for_next_level():
                xp -= self._get_needed_xp_for_next_level()
                self.xp_level += 1
            else:
                xp = xp - (self._get_needed_xp_for_next_level() - self.xp)
                self.xp_level += 1

    def add_xp_level(self, xp_levels: int):
        self.xp_level += 1

