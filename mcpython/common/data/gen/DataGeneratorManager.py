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
import simplejson
import os
from mcpython import logger
from mcpython import shared


class UnsupportedIndirectDumpException(Exception):
    pass


class IDataGenerator:
    def dump(self, generator: "DataGeneratorInstance"):
        raise UnsupportedIndirectDumpException()

    def write(self, generator: "DataGeneratorInstance", name: str):
        file = self.get_default_location(generator, name)
        if file is None:
            logger.println(
                "Failed to dump data generator {} named '{}', as no file was returned".format(
                    self, name
                )
            )
            return

        try:
            data = self.dump(generator)
        except:
            logger.print_exception(
                f"Failed to serialize data generator {self} named '{name}', This is a bad thing!"
            )
            return

        generator.write(
            simplejson.dumps(data, indent="  ").encode("utf-8"), file
        )

    def get_default_location(
        self, generator: "DataGeneratorInstance", name: str
    ) -> str:
        pass


class DataGeneratorInstance:
    def __init__(self, location: str):
        self.default_namespace = None
        self.to_generate = []
        self.location = location.format(local=shared.local)
        shared.mod_loader["minecraft"].eventbus.subscribe(
            "special:datagen:generate", self.generate
        )

    def write(self, data: bytes, file: str):
        file = self.get_full_path(file)
        os.makedirs(os.path.dirname(file), exist_ok=True)
        with open(file, mode="wb") as f:
            f.write(data)

    def get_full_path(self, file: str) -> str:
        return os.path.join(self.location, file)

    def annotate(self, generator: IDataGenerator, name: str):
        self.to_generate.append((generator, name))

    def generate(self):
        for generator, name in self.to_generate:
            print(f"running data generator named '{name}'")
            try:
                generator.write(self, name)
            except UnsupportedIndirectDumpException:
                logger.print_exception(
                    "Failed to write data generator {} named '{}', This is a bad thing!".format(
                        generator, name
                    )
                )
