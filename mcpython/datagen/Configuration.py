"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import pickle
import os
import simplejson


class IDataGenerator:
    """
    base class for every data generator
    """

    def __init__(self, config):
        config.add_element(self)
        self.config = config

    def generate(self):
        raise NotImplementedError()


class DataGeneratorConfig:
    """
    configuration class for the data generators.
    Used to store some global stuff
    """

    def __init__(self, modname: str, output_folder: str, file_scheme: str = "{group}/{namespace}/{sub-group}/{path}"):
        self.output_folder = output_folder
        self.modname = modname
        self.file_scheme = file_scheme
        self.elements = []
        G.modloader(modname, "special:datagen:generate")(self.__build)

    def add_element(self, element: IDataGenerator):
        self.elements.append(element)

    def shaped_recipe(self, name: str):
        import mcpython.datagen.RecipeGenerator
        return mcpython.datagen.RecipeGenerator.ShapedRecipeGenerator(name, self)

    def shapeless_recipe(self, name: str):
        import mcpython.datagen.RecipeGenerator
        return mcpython.datagen.RecipeGenerator.ShapelessGenerator(name,  self)

    def smelting_recipe(self, *args, **kwargs):
        import mcpython.datagen.RecipeGenerator
        return mcpython.datagen.RecipeGenerator.SmeltingGenerator(args[0], self, *args[1:], **kwargs)

    def __build(self):
        [element.generate() for element in self.elements]

    def write(self, data, *args):
        if len(args) == 4:
            group, namespace, sub_group, path = args
        elif len(args) == 3:
            group, sub_group, path = args
            namespace = self.modname
        else: raise ValueError("invalid target {}!".format(args))
        file = "{}/{}/{}/{}/{}".format(self.output_folder, group, namespace, sub_group, path)
        d = os.path.dirname(file)
        if not os.path.exists(d): os.makedirs(d)
        if type(data) == str:
            with open(file, mode="w") as f:
                f.write(data)
        elif type(data) == bytes:
            with open(file, mode="wb") as f:
                f.write(data)
        else:
            with open(file, mode="wb") as f:
                pickle.dump(data, f)

    def write_json(self, data, *args):
        self.write(simplejson.dumps(data, sort_keys=True, indent="  "), *args)

