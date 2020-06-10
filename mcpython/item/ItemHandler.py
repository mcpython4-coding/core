"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import mcpython.ResourceLocator
import mcpython.event.Registry
import mcpython.texture.TextureAtlas
import json
import os
import PIL.Image
import pyglet
import mcpython.factory.ItemFactory
import mcpython.mod.ModMcpython
import logger


TEXTURE_ATLASES = []


def build():
    if not os.path.exists(G.build+"/itematlases"):
        os.makedirs(G.build+"/itematlases")

    logger.println("building item texture atlases...")
    G.eventhandler.call("itemhandler:build:atlases:save")
    indexdata = {}
    for i, textureatlas in enumerate(TEXTURE_ATLASES):
        file = "atlas_{}.png".format(i)
        textureatlas.texture.save(G.build+"/itematlases/"+file)
        textureatlas.group = pyglet.image.ImageGrid(pyglet.image.load(G.build+"/itematlases/"+file),
                                                      *textureatlas.size)
        indexdata[file] = {"size": textureatlas.size, "loaded_item_file_names": textureatlas.images,
                           "locations": textureatlas.imagelocations}
    indexdata["loaded_item_file_names"] = items.itemindextable
    with open(G.build+"/itematlases/index.json", mode="w") as f:
        json.dump(indexdata, f)


def load_data(from_block_item_generator=False):
    if G.prebuilding and not from_block_item_generator: return
    G.eventhandler.call("itemhandler:build:atlases:load")
    if not os.path.exists(G.build+"/itematlases"):
        os.makedirs(G.build+"/itematlases")
    elif os.path.exists(G.build+"/itematlases/index.json"):
        with open(G.build+"/itematlases/index.json") as f:
            indextable = json.load(f)
        for file in os.listdir(G.build+"/itematlases"):
            if not file.endswith(".json") and file in indextable:
                atlas = mcpython.texture.TextureAtlas.TextureAtlas(size=indextable[file]["size"], image_size=(32, 32),
                                                          add_missing_texture=False, pyglet_special_pos=False)
                image = PIL.Image.open(G.build+"/itematlases/"+file)
                atlas.texture = image
                atlas.images = indextable[file]["loaded_item_file_names"]
                atlas.imagelocations = indextable[file]["locations"]
                TEXTURE_ATLASES.append(atlas)
                if not G.prebuilding:
                    atlas.group = pyglet.image.ImageGrid(pyglet.image.load(G.build+"/itematlases/" + file),
                                                         *atlas.size)
        items.itemindextable = indextable["loaded_item_file_names"]
        if not G.prebuilding:
            with open(G.build+"/itemblockfactory.json") as f:
                data = json.load(f)
            for entry in data[:]:
                name = entry[0]
                obj = mcpython.factory.ItemFactory.ItemFactory().setName(name).setHasBlockFlag(True).setDefaultItemFile(entry[1])
                blocktable = G.registry.get_by_name("block").registered_object_map
                if name in blocktable:
                    block = blocktable[name]
                    block.modify_block_item(obj)
                    obj.finish()
                else:
                    logger.println("[ERROR] during constructing block item for '{}': Failed to find block in active "
                                   "registry".format(name))
                    data.remove(entry)
            with open(G.build+"/itemblockfactory.json", mode="w") as f:
                json.dump(data, f)


def add_to_image_atlas(textureatlas, image, file):
    pos = textureatlas.add_image(image, ind=file)
    pos = (textureatlas.size[1] - pos[1] - 1, pos[0])
    return pos, TEXTURE_ATLASES.index(textureatlas)


def register_item(registry, itemclass):
    items.registered_object_map[itemclass.NAME.split(":")[-1]] = itemclass
    if itemclass.NAME in items.itemindextable: return
    table = items.itemindextable
    table.setdefault(itemclass.NAME, {})
    try:
        files = itemclass.get_used_texture_files()
        try:
            images = [mcpython.ResourceLocator.read(file, "pil").resize((32, 32), PIL.Image.NEAREST) for file in files]
        except ValueError:
            images = [mcpython.texture.TextureAtlas.MISSING_TEXTURE] * len(files)
            logger.write_exception("during not finding files: {}".format(files))
        flag = True
        for textureatlas in TEXTURE_ATLASES:
            if textureatlas.is_free_for(files):
                for i, image in enumerate(images):
                    table[itemclass.NAME][files[i]] = add_to_image_atlas(textureatlas, image, files[i])
                flag = False
                break
        if flag:
            textureatlas = mcpython.texture.TextureAtlas.TextureAtlas(add_missing_texture=False, image_size=(32, 32),
                                                             pyglet_special_pos=False, size=(16, 16))
            TEXTURE_ATLASES.append(textureatlas)
            for i, image in enumerate(images):
                table[itemclass.NAME][files[i]] = add_to_image_atlas(textureatlas, image, files[i])
    except:
        logger.println("information for exception: ", itemclass.NAME, itemclass.get_used_texture_files())
        raise


items = mcpython.event.Registry.Registry("item", ["minecraft:item"], injection_function=register_item)
items.itemindextable = {}


def load_items():
    from . import (ItemArmor, ItemFood, ItemTool)


mcpython.mod.ModMcpython.mcpython.eventbus.subscribe("stage:block:overwrite", load_data, info="loading prepared item data")
mcpython.mod.ModMcpython.mcpython.eventbus.subscribe("stage:item:load", load_items, info="loading items")

import mcpython.item.Items

