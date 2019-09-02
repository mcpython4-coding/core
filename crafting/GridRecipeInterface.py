"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import crafting.IRecipeInterface
import crafting.IRecipeType
import crafting.GridRecipes
import event.EventInfo
import gui.Slot


class GridRecipeInterface(crafting.IRecipeInterface.IRecipeInterface):
    @staticmethod
    def get_name() -> str:
        return "minecraft:crafting_interface"

    def __init__(self, slotinputmap, slotoutputmap, maxsize=None, minsize=None, validation=None, lookover=None,
                 enabled=True):
        """
        creates an new grid recipe interface
        :param slotinputmap: an Slot[[ for input
        :param slotoutputmap: an Slot for output
        :param maxsize: the max size for recipes. may be None for full grid size
        :param minsize: the min size for recipes. default is (1, 1)
        :param validation: an function to validate an recipe to this interface. If None is set, only with above
            informations is checked
        :param lookover: an function which gets recipe, input slots & output stack and can modify them for special
            reasons
        :param enabled: if recipes should be craftable
        """
        self.slotinputmap = slotinputmap
        self.slotoutputmap: gui.Slot.Slot = slotoutputmap
        self.gridsize = (len(slotinputmap[0]), len(slotinputmap))
        self.maxsize = maxsize if maxsize else self.gridsize
        self.minsize = minsize if minsize else (1, 1)
        self.validate = validation
        self.lookover = lookover
        for y, row in enumerate(slotinputmap):
            for x, slot in enumerate(row):
                slot.on_update.append(event.EventInfo.CallbackHelper(self.on_input_update, args=[x, y]))
        slotoutputmap.on_update.append(event.EventInfo.CallbackHelper(self.on_output_update))
        slotoutputmap.allow_half_getting = False
        slotoutputmap.on_shift_click = self.on_output_shift_click
        self.active_recipe: crafting.IRecipeType.IRecipe = None
        self.used_input_slots = None
        self.enabled = enabled

    def check_recipe_state(self):
        for x in range(self.minsize[0], self.maxsize[0]+1):
            for y in range(self.minsize[1], self.maxsize[1]+1):
                if (x, y) in G.craftinghandler.recipes["minecraft:crafting_shaped"]:
                    for recipe in G.craftinghandler.recipes["minecraft:crafting_shaped"][(x, y)]:
                        if self._check_shaped_recipe(recipe):
                            self.active_recipe = recipe
                            if recipe.on_select:
                                recipe.on_select()
                            # print(recipe)
                            return
        used_slots = []
        for row in self.slotinputmap:
            for slot in row:
                if slot.itemstack.item:
                    used_slots.append(slot)
        if len(used_slots) in G.craftinghandler.recipes["minecraft:crafting_shapeless"]:
            for recipe in G.craftinghandler.recipes["minecraft:crafting_shapeless"][len(used_slots)]:
                used = used_slots.copy()
                recipevalid = True
                # print([[x.item.get_name() if x.item else None for x in using] for using in recipe.inputs])
                for using in recipe.inputs:
                    # print(using)
                    if recipevalid:
                        flag = True
                        for itemstack in using[:]:
                            for slot in used:
                                if flag and itemstack.item and slot.itemstack.item.get_name() == itemstack.item.\
                                        get_name():
                                    flag = False
                                    used.remove(slot)
                                    # print(recipe, flag)
                        if flag:
                            recipevalid = False
                if recipevalid:
                    self.active_recipe = recipe
                    self.used_input_slots = used_slots
                    # print(self.active_recipe, recipe, self.used_input_slots)
                    return
        self.active_recipe = None
        self.used_input_slots = None

    def _check_shaped_recipe(self, recipe: crafting.IRecipeType.IRecipe, write_slots_to_local=True) -> bool:
        if not recipe.enabled: return False
        if type(recipe) == crafting.GridRecipes.GridShaped:
            ix, iy = self.gridsize[0] - recipe.gridsize[0], self.gridsize[1] - recipe.gridsize[1]
            for sx in range(ix):
                for sy in range(iy):
                    slots, empty = self._get_slot_map((sx, sy), recipe.gridsize)
                    if all([itemstack.amount == 0 for itemstack in empty]):  # is everything else empty?
                        flag = True
                        for ix in range(recipe.gridsize[0]):
                            for iy in range(recipe.gridsize[1]):
                                if not any([x != slots[ix][iy] for x in recipe.grid[ix][iy]]):
                                    flag = False
                        if flag:
                            if write_slots_to_local:
                                self.used_input_slots = slots
                            return True
        return False

    def _get_slot_map(self, start, size) -> tuple:
        """
        gets the map of selected slots and an list of unused slots
        :param start: the start x, y
        :param size: the size to search for
        :return: a (map, list) tuple
        """
        sx, sy = start
        ex, ey = size
        used = [[None] * size[1]] * size[0]
        unused = []
        for x in range(self.gridsize[0]):
            for y in range(self.gridsize[1]):
                if x < sx or x >= sx + ex or y < sy or y >= sy + ey:
                    unused.append(self.slotinputmap[x][y])
                else:
                    used[x][y] = self.slotinputmap[x][y]
        return used, unused

    def update_output(self):
        if not self.active_recipe:
            self.slotoutputmap.itemstack.clean()
        else:
            self.slotoutputmap.itemstack = self.active_recipe.output.copy()
        if self.lookover:
            self.lookover(self.active_recipe, self.used_input_slots, self.slotoutputmap)

    def remove_one_input(self):
        if type(self.active_recipe) == crafting.GridRecipes.GridShaped:
            pass  # todo: implement
        elif type(self.active_recipe) == crafting.GridRecipes.GridShapeless:
            # print(self.used_input_slots)
            for slot in self.used_input_slots:
                slot.itemstack.amount -= 1
                if slot.itemstack.amount == 0:
                    slot.itemstack.clean()
        else:
            raise RuntimeError("recipe not valid")

    def on_input_update(self, fromstack, tostack, x, y):
        self.check_recipe_state()
        self.update_output()
        # print(self.active_recipe.output.amount)

    def on_output_update(self, fromstack, tostack):
        if not self.active_recipe: return
        # print(self.slotoutputmap.itemstack.item.get_name() if self.slotoutputmap.itemstack.item else None)
        if self.active_recipe.on_craft: self.active_recipe.on_craft()
        if not self.slotoutputmap.itemstack.item:
            self.remove_one_input()
            self.check_recipe_state()
            self.update_output()

    def on_output_shift_click(self, x, y, button, modifiers):
        startrecipe = self.active_recipe
        while self.active_recipe == startrecipe:
            G.player.add_to_free_place(self.slotoutputmap.itemstack)
            self.slotoutputmap.itemstack.clean()
            self.on_output_update(None, None)
