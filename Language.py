"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import ResourceLocator
import globals as G
import warnings


LANGUAGES = {}
# change this for having another language, you have to include the needed lang files yourself :/
ACTIVE_LANGUAGE = "en_us"


def get(key, formatting=None):
    """
    get the translated name for an given key
    :param key: the key to get
    :param formatting: an list of formatting to use
    :return:
    """
    return LANGUAGES[ACTIVE_LANGUAGE].read_value(key).format(*list(
        formatting) if formatting is not None else [])


def translate(s: str):
    """
    translates an special string to an translated one
    :param s: an string defining it
    :return: the formatted string
    """
    while s.count("#*") > 0 and s.count("*#") > 0:
        start = s.index("#*")
        end = s.index("*#")
        substring = s[start+2:end].split("|")
        s = s[:start] + get(substring[0], formatting=substring[1:]) + s[end+2:]
    return s


class Language:
    @classmethod
    def from_file(cls, file: str, name=None):
        Language.from_data(file.split("/")[-1].split(".")[0] if name is None else name,
                           ResourceLocator.read(file, "json").copy())

    @classmethod
    def from_data(cls, name: str, data: dict):
        if name in LANGUAGES:
            LANGUAGES[name].table = {**LANGUAGES[name].table, **data}
        else:
            LANGUAGES[name] = cls()
            LANGUAGES[name].table = data

    def __init__(self):
        self.table = {}

    def add_entry(self, key: str, value: str):
        self.table[key] = value

    def read_value(self, key: str):
        return self.table[key] if key in self.table else key


def from_directory(directory: str, modname: str):
    files = ResourceLocator.get_all_entries_special(directory)
    m = len(files)
    for i, f in enumerate(files):
        if f.endswith(".json"):  # new language format
            G.modloader.mods[modname].eventbus.subscribe("stage:language", Language.from_file, f[:],
                                                         info="loading language file {} ({}/{})".format(f, i+1, m))


def from_mod_name(modname: str): from_directory("assets/{}/lang".format(modname), modname)


from_mod_name("minecraft")

# todo: move to an load-function over "assets/minecraft/lang" or "minecraft"
# todo: make load of only the active language and load others when needed -> reduce RAM usage
# todo: make an sys.argv option to disable loading & translating

