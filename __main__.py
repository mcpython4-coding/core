"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""

print("[DEVELOPMENT][WARNING] these branch is worked on and may be not runnable at all. Please do only report bugs on "
      "features which have been finished in this branch.")
input("you have written above notice and you are sure to run the program: ")

try:
    print("---------------------")
    print("- Game Loading Area -")
    print("---------------------")

    import event.EventHandler

    import opengl_setup

    import rendering.window

    import os
    import globals

    while os.path.exists(globals.local + "/tmp"):
        try:
            import shutil
            shutil.rmtree(globals.local + "/tmp")
        except (shutil.Error, ImportError, FileNotFoundError, PermissionError):
            pass

    import globals as G

    if not os.path.exists(G.local+"/build"):
        G.prebuilding = True

    os.makedirs(globals.local + "/tmp")

    import ResourceLocator
    ResourceLocator.load_resources()

    import mod.ModLoader

    G.modloader.look_out()

    G.modloader.sort_mods()

    import sys

    import setup as systemsetup

    import texture.model.ModelHandler
    import texture.model.BlockState

    import tags.TagHandler
    import block.BlockHandler
    import item.ItemHandler
    import world.gen.WorldGenerationHandler

    import world.gen.biome.BiomeHandler


    def setup():
        import globals as G
        import world.World
        globals.world = world.World.World()
        import texture.model.BlockState
        import Language

        opengl_setup.setup()

        import world.gen.mode.DebugOverWorldGenerator

    def run():
        import pyglet
        rendering.window.Window(width=800, height=600, caption='mcpython 4', resizable=True).reset_caption()
        G.eventhandler.call("game:gameloop_startup")
        pyglet.app.run()


    def main():
        G.eventhandler.call("game:startup")
        setup()
        run()
except Exception:
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
