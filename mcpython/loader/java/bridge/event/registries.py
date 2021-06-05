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
    """
    Wrapper around the forge registry instances lying around in the system
    register() wraps the underlying registry around our internal registries
    todo: add some mapping registry name -> obj transformer
    """

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
    """
    Wrapper around the class holding all arrival registries
    Contains suppliers to the internal registries where arrival

    This is equivalent to shared/registry and shared/registry.get_by_name(...)
    """

    NAME = "net/minecraftforge/registries/ForgeRegistries"

    def __init__(self):
        super().__init__()
        self.exposed_attributes = {
            "WORLD_TYPES": None,
            "BLOCKS": lambda: shared.registry.get_by_name("minecraft:block"),
            "ITEMS": lambda: shared.registry.get_by_name("minecraft:item"),
        }


class Registry(NativeClass):
    """
    The default mc registry
    All registries implement IForgeRegistry, so this is only decoration

    This is the equivalent to mcpython/event/registry/Registry
    """

    NAME = "net/minecraft/util/registry/Registry"

    def __init__(self):
        super().__init__()
        self.exposed_attributes = {"field_239689_aA_": None, "field_239720_u_": None}

    @native(
        "func_218325_a",
        "(Lnet/minecraft/util/registry/Registry;Ljava/lang/String;Ljava/lang/Object;)Ljava/lang/Object;",
    )
    def func_218325_a(self, registry: mcpython.common.event.Registry.Registry, name: str, obj):
        pass


class RegistryKey(NativeClass):
    NAME = "net/minecraft/util/RegistryKey"

    @native("func_240903_a_", "(Lnet/minecraft/util/RegistryKey;Lnet/minecraft/util/ResourceLocation;)Lnet/minecraft/util/RegistryKey;")
    def func_240903_a_(self, key, location):
        return key


def parseBlockToFactory(obj):
    if not hasattr(obj, "registry_name"):
        logger.println(f"[JAVAFML][TRANSFORMER] transformation of {obj} failed as no registry name is set!")
        return

    import mcpython.common.factory.BlockFactory

    instance = mcpython.common.factory.BlockFactory.BlockFactory().set_name(shared.CURRENT_EVENT_SUB+":"+obj.registry_name)
    cls = obj.get_class()

    if cls.is_subclass_of("net/minecraft/block/SandBlock"):
        instance.set_fall_able()
    elif cls.is_subclass_of("net/minecraft/block/StairBlock"):
        instance.set_default_model_state("facing=east,half=bottom,shape=inner_left")
    elif cls.is_subclass_of("net/minecraft/block/SlabBlock"):
        instance.set_slab()
    elif cls.is_subclass_of("net/minecraft/block/WallBlock"):
        instance.set_wall()
    elif cls.is_subclass_of("net/minecraft/block/FlowerPotBlock") or cls.is_subclass_of("net/minecraft/block/LeavesBlock"):
        instance.set_solid(False).set_all_side_solid(False)
    elif cls.is_subclass_of("net/minecraft/block/RotatedPillarBlock"):
        instance.set_log()
    else:
        print(obj, obj.registry_name)

    try:
        instance.set_strength(obj.properties.hardness, obj.properties.blast_resistance)
    except AttributeError:
        raise AttributeError(obj, instance)

    instance.finish()
