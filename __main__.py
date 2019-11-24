"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""

print("[DEVELOPMENT][WARNING] these branch is worked on and may be not runnable at all. Please do only report bugs on "
      "features which have been finished in this branch.")
input("you have written above notice and you are sure to run the program: ")

try:
    import globals as G
    version = G.VERSION.upper()
    print("---------------"+"-"*len(version))
    print("- MCPYTHON 4 {} -".format(version))
    print("---------------"+"-"*len(version))

    import globals
    import os
    import shutil

    # todo: add security check after 10 tries -> crash

    while os.path.exists(globals.local + "/tmp"):
        try:
            shutil.rmtree(globals.local + "/tmp")
        except (shutil.Error, ImportError, FileNotFoundError, PermissionError):
            pass

    os.makedirs(globals.local + "/tmp")

    import event.EventHandler

    import opengl_setup

    import rendering.window

    import os

    import globals as G

    # check if build folder exists, if not, we need to create its content
    if not os.path.exists(G.local+"/build"): G.prebuilding = True

    import ResourceLocator
    ResourceLocator.load_resources()

    import mod.ModLoader

    G.modloader.look_out()

    G.modloader.sort_mods()

    import sys

    import setup as systemsetup

    import tags.TagHandler
    import block.BlockHandler
    import item.ItemHandler
    import world.gen.WorldGenerationHandler

    import world.gen.biome.BiomeHandler


    def setup():
        import globals as G
        import world.World
        globals.world = world.World.World()
        import Language

        opengl_setup.setup()

        import world.gen.mode.DebugOverWorldGenerator

    def run():
        import pyglet
        # todo: move size to config.py
        rendering.window.Window(width=800, height=600, resizable=True).reset_caption()
        G.eventhandler.call("game:gameloop_startup")
        pyglet.app.run()


    def main():
        G.eventhandler.call("game:startup")
        setup()
        run()
except:
    import ResourceLocator
    ResourceLocator.close_all_resources()
    raise


if __name__ == "__main__":
    import sys
    
    try:
        main()
    finally:
        import ResourceLocator
        ResourceLocator.close_all_resources()
