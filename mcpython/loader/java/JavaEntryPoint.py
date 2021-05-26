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
import sys
import traceback

import mcpython.common.mod.ExtensionPoint
import mcpython.common.mod.Mod
import mcpython.loader.java.Java
import mcpython.loader.java.Runtime
import mcpython.ResourceLoader
import pyglet.app
from mcpython import logger, shared
from mcpython.loader.java.Java import vm as jvm

jvm.init_builtins()
jvm.init_bridge()


# Replace java bytecode loader with ResourceLoader's lookup system
mcpython.loader.java.Java.get_bytecode_of_class = (
    lambda file: mcpython.ResourceLoader.read_raw(file.replace(".", "/") + ".class")
)
mcpython.loader.java.Java.info = lambda text: logger.println("[JAVA][INFO]", text)
mcpython.loader.java.Java.warn = lambda text: logger.println("[JAVA][WARN]", text)


class JavaMod(mcpython.common.mod.Mod.Mod):
    runtime = mcpython.loader.java.Runtime.Runtime()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loader_version = 0
        self.main_classes = []

    def mod_string(self):
        return super().mod_string() + " [JavaFML]"

    def load_underlying_classes(self):
        """
        Called during mod init for loading the java code from the .jar archives
        """

        for cls in self.main_classes:
            try:
                logger.println(f"[JAVA FML][INFO] loading class {cls}")
                java_class = jvm.get_class(cls)
                jvm.load_lazy()

                logger.println(f"[JAVA FML][INFO] executing class {cls}")
                instance = java_class.create_instance()
                self.runtime.run_method(instance.get_method("<init>", "()V"), instance)

            except:
                logger.print_exception("[JAVA][FATAL] fatal class loader exception")

                if shared.IS_CLIENT:
                    shared.window.set_caption("JavaFML JVM error")

                    try:
                        import mcpython.client.state.StateLoadingException

                        mcpython.client.state.StateLoadingException.error_occur(
                            traceback.format_exc()
                        )
                    except:
                        logger.print_exception("error screen error")
                    else:
                        import mcpython.common.mod.ModLoader

                        raise mcpython.common.mod.ModLoader.LoadingInterruptException

                shared.window.close()
                pyglet.app.exit()
                sys.exit(-1)


class JavaModLoader(mcpython.common.mod.ExtensionPoint.ModLoaderExtensionPoint):
    """
    This is an example extension point for the mod loader
    It binds the java bytecode loader framework together with its bridges to mcpython mod loader
    """

    NAME = "javafml"
    ENABLE_MODS_TOML = True

    @classmethod
    def load_mod_from_toml(cls, file, data):
        loader_version = int(data["loaderVersion"].removeprefix("[").removesuffix(",)"))

        mods = {}

        for d in data["mods"]:
            mod = JavaMod(d["modId"], d["version"].split("-")[-1])
            mods[d["modId"]] = mod
            mod.loader_version = loader_version

            if "mainClass" in d:
                mod.main_classes.append(d["mainClass"])
            else:
                logger.println(
                    "[WARN] java-fml does currently not support dynamic class lookup"
                )

            shared.mod_loader(d["modId"], "stage:mod:init")(mod.load_underlying_classes)

        for mod in data["dependencies"]:
            for d in data["dependencies"][mod]:
                mods[mod].add_dependency(
                    d["modId"] if d["modId"] != "forge" else "minecraft"
                )
