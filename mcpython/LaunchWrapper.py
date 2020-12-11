"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import os
import sys
import typing

import mcpython.ResourceLoader
import mcpython.common.config
from mcpython import shared, logger


class LaunchWrapper:
    """
    Class for launching the game in an certain configuration
    Loads all needed part and executed the loading task cycle.
    todo: move globals.py content into here & remove globals.py
    """

    def __init__(self):
        pass

    def inject_sys_argv(self, argv: typing.List[str]):
        """
        Currently unused helper function for loading the sys.argv config into the game
        todo: all sys.argv parsing belongs here
        """

    def setup(self):
        """
        Setup general stuff which does not take long to complete
        Loads first modules into memory
        """

        import mcpython.ResourceLoader
        import mcpython.common.event.EventHandler

        mcpython.ResourceLoader.load_resource_packs()

        self.setup_files()

        self.setup_opengl()

        import mcpython.client.state.StateHandler

        self.setup_registries()

        shared.eventhandler.call("game:startup")

    def setup_registries(self):
        """
        Helper functions for loading the modules which create registries
        """
        import mcpython.common.mod.ModLoader
        import mcpython.common.mod.ModMcpython
        import mcpython.common.mod.ConfigFile

        # from mcpython.common.data.gen.mcpython import (
        # )

        @shared.modloader("minecraft", "special:exit")
        def exit():
            sys.exit()

        import mcpython.common.event.Registry
        import mcpython.common.block.BlockHandler
        import mcpython.common.item.ItemHandler
        import mcpython.common.entity.EntityHandler
        import mcpython.server.worldgen.WorldGenerationHandler
        import mcpython.server.worldgen.biome.BiomeHandler
        import mcpython.server.worldgen.layer
        import mcpython.server.worldgen.feature

        import mcpython.client.rendering.model.ModelHandler
        import mcpython.common.data.tags.TagHandler

        import mcpython.client.rendering.model.ItemModel

        import mcpython.client.texture.factory

    def setup_opengl(self):
        """
        Helper function for OpenGL setup
        todo: DO NOT USE OpenGLSetupFile
        """

        import mcpython.client.rendering.util

        mcpython.client.rendering.util.setup()

    def print_header(self):
        """
        Prints an header describing the program name and its version
        """

        version = mcpython.common.config.FULL_VERSION_NAME.upper()
        logger.println("---------------" + "-" * len(version))
        logger.println("- MCPYTHON 4 {} -".format(version))
        logger.println("---------------" + "-" * len(version))

    def setup_files(self):
        """
        Setup for certain files in the system.
        """

        if not os.path.exists(shared.home + "/datapacks"):
            os.makedirs(shared.home + "/datapacks")

        if not os.path.isdir(shared.home):
            os.makedirs(shared.home)

        sys.path.append(shared.local + "/mcpython")

        # check if build folder exists, if not, we need to create its content
        if not os.path.exists(shared.build):
            logger.println("rebuild mode due to missing cache folder")
            shared.invalidate_cacheing = True

        if os.path.exists(shared.build):  # copy default skin to make it start correctly
            try:
                mcpython.ResourceLoader.read_image(
                    "assets/minecraft/textures/entity/steve.png"
                ).save(shared.build + "/skin.png")
            except:
                logger.print_exception("[FATAL] failed to load default skin")
                sys.exit(-1)

    def load_mods(self):
        """
        Do ModLoader inital stuff
        """
        shared.modloader.look_out()
        shared.modloader.sort_mods()
        shared.modloader.write_mod_info()

    def launch(self):
        """
        Launches the game in the current configuration
        Starts the main cycle of pyglet

        todo: move state selection here
        """

        logger.println("tmp storage at {}".format(shared.tmp.name))
        self.load_mods()

        # Create the world instance
        import mcpython.common.world.World

        shared.world = mcpython.common.world.World.World()

        import pyglet
        import mcpython.client.rendering.window

        # todo: move size to config files / sys.argv
        mcpython.client.rendering.window.Window(
            width=800, height=600, resizable=True
        ).reset_caption()
        try:
            # todo: can we find an better icon?
            shared.window.set_icon(
                mcpython.ResourceLoader.read_pyglet_image("icon_16x16.png"),
                mcpython.ResourceLoader.read_pyglet_image("icon_32x32.png"),
            )
            shared.eventhandler.call("game:gameloop_startup")
        except:
            logger.print_exception("[FATAL] failed to load window images")
            sys.exit(-1)
        try:
            pyglet.app.run()
        except SystemExit:
            raise
        except:
            logger.print_exception("ERROR DURING RUNTIME")
            raise

    def error_clean(self):
        """
        Helper function for cleaning up in an half-inited environment
        (save)
        Will enforce cleanup when possible
        """
        import mcpython.ResourceLoader

        mcpython.ResourceLoader.close_all_resources()
        logger.print_exception("general uncaught exception during running the game")
        try:
            shared.tmp.cleanup()
        except NameError:
            pass
        except:
            logger.print_exception("cleanup exception")

    def clean(self):
        """
        Helper function for normal cleanup
        (not save)
        """
        import mcpython.ResourceLoader

        mcpython.ResourceLoader.close_all_resources()
        shared.eventhandler.call("game:close")
        shared.tmp.cleanup()
