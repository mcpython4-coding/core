"""
mcpython - a minecraft clone written in python licenced under the MIT-licence 
(https://github.com/mcpython4-coding/core)

Contributors: uuk, xkcdjerry (inactive)

Based on the game of fogleman (https://github.com/fogleman/Minecraft), licenced under the MIT-licence
Original game "minecraft" by Mojang Studios (www.minecraft.net), licenced under the EULA
(https://account.mojang.com/documents/minecraft_eula)
Mod loader inspired by "Minecraft Forge" (https://github.com/MinecraftForge/MinecraftForge) and similar

This project is not official by mojang and does not relate to it.
"""
import os
import sys
import traceback
import typing

import pyglet.app

import mcpython.ResourceLoader
import mcpython.common.config
from mcpython import shared, logger


class LaunchWrapper:
    """
    Class for launching the game in a certain configuration
    Loads all needed part and executed the loading task cycle.
    """

    def __init__(self):
        self.is_client = True
        self.__side_prepared = False

    def prepare_client(self):
        """
        Prepares a client setup

        Sets up the OpenGL driver backend
        Spawns a window
        """

        assert not self.__side_prepared, "can only prepare ones"

        # init OpenGL
        import pyglet

        self.__side_prepared = True
        shared.IS_CLIENT = self.is_client = True
        shared.NO_WINDOW = "--no-window" in sys.argv

        import mcpython.client.rendering.window

        # todo: move size & screen to config files / sys.argv
        # screen = pyglet.canvas.get_display().get_screens()[-1]
        mcpython.client.rendering.window.Window(width=800, height=600, resizable=True)
        # shared.window.set_location(screen.x+20, screen.y+60)
        shared.window.set_caption("mcpython 4 early loading stage")

        import mcpython.common.network.Backend

        shared.CLIENT_NETWORK_HANDLER = mcpython.common.network.Backend.ClientBackend()

        return self

    def prepare_server(self):
        """
        Prepares a sever
        Spawns a fake "window"
        WARNING: currently, also initializes the OpenGL driver
        """

        assert not self.__side_prepared, "can only prepare ones"

        self.__side_prepared = True
        shared.IS_CLIENT = self.is_client = False
        shared.NO_WINDOW = True

        # todo: fake-window here!
        import mcpython.client.rendering.window

        mcpython.client.rendering.window.Window()

        import mcpython.common.network.Backend

        shared.SERVER_NETWORK_HANDLER = mcpython.common.network.Backend.ServerBackend()

        return self

    def inject_sys_argv(self, argv: typing.List[str]):
        """
        Helper function for loading the sys.argv config into the game
        todo: all sys.argv parsing belongs here, with a general parser for options not specified
        """
        if not self.is_client:
            if "--console" in argv:
                import mcpython.server.ServerConsoleHandler

                mcpython.server.ServerConsoleHandler.handler.run()

            if "--no-mods" in sys.argv:
                shared.ENABLE_MOD_LOADER = False

            if "--no-data-packs" in sys.argv:
                shared.ENABLE_DATAPACK_LOADER = False

            if "--no-resource-packs" in sys.argv:
                shared.ENABLE_RESOURCE_PACK_LOADER = False

        return self

    def setup(self):
        """
        Setup general stuff which does not take long to complete
        Loads first modules into memory and launches registry setup
        """

        if not self.__side_prepared:
            logger.println("[WARN] no side was set up. Falling back to client...")
            self.prepare_client()

        import mcpython.ResourceLoader
        import mcpython.common.event.EventHandler

        mcpython.ResourceLoader.load_resource_packs()

        self.setup_files()

        if shared.IS_CLIENT:
            self.setup_opengl()

        import mcpython.client.state.StateHandler

        self.setup_registries()

        shared.event_handler.call("game:startup")

        return self

    def setup_registries(self):
        """
        Helper functions for loading the modules which create registries and do similar stuff
        """
        import mcpython.common.mod.ModLoader
        import mcpython.common.mod.ModMcpython
        import mcpython.common.mod.ConfigFile

        # from mcpython.common.data.gen.mcpython import (
        # )

        @shared.mod_loader("minecraft", "special:exit")
        def exit():
            logger.println(
                "[INFO] stopping program as requested. If you the program continues execution, please report this"
            )

            shared.window.close()

            pyglet.app.exit()

            sys.exit(-1)

        import mcpython.common.event.Registry
        import mcpython.common.block.BlockManager
        import mcpython.common.item.ItemManager
        import mcpython.common.entity.EntityManager
        import mcpython.common.fluid.FluidManager
        import mcpython.server.worldgen.WorldGenerationHandler
        import mcpython.server.worldgen.biome.BiomeManager
        import mcpython.server.worldgen.layer
        import mcpython.server.worldgen.feature

        import mcpython.client.rendering.model.ModelHandler
        import mcpython.common.data.tags.TagHandler

        import mcpython.client.rendering.model.ItemModel

        import mcpython.common.data.ResourcePipe

        mcpython.common.data.ResourcePipe.load()

        import mcpython.common.Language

        mcpython.common.Language.load()

        return self

    def setup_opengl(self):
        """
        Helper function for OpenGL setup
        Loads also the needed API
        todo: move more rendering setup code here
        """
        assert (
            shared.IS_CLIENT
        ), "can only setup on client, this is set up for being a dedicated server"

        import mcpython.client.rendering.util

        mcpython.client.rendering.util.setup()

        return self

    def print_header(self):
        """
        Prints an header describing the program name and its version
        todo: include some more information about the system
        """

        version = mcpython.common.config.FULL_VERSION_NAME.upper()
        logger.println("---------------" + "-" * len(version))
        logger.println("- MCPYTHON 4 {} -".format(version))
        logger.println("---------------" + "-" * len(version))

        return self

    def setup_files(self):
        """
        Setup for certain files in the system.
        """

        if not os.path.exists(shared.home + "/datapacks"):
            os.makedirs(shared.home + "/datapacks")

        if not os.path.isdir(shared.home):
            os.makedirs(shared.home)

        if not os.path.exists(shared.home + "/mods"):
            os.makedirs(shared.home + "/mods")

        # check if build folder exists, if not, we need to create its content
        if not os.path.exists(shared.build):
            logger.println("rebuild mode due to missing cache folder")
            shared.invalidate_cache = True

        if os.path.exists(shared.build):  # copy default skin to make it start correctly
            try:
                mcpython.ResourceLoader.read_image(
                    "assets/minecraft/textures/entity/steve.png"
                ).save(shared.build + "/skin.png")
            except:
                logger.print_exception("[FATAL] failed to load default skin")
                sys.exit(-1)

        return self

    def load_mods(self):
        """
        Do ModLoader initial stuff
        Looks for mods in the path only when shared.ENABLE_MOD_LOADER is True
        """
        shared.mod_loader.look_out(from_files=shared.ENABLE_MOD_LOADER)
        shared.mod_loader.sort_mods()
        shared.mod_loader.write_mod_info()

        return self

    def launch(self):
        """
        Launches the game in the current configuration
        Starts the main cycle with pyglet
        Loads the mods (finally!)

        todo: move state selection here
        """
        self.load_mods()

        import mcpython.common.container.crafting.CraftingManager

        # Create the world instance
        import mcpython.common.world.World

        shared.world = mcpython.common.world.World.World()

        import pyglet

        if shared.window is not None:
            shared.window.load()
            shared.window.reset_caption()

        if shared.IS_CLIENT:
            try:
                # todo: sometimes, this does not work correctly
                shared.window.set_icon(
                    mcpython.ResourceLoader.read_pyglet_image("icon_16x16.png"),
                    mcpython.ResourceLoader.read_pyglet_image("icon_32x32.png"),
                )
                shared.event_handler.call("game:gameloop_startup")
            except:
                logger.print_exception("[FATAL] failed to load window images")
                sys.exit(-1)

        try:
            pyglet.app.run()
        except SystemExit:
            # sys.exit() should not be handled
            raise
        except:
            logger.print_exception("ERROR DURING RUNTIME (UNHANDLED)")
            import mcpython.client.state.StateLoadingException

            mcpython.client.state.StateLoadingException.error_occur(
                traceback.format_exc()
            )
            return self

        return self

    def error_clean(self):
        """
        Helper function for cleaning up in an half-inited environment
        (save)
        Will enforce cleanup when possible
        """
        logger.println(
            "[WARN] Closing the game in a bad way, please make sure that nothing broke..."
        )

        import mcpython.ResourceLoader

        try:
            mcpython.ResourceLoader.close_all_resources()
            logger.print_exception("general uncaught exception during running the game")
        except:
            logger.print_exception("failed to close resources, skipping")

        try:
            shared.tmp.cleanup()
        except NameError:
            pass
        except:
            logger.print_exception("file cleanup exception [NON-FATAL], skipping")

        sys.exit(-1)

    def clean(self):
        """
        Helper function for normal cleanup (not save, will hard-crash in some cases)
        MAY crash on non-fully stable systems
        Also invokes the event for closing the game, stops the world generation process, ...
        """
        shared.world.world_generation_process.stop()
        import mcpython.ResourceLoader

        mcpython.ResourceLoader.close_all_resources()
        shared.event_handler.call("game:close")
        shared.tmp.cleanup()
