"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import traceback
from datetime import datetime
import globals as G
import os
import sys
import config
import platform
import random


# adapted from mc version 1.15.2, decompiled with mc-forge located under net.minecraft.crash.CrashReport
# added some extra entries
FUNNY_STRINGS = [
    "Who set us up the TNT?", "Everything's going to plan. No, really, that was supposed to happen.",
    "Uh... Did I do that?", "Oops.", "Why did you do that?", "I feel sad now :(", "My bad.", "I'm sorry, Dave.",
    "I let you down. Sorry :(", "On the bright side, I bought you a teddy bear!", "Daisy, daisy...",
    "Oh - I know what I did wrong!", "Hey, that tickles! Hehehe!", "I blame Dinnerbone. Seriously, he has here no fault",
    "You should try our sister game, Minceraft!", "Don't be sad. I'll do better next time, I promise!",
    "Don't be sad, have a hug! <3", "I just don't know what went wrong :(", "Shall we play a game?",
    "Quite honestly, I wouldn't worry myself about that.", "I bet Cylons wouldn't have this problem.",
    "Sorry :(", "Surprise! Haha. Well, this is awkward.",
    "Would you like a cupcake?", "Hi. I'm McPython, and I'm a crashaholic.", "Ooh. Shiny.",
    "This doesn't make any sense!", "Why is it breaking :(", "Don't do that.", "Ouch. That hurt :(",
    "You're mean.", "This is a token for 1 free hug. Redeem at your nearest Mojangsta: [~~HUG~~]",
    "There are four lights!", "But it works on my machine.", "You should try our mother game, Minecraft!",
    "Warning: your game has crashed!"
]


if not os.path.exists(G.local+"/logs"):
    os.makedirs(G.local+"/logs")


log_file = datetime.now().strftime(G.local+"/logs/log_%d.%m.%y_%H.%M.%S.txt")
inter_home = os.path.dirname(sys.executable).replace("\\", "/")


def println(*msg, sep=" ", end="\n", write_into_console=True):
    if write_into_console: print(*msg, sep=sep, end=end)
    with open(log_file, mode="a") as f:
        # print(datetime.now().strftime("\n[timestamp: %H.%M.%S]"), file=f)
        print(*msg, sep=sep, end=end, file=f)


def write_exception(*info):
    println("[ERROR][EXCEPTION] gotten exception", write_into_console=False)
    println(*info, write_into_console=False)
    data = traceback.format_exc().replace("\\", "/").replace(G.local, "%LOCAL%").replace(inter_home, "%PYTHON%")
    println(data, write_into_console=False)


println("""MCPYTHON version {} ({}) running on {}
machine: {}
processor: {}
python version: {}, implementation: {}
""".format(
    config.VERSION_NAME, config.VERSION_TYPE, platform.system().replace("Darwin", "MacOS"), platform.machine(),
    platform.processor(), platform.python_version(), platform.python_implementation()
), write_into_console=False)


def add_funny_line():
    println(random.choice(FUNNY_STRINGS), write_into_console=False)

