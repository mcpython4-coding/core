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
import mcpython.common.event.Registry
from mcpython import logger, shared
from mcpython.loader.java.Java import NativeClass, native


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
            logger.println(
                f"[JAVAFML][WARN] object {entry} could not get registered to registry!"
            )
            return

        registry = registry()

        if registry.name == "minecraft:block":
            parseBlockToFactory(entry)
        elif registry.name == "minecraft:item":
            parseItemToFactory(entry)


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
            "SOUND_EVENTS": None,
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
        self.exposed_attributes = {
            "field_239689_aA_": None,
            "field_239720_u_": None,
            "field_212618_g": None,
            "field_239690_aB_": None,
        }

    @native(
        "func_218325_a",
        "(Lnet/minecraft/util/registry/Registry;Ljava/lang/String;Ljava/lang/Object;)Ljava/lang/Object;",
    )
    def func_218325_a(
        self, registry: mcpython.common.event.Registry.Registry, name: str, obj
    ):
        pass

    @native("func_218322_a", "(Lnet/minecraft/util/registry/Registry;Lnet/minecraft/util/ResourceLocation;Ljava/lang/Object;)Ljava/lang/Object;")
    def func_218322_a(self, registry, name, obj):
        return obj


class RegistryKey(NativeClass):
    NAME = "net/minecraft/util/RegistryKey"

    @native(
        "func_240903_a_",
        "(Lnet/minecraft/util/RegistryKey;Lnet/minecraft/util/ResourceLocation;)Lnet/minecraft/util/RegistryKey;",
    )
    def func_240903_a_(self, key, location):
        return key


class RegistryObject(NativeClass):
    NAME = "net/minecraftforge/fml/RegistryObject"

    @native(
        "of",
        "(Lnet/minecraft/util/ResourceLocation;Lnet/minecraftforge/registries/IForgeRegistry;)Lnet/minecraftforge/fml/RegistryObject;",
    )
    def of(self, location, registry):
        return registry().get(location.name) if registry is not None else None


class ObjectHolder(NativeClass):
    NAME = "net/minecraftforge/registries/ObjectHolder"

    def on_annotate(self, cls, args):
        pass


def parseBlockToFactory(obj):
    if not hasattr(obj, "registry_name"):
        logger.println(
            f"[JAVAFML][TRANSFORMER] transformation of {obj} failed as no registry name is set!"
        )
        return

    import mcpython.common.factory.BlockFactory

    instance = mcpython.common.factory.BlockFactory.BlockFactory().set_name(
        shared.CURRENT_EVENT_SUB + ":" + obj.registry_name
    )
    cls = obj.get_class()

    if cls.is_subclass_of("net/minecraft/block/SandBlock"):
        instance.set_fall_able()
    elif cls.is_subclass_of("net/minecraft/block/StairsBlock"):
        instance.set_default_model_state(
            "facing=east,half=bottom,shape=inner_left"
        ).set_solid(False).set_all_side_solid(False)
    elif cls.is_subclass_of("net/minecraft/block/SlabBlock"):
        instance.set_slab()
    elif cls.is_subclass_of("net/minecraft/block/WallBlock"):
        instance.set_wall()
    elif cls.is_subclass_of("net/minecraft/block/FlowerPotBlock") or cls.is_subclass_of(
        "net/minecraft/block/LeavesBlock"
    ):
        instance.set_solid(False).set_all_side_solid(False)
    elif cls.is_subclass_of("net/minecraft/block/RotatedPillarBlock"):
        instance.set_log()
    # else:
    #     print(obj, obj.registry_name)

    try:
        instance.set_strength(obj.properties.hardness, obj.properties.blast_resistance)
    except AttributeError:
        raise AttributeError(obj, instance)

    instance.finish()


def parseItemToFactory(obj):
    cls = obj.get_class()

    name = shared.CURRENT_EVENT_SUB + ":" + obj.registry_name

    # we can skip BlockItems as they are created on the fly
    # todo: inject item properties somewhere
    if cls.is_subclass_of("net/minecraft/item/BlockItem"):
        if obj.properties is not None and obj.properties.item_group is not None:
            obj.properties.item_group.underlying_tab.add_item(name)
        return

    import mcpython.common.factory.ItemFactory

    instance = mcpython.common.factory.ItemFactory.ItemFactory().set_name(name)

    try:
        tab = obj.properties.item_group

        if tab is not None:
            # todo: do we need a lazy here?
            tab.underlying_tab.add_item(name)
    except AttributeError:
        raise AttributeError(obj, instance)

    instance.finish()


class RegistryEvent__Register(NativeClass):
    NAME = "net/minecraftforge/event/RegistryEvent$Register"

    @native("getRegistry", "()Lnet/minecraftforge/registries/IForgeRegistry;")
    def getRegistry(self, instance):
        return lambda: instance


class RenderingRegistry(NativeClass):
    NAME = "net/minecraftforge/fml/client/registry/RenderingRegistry"

    @native(
        "registerEntityRenderingHandler",
        "(Lnet/minecraft/entity/EntityType;Lnet/minecraftforge/fml/client/registry/IRenderFactory;)V",
    )
    def registerEntityRenderingHandler(self, entity_type, render_factory):
        pass


class DefaultRegistry(NativeClass):
    NAME = "net/minecraft/util/registry/DefaultedRegistry"

    @native(
        "func_177774_c", "(Ljava/lang/Object;)Lnet/minecraft/util/ResourceLocation;"
    )
    def func_177774_c(self, instance, obj):
        pass

    @native("func_241873_b", "(Lnet/minecraft/util/ResourceLocation;)Ljava/util/Optional;")
    def func_241873_b(self, instance, obj):
        pass
