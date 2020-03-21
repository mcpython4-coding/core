"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import item.Item
import item.ItemFood
import item.ItemTool
import item.ItemArmor
import globals as G
import mod.ModMcpython
import sys


# todo: add ItemFactoryHandler which make it possible to add custom functions & custom class constructing
class ItemFactory:
    TASKS = []

    @classmethod
    def process(cls):
        for itemfactory, flag in cls.TASKS:
            itemfactory._finish(flag)

    def __init__(self):
        self.name = None
        self.itemfile = None
        self.used_itemfiles = []
        self.has_block = False
        self.blockname = None
        self.stacksize = 64
        self.creation_callback = None
        self.interaction_callback = None
        self.customfromitemfunction = None

        # food related stuff
        self.hungerregen = None
        self.eat_callback = None

        self.baseclass = [item.Item.Item]

        self.tool_level = 0
        self.tool_type = []
        self.tool_speed_multi = 1
        self.tool_speed_callback = None

        self.armor_points = 0

        self.fuel_level = None

    def finish(self, register=True, task_list=False):
        modname, itemname = tuple(self.name.split(":"))
        if not G.prebuilding and not task_list:
            G.modloader.mods[modname].eventbus.subscribe("stage:item:load", self._finish, register,
                                                         info="loading item named {}".format(itemname))
        else:
            self.TASKS.append((self, register))

    def _finish(self, register):
        master = self

        class baseclass(object): pass

        if self.itemfile is None:
            self.itemfile = "{}:item/{}".format(*self.name.split(":"))
            if self.itemfile not in self.used_itemfiles:
                self.used_itemfiles.append(self.itemfile)
        if self.blockname is None and self.has_block:
            self.blockname = self.name

        # go over the whole list and create every time an new sub-class based on old and item of list
        for cls in self.baseclass:
            class baseclass(baseclass, cls): pass

        class ConstructedItem(baseclass):  # and now insert these class into the ConstructedItem-class
            @classmethod
            def get_used_texture_files(cls): return master.used_itemfiles

            NAME = master.name

            @staticmethod
            def has_block() -> bool: return master.has_block

            def get_block(self) -> str: return master.blockname

            @staticmethod
            def get_default_item_image_location() -> str: return master.itemfile

            def get_active_image_location(self): return master.itemfile

            def __init__(self):
                if master.creation_callback: master.creation_callback(self)

            def get_max_stack_size(self) -> int: return master.stacksize

            def on_player_interact(self, player, block, button, modifiers) -> bool:
                return master.interaction_callback(block, button, modifiers) if master.interaction_callback else False

            def on_set_from_item(self, block):
                if master.customfromitemfunction:
                    master.customfromitemfunction(self, block)

        if item.ItemFood.ItemFood in self.baseclass:  # is food stuff active?
            class ConstructedItem(ConstructedItem):  # so construct an new class with additional functions
                def on_eat(self):
                    """
                    called when the player eats the item
                    :return: if the item was eaten or not
                    """
                    if master.eat_callback and master.eat_callback():
                        return True
                    if G.world.get_active_player().hunger == 20:
                        return False
                    G.world.get_active_player().hunger = min(self.get_eat_hunger_addition() + G.world.get_active_player().hunger, 20)
                    return True

                def get_eat_hunger_addition(self) -> int: return master.hungerregen

        if item.ItemTool.ItemTool in self.baseclass:  # is an tool
            class ConstructedItem(ConstructedItem):  # so construct an new class with additional functions
                def get_tool_level(self):
                    return master.tool_level

                def get_tool_type(self):
                    return master.tool_type

                def get_speed_multiplyer(self, itemstack):
                    return master.tool_speed_multi if not master.tool_speed_callback else master.tool_speed_callback(
                        itemstack)

        if master.armor_points:
            class ConstructedItem(ConstructedItem):
                def getDefensePoints(self):
                    return master.armor_points

        if master.fuel_level is not None:
            class ConstructedItem(ConstructedItem):
                FUEL = master.fuel_level

        if register: G.registry.register(ConstructedItem)

    def setBaseClass(self, baseclass):   # overwrites all previous base classes and replace them with the new(s)
        self.baseclass = baseclass if type(baseclass) == list else [baseclass]
        return self

    def setBaseClassByName(self, baseclassname: str):
        if baseclassname == "food" and item.ItemFood.ItemFood not in self.baseclass:
            self.baseclass.append(item.ItemFood.ItemFood)
        elif baseclassname == "default":
            self.setBaseClass(item.Item.Item)
        return self

    def setName(self, name: str):
        self.name = name
        return self

    def setDefaultItemFile(self, itemfile: str):
        self.itemfile = itemfile
        if itemfile not in self.used_itemfiles:
            self.used_itemfiles.append(itemfile)
        return self

    def setHasBlockFlag(self, hasblock: bool):
        self.has_block = hasblock
        return self

    def setBlockName(self, blockname: str):
        self.blockname = blockname
        return self

    def setUsedItemTextures(self, itemtextures: list):
        self.used_itemfiles = itemtextures
        if not self.itemfile:
            self.itemfile = itemtextures[0]
        return self

    def setMaxStackSize(self, stacksize: int):
        self.stacksize = stacksize
        return self

    def setCreationCallback(self, function):
        self.creation_callback = function
        return self

    def setInteractionCallback(self, function):
        self.interaction_callback = function
        return self

    # food related stuff

    def setFoodValue(self, value: int):
        if item.ItemFood.ItemFood not in self.baseclass:
            self.baseclass.append(item.ItemFood.ItemFood)
        self.hungerregen = value
        return self

    def setEatCallback(self, function):
        if item.ItemFood.ItemFood not in self.baseclass:
            self.baseclass.append(item.ItemFood.ItemFood)
        self.eat_callback = function
        return self

    def setToolLevel(self, level: int):
        self.tool_level = level
        if item.ItemTool.ItemTool not in self.baseclass:
            self.baseclass.append(item.ItemTool.ItemTool)
        return self

    def setToolType(self, tooltype: list):
        self.tool_type = tooltype
        if item.ItemTool.ItemTool not in self.baseclass:
            self.baseclass.append(item.ItemTool.ItemTool)
        return self

    def setToolBrakeMutli(self, multi: float):
        self.tool_speed_multi = multi
        if item.ItemTool.ItemTool not in self.baseclass:
            self.baseclass.append(item.ItemTool.ItemTool)
        return self

    def setToolBrakeMultiCallback(self, function):
        self.tool_speed_callback = function
        if item.ItemTool.ItemTool not in self.baseclass:
            self.baseclass.append(item.ItemTool.ItemTool)
        return self

    def setArmorPoints(self, points: int):
        self.armor_points = points
        if item.ItemArmor.ItemArmor not in self.baseclass:
            self.baseclass.append(item.ItemArmor.ItemArmor)
        return self

    def setCustomFromItemFunction(self, function):
        self.customfromitemfunction = function
        return self

    def setFuelLevel(self, level):
        self.fuel_level = level
        return self

