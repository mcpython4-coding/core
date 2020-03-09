"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""

import logger
import pyglet_fix

try:
    import config
    version = config.FULL_VERSION_NAME.upper()
    logger.println("---------------"+"-"*len(version))
    logger.println("- MCPYTHON 4 {} -".format(version))
    logger.println("---------------"+"-"*len(version))

    import globals
    import os
    import shutil

    logger.println("tmp storage at {}".format(globals.tmp.name))

    if not os.path.exists(globals.local + "/datapacks"): os.makedirs(globals.local + "/datapacks")

    import event.EventHandler

    from rendering import config

    import rendering.window

    import os

    import globals as G

    # check if build folder exists, if not, we need to create its content
    if not os.path.exists(G.local+"/build"):
        G.prebuilding = True

    import ResourceLocator
    ResourceLocator.load_resource_packs()

    import mod.ModLoader

    G.modloader.look_out()

    G.modloader.sort_mods()

    import sys

    import setup as systemsetup

    import rendering.model.ModelHandler
    import rendering.model.BlockState

    import tags.TagHandler
    import block.BlockHandler
    import item.ItemHandler
    import world.gen.WorldGenerationHandler

    import world.gen.biome.BiomeHandler


    def setup():
        import globals as G
        import world.World
        globals.world = world.World.World()
        import rendering.model.BlockState
        import Language

        config.setup()

        import world.gen.mode.DebugOverWorldGenerator

    def run():
        import pyglet
        # todo: move size to config.py
        rendering.window.Window(width=800, height=600, resizable=True).reset_caption()
        G.window.set_icon(ResourceLocator.read("icon_16x16.png", "pyglet"),
                          ResourceLocator.read("icon_32x32.png", "pyglet"))
        G.eventhandler.call("game:gameloop_startup")
        try:
            pyglet.app.run()
        except:
            # todo: implement crash logging
            raise


    def main():
        G.eventhandler.call("game:startup")
        setup()
        run()
except:  # when we crash on loading, make sure that all resources are closed
    import ResourceLocator
    ResourceLocator.close_all_resources()
    logger.write_exception()
    logger.add_funny_line()
    G.tmp.cleanup()
    raise


if __name__ == "__main__":

    try:
        main()
    except SystemExit: pass  # sys.exit() was called
    except:
        logger.write_exception()
        logger.add_funny_line()
        G.tmp.cleanup()
        raise
    finally:
        import ResourceLocator
        ResourceLocator.close_all_resources()
        G.eventhandler.call("game:close")
        G.tmp.cleanup()
