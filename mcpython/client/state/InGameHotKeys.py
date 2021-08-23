import enum
import time

from mcpython import shared
from mcpython.util.annotation import onlyInClient
from pyglet.window import key


@onlyInClient()
class HotKeys(enum.Enum):
    # from https://minecraft.gamepedia.com/Debug_screen

    RELOAD_CHUNKS = ([key.F3, key.A], "hotkey:chunk_reload")
    GAME_CRASH = ([key.F3, key.C], "hotkey:game_crash", 10)
    GET_PLAYER_POSITION = ([key.F3, key.C], "hotkey:get_player_position")
    CLEAR_CHAT = ([key.F3, key.D], "hotkey:clear_chat")
    COPY_BLOCK_OR_ENTITY_DATA = ([key.F3, key.I], "hotkey:copy_block_or_entity_data")
    TOGGLE_GAMEMODE_1_3 = ([key.F3, key.N], "hotkey:gamemode_1-3_toggle")
    RELOAD_TEXTURES = ([key.F3, key.T], "hotkey:reload_textures")

    def __init__(self, keys, event, min_press=0):
        self.keys = keys
        self.event = event
        self.active = False
        self.min_press = min_press
        self.press_start = 0

    def check(self):
        status = all([shared.window.keys[symbol] for symbol in self.keys])
        if self.active and not status:
            self.active = False
            if time.time() - self.press_start < self.min_press:
                return
            shared.event_handler.call(self.event)
        if not self.active and status:
            self.active = True
            self.press_start = time.time()

    def blocks(self, symbol, mods) -> bool:
        return (
            symbol in self.keys and self.check()
        )  # is this key a) affected by this and b) is our combo active


ALL_KEY_COMBOS = [
    HotKeys.RELOAD_CHUNKS,
    HotKeys.GAME_CRASH,
    HotKeys.GET_PLAYER_POSITION,
    HotKeys.CLEAR_CHAT,
    HotKeys.COPY_BLOCK_OR_ENTITY_DATA,
    HotKeys.TOGGLE_GAMEMODE_1_3,
    HotKeys.RELOAD_TEXTURES,
]
