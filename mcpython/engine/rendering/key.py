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
# ----------------------------------------------------------------------------
# pyglet
# Copyright (c) 2006-2008 Alex Holkner
# Copyright (c) 2008-2021 pyglet contributors
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of pyglet nor the names of its
#    contributors may be used to endorse or promote products
#    derived from this software without specific prior written
#    permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------

"""Key constants and utilities for pyglet.window.

Usage::

    from pyglet.window import Window
    from pyglet.window import key

    window = Window()

    @window.event
    def on_key_press(symbol, modifiers):
        # Symbolic names:
        if symbol == key.RETURN:

        # Alphabet keys:
        elif symbol == key.Z:

        # Number keys:
        elif symbol == key._1:

        # Number keypad keys:
        elif symbol == key.NUM_1:

        # Modifiers:
        if modifiers & key.MOD_CTRL:

"""

from pyglet import compat_platform


class KeyStateHandler(dict):
    """Simple handler that tracks the state of keys on the keyboard. If a
    key is pressed then this handler holds a True value for it.

    For example::

        >>> win = window.Window
        >>> keyboard = key.KeyStateHandler()
        >>> win.push_handlers(keyboard)

        # Hold down the "up" arrow...

        >>> keyboard[key.UP]
        True
        >>> keyboard[key.DOWN]
        False

    """

    def on_key_press(self, symbol, modifiers):
        self[symbol] = True

    def on_key_release(self, symbol, modifiers):
        self[symbol] = False

    def __getitem__(self, key):
        return self.get(key, False)


def modifiers_string(modifiers):
    """Return a string describing a set of modifiers.

    Example::

        >>> modifiers_string(MOD_SHIFT | MOD_CTRL)
        'MOD_SHIFT|MOD_CTRL'

    :Parameters:
        `modifiers` : int
            Bitwise combination of modifier constants.

    :rtype: str
    """
    mod_names = []
    if modifiers & MOD_SHIFT:
        mod_names.append("MOD_SHIFT")
    if modifiers & MOD_CTRL:
        mod_names.append("MOD_CTRL")
    if modifiers & MOD_ALT:
        mod_names.append("MOD_ALT")
    if modifiers & MOD_CAPSLOCK:
        mod_names.append("MOD_CAPSLOCK")
    if modifiers & MOD_NUMLOCK:
        mod_names.append("MOD_NUMLOCK")
    if modifiers & MOD_SCROLLLOCK:
        mod_names.append("MOD_SCROLLLOCK")
    if modifiers & MOD_COMMAND:
        mod_names.append("MOD_COMMAND")
    if modifiers & MOD_OPTION:
        mod_names.append("MOD_OPTION")
    if modifiers & MOD_FUNCTION:
        mod_names.append("MOD_FUNCTION")
    return "|".join(mod_names)


def symbol_string(symbol):
    """Return a string describing a key symbol.

    Example::

        >>> symbol_string(BACKSPACE)
        'BACKSPACE'

    :Parameters:
        `symbol` : int
            Symbolic key constant.

    :rtype: str
    """
    if symbol < 1 << 32:
        return _key_names.get(symbol, str(symbol))
    else:
        return "user_key(%x)" % (symbol >> 32)


def motion_string(motion):
    """Return a string describing a text motion.

    Example::

        >>> motion_string(MOTION_NEXT_WORD)
        'MOTION_NEXT_WORD'

    :Parameters:
        `motion` : int
            Text motion constant.

    :rtype: str
    """
    return _motion_names.get(motion, str(motion))


def user_key(scancode):
    """Return a key symbol for a key not supported by pyglet.

    This can be used to map virtual keys or scancodes from unsupported
    keyboard layouts into a machine-specific symbol.  The symbol will
    be meaningless on any other machine, or under a different keyboard layout.

    Applications should use user-keys only when user explicitly binds them
    (for example, mapping keys to actions in a game options screen).
    """
    assert scancode > 0
    return scancode << 32


# Modifier mask constants
MOD_SHIFT = 1 << 0
MOD_CTRL = 1 << 1
MOD_ALT = 1 << 2
MOD_CAPSLOCK = 1 << 3
MOD_NUMLOCK = 1 << 4
MOD_WINDOWS = 1 << 5
MOD_COMMAND = 1 << 6
MOD_OPTION = 1 << 7
MOD_SCROLLLOCK = 1 << 8
MOD_FUNCTION = 1 << 9

#: Accelerator modifier.  On Windows and Linux, this is ``MOD_CTRL``, on
#: Mac OS X it's ``MOD_COMMAND``.
MOD_ACCEL = MOD_CTRL
if compat_platform == "darwin":
    MOD_ACCEL = MOD_COMMAND


# Key symbol constants

# ASCII commands
BACKSPACE = 0xFF08
TAB = 0xFF09
LINEFEED = 0xFF0A
CLEAR = 0xFF0B
RETURN = 0xFF0D
ENTER = 0xFF0D  # synonym
PAUSE = 0xFF13
SCROLLLOCK = 0xFF14
SYSREQ = 0xFF15
ESCAPE = 0xFF1B
# SPACE = 0xFF20

# Cursor control and motion
HOME = 0xFF50
LEFT = 0xFF51
UP = 0xFF52
RIGHT = 0xFF53
DOWN = 0xFF54
PAGEUP = 0xFF55
PAGEDOWN = 0xFF56
END = 0xFF57
BEGIN = 0xFF58

# Misc functions
DELETE = 0xFFFF
SELECT = 0xFF60
PRINT = 0xFF61
EXECUTE = 0xFF62
INSERT = 0xFF63
UNDO = 0xFF65
REDO = 0xFF66
MENU = 0xFF67
FIND = 0xFF68
CANCEL = 0xFF69
HELP = 0xFF6A
BREAK = 0xFF6B
MODESWITCH = 0xFF7E
SCRIPTSWITCH = 0xFF7E
FUNCTION = 0xFFD2

# Text motion constants: these are allowed to clash with key constants
MOTION_UP = UP
MOTION_RIGHT = RIGHT
MOTION_DOWN = DOWN
MOTION_LEFT = LEFT
MOTION_NEXT_WORD = 1
MOTION_PREVIOUS_WORD = 2
MOTION_BEGINNING_OF_LINE = 3
MOTION_END_OF_LINE = 4
MOTION_NEXT_PAGE = PAGEDOWN
MOTION_PREVIOUS_PAGE = PAGEUP
MOTION_BEGINNING_OF_FILE = 5
MOTION_END_OF_FILE = 6
MOTION_BACKSPACE = BACKSPACE
MOTION_DELETE = DELETE

# Number pad
NUMLOCK = 0xFF7F
NUM_SPACE = 0xFF80
NUM_TAB = 0xFF89
NUM_ENTER = 0xFF8D
NUM_F1 = 0xFF91
NUM_F2 = 0xFF92
NUM_F3 = 0xFF93
NUM_F4 = 0xFF94
NUM_HOME = 0xFF95
NUM_LEFT = 0xFF96
NUM_UP = 0xFF97
NUM_RIGHT = 0xFF98
NUM_DOWN = 0xFF99
NUM_PRIOR = 0xFF9A
NUM_PAGE_UP = 0xFF9A
NUM_NEXT = 0xFF9B
NUM_PAGE_DOWN = 0xFF9B
NUM_END = 0xFF9C
NUM_BEGIN = 0xFF9D
NUM_INSERT = 0xFF9E
NUM_DELETE = 0xFF9F
NUM_EQUAL = 0xFFBD
NUM_MULTIPLY = 0xFFAA
NUM_ADD = 0xFFAB
NUM_SEPARATOR = 0xFFAC
NUM_SUBTRACT = 0xFFAD
NUM_DECIMAL = 0xFFAE
NUM_DIVIDE = 0xFFAF

NUM_0 = 0xFFB0
NUM_1 = 0xFFB1
NUM_2 = 0xFFB2
NUM_3 = 0xFFB3
NUM_4 = 0xFFB4
NUM_5 = 0xFFB5
NUM_6 = 0xFFB6
NUM_7 = 0xFFB7
NUM_8 = 0xFFB8
NUM_9 = 0xFFB9

# Function keys
F1 = 0xFFBE
F2 = 0xFFBF
F3 = 0xFFC0
F4 = 0xFFC1
F5 = 0xFFC2
F6 = 0xFFC3
F7 = 0xFFC4
F8 = 0xFFC5
F9 = 0xFFC6
F10 = 0xFFC7
F11 = 0xFFC8
F12 = 0xFFC9
F13 = 0xFFCA
F14 = 0xFFCB
F15 = 0xFFCC
F16 = 0xFFCD
F17 = 0xFFCE
F18 = 0xFFCF
F19 = 0xFFD0
F20 = 0xFFD1

# Modifiers
LSHIFT = 0xFFE1
RSHIFT = 0xFFE2
LCTRL = 0xFFE3
RCTRL = 0xFFE4
CAPSLOCK = 0xFFE5
LMETA = 0xFFE7
RMETA = 0xFFE8
LALT = 0xFFE9
RALT = 0xFFEA
LWINDOWS = 0xFFEB
RWINDOWS = 0xFFEC
LCOMMAND = 0xFFED
RCOMMAND = 0xFFEE
LOPTION = 0xFFEF
ROPTION = 0xFFF0

# Latin-1
SPACE = 0x020
EXCLAMATION = 0x021
DOUBLEQUOTE = 0x022
HASH = 0x023
POUND = 0x023  # synonym
DOLLAR = 0x024
PERCENT = 0x025
AMPERSAND = 0x026
APOSTROPHE = 0x027
PARENLEFT = 0x028
PARENRIGHT = 0x029
ASTERISK = 0x02A
PLUS = 0x02B
COMMA = 0x02C
MINUS = 0x02D
PERIOD = 0x02E
SLASH = 0x02F
_0 = 0x030
_1 = 0x031
_2 = 0x032
_3 = 0x033
_4 = 0x034
_5 = 0x035
_6 = 0x036
_7 = 0x037
_8 = 0x038
_9 = 0x039
COLON = 0x03A
SEMICOLON = 0x03B
LESS = 0x03C
EQUAL = 0x03D
GREATER = 0x03E
QUESTION = 0x03F
AT = 0x040
BRACKETLEFT = 0x05B
BACKSLASH = 0x05C
BRACKETRIGHT = 0x05D
ASCIICIRCUM = 0x05E
UNDERSCORE = 0x05F
GRAVE = 0x060
QUOTELEFT = 0x060
A = 0x061
B = 0x062
C = 0x063
D = 0x064
E = 0x065
F = 0x066
G = 0x067
H = 0x068
I = 0x069
J = 0x06A
K = 0x06B
L = 0x06C
M = 0x06D
N = 0x06E
O = 0x06F
P = 0x070
Q = 0x071
R = 0x072
S = 0x073
T = 0x074
U = 0x075
V = 0x076
W = 0x077
X = 0x078
Y = 0x079
Z = 0x07A
BRACELEFT = 0x07B
BAR = 0x07C
BRACERIGHT = 0x07D
ASCIITILDE = 0x07E

_key_names = {}
_motion_names = {}
for _name, _value in locals().copy().items():
    if _name[:2] != "__" and _name.upper() == _name and not _name.startswith("MOD_"):
        if _name.startswith("MOTION_"):
            _motion_names[_value] = _name
        else:
            _key_names[_value] = _name
