"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import os
import sys
from abc import ABC

from mcpython import shared as G, logger

if not os.path.isdir(G.home + "/config"):
    os.makedirs(G.home + "/config")


class InvalidMapperData(Exception):
    pass


class StringParsingPool:
    """
    An system dedicated to handling an file context with the ability to pop and get lines.
    """

    def __init__(self, text: str):
        self.data = text.split("\n")

    def pop_line(self) -> str:
        return self.data.pop(0).lstrip()

    def pop_lines(self, count: int) -> list:
        d = self.data[:count]
        self.data = self.data[count:]
        return [e.lstrip() for e in d]

    def get_line(self) -> str:
        return self.data[0].lstrip()


def toDataMapper(value):
    """
    will 'map' the given value to an IDataMapper-object
    :param value: the value to map
    :return: an IDataMapper-instance
    WARNING: in case of non normal data mapper found, an StringDataMapper is used
    """
    if issubclass(type(value), IDataMapper):
        return value
    elif type(value) == dict:
        obj = DictDataMapper()
        obj.write(value)
        return obj
    elif type(value) == list:
        obj = ListDataMapper()
        obj.write(value)
        return obj
    elif type(value) == int:
        return IntDataMapper(value)
    elif type(value) == float:
        return FloatDataMapper(value)
    elif type(value) == bool:
        return BooleanDataMapper(value)
    else:
        for mapper in MAPPERS:
            if issubclass(mapper, ICustomDataMapper) and mapper.valid_value_to_parse(
                value
            ):
                return mapper.parse(value)
        return StringDataMapper(value)


class IDataMapper:
    """
    base class for every serialize-able content in config files
    """

    def __init__(self, default_value):
        self.value = None
        self.write(default_value)

    def read(self):
        """
        will return an pythonic representation of the content
        """
        raise NotImplementedError()

    def write(self, value):
        """
        will write to the internal buffer the data
        :param value: the value to write
        """
        raise NotImplementedError()

    def serialize(self) -> str:
        """
        will compress the mapper into an string-representation
        :return: the stringified version
        """
        raise NotImplementedError()

    def deserialize(self, d: StringParsingPool):
        """
        will write certain data into the mapper
        :param d: the pool to read from
        """
        raise NotImplementedError()

    def integrate(self, other):
        """
        will integrate the data from other into this
        :param other: the mapper to integrate
        """
        if type(self) != type(other):
            raise ValueError(
                "invalid integration mapper target: {} (source: {})".format(
                    type(other), type(self)
                )
            )
        self.write(other.read())


class ICustomDataMapper(IDataMapper, ABC):
    """
    For modders which would like to add their own config data types
    Will need to add to the MAPPERS list to work with config system

    WARNING: lower priority than normal aata mappers beside string mapper. Overriding with this not possible
    """

    @classmethod
    def valid_value_to_parse(cls, data) -> bool:
        raise NotImplementedError()

    @classmethod
    def parse(cls, data) -> IDataMapper:
        raise NotImplementedError()


class DictDataMapper(IDataMapper):
    """
    implementation of an mapper mapping dict-objects
    """

    def __init__(self):
        super().__init__({})

    def add_entry(self, key: str, default_mapper=None, description=None):
        self.value[key] = (toDataMapper(default_mapper), description)
        return self

    def __getitem__(self, item):
        return self.value[item][0]

    def __setitem__(self, key, value):
        if key not in self.value:
            self.value[key] = (value, None)
        else:
            self.value[key][0] = value

    def __contains__(self, item):
        return item in self.value

    def read(self) -> dict:
        return {key: self.value[key][0].read() for key in self.value}

    def write(self, value: dict):
        if self.value is not None:
            self.value.clear()
        else:
            self.value = {}
        for key in value.keys():
            self.value[key] = toDataMapper(value[key])

    def serialize(self) -> str:
        data = "D{\n"
        for key in self.value:
            d = self.value[key][0].serialize()
            d = "    " + "\n    ".join(d.split("\n"))
            if self.value[key][1] is not None:
                data += "\n//{}\n{} -> {{\n{}\n}}n".format(self.value[key][1], key, d)
            else:
                data += "\n{} -> {{\n{}\n}}".format(key, d)
        data += "\n}"
        return data

    @classmethod
    def deserialize(cls, d: StringParsingPool):
        if d.get_line() != "D{":
            raise InvalidMapperData()
        obj = cls()
        d.pop_line()
        while True:
            l = d.pop_line()
            if l == "}":
                break
            if l.startswith("//"):
                continue
            if "->" in l:
                obj[l.split(" -> {")[0]] = bufferToMapper(
                    d
                )  # handle the following like an data buffer
                if d.get_line() == "}":
                    d.pop_line()
        return obj

    def integrate(self, other):
        if type(self) != type(other):
            raise ValueError("invalid integration mapper target: {}".format(other))
        for key in other.value:
            if key in self.value:  # remove any key above the needed
                self.value[key][0].integrate(other.value[key][0])


class ListDataMapper(IDataMapper):
    def __init__(self, default=[]):
        super().__init__(default)

    def __getitem__(self, item):
        return self.value[item]

    def __setitem__(self, key, value):
        self.value[key] = value

    def __contains__(self, item):
        return item in self.value

    def append(self, item):
        self.value.append(toDataMapper(item))
        return self

    def add(self, items: list):
        self.value += [toDataMapper(e) for e in items]
        return self

    def read(self):
        return [obj.read() for obj in self.value]

    def write(self, value):
        if self.value is not None:
            self.value.clear()
        else:
            self.value = []
        for v in value:
            self.value.append(toDataMapper(v))

    def serialize(self) -> str:
        return "L[\n{}\n]".format(
            "    " + "\n    ".join([e.serialize() for e in self.value])
        )

    @classmethod
    def deserialize(cls, d: StringParsingPool):
        if d.get_line() != "L[":
            raise InvalidMapperData()
        obj = cls()
        d.pop_line()
        while True:
            line = d.get_line()
            if line == "]":
                d.pop_line()
                break
            value = bufferToMapper(d)
            if value is None:
                continue
            obj.value.append(value)
        return obj


class IntDataMapper(IDataMapper):
    def __init__(self, value=0):
        super().__init__(value)

    def read(self):
        return self.value

    def write(self, value):
        self.value = int(value)

    def serialize(self) -> str:
        return "I{}".format(self.value)

    @classmethod
    def deserialize(cls, d: StringParsingPool):
        line = d.get_line()
        if not line.startswith("I"):
            raise InvalidMapperData()
        return IntDataMapper(int(d.pop_line()[1:]))

    def integrate(self, other):
        self.value = round(other.value)


class FloatDataMapper(IDataMapper):
    def __init__(self, value=0.0):
        super().__init__(value)

    def read(self):
        return self.value

    def write(self, value):
        self.value = float(value)

    def serialize(self) -> str:
        return "F{}".format(self.value)

    @classmethod
    def deserialize(cls, d: StringParsingPool):
        line = d.get_line()
        if not line.startswith("F"):
            raise InvalidMapperData()
        return FloatDataMapper(float(d.pop_line()[1:]))


class StringDataMapper(IDataMapper):
    def __init__(self, value=""):
        super().__init__(value)

    def read(self):
        return self.value

    def write(self, value):
        self.value = str(value)

    def serialize(self) -> str:
        return 'S"{}"'.format(self.value)

    @classmethod
    def deserialize(cls, d: StringParsingPool):
        line = d.get_line()
        if not line.startswith('S"'):
            raise InvalidMapperData()
        return StringDataMapper(d.pop_line()[2:-1])


class BooleanDataMapper(IDataMapper):
    def __init__(self, value=False):
        super().__init__(value)

    def read(self):
        return self.value

    def write(self, value):
        self.value = bool(value)

    def serialize(self) -> str:
        return "B{}".format(str(self.value).lower())

    @classmethod
    def deserialize(cls, d: StringParsingPool):
        line = d.get_line()
        if not line.startswith("B"):
            raise InvalidMapperData()
        return BooleanDataMapper(value=d.pop_line()[1:].lower() == "true")


MAPPERS = [
    DictDataMapper,
    ListDataMapper,
    IntDataMapper,
    FloatDataMapper,
    StringDataMapper,
    BooleanDataMapper,
]


def stringToMapper(d: str) -> IDataMapper:
    return bufferToMapper(StringParsingPool(d))


def bufferToMapper(d: StringParsingPool) -> IDataMapper:
    for mapper in MAPPERS:
        try:
            return mapper.deserialize(d)
        except InvalidMapperData:
            pass
    raise ValueError("Invalid mapper header '{}'".format(d.pop_line()))


class ConfigFile:
    """
    class representation of an config file. Process of config reading MUST be started by mod
    """

    def __init__(self, file_name: str, assigned_mod: str):
        assert assigned_mod in G.mod_loader.mods
        self.file_name = file_name
        self.assigned_mod = assigned_mod
        self.main_tag = DictDataMapper()
        self.file = G.home + "/config/{}/{}.conf".format(assigned_mod, file_name)
        G.mod_loader(
            self.assigned_mod,
            "stage:mod:config:load",
            info="building config file {}".format(self.file),
        )(self.build)

    def add_entry(self, key: str, default_mapper=None, description=None):
        self.main_tag.add_entry(key, default_mapper, description)
        return self

    def __getitem__(self, item):
        return self.main_tag[item]

    def __setitem__(self, key, value):
        self.main_tag[key] = value

    def __contains__(self, item):
        return item in self.main_tag

    def build(self):
        if os.path.exists(self.file) and "--delete-configs" not in sys.argv:
            old_buffer = self.main_tag
            try:
                self.read()
            except AssertionError:
                logger.println("[ERROR] invalid config file '{}'".format(self.file))
                logger.println("[ERROR] interrupting file load...")
                self.main_tag = old_buffer
                return
            except:
                logger.print_exception("loading config file {}".format(self.file))
        self.write()

    def read(self):
        with open(self.file) as f:
            d = StringParsingPool(f.read())
        assert d.pop_line() == "// mcpython config file"
        assert d.pop_line() == "VERSION=1.0.0"
        assert d.pop_line() == "PROVIDING_MOD={}".format(self.assigned_mod)
        d.pop_line()
        while len(d.get_line().strip()) == 0:
            d.pop_line()
        try:
            mapper = bufferToMapper(d)
            self.main_tag.integrate(mapper)
        except:
            logger.print_exception("during loading config file '{}'".format(self.file))

    def write(self):
        data = "// mcpython config file\nVERSION=1.0.0\nPROVIDING_MOD={}\nPROVIDING_MOD_VERSION={}\n\n{}".format(
            self.assigned_mod,
            G.mod_loader.mods[self.assigned_mod].version,
            self.main_tag.serialize(),
        )
        d = os.path.dirname(self.file)
        if not os.path.isdir(d):
            os.makedirs(d)
        with open(self.file, mode="w") as f:
            f.write(data)


@G.mod_loader("minecraft", "stage:mod:config:define")
def load():
    import mcpython.common.config

    mcpython.common.config.load()
