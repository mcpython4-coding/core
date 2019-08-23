"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""

try:
    print("---------------------")
    print("- Game Loading Area -")
    print("---------------------")

    import event.EventHandler


    import opengl_setup

    import rendering.window

    import os
    import globals as G

    while os.path.exists(G.local+"/tmp"):
        try:
            import shutil
            shutil.rmtree(G.local+"/tmp")
        except:
            pass

    os.makedirs(G.local+"/tmp")

    import zipfile

    G.jar_archive = zipfile.ZipFile(G.local+"/assets/1.14.4.jar")

    import texture.atlas

    print("generating textures...")
    import texture.factory

    G.texturefactoryhandler.add_location(G.local + "/assets/factory/texture")
    G.texturefactoryhandler.build()

    import world.World
    G.world = world.World.World()

    print("loading blocks...")
    import block.BlockHandler
    block.BlockHandler.load()

    import texture.ModelLoader
    print("searching for models...")
    texture.ModelLoader.loader.search_in_main_jar()
    print("finished!")

    import world.gen.WorldGenerationHandler


    def setup():
        opengl_setup.setup()
        print("generating models...")
        texture.ModelLoader.loader.build()
        G.modelloader.from_data(
            "missing_texture",
            {
                "parent": "block/cube_all",
                "textures": {
                    "all": "assets/missingtexture.png"
                }
            }
        )
        print("generating image atlases...")
        texture.atlas.generator.build()
        print("finished!")

    def run():
        import pyglet
        rendering.window.Window(width=800, height=600, caption='Pyglet', resizable=True)
        event.EventHandler.handler.call("game:gameloop_startup")
        pyglet.app.run()


    def main():
        event.EventHandler.handler.call("game:startup")
        setup()
        event.EventHandler.handler.call("game:load_finished")
        print("------------------")
        print("- Game Info Area -")
        print("------------------")
        print("blocks (loaded):\n -count: {}\n -blockmodel count: {}\n -injection class count: {}".format(
            len(G.blockhandler.blockclasses), len(G.blockhandler.used_models), len(G.blockhandler.injectionclasses)
        ))
        print("items (loaded): count: {}".format(len(G.itemhandler.items)))
        print("commands (loaded):\n -count: {}".format(len(G.commandhandler.commands)))
        print(("inventorys (loaded & created):\n -count: {}\n -opened: {}\n -slot count: {}\n -marked as always opened" +
              ": {}").format(
            len(G.inventoryhandler.inventorys), len(G.inventoryhandler.opened_inventorystack),
            sum([len(inventory.slots) for inventory in G.inventoryhandler.inventorys]),
            len(G.inventoryhandler.alwaysopened)))
        print("states (loaded): count: {}".format(len(G.statehandler.states)))
        print("generation layers (loaded): count: {}".format(len(G.worldgenerationhandler.layers)))
        print("generation configurations (loaded): count: {}".format(len(G.worldgenerationhandler.configs)))
        print("biomes (loaded): count: {}".format(len(G.biomehandler.biomes)))
        print("----------------------------------------------")
        print("- END OF LOADING. NOW STARTING UPDATE CYCLUS -")
        print("----------------------------------------------")
        run()
except:
    import sys
    import globals as G
    if G.jar_archive:
        G.jar_archive.close()
    raise


if __name__ == "__main__":
    try:
        main()
    finally:
        G.jar_archive.close()

