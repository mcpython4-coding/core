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
import json
import os
import shutil
import zipfile

local = os.path.dirname(__file__)


print("collecting files...")

if os.path.exists(local + "/tmp"):
    shutil.rmtree(local + "/tmp")
os.makedirs(local + "/tmp")

pre = len(local + "/source/")

for root, dirs, files in os.walk(local + "/source"):
    for f in files:
        file = os.path.join(root, f)
        localized = file[pre:]
        target = local + "/tmp/" + localized
        d = os.path.dirname(target)
        if not os.path.exists(d):
            os.makedirs(d)
        shutil.copy(file, target)

if os.path.isdir(local + "/api"):
    for folder in os.listdir(local + "/api"):
        root_l = len(local + "/api/" + folder) + 1
        for root, dirs, files in os.walk(local + "/api/" + folder):
            for f in files:
                file = os.path.join(root, f)
                localized = file[root_l:]
                target = localized + "/tmp/" + localized
                d = os.path.dirname(target)
                if not os.path.exists(d):
                    os.makedirs(d)
                shutil.copy(file, target)


if not os.path.isdir(local + "/builds"):
    os.makedirs(local + "/builds")

name = input("name of the build? ")

print("creating dev-version...")

with zipfile.ZipFile(local + "/builds/" + name + "_dev.zip", mode="w") as instance:
    root_l = len(local + "/tmp/")
    for root, dirs, files in os.walk(local + "/tmp"):
        for f in files:
            file = os.path.join(root, f)
            localized = file[root_l:]
            instance.write(file, localized)

print("filtering code...")


root_l = len(local + "/tmp/")
for root, dirs, files in os.walk(local + "/tmp"):
    for loc in files:
        if not loc.endswith(".py"):
            continue  # only python files to work with
        file = os.path.join(root, loc)
        print("transforming file '{}'".format(file[root_l:]))
        with open(file) as f:
            data = f.readlines()

        result = []  # here we store the context
        in_multi_line_comment = 0
        for line_n, line in enumerate(data):
            line = line[:-1]
            multi_line_change = False
            index = None
            in_string = 0
            skip_entries = 0
            for i, e in enumerate(line):
                if e == '"' and not (i > 0 and line[i - 1] == "\\"):
                    if len(line) > i + 1 and line[i : i + 3] == '"""':
                        if in_multi_line_comment == 0:
                            in_multi_line_comment = 1
                            line = line[:index]
                            multi_line_change = True
                        elif in_multi_line_comment == 1:
                            in_multi_line_comment = 0
                            multi_line_change = True
                    elif in_string == 0:
                        in_string = 1
                    elif in_string == 1:
                        in_string = 0
                elif e == "'" and not (i > 0 and line[i - 1] == "\\"):
                    if len(line) > i + 1 and line[i : i + 3] == "'''":
                        if in_multi_line_comment == 0:
                            in_multi_line_comment = 2
                            line = line[:index]
                            multi_line_change = True
                        elif in_multi_line_comment == 2:
                            in_multi_line_comment = 0
                            multi_line_change = True
                    elif in_string == 0:
                        in_string = 2
                    elif in_string == 2:
                        in_string = 0
                elif e == "#" and in_string == 0 and index is None:
                    index = i
                    break
            if index is not None:
                line = line[:index]
            if not (not multi_line_change and in_multi_line_comment != 0):
                result.append(line)

        with open(file, mode="w") as f:
            i = 0
            while i < len(result):
                line = result[i]
                if len(line.strip()) == 0 or line.strip() in ("'''", '"""'):
                    result.pop(i)
                else:
                    i += 1
            f.write("\n".join(result))

# todo: check for compression in imports

print("creating end user version...")

with zipfile.ZipFile(local + "/builds/" + name + ".zip", mode="w") as instance:
    root_l = len(local + "/tmp/")
    for root, dirs, files in os.walk(local + "/tmp"):
        for f in files:
            file = os.path.join(root, f)
            localized = file[root_l:]
            instance.write(file, localized)

if os.path.exists(local + "/api.json"):
    print("creating api-build")

    with open(local + "/api.json") as f:
        data = json.load(f)

    for name in data:
        if data[name]["source"]:
            with zipfile.ZipFile(
                local + "/builds/" + name + "_api_{}.zip".format(name), mode="w"
            ) as instance:
                root_l = len(local + "/api/{}/".format(name))
                for root, dirs, files in os.walk(local + "/api/{}".format(name)):
                    for f in files:
                        file = os.path.join(root, f)
                        localized = file[root_l:]
                        instance.write(file, localized)

print("cleaning up...")
shutil.rmtree(local + "/tmp")
