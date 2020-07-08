"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""

import json
import os


local = os.path.dirname(os.path.dirname(__file__))


def transform_profile(file):
    with open(file) as f: data = f.readlines()[1:]
    table = {}
    for line in data:
        if line.startswith("//") or line.startswith("event subscription of"): continue
        sp = line.split(" ")
        if line.startswith("event call of"):
            function = " ".join(sp[3:-4])
            time = float(sp[-3][:-1])
            table.setdefault(function, {"times": []})["times"].append(time)
    for entry in table.keys():
        times = table[entry]["times"]
        table[entry]["avg"] = sum(times) / len(times)
    with open(local+"/debug/"+file.split("/")[-1]+".json", mode="w") as f:
        json.dump(table, f)


if __name__ == "__main__":
    for profile in os.listdir(local+"/debug"):
        if profile.startswith("eventbus_") and profile.endswith(".txt"):
            transform_profile(local+"/debug/"+profile)
