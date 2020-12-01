"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
# todo: can we optimize file writing by using an small cache?

import os
import platform
import random
import sys
from datetime import datetime
import typing

import mcpython.common.config
from mcpython import shared
import traceback

# adapted from mc version 1.15.2, decompiled with mc-forge located under net.minecraft.crash.CrashReport
# added some extra entries
FUNNY_STRINGS = [
    "Who set us up the TNT?",
    "Everything's going to plan. No, really, that was supposed to happen.",
    "Uh... Did I do that?",
    "Oops.",
    "Why did you do that?",
    "I feel sad now :(",
    "My bad.",
    "I'm sorry, Dave.",
    "I let you down. Sorry :(",
    "On the bright side, I bought you a teddy bear!",
    "Daisy, daisy...",
    "Oh - I know what I did wrong!",
    "Hey, that tickles! Hehehe!",
    "I blame Dinnerbone. Seriously, he has here no fault",
    "You should try our sister game, Minceraft!",
    "Don't be sad. I'll do better next time, I promise!",
    "Don't be sad, have a hug! <3",
    "I just don't know what went wrong :(",
    "Shall we play a game?",
    "Quite honestly, I wouldn't worry myself about that.",
    "I bet Cylons wouldn't have this problem.",
    "Sorry :(",
    "Surprise! Haha. Well, this is awkward.",
    "Would you like a cupcake?",
    "Hi. I'm McPython, and I'm a crashaholic.",
    "Ooh. Shiny.",
    "This doesn't make any sense!",
    "Why is it breaking :(",
    "Don't do that.",
    "Ouch. That hurt :(",
    "You're mean.",
    "This is a token for 1 free hug. Redeem at your nearest Mojangsta: [~~HUG~~]",
    "There are four lights!",
    "But it works on my machine.",
    "You should try our mother game, Minecraft!",
    "Warning: your game has crashed!",
]

if not os.path.exists(shared.home + "/logs"):
    os.makedirs(shared.home + "/logs")

log_file_path = datetime.now().strftime(shared.home + "/logs/log_%d.%m.%y_%H.%M.%S.txt")
execute_able_source = os.path.dirname(sys.executable).replace("\\", "/")  # execute-able home


ESCAPE = {
    shared.local: "%LOCAL%",
    execute_able_source: "%PYTHON%",
    shared.home: "%HOME%",
    shared.build: "%BUILD%",
}
if "--no-log-escape" in sys.argv:  # should be escape these files?
    ESCAPE.clear()


def escape(string: str) -> str:
    """
    Helper function for escaping the string via above dict
    :param string: the string to escape
    :return: the escaped string
    """
    for key in ESCAPE:
        if key in string:
            string = string.replace(key, ESCAPE[key])
    return string


def println(*msg, sep=" ", end="\n", console=True, log_file=True):
    """
    will print an line into the console with formatting
    :param msg: the msg to log
    :param sep: how to separate the elements
    :param end: how the message ends
    :param console: if the data should be written into the console
    :param log_file: if the data should be written into the log file
    """
    now = datetime.now()
    msg = [
        "[{}][{}][{}][{}][{}][{}] ".format(
            now.year, now.month, now.day, now.hour, now.minute, now.second
        )
    ] + [escape(str(e).replace("\\", "/")) for e in msg]
    if console:
        print(*msg, sep=sep, end=end)
    if log_file:
        with open(log_file_path, mode="a") as f:
            print(*msg, sep=sep, end=end, file=f)


def transform_any_str_list(data: typing.Any) -> typing.List[str]:
    """
    Helper function for transforming any type to an list of strings split by "\n"
    :param data: the data to transform
    :return: the transformed data
    """
    if type(data) == str:
        return data.split("\n")
    if type(data) == list:
        return data
    return str(data).split("\n")


def write_into_container(
    *container_areas,
    style=("+", "-", "|"),
    header=None,
    outer_line_distance=2,
    empty_lines_before_separate=1
):
    """
    will print the given data into an container-like structure
    :param container_areas: an list of container areas. Every area must be str or list. Areas are separated by
        horizontal lines from each other.
    :param style: the style to print with
    :param header: the header line of the table, may be str or list
    :param outer_line_distance: the distance from the vertical line to the string, in spaces
    :param empty_lines_before_separate: the new lines between text and an horizontal line
    """
    areas = ([transform_any_str_list(header)] if header is not None else []) + [
        transform_any_str_list(a) for a in container_areas
    ]
    max_characters_in_line = (
        max(
            [
                max([len(str(line)) for line in area]) if len(area) > 0 else 0
                for area in areas
            ]
        )
        if len(areas) > 0
        else 0
    )
    horizontal_line = (
        style[0]
        + style[1] * (max_characters_in_line + 2 * outer_line_distance)
        + style[0]
    )
    empty_line = (
        style[2] + " " * (max_characters_in_line + 2 * outer_line_distance) + style[2]
    )
    for area in areas:
        println(horizontal_line)
        [println(empty_line) for _ in range(empty_lines_before_separate)]
        for line in area:
            println(style[2]
                    + " " * outer_line_distance
                    + str(line)
                    + " " * (outer_line_distance + max_characters_in_line - len(str(line)))
                    + style[2])
        [println(empty_line) for _ in range(empty_lines_before_separate)]
    println(horizontal_line)


def print_exception(*info):
    """
    write the current exception into console and log
    :param info: the info to use
    """
    pdata = [["EXCEPTION", random.choice(FUNNY_STRINGS)] + list(info)]
    sdata = traceback.format_stack()[:-2]
    data = escape(traceback.format_exc()).split("\n")
    pdata.append([data[0]] + "".join(sdata).split("\n") + data[1:-1])
    write_into_container(*pdata)
    if mcpython.common.config.WRITE_NOT_FORMATTED_EXCEPTION:
        println(info, log_file=False)
        traceback.print_stack()
        traceback.print_exc()


def print_stack(*info):
    """
    Prints the current calling stack into the console.
    :param info: info to provide
    """
    pdata = [["TRACE", random.choice(FUNNY_STRINGS)] + list(info)]
    sdata = traceback.format_stack()[:-2]
    pdata.append(escape("".join(sdata)).split("\n"))
    write_into_container(*pdata)


# todo: add function for this
println("""MCPYTHON version {} ({}) running on {}
machine: {}
processor: {}
python version: {}, implementation: {}
""".format(
    mcpython.common.config.VERSION_NAME,
    mcpython.common.config.VERSION_TYPE,
    platform.system().replace("Darwin", "MacOS"),
    platform.machine(),
    platform.processor(),
    platform.python_version(),
    platform.python_implementation(),
), console=False)


def add_funny_line():
    println(random.choice(FUNNY_STRINGS), console=False)
