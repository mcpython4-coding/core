"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import ResourceLocator
import globals as G
import os
import mod.ModMcpython


LANGUAGES = {}
ACTIVE_LANGUAGE = "en_us"  # change this for having another language


def get(key):
    values = key.split("|")
    return LANGUAGES[ACTIVE_LANGUAGE].read_value(values[0]).format(*values[1:])


def decode(s: str):
    """
    decodes an special string to an translated one
    :param s: an string defining it
    :return: the formated string
    """
    while s.count("#*") > 0 and s.count("*#") > 0:
        start = s.index("#*")
        end = s.index("*#")
        s = s[:start] + get(s[start+2:end]) + s[end+2:]
    # print(s, s.count("#*"), s.count("*#"))
    return s


class Language:
    @classmethod
    def from_file(cls, file: str):
        Language.from_data(file.split("/")[-1].split(".")[0], ResourceLocator.read(file, "json").copy())

    @classmethod
    def from_data(cls, filex: str, data: dict):
        if filex in LANGUAGES:
            LANGUAGES[filex].table = {**LANGUAGES[filex].table, **data}
        else:
            LANGUAGES[filex] = cls()
            LANGUAGES[filex].table = data

    def __init__(self):
        self.table = {}

    def add_entry(self, key, value):
        self.table[key] = value

    def read_value(self, key):
        return self.table[key] if key in self.table else key


files = ResourceLocator.get_all_entries_special("assets/minecraft/lang")
m = len(files)
for i, f in enumerate(files):
    if f.endswith(".json"):  # new language format
        mod.ModMcpython.mcpython.eventbus.subscribe("stage:language", Language.from_file, f[:],
                                                    info="loading language file {}".format(f))

# todo: move to an load-function over "assets/minecraft/lang" or "minecraft", add support for old format

