"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import typing

import mcpython.common.item.AbstractItem
import mcpython.common.item.ItemFood
import mcpython.common.item.ItemTool
import mcpython.common.item.ItemArmor
from mcpython import shared as G


# todo: add ItemFactoryHandler which make it possible to add custom functions & custom class constructing
class ItemFactory:
    TASKS = []

    @classmethod
    def process(cls):
        for factory, flag in cls.TASKS:
            factory.finish_up(flag)

    def __init__(self, name=None):
        self.set_name_finises_previous = False

        self.name = name
        self.modname = None
        self.item_file = None
        self.used_item_files = []
        self.has_block = False
        self.blockname = None
        self.max_stack_size = 64
        self.creation_callback = None
        self.interaction_callback = None
        self.custom_from_item_function = None

        # food related stuff
        self.hungerregen = None
        self.eat_callback = None

        self.baseclass = [mcpython.common.item.AbstractItem.AbstractItem]

        self.tool_level = 0
        self.tool_type = []
        self.tool_speed_multi = 1
        self.tool_speed_callback = None

        self.armor_points = 0

        self.fuel_level = None

        self.template = None

        self.tooltip_renderer = None
        self.tooltip_extra = None
        self.tooltip_color = "white"

    def __call__(self, name: str = None):
        if name is not None:
            self.setName(name)
        return self

    def setTemplate(self, set_name_finises_previous=False):
        """
        sets the current status as "template". This status will be set to on every .finish() call, but will not affect
        the new generated entry.
        """
        self.set_name_finises_previous = set_name_finises_previous
        self.template = self.copy()
        return self

    def setToTemplate(self):
        if self.template is not None:
            self.__dict__ = self.template.__dict__.copy()

    def resetTemplate(self):
        self.template = None
        return self

    def finish(self, register=True, task_list=False):
        # logger.println("scheduling finishing '{}' of {}".format(self.name, self))

        copied = self.copy()
        copied.resetTemplate()

        if copied.modname is None:
            modname, item_name = tuple(copied.name.split(":"))
        else:
            modname, item_name = copied.modname, copied.name
        if not G.invalidate_cache and not task_list:
            G.mod_loader.mods[modname].eventbus.subscribe(
                "stage:item:load",
                copied.finish_up,
                register,
                info="loading item named '{}'".format(item_name),
            )
        else:
            copied.TASKS.append((copied, register))

        self.setToTemplate()

        return copied

    def copy(self):
        obj = type(self)()
        obj.__dict__ = self.__dict__.copy()
        return obj

    def finish_up(self, register=False):
        """
        will finish up the creation
        :param register: if the result should be registered to the registry
        todo: clean up this mess!!!!!
        """
        # logger.println("finishing '{}' of {}".format(self.name, self))

        master = self

        assert self.name is not None, "name must be set"

        if self.modname is not None and self.name.count(":") == 0:
            self.name = self.modname + ":" + self.name

        class BaseClass(object):
            pass

        if self.item_file is None:
            self.item_file = "{}:item/{}".format(*self.name.split(":"))
            if self.item_file not in self.used_item_files:
                self.used_item_files.append(self.item_file)
        if self.blockname is None and self.has_block:
            self.blockname = self.name

        # go over the whole list and create every time an new sub-class based on old and item of list
        for cls in self.baseclass:

            class BaseClass(BaseClass, cls):
                pass

        class ConstructedItem(
            BaseClass
        ):  # and now insert these class into the ConstructedItem-class
            @classmethod
            def get_used_texture_files(cls):
                return master.used_item_files

            NAME = master.name

            HAS_BLOCK = master.has_block

            ITEM_NAME_COLOR = master.tooltip_color

            def get_block(self) -> str:
                return master.blockname

            @staticmethod
            def get_default_item_image_location() -> str:
                return master.item_file

            def get_active_image_location(self):
                return master.item_file

            def __init__(self):
                if master.creation_callback:
                    master.creation_callback(self)

            STACK_SIZE = master.max_stack_size

            def on_player_interact(self, player, block, button, modifiers) -> bool:
                return (
                    master.interaction_callback(block, button, modifiers)
                    if master.interaction_callback
                    else False
                )

            def on_set_from_item(self, block):
                if master.custom_from_item_function:
                    master.custom_from_item_function(self, block)

        if (
            mcpython.common.item.ItemFood.ItemFood in self.baseclass
        ):  # is food stuff active?

            class ConstructedItem(
                ConstructedItem
            ):  # so construct an new class with additional functions
                def on_eat(self):
                    """
                    called when the player eats the item
                    :return: if the item was eaten or not
                    """
                    if master.eat_callback and master.eat_callback():
                        return True
                    if G.world.get_active_player().hunger == 20:
                        return False
                    G.world.get_active_player().hunger = min(
                        self.HUNGER_ADDITION + G.world.get_active_player().hunger, 20
                    )
                    return True

                HUNGER_ADDITION = master.hungerregen

        if mcpython.common.item.ItemTool.ItemTool in self.baseclass:  # is an tool

            class ConstructedItem(
                ConstructedItem
            ):  # so construct an new class with additional functions
                TOOL_LEVEL = master.tool_level

                TOOL_TYPE = master.tool_type

                def get_speed_multiplyer(self, itemstack):
                    return (
                        master.tool_speed_multi
                        if not master.tool_speed_callback
                        else master.tool_speed_callback(itemstack)
                    )

        if master.armor_points:

            class ConstructedItem(ConstructedItem):
                DEFENSE_POINTS = master.armor_points

        if master.fuel_level is not None:

            class ConstructedItem(ConstructedItem):
                FUEL = master.fuel_level

        if master.tooltip_renderer is not None:

            class ConstructedItem(ConstructedItem):
                @classmethod
                def get_tooltip_provider(cls):
                    return master.tooltip_renderer

        if master.tooltip_extra is not None:

            class ConstructedItem(ConstructedItem):
                @classmethod
                def getAdditionalTooltipText(cls, *_) -> list:
                    return master.tooltip_extra

        if register:
            G.registry.register(ConstructedItem)

    def setBaseClass(
        self, baseclass
    ):  # overwrites all previous base classes and replace them with the new(s)
        self.baseclass = baseclass if type(baseclass) == list else [baseclass]
        return self

    def setBaseClassByName(self, baseclassname: str):
        if (
            baseclassname == "food"
            and mcpython.common.item.ItemFood.ItemFood not in self.baseclass
        ):
            self.baseclass.append(mcpython.common.item.ItemFood.ItemFood)
        elif baseclassname == "default":
            self.setBaseClass(mcpython.common.item.AbstractItem.AbstractItem)
        return self

    def setGlobalModName(self, name: str):
        if name.endswith(":"):
            name = name[:-1]
        self.modname = name
        return self

    def setName(self, name: str):
        if self.set_name_finises_previous and self.name is not None:
            self.finish()
        self.name = ("" if self.modname is None else self.modname + ":") + name
        return self

    def setDefaultItemFile(self, itemfile: str):
        self.item_file = itemfile
        if itemfile not in self.used_item_files:
            self.used_item_files.append(itemfile)
        return self

    def setHasBlockFlag(self, hasblock: bool):
        self.has_block = hasblock
        return self

    def setBlockName(self, blockname: str):
        self.blockname = blockname
        return self

    def setUsedItemTextures(self, textures: list):
        self.used_item_files = textures
        if not self.item_file:
            self.item_file = textures[0]
        return self

    def setMaxStackSize(self, size: int):
        self.max_stack_size = size
        return self

    def setCreationCallback(self, function):
        self.creation_callback = function
        return self

    def setInteractionCallback(self, function):
        self.interaction_callback = function
        return self

    # food related stuff

    def setFoodValue(self, value: int):
        if mcpython.common.item.ItemFood.ItemFood not in self.baseclass:
            self.baseclass.append(mcpython.common.item.ItemFood.ItemFood)
        self.hungerregen = value
        return self

    def setEatCallback(self, function):
        if mcpython.common.item.ItemFood.ItemFood not in self.baseclass:
            self.baseclass.append(mcpython.common.item.ItemFood.ItemFood)
        self.eat_callback = function
        return self

    def setToolLevel(self, level: int):
        self.tool_level = level
        if mcpython.common.item.ItemTool.ItemTool not in self.baseclass:
            self.baseclass.append(mcpython.common.item.ItemTool.ItemTool)
        return self

    def setToolType(self, tool_types: typing.List[mcpython.common.item.ItemTool.ItemTool]):
        self.tool_type = tool_types
        if mcpython.common.item.ItemTool.ItemTool not in self.baseclass:
            self.baseclass.append(mcpython.common.item.ItemTool.ItemTool)
        return self

    def setToolBrakeMutli(self, multi: float):
        self.tool_speed_multi = multi
        if mcpython.common.item.ItemTool.ItemTool not in self.baseclass:
            self.baseclass.append(mcpython.common.item.ItemTool.ItemTool)
        return self

    def setToolBrakeMultiCallback(self, function):
        self.tool_speed_callback = function
        if mcpython.common.item.ItemTool.ItemTool not in self.baseclass:
            self.baseclass.append(mcpython.common.item.ItemTool.ItemTool)
        return self

    def setArmorPoints(self, points: int):
        self.armor_points = points
        if mcpython.common.item.ItemArmor.ItemArmor not in self.baseclass:
            self.baseclass.append(mcpython.common.item.ItemArmor.ItemArmor)
        return self

    def setCustomFromItemFunction(self, function):
        self.custom_from_item_function = function
        return self

    def setFuelLevel(self, level):
        self.fuel_level = level
        return self

    def setToolTipRenderer(self, renderer):
        self.tooltip_renderer = renderer
        return self

    def setTooltipExtraLines(self, lines):
        if type(lines) == str:
            lines = lines.split("\n")
        self.tooltip_extra = lines
        return self

    def setToolTipItemNameColor(self, color_name: str):
        self.tooltip_color = color_name
        return self
