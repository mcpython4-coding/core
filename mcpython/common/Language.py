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
import typing

import mcpython.ResourceLoader
from mcpython import logger, shared

LANGUAGES: typing.Dict[str, "Language"] = {}  # table of data of Languages
# change this for having another language, you have to include the needed lang files yourself :/
ACTIVE_LANGUAGE = "en_us"  # the active language


def get(key: str, formatting=None):
    """
    get the translated name for an given key
    :param key: the key to get
    :param formatting: an list of formatting to use
    :return:
    """
    return (
        LANGUAGES[ACTIVE_LANGUAGE]
        .read_value(key)
        .format(*list(formatting) if formatting is not None else [])
    )


def translate(s: str):
    """
    translates an special string to an translated one
    :param s: an string defining it
    :return: the formatted string
    """
    while s.count("#*") > 0 and s.count("*#") > 0:
        start = s.index("#*")
        end = s.index("*#")
        substring = s[start + 2 : end].split("|")
        s = s[:start] + get(substring[0], formatting=substring[1:]) + s[end + 2 :]
    return s


class Language:
    """
    base class for language data
    """

    @classmethod
    def from_file(cls, file: str, name=None):
        """
        will load an file into the system
        :param file: the file to load, as ResourceLocate-able
        :param name: the name of the language to use or None for generation from file name
        """
        try:
            Language.from_data(
                file.split("/")[-1].split(".")[0] if name is None else name,
                mcpython.ResourceLoader.read_json(file).copy(),
            )
        except:
            logger.print_exception(
                "[ERROR] failed to load language file {}".format(file)
            )

    @classmethod
    def from_old_data(cls, file: str, name=None):
        """
        will load an file from the old format into the system
        :param file: the file to load
        :param name: the name to load under, or None if to read from the file name
        """
        name = file.split("/")[-1].split(".")[0] if name is None else name

        if not shared.IS_CLIENT and name != "en_us":
            return

        if name not in LANGUAGES:
            LANGUAGES[name] = cls()
        language = LANGUAGES[name]
        try:
            lines = mcpython.ResourceLoader.read_raw(file).decode("UTF-8").split("\n")
        except:
            logger.print_exception(
                "[ERROR] failed to load (old) language file {}".format(file)
            )
            return
        for line in lines:
            if line.startswith("#"):
                continue
            if line.count(" ") + line.count("   ") + line.count("\r") >= len(line):
                continue
            pre, *post = line.split("=")
            language.table[pre] = "=".join(post)

    @classmethod
    def from_data(cls, name: str, data: dict):
        """
        will load data into the system
        :param name: the name to load under
        :param data: the data to load
        """
        if not shared.IS_CLIENT and name != "en_us":
            return

        if name in LANGUAGES:
            LANGUAGES[name].table = {**LANGUAGES[name].table, **data}
        else:
            LANGUAGES[name] = cls()
            LANGUAGES[name].table = data

    def __init__(self):
        self.table: typing.Dict[str, str] = {}

    def add_entry(self, key: str, value: str):
        self.table[key] = value

    def read_value(self, key: str):
        return self.table[key] if key in self.table else key


def from_directory(directory: str, modname: str):
    """
    will create Language data for an directory
    :param directory: the directory name
    :param modname: the mod name
    """
    if modname not in shared.mod_loader.mods:
        modname = "minecraft"
    files = list(mcpython.ResourceLoader.get_all_entries_special(directory))
    m = len(files)
    for i, f in enumerate(files):
        if f.endswith(".json"):  # new language format
            shared.mod_loader.mods[modname].eventbus.subscribe(
                "stage:language",
                Language.from_file,
                f[:],
                info="loading language file {} ({}/{})".format(f, i + 1, m),
            )
        elif f.endswith(".lang"):  # old language format
            shared.mod_loader.mods[modname].eventbus.subscribe(
                "stage:language",
                Language.from_old_data,
                f[:],
                info="loading language file {} ({}/{})".format(f, i + 1, m),
            )


def from_mod_name(modname: str):
    from_directory("assets/{}/lang".format(modname), modname)


from_mod_name("mcpython")
from_mod_name("minecraft")

# todo: make load of only the active language and load others when needed -> reduce RAM usage
# todo: make an sys.argv option to disable loading & translating
