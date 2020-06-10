"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import os
import json
import typing
import collections


local = os.path.dirname(os.path.dirname(__file__))
REPLACE_NAMESPACE = "minecraft:"


def decode_items_without_quotes(d) -> str:
    if type(d) == list:
        return str([decode_items_without_quotes(e) for e in d])
    elif type(d) == dict:
        if "item" in d: return d["item"].replace(REPLACE_NAMESPACE, "")
        return "#{}".format(d["tag"]).replace(REPLACE_NAMESPACE, "")


def decode_item(d) -> str:
    if type(d) == list: return str([decode_items_without_quotes(e) for e in d])
    elif type(d) == dict:
        if "item" in d: return "\"{}\"".format(d["item"]).replace(REPLACE_NAMESPACE, "")
        return "\"#{}\"".format(d["tag"]).replace(REPLACE_NAMESPACE, "")
    raise NotImplementedError()


def generate_recipe_generator(file: str) -> typing.Union[typing.Tuple[str, typing.Iterable[str]], None]:
    with open(file) as f:
        data = json.load(f)
    name = file.split("/")[-1].split(".")[0]
    t = data["type"]
    if t == "minecraft:crafting_shaped":
        os.remove(file)
        ex = set()
        i = []
        item_to_pos = {}
        for key in data["key"]:
            item = decode_item(data["key"][key])
            positions = []
            for y, row in enumerate(data["pattern"]):
                for x, e in enumerate(row):
                    if e == key:
                        positions.append((x, y))
            item_to_pos[item] = positions
        for item in item_to_pos:
            pos = item_to_pos[item]
            pos.sort(key=lambda x: x[1])
            pos.sort(key=lambda x: x[0])
            pos = str(pos)
            i.append(".setEntries({}, {})".format(pos, item))
            ex.add(pos)
            ex.add(item)
        oitem = data["result"]["item"] if "count" not in data else "({}, {})".format(
            data["result"]["count"], data["result"]["item"])
        oitem = oitem.replace(REPLACE_NAMESPACE, "")
        ex.add('"{}"'.format(oitem))
        o = ".setOutput(\"{}\")".format(oitem)
        if "group" in data:
            o += ".setGroup(\"{}\")".format(data["group"])
            ex.add('"{}"'.format(data["group"]))

        return "config.shaped_recipe(\"{}\"){}{}".format(name, "".join(i), o), ex
    elif t == "minecraft:crafting_shapeless":
        os.remove(file)
        i = []
        ex = set()
        entry_counter = collections.defaultdict(lambda: 0)
        for entry in data["ingredients"]:
            if "tag" in entry:
                entry_counter["#"+entry["tag"]] += 1
            elif "item" in entry:
                entry_counter[entry["item"]] += 1
            elif type(entry) == list:
                pass
        for key in entry_counter:
            item = '"{}"'.format(key)
            i.append(".addInput({}, {})".format(item.replace(REPLACE_NAMESPACE, ""), entry_counter[key]))
            ex.add(item)
        oitem = data["result"]["item"] if "count" not in data else "({}, {})".format(
            data["result"]["count"], data["result"]["item"])
        oitem = oitem.replace(REPLACE_NAMESPACE, "")
        ex.add('"{}"'.format(oitem))
        o = ".setOutput(\"{}\")".format(oitem)
        if "group" in data:
            o += ".setGroup(\"{}\")".format(data["group"])
            ex.add('"{}"'.format(data["group"]))
        return "config.shapeless_recipe(\"{}\"){}{}".format(name, "".join(i), o), ex
    elif t in ["minecraft:smelting", 'minecraft:campfire_cooking', 'minecraft:smoking', 'minecraft:blasting']:
        os.remove(file)
        ex = set()
        m = "" if t == "minecraft:smelting" else ', "{}"'.format(t, ex.add('"{}"'.format(t)))
        i = decode_item(data["ingredient"])
        ex.add(i)
        xp = ".setXp({})".format(data["experience"])
        ex.add(str(data["experience"]))
        o = ".setOutput(\"{}\")".format(data["result"]).replace(REPLACE_NAMESPACE, "")
        ex.add('"{}"'.format(data["result"].replace(REPLACE_NAMESPACE, "")))
        if "group" in data:
            o += ".setGroup(\"{}\")".format(data["group"])
            ex.add('"{}"'.format(data["group"]))
        if "cookingtime" in data and data["cookingtime"] != 200:
            o += ".setCookingTime({})".format(data["cookingtime"])
            ex.add(str(data["cookingtime"]))
        return "config.smelting_recipe(\"{}\"{}).add_ingredient({}){}{}".format(
            name, m, i.replace(REPLACE_NAMESPACE, ""), xp, o), ex
    else:
        print("[WARN] failed to encode file '{}' as type-serializer '{}' is not arrival for encoding".format(file, t))


NAMES = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def name_builder():
    for a in NAMES:
        for b in NAMES:
            for c in NAMES:
                x = a + b + c
                yield x


def generate_recipe_generators(directory: str) -> str:
    content = []
    exchangeable = set()
    for root, dirs, files in os.walk(directory):
        for file in files:
            d = generate_recipe_generator(os.path.join(root, file).replace("\\", "/"))
            if d is None: continue
            en, ex = d
            content.append(en)
            exchangeable.update(set(ex))
    string = "\n".join(content)
    front = []
    names = name_builder()
    exchangeable = list(exchangeable)
    exchangeable.sort(key=lambda e: -len(e))
    for replace in exchangeable:
        if string.count(replace) <= 1: continue
        name = next(names)
        while name in ["and"]: name = next(names)
        string = string.replace(replace, name)
        front.append("{} = {}".format(name, replace))
    return "\n".join(front) + "\n" + string


print(generate_recipe_generators(local+"/resources/source/data/minecraft/recipes"))


