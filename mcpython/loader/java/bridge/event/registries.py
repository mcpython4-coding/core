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
from mcpython import shared, logger
from mcpython.loader.java.Java import NativeClass, native
import mcpython.common.event.Registry


class GameData(NativeClass):
    NAME = "net/minecraftforge/registries/GameData"


class IForgeRegistry(NativeClass):
    NAME = "net/minecraftforge/registries/IForgeRegistry"

    @native("register", "(Lnet/minecraftforge/registries/IForgeRegistryEntry;)V")
    def register(self, registry, entry):
        if registry is None:
            logger.println(f"[JAVAFML][WARN] object {entry} could not get registered to registry!")
            return

        registry = registry()

        if registry.name == "minecraft:block":
            parseBlockToFactory(entry)


class ForgeRegistries(NativeClass):
    NAME = "net/minecraftforge/registries/ForgeRegistries"

    def __init__(self):
        super().__init__()
        self.exposed_attributes = {
            "WORLD_TYPES": None,
            "BLOCKS": lambda: shared.registry.get_by_name("minecraft:block"),
            "ITEMS": lambda: shared.registry.get_by_name("minecraft:item"),
        }


class Registry(NativeClass):
    NAME = "net/minecraft/util/registry/Registry"

    def __init__(self):
        super().__init__()
        self.exposed_attributes = {"field_239689_aA_": None}

    @native(
        "func_218325_a",
        "(Lnet/minecraft/util/registry/Registry;Ljava/lang/String;Ljava/lang/Object;)Ljava/lang/Object;",
    )
    def func_218325_a(self, registry: mcpython.common.event.Registry.Registry, name: str, obj):
        pass


def parseBlockToFactory(obj):
    if not hasattr(obj, "registry_name"):
        logger.println(f"[JAVAFML][TRANSFORMER] transformation of {obj} failed as no registry name is set!")
        return

    import mcpython.common.factory.BlockFactory

    instance = mcpython.common.factory.BlockFactory.BlockFactory().set_name("biomesoplenty:"+obj.registry_name)
    instance.finish()

