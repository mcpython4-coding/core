"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
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
    import globals

    while os.path.exists(globals.local + "/tmp"):
        try:
            import shutil
            shutil.rmtree(globals.local + "/tmp")
        except (shutil.Error, ImportError):
            pass

    import globals as G

    os.makedirs(globals.local + "/tmp")

    import ResourceLocator
    ResourceLocator.load_resources()

    # import texture.atlas

    # print("generating textures...")
    # import texture.factory
    # globals.texturefactoryhandler.load()

    import world.World
    globals.world = world.World.World()

    import texture.model.ModelHandler
    import texture.model.BlockState

    print("loading tags...")
    import tags.TagHandler

    G.taghandler.load()
    print("finished!")

    print("loading blocks...")
    import block.BlockHandler
    block.BlockHandler.load()

    print("loading items...")
    import item.ItemHandler
    item.ItemHandler.load()

    import world.gen.WorldGenerationHandler


    def setup():
        import globals as G
        import world.World
        globals.world = world.World.World()
        import texture.model.BlockState
        print("searching for models & blockstates...")
        globals.modelhandler.search()
        texture.model.BlockState.BlockStateDefinition.from_directory("assets/minecraft/blockstates")
        print("finished!")
        
        opengl_setup.setup()

        print("generating models...")
        globals.modelhandler.build()
        print("generating image atlases...")
        import texture.TextureAtlas
        texture.TextureAtlas.handler.output()
        print("finished!")

        G.craftinghandler.load()

        import world.gen.mode.DebugOverWorldGenerator
        world.gen.mode.DebugOverWorldGenerator.blockinfo.construct()

    def run():
        import pyglet
        rendering.window.Window(width=800, height=600, caption='Pyglet', resizable=True)
        event.EventHandler.handler.call("game:gameloop_startup")
        pyglet.app.run()


    def main():
        event.EventHandler.handler.call("game:startup")
        setup()
        event.EventHandler.handler.call("game:load_finished")
        print("----------------------------------------------")
        print("- END OF LOADING. NOW STARTING UPDATE CYCLES -")
        print("----------------------------------------------")
        run()
except BaseException:
    import ResourceLocator
    ResourceLocator.close_all_resources()
    raise


if __name__ == "__main__":
    import sys

    if "--rebuild" in sys.argv:
        import setup as systemsetup

        systemsetup.execute()
    
    try:
        main()
    finally:
        import ResourceLocator
        ResourceLocator.close_all_resources()
