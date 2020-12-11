"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import json
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
                "[WARN] failed to dump data generator {} named {}, as no file was returned".format(
                    self, name
                )
            )
            return
        generator.write(json.dumps(self.dump(generator)).encode("utf-8"), file)

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
        with open(file, mode="wb") as f:
            f.write(data)

    def get_full_path(self, file: str) -> str:
        return os.path.join(self.location, file)

    def annotate(self, generator: IDataGenerator, name: str):
        self.to_generate.append((generator, name))

    def generate(self):
        for generator, name in self.to_generate:
            try:
                generator.write(self, name)
            except UnsupportedIndirectDumpException:
                logger.print_exception(
                    "[WARN] failed to dump data generator {} named {}".format(
                        generator, name
                    )
                )
