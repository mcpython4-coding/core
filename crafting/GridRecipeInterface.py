"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import crafting.IRecipeInterface
import crafting.IRecipeType
import crafting.GridRecipes
import event.EventInfo
import gui.Slot
import gui.ItemStack


class GridRecipeInterface(crafting.IRecipeInterface.IRecipeInterface):
    NAME = "minecraft:crafting_interface"

    def __init__(self, slot_input_map, slot_output_map, maxsize=None, minsize=None, enabled=True,
                 enable_shaped_recipes=True, enable_shapeless_recipes=True):
        """
        creates an new grid recipe interface
        recipe order: first in, first checked
        :param slot_input_map: an Slot[[ for input
        :param slot_output_map: an Slot for output
        :param maxsize: the max size for recipes. may be None for full grid size
        :param minsize: the min size for recipes. default is (1, 1)
        :param enabled: if recipes should be craftable
        :param enable_shaped_recipes: if shaped recipes should be enabled
        :param enable_shapeless_recipes: if shapeless recipes should be enabled
        """
        self.slot_input_map = slot_input_map
        self.slot_output_map: gui.Slot.Slot = slot_output_map
        self.grid_size = (len(slot_input_map[0]), len(slot_input_map))
        self.maxsize = maxsize if maxsize else self.grid_size
        self.minsize = minsize if minsize else (1, 1)
        for y, row in enumerate(slot_input_map):
            for x, slot in enumerate(row):
                slot.on_update.append(self.on_input_update)
        slot_output_map.on_update.append(self.on_output_update)
        slot_output_map.allow_half_getting = False
        slot_output_map.on_shift_click = self.on_output_shift_click
        self.active_recipe: crafting.IRecipeType.IRecipe = None
        self.shaped_enabled = enable_shaped_recipes and enabled
        self.shapeless_enabled = enable_shapeless_recipes and enabled

    def check_recipe_state(self):
        # get info about the items which are in the interface
        itemlenght = 0
        itemtable = {}
        shapelessitems = []
        for y, row in enumerate(self.slot_input_map):
            for x, slot in enumerate(row):
                if not slot.get_itemstack().is_empty():
                    itemlenght += 1
                    itemtable[(x, y)] = slot.get_itemstack().get_item_name()
                    shapelessitems.append(slot.get_itemstack().get_item_name())
        if len(shapelessitems) == 0: return  # have we any item in the grid?
        shapelessitems.sort()
        itemtable = self._minimize_slotmap(itemtable)
        sx = max(itemtable, key=lambda v: v[0])[0]
        sy = max(itemtable, key=lambda v: v[1])[1]
        size = (sx, sy)
        self.active_recipe = None
        recipes = []
        if itemlenght in G.craftinghandler.crafting_recipes_shaped and size in G.craftinghandler.\
                crafting_recipes_shaped[itemlenght]:
            recipes += G.craftinghandler.crafting_recipes_shaped[itemlenght][size]
        if itemlenght in G.craftinghandler.crafting_recipes_shapeless:
            recipes += G.craftinghandler.crafting_recipes_shapeless[itemlenght]
        for recipe in recipes:
            state = False
            if issubclass(type(recipe), crafting.GridRecipes.GridShaped) and self.shaped_enabled:
                state = self._check_shaped(recipe, itemtable)
            elif issubclass(type(recipe), crafting.GridRecipes.GridShapeless) and self.shapeless_enabled:
                state = self._check_shapeless(recipe, shapelessitems)
            if state:
                self.active_recipe = recipe
                return
        self.active_recipe = None

    @staticmethod
    def _minimize_slotmap(slotmap: dict) -> dict:
        keys = list(slotmap.keys())
        transform = keys.copy()
        # check if everything in the top left corner
        minx = min(keys, key=lambda x: x[0])[0]
        miny = min(keys, key=lambda y: y[1])[1]
        if minx == miny == 0:  # is it in the top left corner?
            return slotmap
        if minx > 0:  # move to left if not
            for i, element in enumerate(transform):
                transform[i] = (element[0] - minx, element[1])
        if miny > 0:  # move up if not on top
            for i, element in enumerate(transform):
                transform[i] = (element[0], element[1]-miny)
        new_map = {}
        for i, key in enumerate(keys):  # transform the slot positions to the new positions
            new_map[transform[i]] = slotmap[key]
        return new_map

    @staticmethod
    def _check_shaped(recipe: crafting.GridRecipes.GridShaped, itemtable: dict) -> bool:
        # check if all necessary slots are used
        if any([x not in itemtable for x in recipe.inputs.keys()]) or \
                any([x not in recipe.inputs for x in itemtable.keys()]):
            return False
        # check every slot if the right item is in it
        # logger.println(recipe.output)
        for pos in itemtable.keys():
            item = itemtable[pos]
            if not any([item == (x[0] if type(x) != str else x) for x in recipe.inputs[pos]]):
                return False
        return True
    
    @staticmethod
    def _check_shapeless(recipe: crafting.GridRecipes.GridShapeless, items: list) -> bool:
        items = items[:]
        for initem in recipe.inputs:
            flag = True
            for value in initem:
                item, _ = (value, None) if type(value) == str else value
                if flag and item in items:
                    items.remove(item)
                    flag = False
            if flag:
                return False
        return len(items) == 0

    def update_output(self):
        self.slot_output_map.get_itemstack().clean()
        if self.active_recipe:
            self.slot_output_map.set_itemstack(gui.ItemStack.ItemStack(self.active_recipe.output[0],
                                                                       amount=self.active_recipe.output[1]),
                                               update=False)

    def remove_input(self, count=1):
        # removes from every input slot count item (called when an item is crafted)
        for row in self.slot_input_map:  # go over all slots
            for slot in row:
                if not slot.get_itemstack().is_empty():  # check if the slot is used
                    slot.get_itemstack().add_amount(-count)
                    if slot.get_itemstack().amount <= 0:
                        slot.get_itemstack().clean()

    def on_input_update(self, player=False):
        self.check_recipe_state()
        self.update_output()

    def on_output_update(self, player=False):
        if not self.active_recipe: return
        if self.slot_output_map.get_itemstack().is_empty() and player:  # have we removed items?
            self.remove_input()
            self.check_recipe_state()
            if all([all([slot.get_itemstack().is_empty() for slot in row]) for row in self.slot_input_map]):
                self.active_recipe = None
            self.update_output()

    def on_output_shift_click(self, slot, x, y, button, modifiers):
        if not self.active_recipe: return
        old_recipe = self.active_recipe
        count = 0
        while self.active_recipe == old_recipe:
            itemstack = self.slot_output_map.get_itemstack().copy()
            self.slot_output_map.set_itemstack(gui.ItemStack.ItemStack.get_empty())
            self.slot_output_map.call_update(player=True)
            count += itemstack.amount
        max_size = itemstack.item.STACK_SIZE
        for _ in range(count // max_size):
            G.world.get_active_player().pick_up(itemstack.copy().set_amount(max_size))
            count -= max_size
        G.world.get_active_player().pick_up(itemstack.copy().set_amount(count))

