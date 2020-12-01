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

from mcpython import globals as G, logger
import mcpython.common.config
import mcpython.ResourceLocator


class LaunchWrapper:
    def __init__(self):  # todo: store in globals.py
        pass

    def inject_sys_argv(self):  # todo: all sys.argv parsing belongs here
        pass

    def setup(self):
        self.print_header()

        import mcpython.common.event.EventHandler

        import mcpython.ResourceLocator

        mcpython.ResourceLocator.load_resource_packs()

        self.setup_files()

        self.setup_opengl()

        import mcpython.client.state.StateHandler

        self.setup_registries()

        G.eventhandler.call("game:startup")

    def setup_registries(self):
        import mcpython.common.mod.ModLoader

        import mcpython.common.mod.ModMcpython
        import mcpython.common.mod.ConfigFile
        from mcpython.common.data.datagen.mcpython import (
            recipes,
            textures,
            entity,
            blockmodels,
        )

        @G.modloader("minecraft", "special:exit")
        def exit():
            sys.exit()

        import mcpython.common.event.Registry
        import mcpython.common.block.BlockHandler
        import mcpython.common.item.ItemHandler
        import mcpython.common.entity.EntityHandler
        import mcpython.server.gen.WorldGenerationHandler
        import mcpython.server.gen.biome.BiomeHandler
        import mcpython.server.gen.layer
        import mcpython.server.gen.feature

        import mcpython.client.rendering.model.ModelHandler
        import mcpython.common.data.tags.TagHandler

        import mcpython.client.rendering.model.ItemModel

        import mcpython.texture.factory
        import mcpython.setup

    def setup_opengl(self):
        import mcpython.client.rendering.OpenGLSetupFile

        mcpython.client.rendering.OpenGLSetupFile.execute_file_by_name("setup")

    def print_header(self):
        version = mcpython.common.config.FULL_VERSION_NAME.upper()
        logger.println("---------------" + "-" * len(version))
        logger.println("- MCPYTHON 4 {} -".format(version))
        logger.println("---------------" + "-" * len(version))

    def setup_files(self):
        if not os.path.exists(G.home + "/datapacks"):
            os.makedirs(G.home + "/datapacks")

        if not os.path.isdir(G.home):
            os.makedirs(G.home)

        sys.path.append(G.local + "/mcpython")

        # check if build folder exists, if not, we need to create its content
        if not os.path.exists(G.build):
            logger.println("rebuild mode due to missing cache folder")
            G.prebuilding = True

        if os.path.exists(G.build):  # copy default skin to make it start correctly
            try:
                mcpython.ResourceLocator.read(
                    "assets/minecraft/textures/entity/steve.png", "pil"
                ).save(G.build + "/skin.png")
            except:
                logger.print_exception("[FATAL] failed to load default skin")
                sys.exit(-1)

    def load_mods(self):
        G.modloader.look_out()
        G.modloader.sort_mods()
        G.modloader.write_mod_info()

    def launch(self):
        logger.println("tmp storage at {}".format(G.tmp.name))
        self.load_mods()

        # Create the world instance
        import mcpython.common.world.World

        G.world = mcpython.common.world.World.World()

        import pyglet
        import mcpython.client.rendering.window

        # todo: move size to config files
        mcpython.client.rendering.window.Window(
            width=800, height=600, resizable=True
        ).reset_caption()
        try:
            G.window.set_icon(
                mcpython.ResourceLocator.read("icon_16x16.png", "pyglet"),
                mcpython.ResourceLocator.read("icon_32x32.png", "pyglet"),
            )
            G.eventhandler.call("game:gameloop_startup")
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
