"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import mcpython.datagen.Configuration
import mcpython.gui.ItemStack
import typing


class ICraftingKeyEncoder:
    @classmethod
    def valid(cls, data) -> bool: raise NotImplementedError()

    @classmethod
    def encode(cls, data): raise NotImplementedError()


class ItemStackEncoder(ICraftingKeyEncoder):
    @classmethod
    def valid(cls, data) -> bool:
        return type(data) == mcpython.gui.ItemStack.ItemStack

    @classmethod
    def encode(cls, data: mcpython.gui.ItemStack.ItemStack):
        return {"item": data.get_item_name()}


class TagEncoder(ICraftingKeyEncoder):
    @classmethod
    def valid(cls, data) -> bool:
        return type(data) == str and data.startswith("#")

    @classmethod
    def encode(cls, data: str):
        return {"tag": data[1:]}


class StringTypedItem(ICraftingKeyEncoder):
    @classmethod
    def valid(cls, data) -> bool:
        return type(data) == str and not data.startswith("#")

    @classmethod
    def encode(cls, data):
        return {"item": data}


class MixedTypeList(ICraftingKeyEncoder):
    @classmethod
    def valid(cls, data) -> bool:
        return type(data) == list

    @classmethod
    def encode(cls, data: list):
        return [encode_data(e) for e in data]


CRAFTING_ENCODERS = [ItemStackEncoder, TagEncoder, MixedTypeList, StringTypedItem]


def encode_data(data):
    for encoder in CRAFTING_ENCODERS:
        if encoder.valid(data):
            return encoder.encode(data)
    raise ValueError("no encoder found for {}".format(data))


INDICATOR_LIST = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


class ShapedRecipeGenerator(mcpython.datagen.Configuration.IDataGenerator):
    def __init__(self, name: str, config):
        super().__init__(config)
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
        if type(stack) == str: stack = (1, stack)
        self.output = stack
        return self

    def generate(self):
        assert self.output is not None, "name {} failed".format(self.name)

        pattern = []
        sx = max(self.grid.keys(), key=lambda x: x[0])[0]
        sy = max(self.grid.keys(), key=lambda x: x[1])[1]

        for y in range(sy+1):
            p = ""
            for x in range(sx+1):
                p += INDICATOR_LIST[self.grid[(x, y)]] if (x, y) in self.grid else " "
            pattern.append(p)

        pattern.reverse()

        table = {}
        for i, entry in enumerate(self.types):
            table[INDICATOR_LIST[i]] = encode_data(entry)

        data = {"type": "minecraft:crafting_shaped", "pattern": pattern, "key": table, "result": {
                "count": self.output[0], "item": self.output[1]}}
        if self.group is not None:
            data["group"] = self.group

        self.config.write_json(data, "data", "recipes", self.name+".json")


class ShapelessGenerator(mcpython.datagen.Configuration.IDataGenerator):
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
        if type(stack) == str: stack = (1, stack)
        self.output = stack
        return self

    def addInput(self, identifier, count=1):
        self.inputs += [identifier] * count
        return self

    def addInputs(self, *identifiers):
        self.inputs += identifiers
        return self

    def generate(self):
        data = {"type": "minecraft:crafting_shapeless", "ingredients": [encode_data(e) for e in self.inputs],
                "result": {"count": self.output[0], "item": self.output[1]}}
        if self.group is not None:
            data["group"] = self.group

        self.config.write_json(data, "data", "recipes", self.name+".json")

