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
import random
import typing

import mcpython.util.enums
from mcpython import shared

UV_ORDER = [
    mcpython.util.enums.EnumSide.UP,
    mcpython.util.enums.EnumSide.DOWN,
    mcpython.util.enums.EnumSide.WEST,
    mcpython.util.enums.EnumSide.EAST,
    mcpython.util.enums.EnumSide.NORTH,
    mcpython.util.enums.EnumSide.SOUTH,
]
SIDE_ORDER = [
    mcpython.util.enums.EnumSide.UP,
    mcpython.util.enums.EnumSide.DOWN,
    mcpython.util.enums.EnumSide.NORTH,
    mcpython.util.enums.EnumSide.SOUTH,
    mcpython.util.enums.EnumSide.WEST,
    mcpython.util.enums.EnumSide.EAST,
]

# representative for the order of uv insertion
UV_INDICES = [(0, 3, 2, 1), (1, 0, 3, 2)] + [(0, 1, 2, 3)] * 4


def get_model_choice(data, instance):
    if instance.block_state is None:
        entries = [decode_entry(e) for e in data]
        model, config, _ = entry = random.choices(
            entries, weights=[e[2] for e in entries]
        )[0]
        instance.block_state = entries.index(entry)
    else:
        model, config, _ = decode_entry(data[instance.block_state])
    return config, model


def decode_entry(data: typing.Dict[str, typing.Any]):
    model = data["model"]
    shared.model_handler.used_models.add(model)
    rotations = (
        data["x"] if "x" in data else 0,
        data["y"] if "y" in data else 0,
        data["z"] if "z" in data else 0,
    )
    return (
        model,
        {"rotation": rotations, "uv_lock": data.setdefault("uvlock", False)},
        1 if "weight" not in data else data["weight"],
    )


def calculate_default_layout_uvs(
    texture_size: typing.Tuple[int, int],
    box_size: typing.Tuple[int, int, int],
    offset: typing.Tuple[int, int],
):
    """
    Util method for calculating uv's
    Cache result whenever possible!
    WARNING: currently not working correctly
    :param texture_size: the size of the texture, a simple factor for the result
    :param box_size: the sizes of the box
    :param offset: an offset of the texture origin
    :return: the uv's, to pass to e.g. box models
    """

    sx, sy = texture_size
    dx, dy = offset
    x, y, z = box_size
    x -= 1
    y -= 1
    z -= 1

    return list(
        map(
            lambda e: (
                (e[0] + dx) / sx,
                (e[3] + dy) / sy,
                (e[2] + dx) / sx,
                (e[1] + dy) / sy,
            ),
            [
                (x + z, y, x + 2 * z, y + x),
                (x, y, x + z, y + x),
                (x, -1, x + z, y),
                (x + 2 * z, -1, 2 * x + 2 * z, y),
                (0, -1, z, y),
                (x + z, -1, x + 2 * z, y),
            ],
        )
    )
