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

import mcpython.engine.ResourceLoader
import mcpython.common.config
from mcpython import shared
from mcpython.engine import logger


class LaunchWrapper:
    """
    Class for launching the game in a certain configuration
    Loads all needed part and executed the loading task cycle.
    """

    def __init__(self):
        self.is_client = -1

        self.launch_config: typing.Dict[
            str, typing.Union[typing.List[typing.Tuple[str]], bool]
        ] = {}

        shared.launch_wrapper = self

    @classmethod
    def check_py_version(cls):
        # everything lower than python 3.9 is not supported, we are using python 3.9 features!
        if sys.version_info.major != 3 or sys.version_info.minor < 9:
            print(
                "[VERSION DETECTOR][FATAL] you are using an not supported version of python. "
                "You need at least python 3.9 in order to run the game!"
            )
            sys.exit(-1)

        if sys.version_info.minor == 9:
            print(
                "[INTERNAL][WARN] You are using python 3.9 which will be unsupported in a handful of released"
            )
            print(
                "                 We made our game compatible with python 3.10 some releases ago, so please update!"
            )

        if sys.version_info.minor >= 11:
            print(
                f"[VERSION DETECTOR][WARN] Detected python version 3.{sys.version_info.minor}, which is >= 11, which may break at any point"
            )

    def set_client(self):
        self.is_client = True

    def set_server(self):
        self.is_client = False

    def full_launch(self):
        """
        Method to launch everything at ones

        General layout:
        - logger & header
        - argv
        - modloader file lookup
        - modloader file information lookup
        - modloader loader lookup
        - modloader mixin parse
        """
        logger.println("[LAUNCH WRAPPER][INFO] starting loading cycle")
        self.print_header()
        self.parse_argv()

        shared.IS_CLIENT = self.is_client

        import mcpython.common.mod.ModLoader

        try:
            import jvm.JavaEntryPoint
        except ImportError:
            pass

        import mcpython.common.mod.ModMcpython

        shared.mod_loader.look_for_mod_files()
        shared.mod_loader.parse_mod_files()

        shared.mod_loader.check_errors()

        shared.mod_loader.load_missing_mods()

        shared.mod_loader.check_for_updates()
        shared.mod_loader.write_mod_info()

        shared.mod_loader.sort_mods()

        # todo: parse mixins

        import mcpython.engine.network.NetworkManager

        if self.is_client:
            import mcpython.engine.rendering.window

            # todo: move size & screen to config files / sys.argv
            # screen = pyglet.canvas.get_display().get_screens()[-1]
            mcpython.engine.rendering.window.Window(
                width=800, height=600, resizable=True
            )
            # shared.window.set_location(screen.x+20, screen.y+60)
            shared.window.set_caption("mcpython 4 early loading stage")

            import mcpython.engine.network.Backend

            shared.CLIENT_NETWORK_HANDLER = (
                mcpython.engine.network.Backend.ClientBackend()
            )

        else:
            import mcpython.engine.network.Backend

            shared.SERVER_NETWORK_HANDLER = (
                mcpython.engine.network.Backend.ServerBackend()
            )
            # todo: get server ip from argv
            shared.SERVER_NETWORK_HANDLER.connect()

        self.setup()
        self.launch()

    def parse_argv(self):
        args = sys.argv[1:]

        if "--console" in args:
            import mcpython.server.ServerConsoleHandler

            mcpython.server.ServerConsoleHandler.handler.run()

        if "--no-mods" in args:
            shared.ENABLE_MOD_LOADER = False

        if "--no-data-packs" in args:
            shared.ENABLE_DATAPACK_LOADER = False

        if "--no-resource-packs" in args:
            shared.ENABLE_RESOURCE_PACK_LOADER = False

        current_arg: typing.Optional[str] = None
        arg_collector: typing.List[str] = []

        for e in args:
            if e.startswith("-"):
                if current_arg is not None:
                    self.launch_config.setdefault(current_arg, []).append(
                        tuple(arg_collector)
                    )
                elif arg_collector:
                    logger.println(
                        "[LAUNCH WRAPPER][WARN] got arg values before arg config"
                    )
                arg_collector.clear()

            if e.startswith("--"):
                current_arg = e.removeprefix("--")
            elif e.startswith("-"):
                self.launch_config[e.removeprefix("-")] = True
                current_arg = None
            else:
                arg_collector.append(e)

        if current_arg is not None:
            self.launch_config.setdefault(current_arg, []).append(tuple(arg_collector))
        elif arg_collector:
            logger.println("[LAUNCH WRAPPER][WARN] got arg values before arg config")

    def is_flag_arrival(self, flag: str):
        return flag in self.launch_config

    def get_flag_status(self, flag: str, default=None):
        return default if flag not in self.launch_config else self.launch_config[flag]

    def setup(self):
        """
        Setup general stuff which does not take long to complete
        Loads first modules into memory and launches registry setup
        """

        import mcpython.engine.ResourceLoader
        import mcpython.engine.event.EventHandler

        mcpython.engine.ResourceLoader.load_resource_packs()

        self.setup_files()

        if shared.IS_CLIENT:
            self.setup_opengl()

        import mcpython.common.state.StateHandler

        self.setup_registries()

        shared.event_handler.call("minecraft:game:startup")

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

            import pyglet.app

            pyglet.app.exit()

            print("closing due to event stage")
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
        import mcpython.client.gui.ContainerRenderingManager
        import mcpython.common.state.StateHandler

        if not shared.IS_CLIENT:
            mcpython.common.state.StateHandler.load_states()

            import mcpython.common.event.TickHandler

        import mcpython.client.rendering.model.ModelHandler
        import mcpython.common.data.serializer.tags.TagHandler

        import mcpython.client.rendering.model.ItemModel

        import mcpython.common.data.ResourcePipe

        mcpython.common.data.ResourcePipe.load()

        import mcpython.common.data.Language

        mcpython.common.data.Language.load()

        return self

    def setup_opengl(self):
        """
        Helper function for OpenGL setup
        Loads also the needed API
        todo: move more rendering setup code here
        """
        if not shared.IS_CLIENT:
            raise RuntimeError("OpenGL cannot be set up on dedicated server")

        import mcpython.engine.rendering.util

        mcpython.engine.rendering.util.setup()

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
                mcpython.engine.ResourceLoader.read_image(
                    "assets/minecraft/textures/entity/steve.png"
                ).save(shared.build + "/skin.png")
            except:
                logger.print_exception("[FATAL] failed to load default skin")
                sys.exit(-1)

        return self

    def launch(self):
        """
        Launches the game in the current configuration
        Starts the main cycle with pyglet
        Loads the mods (finally!)

        todo: move state selection here
        """

        import mcpython.common.container.crafting.CraftingManager

        # Create the world instance
        import mcpython.common.world.World

        shared.world = mcpython.common.world.World.World()

        if shared.window is not None:
            shared.window.load()
            shared.window.reset_caption()

        if shared.IS_CLIENT:
            try:
                # todo: sometimes, this does not work correctly
                shared.window.set_icon(
                    mcpython.engine.ResourceLoader.read_pyglet_image("icon_16x16.png"),
                    mcpython.engine.ResourceLoader.read_pyglet_image("icon_32x32.png"),
                )
            except:
                logger.print_exception("[FATAL] failed to load window images")
                sys.exit(-1)
        else:
            shared.SERVER_NETWORK_HANDLER.enable_server()

        shared.event_handler.call("minecraft:game:gameloop_startup")

        try:
            import mcpython.engine.Lifecycle
            import pyglet

            pyglet.app.event_loop = mcpython.engine.Lifecycle.Lifecycle()
            pyglet.app.event_loop.run()
        except SystemExit:
            # sys.exit() should not be handled
            raise
        except KeyboardInterrupt:
            sys.exit(-1)
        except:
            logger.print_exception("ERROR DURING RUNTIME (UNHANDLED)")
            import mcpython.common.state.LoadingExceptionViewState

            mcpython.common.state.LoadingExceptionViewState.error_occur(
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

        import mcpython.engine.ResourceLoader

        try:
            mcpython.engine.ResourceLoader.close_all_resources()
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

    @classmethod
    def clean(cls):
        """
        Helper function for normal cleanup (not save, will hard-crash in some cases)
        MAY crash on non-fully stable systems
        Also invokes the event for closing the game, stops the world generation process, ...
        """
        shared.world.world_generation_process.stop()
        import mcpython.engine.ResourceLoader

        mcpython.engine.ResourceLoader.close_all_resources()
        shared.tmp.cleanup()
