"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
from mcpython import globals as G, logger
import pickle
import os
import simplejson
import PIL.Image
import time


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
        """
        creates an new configuration object for an data generation
        :param modname: the mod-name to use
        :param output_folder: the folder to put data to, MUST be full-path, not local path
        :param file_scheme: an schema how to store the data. formatted with .format().
            group is "assets" or "data", namespace is the namespace, sub-group is e.g. recipes or textures and path is
            the path to store under, like in "minecraft:block/example" it is block/example.<what file ending ever>
        """
        self.enabled = True
        if modname not in G.modloader.mods:
            logger.println("[WARN] mod allocated for ({}) not found! Skipping build...".format(modname))
            self.enabled = False
        self.output_folder = output_folder
        self.modname = modname
        self.file_scheme = file_scheme
        self.elements = []
        self.default_namespace = None
        G.modloader(modname, "special:datagen:generate")(self.__build)

    def setDefaultNamespace(self, namespace: str):
        """
        will set the default namespace when not specified for namespace-needed items [like items, blocks, ...]
        :param namespace: the namespace to use
        """
        self.default_namespace = namespace
        return self

    def add_element(self, element: IDataGenerator):
        """
        will insert an generator into the config for later generation
        :param element: the element to insert
        """
        self.elements.append(element)

    def shaped_recipe(self, name: str):
        """
        will create an new mcpython.datagen.RecipeGenerator.ShapedRecipeGenerator create with these config object
        :param name: the name to generate under; used for the path-formatter
        """
        import mcpython.common.data.datagen.RecipeGenerator
        return mcpython.datagen.RecipeGenerator.ShapedRecipeGenerator(name, self)

    def shapeless_recipe(self, name: str):
        """
        will create an new mcpython.datagen.RecipeGenerator.ShapelessRecipeGenerator create with these config object
        :param name: the name to generate under; used for the path-formatter
        """
        import mcpython.common.data.datagen.RecipeGenerator
        return mcpython.datagen.RecipeGenerator.ShapelessGenerator(name,  self)

    def one_to_one(self, name: str, i, o):
        """
        simple way to create an shapeless recipe with only one input and one output
        :param name: the name to generate under; used for the path-formatter
        :param i: the input
        :param o: the output
        """
        return self.shapeless_recipe(name).addInput(i).setOutput(o)

    def smelting_recipe(self, *args, **kwargs):
        """
        will create an new mcpython.datagen.RecipeGenerator.SmeltingGenerator create with these config object
        :param args: [0]: the name to generate under; used for the path-formatter
                     ... send to constructor of class
        """
        import mcpython.common.data.datagen.RecipeGenerator
        return mcpython.datagen.RecipeGenerator.SmeltingGenerator(args[0], self, *args[1:], **kwargs)

    def __build(self):
        """
        Internal function to build the config
        Will decide if the system should data-gen or not
        """
        if not G.data_gen or (not G.dev_environment and self.modname == "minecraft"): return

        if not self.enabled: return
        logger.println("[INFO] building data generators for '{}'...".format(self.modname))
        start = time.time()
        total = 0
        while len(self.elements) > 0:
            element = self.elements.pop(0)
            total += 1
            try:
                element.generate()
            except:
                logger.print_exception("during building {}".format(element))
        logger.println("[INFO] finished in {}s ({} tasks to do)".format(time.time() - start, total))

    def write(self, data, *args):
        """
        writes certain data into the file system
        :param data: the data to write, possible: str, bytes or pickle-able
        :param args: the formatting args, must be 3 or 4 long
        :return:
        """
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
        elif type(data) == PIL.Image.Image:
            data.save(file)
        else:
            with open(file, mode="wb") as f:
                pickle.dump(data, f)

    def write_json(self, data, *args):
        """
        Will write data in human-readable json mode (with \n in place and right indent) via the simple json format
        It will sort the keys
        :param data: the data to save
        :param args: the args to pass to self.write()
        """
        self.write(simplejson.dumps(data, sort_keys=True, indent="  "), *args)

