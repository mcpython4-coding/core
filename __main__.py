"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""

import deprecation

import logger

try:
    import sys
    import os
    import globals as G

    if sys.version_info.major < 3 or sys.version_info.minor < 7:
        logger.println("[WARN] you are using an not supported version of python. Game may not run!")

    import mcpython.config

    version = mcpython.config.FULL_VERSION_NAME.upper()
    logger.println("---------------" + "-" * len(version))
    logger.println("- MCPYTHON 4 {} -".format(version))
    logger.println("---------------" + "-" * len(version))

    if not os.path.isdir(G.home):
        os.makedirs(G.home)

    sys.path.append(G.local + "/mcpython")

    import globals
    import shutil

    logger.println("tmp storage at {}".format(globals.tmp.name))

    if not os.path.exists(globals.home + "/datapacks"): os.makedirs(globals.home + "/datapacks")

    import mcpython.event.EventHandler

    import mcpython.rendering.window
    import globals as G

    # check if build folder exists, if not, we need to create its content
    if not os.path.exists(G.build):
        logger.println("rebuild mode due to missing cache folder")
        G.prebuilding = True

    import mcpython.ResourceLocator
    mcpython.ResourceLocator.load_resource_packs()

    if os.path.exists(G.build):
        try:
            mcpython.ResourceLocator.read("assets/minecraft/textures/entity/steve.png", "pil").save(G.build+"/skin.png")
        except:
            logger.write_exception("[FATAL] failed to load default skin")
            sys.exit(-1)

    import mcpython.mod.ModLoader

    G.modloader.look_out()

    G.modloader.sort_mods()

    import sys

    import mcpython.setup as systemsetup

    import mcpython.rendering.model.ModelHandler
    import mcpython.rendering.model.BlockState

    import mcpython.tags.TagHandler
    import mcpython.block.BlockHandler
    import mcpython.item.ItemHandler
    import mcpython.world.gen.WorldGenerationHandler

    import mcpython.world.gen.biome.BiomeHandler

    import mcpython.texture.factory


    def setup():
        """
        will set up some stuff
        todo: move to somewhere else
        """
        import globals as G
        import mcpython.world.World
        globals.world = mcpython.world.World.World()
        import mcpython.rendering.model.BlockState
        import mcpython.Language
        import mcpython.rendering.OpenGLSetupFile

        mcpython.rendering.OpenGLSetupFile.execute_file_by_name("setup")

        import mcpython.world.gen.mode.DebugOverWorldGenerator

    def run():
        """
        will launch the game in the active configuration
        """
        import pyglet
        # todo: move size to config.py
        mcpython.rendering.window.Window(width=800, height=600, resizable=True).reset_caption()
        try:
            G.window.set_icon(mcpython.ResourceLocator.read("icon_16x16.png", "pyglet"),
                              mcpython.ResourceLocator.read("icon_32x32.png", "pyglet"))
            G.eventhandler.call("game:gameloop_startup")
        except:
            logger.write_exception("[FATAL] failed to load window images")
            sys.exit(-1)
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
except SystemExit:
    sys.exit(-1)
except:  # when we crash on loading, make sure that all resources are closed and we cleaned up afterwards
    import mcpython.ResourceLocator
    mcpython.ResourceLocator.close_all_resources()
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
        import mcpython.ResourceLocator
        mcpython.ResourceLocator.close_all_resources()
        G.eventhandler.call("game:close")
        G.tmp.cleanup()
