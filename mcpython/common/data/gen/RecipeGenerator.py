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
from abc import ABC

from mcpython.common.container.ResourceStack import ItemStack
from mcpython.common.data.gen.DataGeneratorManager import (
    DataGeneratorInstance,
    IDataGenerator,
)
from mcpython.engine import logger


class ICraftingKeyEncoder(ABC):
    """
    base class for an encoder for an crafting field
    """

    # checks if the given data can be encoded with these instance
    @classmethod
    def valid(cls, data) -> bool:
        raise NotImplementedError()

    # encodes certain data
    @classmethod
    def encode(cls, data, generator):
        raise NotImplementedError()


class ItemStackEncoder(ICraftingKeyEncoder):
    """
    encodes an ItemStack-instance
    WARNING: in normal mode, ItemStacks can NOT be used as they are based on the item-registry which is not yet
        filled with data
    """

    @classmethod
    def valid(cls, data) -> bool:
        return type(data) == ItemStack

    @classmethod
    def encode(cls, data: ItemStack, generator: DataGeneratorInstance):
        return {"item": data.get_item_name()}


class TagEncoder(ICraftingKeyEncoder):
    """
    encodes an string-tag like "#minecraft:logs"
    """

    @classmethod
    def valid(cls, data) -> bool:
        return type(data) == str and data.startswith("#")

    @classmethod
    def encode(cls, data: str, generator):
        tag = data[1:]
        if ":" not in tag and generator.default_namespace is not None:
            tag = generator.default_namespace + ":" + tag
        return {"tag": tag}


class StringTypedItem(ICraftingKeyEncoder):
    """
    encodes an raw item name
    """

    @classmethod
    def valid(cls, data) -> bool:
        return type(data) == str and not data.startswith("#")

    @classmethod
    def encode(cls, data, generator):
        if ":" not in data and generator.default_namespace is not None:
            data = generator.default_namespace + ":" + data
        return {"item": data}


class MixedTypeList(ICraftingKeyEncoder):
    """
    encodes an list of key encode-ables
    """

    @classmethod
    def valid(cls, data) -> bool:
        return type(data) == list

    @classmethod
    def encode(cls, data: list, generator):
        return [encode_data(e, generator) for e in data]


CRAFTING_ENCODERS = [ItemStackEncoder, TagEncoder, MixedTypeList, StringTypedItem]


def encode_data(data, generator: DataGeneratorInstance):
    """
    encodes data together with the configuration to use
    :param data: the data to encode
    :param generator: the config to use
    :return: encoded data for later dumping in data gen
    """
    for encoder in CRAFTING_ENCODERS:
        if encoder.valid(data):
            return encoder.encode(data, generator)
    raise ValueError("no encoder found for {}".format(data))


INDICATOR_LIST = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


class ShapedRecipeGenerator(IDataGenerator):
    """
    Generator for an shaped recipe
    """

    def __init__(self, name: str):
        self.grid = {}
        self.types = []
        self.output = None
        self.group = None
        self.name = name

    def setGroup(self, name: str):
        self.group = name
        return self

    def setEntry(self, x: int, y: int, data):
        """
        will insert data into the grid
        :param x: the x position
        :param y: the y position
        :param data: the data to use, may be ItemStack, ItemStack-Tag-list, tag
        """
        if data in self.types:
            i = self.types.index(data)
        else:
            i = len(self.types)
            self.types.append(data)
        self.grid[(x, y)] = i
        return self

    def setEntries(self, positions, data):
        [self.setEntry(*e, data) for e in positions]
        return self

    def setOutput(self, stack: typing.Union[typing.Tuple[int, str], str]):
        if type(stack) == str:
            stack = (1, stack)
        self.output = stack
        return self

    def dump(self, generator: "DataGeneratorInstance"):
        assert self.output is not None, "name {} failed".format(self.name)

        pattern = []
        sx = max(self.grid.keys(), key=lambda x: x[0])[0]
        sy = max(self.grid.keys(), key=lambda x: x[1])[1]

        for y in range(sy + 1):
            p = ""
            for x in range(sx + 1):
                p += INDICATOR_LIST[self.grid[(x, y)]] if (x, y) in self.grid else " "
            pattern.append(p)

        pattern.reverse()

        table = {}
        for i, entry in enumerate(self.types):
            table[INDICATOR_LIST[i]] = encode_data(entry, generator)

        data = {
            "type": "minecraft:crafting_shaped",
            "pattern": pattern,
            "key": table,
            "result": {"count": self.output[0], "item": self.output[1]},
        }
        if self.group is not None:
            data["group"] = self.group

        return data

    def get_default_location(self, generator: "DataGeneratorInstance", name: str):
        return (
            "data/{}/recipes/{}.json".format(*name.split(":"))
            if name.count(":") == 1
            else "data/{}/recipes/{}.json".format(generator.default_namespace, name)
        )


class ShapelessGenerator(IDataGenerator):
    def __init__(self, name: str, config):
        super().__init__(config)
        self.name = name
        self.inputs = []
        self.output = None
        self.group = None

    def setGroup(self, name: str):
        self.group = name
        return self

    def setOutput(self, stack: typing.Union[typing.Tuple[int, str], str]):
        if type(stack) == str:
            stack = (1, stack)
        self.output = stack
        return self

    def addInput(self, identifier, count=1):
        self.inputs += [identifier] * count
        return self

    def addInputs(self, *identifiers):
        if len(identifiers) == 1 and type(identifiers) == list:
            logger.println(
                "[WARNING] did you mean *[...] instead of [...] for generator named {}?".format(
                    self.name
                )
            )
        self.inputs += identifiers
        return self

    def dump(self, generator: "DataGeneratorInstance"):
        if self.output is None:
            logger.println("recipe {} is missing output!".format(self.name))
            return
        data = {
            "type": "minecraft:crafting_shapeless",
            "ingredients": [encode_data(e, generator) for e in self.inputs],
            "result": {"count": self.output[0], "item": self.output[1]},
        }
        if self.group is not None:
            data["group"] = self.group

        return data

    def get_default_location(self, generator: "DataGeneratorInstance", name: str):
        return (
            "data/{}/recipes/{}.json".format(*name.split(":"))
            if name.count(":") == 1
            else "data/{}/recipes/{}.json".format(generator.default_namespace, name)
        )


class SmeltingGenerator(IDataGenerator):
    def __init__(self, name: str, config, mode="minecraft:smelting"):
        super().__init__(config)
        self.name = name
        self.group = None
        self.output = None
        self.xp = 0
        self.cooking_time = 200
        self.inputs = []
        self.mode = mode

    def setGroup(self, name: str):
        self.group = name
        return self

    def add_ingredient(self, data):
        if type(data) == str:
            self.inputs.append(data)
        else:
            self.inputs += data
        return self

    def add_ingredients(self, *data):
        self.inputs += data
        return self

    def setOutput(self, stack: str):
        self.output = stack
        return self

    def setXp(self, xp: int):
        self.xp = xp
        return self

    def setCookingTime(self, dt: int):
        self.cooking_time = dt
        return self

    def dump(self, generator: "DataGeneratorInstance"):
        inp = (
            encode_data(self.inputs[0], generator)
            if len(self.inputs) == 1
            else [encode_data(e, generator) for e in self.inputs]
        )
        data = {
            "type": self.mode,
            "ingredient": inp,
            "result": self.output,
            "experience": self.xp,
            "cookingtime": self.cooking_time,
        }

        return data

    def get_default_location(self, generator: "DataGeneratorInstance", name: str):
        return (
            "data/{}/recipes/{}.json".format(*name.split(":"))
            if name.count(":") == 1
            else "data/{}/recipes/{}.json".format(generator.default_namespace, name)
        )
