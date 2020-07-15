"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
import shutil
import os
import zipfile
import json

local = os.path.dirname(__file__)


print("collecting files...")

if os.path.exists(local+"/tmp"):
    shutil.rmtree(local+"/tmp")
os.makedirs(local+"/tmp")

pre = len(local+"/source/")

for root, dirs, files in os.walk(local+"/source"):
    for f in files:
        file = os.path.join(root, f)
        localized = file[pre:]
        target = local+"/tmp/"+localized
        d = os.path.dirname(target)
        if not os.path.exists(d):
            os.makedirs(d)
        shutil.copy(file, target)

if os.path.isdir(local+"/api"):
    for folder in os.listdir(local+"/api"):
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


if not os.path.isdir(local+"/builds"):
    os.makedirs(local+"/builds")

name = input("name of the build? ")

# todo: implement
"""
print("creating dev-version...")

with zipfile.ZipFile(local+"/builds/"+name+"_dev.zip", mode="w") as instance:
    root_l = len(local + "/tmp/")
    for root, dirs, files in os.walk(local + "/tmp"):
        for f in files:
            file = os.path.join(root, f)
            local = file[root_l:]
            instance.write(file, local)

print("filtering code...")  
"""

print("creating end user version...")

with zipfile.ZipFile(local+"/builds/"+name+".zip", mode="w") as instance:
    root_l = len(local + "/tmp/")
    for root, dirs, files in os.walk(local + "/tmp"):
        for f in files:
            file = os.path.join(root, f)
            localized = file[root_l:]
            instance.write(file, localized)

if os.path.exists(local+"/api.json"):
    print("creating api-build")

    with open(local+"/api.json") as f:
        data = json.load(f)

    for name in data:
        if data[name]["source"]:
            with zipfile.ZipFile(local + "/builds/" + name + "_api_{}.zip".format(name), mode="w") as instance:
                root_l = len(local + "/api/{}/".format(name))
                for root, dirs, files in os.walk(local + "/api/{}".format(name)):
                    for f in files:
                        file = os.path.join(root, f)
                        localized = file[root_l:]
                        instance.write(file, localized)

print("cleaning up...")
shutil.rmtree(local+"/tmp")

