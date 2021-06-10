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
from mcpython.loader.java.JavaExceptionStack import StackCollectingException

jvm.init_builtins()
jvm.init_bridge()


# Replace java bytecode loader with ResourceLoader's lookup system
mcpython.loader.java.Java.get_bytecode_of_class = (
    lambda file: mcpython.ResourceLoader.read_raw(file.replace(".", "/") + ".class")
)
# mcpython.loader.java.Java.info = lambda text: logger.println("[JAVA][INFO]", text)
mcpython.loader.java.Java.warn = lambda text: logger.println("[JAVA][WARN]", text)


class JavaMod(mcpython.common.mod.Mod.Mod):
    runtime = mcpython.loader.java.Runtime.Runtime()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loader_version = 0

    def mod_string(self):
        return super().mod_string() + " [JavaFML]"

    def load_underlying_classes(self):
        """
        Called during mod init for loading the java code from the .jar archives
        """

        for file in self.resource_access.get_all_entries_in_directory(""):
            if not file.endswith(".class"):
                continue

            self.load_mod_file(file)

    def load_mod_file(self, file: str):
        import mcpython.client.state.StateLoadingException

        cls = file.split(".")[0]
        try:
            # make sure that this is set!
            shared.CURRENT_EVENT_SUB = self.name

            jvm.load_class(cls, version=self.loader_version)

            # todo: check if mod main class

            if False:
                jvm.load_lazy()

                logger.println(f"[JAVA FML][INFO] executing class {cls}")
                instance = java_class.create_instance()
                self.runtime.run_method(instance.get_method("<init>", "()V"), instance)

        except StackCollectingException as e:
            if shared.IS_CLIENT:
                shared.window.set_caption("JavaFML JVM error")

                try:
                    import mcpython.client.state.StateLoadingException

                    exception = e.format_exception()
                    mcpython.client.state.StateLoadingException.error_occur(exception)
                    logger.print_exception("raw exception trace")
                    logger.write_into_container(
                        "fatal FML error", exception.split("\n")
                    )
                except:
                    logger.print_exception("error screen error")
                else:
                    import mcpython.common.mod.ModLoader

                    raise mcpython.common.mod.ModLoader.LoadingInterruptException from None

            shared.window.close()
            pyglet.app.exit()
            sys.exit(-1)

        except mcpython.common.mod.ModLoader.LoadingInterruptException:
            raise

        except:
            logger.print_exception("[JAVA][FATAL] fatal class loader exception")

            if shared.IS_CLIENT:
                shared.window.set_caption("JavaFML JVM error")

                try:
                    mcpython.client.state.StateLoadingException.error_occur(
                        traceback.format_exc()
                    )
                except:
                    logger.print_exception("error screen error")
                else:
                    import mcpython.common.mod.ModLoader

                    raise mcpython.common.mod.ModLoader.LoadingInterruptException from None

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
        loader_version = int(data["loaderVersion"].removeprefix("[").removesuffix(",)").removesuffix(",]").split(".")[0].split(",")[0])

        mods = {}

        for d in data["mods"]:
            mod = JavaMod(d["modId"], d["version"].split("-")[-1])
            mod.add_load_default_resources()
            mods[d["modId"]] = mod
            mod.loader_version = loader_version

            shared.mod_loader(d["modId"], "stage:mod:init")(mod.load_underlying_classes)

        if "dependencies" in data:
            for mod in data["dependencies"]:
                # these are error handlers, they should NOT be here... Some people produce really bad mods!

                if isinstance(mod, dict):
                    logger.println(f"[FML][SEMI FATAL] skipping dependency block {mod} as block is invalid [provided mods: {list(mod.keys())}]")
                    continue

                if mod not in mods:
                    logger.println(f"[FML][HARD WARN] reference error in dependency block to {mod} [provided: {list(mods.keys())}]")
                    continue

                try:
                    for d in data["dependencies"][mod]:
                        # search for optional deps
                        if not d["mandatory"]:
                            continue

                        mods[mod].add_dependency(
                            d["modId"] if d["modId"] != "forge" else "minecraft"
                        )
                except:
                    logger.print_exception("decoding dependency structure", str(mod), data)
