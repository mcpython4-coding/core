"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""

import logger
import deprecation

try:
    import sys
    if sys.version_info.major < 3 or sys.version_info.minor < 7:
        logger.println("[WARN] you are using an not supported version of python. Game may not run!")

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

    import rendering.window

    import os

    import globals as G

    # check if build folder exists, if not, we need to create its content
    if not os.path.exists(G.local+"/build"):
        G.prebuilding = True

    import ResourceLocator
    ResourceLocator.load_resource_packs()

    if os.path.exists(G.local+"/build"):
        ResourceLocator.read("assets/minecraft/textures/entity/steve.png", "pil").save(G.local+"/build/skin.png")

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
        """
        will set up some stuff
        todo: move to somewhere else
        """
        import globals as G
        import world.World
        globals.world = world.World.World()
        import rendering.model.BlockState
        import Language
        import rendering.OpenGLSetupFile

        rendering.OpenGLSetupFile.execute_file_by_name("setup")

        import world.gen.mode.DebugOverWorldGenerator

    def run():
        """
        will launch the game in the active configuration
        """
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


    @deprecation.deprecated()
    def main():
        """
        todo: merge with run()
        """
        G.eventhandler.call("game:startup")
        setup()
        run()

except:  # when we crash on loading, make sure that all resources are closed and we cleaned up afterwards
    import ResourceLocator
    ResourceLocator.close_all_resources()
    logger.write_exception("general loading exception")
    try:
        G.tmp.cleanup()
    except NameError:
        pass
    sys.exit(-1)


if __name__ == "__main__":

    try:
        G.eventhandler.call("game:startup")
        setup()
        run()
    except SystemExit: pass  # sys.exit() was called
    except:
        logger.write_exception("general system exception leading into an crash")
        G.tmp.cleanup()
    finally:
        import ResourceLocator
        ResourceLocator.close_all_resources()
        G.eventhandler.call("game:close")
        G.tmp.cleanup()
