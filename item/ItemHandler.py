"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import item.Item
import util.texture
import ResourceLocator
import event.Registry
import texture.TextureAtlas
import json
import os
import PIL.Image
import pyglet
import sys


TEXTURE_ATLASES = []


def build():
    print("building item texture atlases...")
    indexdata = {}
    for i, textureatlas in enumerate(TEXTURE_ATLASES):
        file = "atlas_{}.png".format(i)
        textureatlas.texture.save(G.local+"/build/itematlases/"+file)
        textureatlas.group = pyglet.image.ImageGrid(pyglet.image.load(G.local+"/build/itematlases/"+file),
                                                      *textureatlas.size)
        indexdata[file] = {"size": textureatlas.size, "loaded_item_file_names": textureatlas.images}
    indexdata["loaded_item_file_names"] = items.get_attribute("itemindextable")
    with open(G.local + "/build/itematlases/index.json", mode="w") as f:
        json.dump(indexdata, f)


def load_data():
    if not os.path.exists(G.local+"/build/itematlases"):
        os.makedirs(G.local+"/build/itematlases")
    else:
        with open(G.local+"/build/itematlases/index.json") as f:
            indextable = json.load(f)
        for file in os.listdir(G.local+"/build/itematlases"):
            if not file.endswith(".json") and file in indextable:
                atlas = texture.TextureAtlas.TextureAtlas(size=indextable[file]["size"], image_size=(32, 32),
                                                          add_missing_texture=False, pyglet_special_pos=False)
                image = PIL.Image.open(G.local+"/build/itematlases/"+file)
                atlas.texture = image
                atlas.images = indextable[file]["loaded_item_file_names"]
                TEXTURE_ATLASES.append(atlas)
                if "--rebuild" not in sys.argv:
                    atlas.group = pyglet.image.ImageGrid(pyglet.image.load(G.local + "/build/itematlases/" + file),
                                                         *atlas.size)
        items.set_attribute("itemindextable", indextable["loaded_item_file_names"])


def add_to_image_atlas(textureatlas, image, file):
    pos = textureatlas.add_image(image, ind=file)
    pos = (textureatlas.size[1] - pos[1] - 1, pos[0])
    return pos, TEXTURE_ATLASES.index(textureatlas)


def register_item(registry, itemclass):
    itemtable = registry.get_attribute("items")
    # pygletimagetable = registry.get_attribute("pygletimagetable")
    itemtable[itemclass.get_name()] = itemclass
    itemtable[itemclass.get_name().split(":")[-1]] = itemclass
    if itemclass.get_name() in items.get_attribute("itemindextable"): return
    table = items.get_attribute("itemindextable")
    table.setdefault(itemclass.get_name(), {})
    try:
        files = itemclass.get_used_texture_files()
        images = [ResourceLocator.read(file, "pil").resize((32, 32)) for file in files]
        locations = []
        flag = True
        for textureatlas in TEXTURE_ATLASES:
            if textureatlas.is_free_for(files):
                for i, image in enumerate(images):
                    table[itemclass.get_name()][files[i]] = add_to_image_atlas(textureatlas, image, files[i])
                flag = False
                break
        if flag:
            textureatlas = texture.TextureAtlas.TextureAtlas(add_missing_texture=False, image_size=(32, 32),
                                                             pyglet_special_pos=False, size=(16, 16))
            TEXTURE_ATLASES.append(textureatlas)
            for i, image in enumerate(images):
                table[itemclass.get_name()][files[i]] = add_to_image_atlas(textureatlas, image, files[i])
    except:
        print(itemclass.get_used_texture_files())
        raise


items = event.Registry.Registry("item", [item.Item.Item], injection_function=register_item)
items.set_attribute("items", {})
items.set_attribute("itemindextable", {})


def load():
    load_data()

    from . import (ItemFactory)

    ItemFactory.ItemFactory.from_directory("assets/factory/item")

    ItemFactory.ItemFactory.load()

