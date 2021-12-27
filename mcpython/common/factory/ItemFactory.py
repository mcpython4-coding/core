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
import copy
import typing

import mcpython.common.factory.IFactoryModifier
import mcpython.common.item.AbstractArmorItem
import mcpython.common.item.AbstractDamageBarItem
import mcpython.common.item.AbstractFoodItem
import mcpython.common.item.AbstractItem
import mcpython.common.item.AbstractToolItem
from mcpython import shared
from mcpython.common.factory.FactoryBuilder import FactoryBuilder

ItemFactoryInstance = FactoryBuilder(
    "minecraft:item", mcpython.common.item.AbstractItem.AbstractItem
)

ItemFactoryInstance.register_configurator(
    FactoryBuilder.SetterFactoryConfigurator("set_name", "name", str)
)
ItemFactoryInstance.register_configurator(
    FactoryBuilder.SetterFactoryConfigurator("set_global_mod_name", "global_name", str)
)
ItemFactoryInstance.register_configurator(
    FactoryBuilder.SetterFactoryConfigurator(
        "set_max_stack_size", "max_stack_size", int
    )
)
ItemFactoryInstance.register_configurator(
    FactoryBuilder.SetterFactoryConfigurator(
        "set_fuel_level", "fuel_level", (float, int)
    )
)
ItemFactoryInstance.register_configurator(
    FactoryBuilder.SetterFactoryConfigurator("set_has_block_flag", "has_block")
)
ItemFactoryInstance.register_configurator(
    FactoryBuilder.SetterFactoryConfigurator(
        "set_tool_tip_renderer", "tool_tip_renderer"
    )
)
ItemFactoryInstance.register_configurator(
    FactoryBuilder.SetterFactoryConfigurator(
        "set_tool_break_multi", "tool_break_multi", (int, float)
    )
)
ItemFactoryInstance.register_configurator(
    FactoryBuilder.SetterFactoryConfigurator(
        "set_tool_level", "tool_level", (int, float)
    )
)


@ItemFactoryInstance.register_configurator(
    FactoryBuilder.AnnotationFactoryConfigurator("set_food_value")
)
def set_food_value(factory, value: int):
    factory.config_table["food_value"] = value
    factory.add_base_class(mcpython.common.item.AbstractFoodItem.AbstractFoodItem)


@ItemFactoryInstance.register_configurator(
    FactoryBuilder.AnnotationFactoryConfigurator("set_default_item_file")
)
def set_default_item_file(factory, file):
    factory.config_table["default_item_file"] = file
    factory.config_table.setdefault("used_item_files", []).append(file)


@ItemFactoryInstance.register_configurator(
    FactoryBuilder.AnnotationFactoryConfigurator("set_eat_callback")
)
def set_eat_callback(instance, callback):
    instance.config_table["eat_callback"] = callback


@ItemFactoryInstance.register_configurator(
    FactoryBuilder.AnnotationFactoryConfigurator("set_durability")
)
def set_durability(instance, value):
    instance.config_table["durability"] = value
    instance.add_base_class(mcpython.common.item.AbstractDamageBarItem.DamageOnUseItem)


@ItemFactoryInstance.register_configurator(
    FactoryBuilder.AnnotationFactoryConfigurator("set_tool_type")
)
def set_tool_type(instance, *value):
    if len(value) != 0:
        if isinstance(value[0], (list, set, tuple)):
            value = set(value[0])
        else:
            value = set(value)

    try:
        instance.config_table.setdefault("tool_type", set()).update(set(value))
    except TypeError:
        print(value)
        raise

    instance.add_base_class(mcpython.common.item.AbstractToolItem.AbstractToolItem)


@ItemFactoryInstance.register_configurator(
    FactoryBuilder.AnnotationFactoryConfigurator("set_armor_points")
)
def set_armor_points(instance, points: int):
    instance.config_table["armor_points"] = points
    instance.add_base_class(mcpython.common.item.AbstractArmorItem.AbstractArmorItem)


ItemFactoryInstance.register_configurator(
    FactoryBuilder.FunctionStackedAnnotator(
        "set_custom_from_item_function", "custom_from_item_funcs"
    )
)


@ItemFactoryInstance.register_class_builder(
    FactoryBuilder.AnnotationFactoryClassBuilder()
)
def build_class(
    cls: typing.Type[mcpython.common.item.AbstractItem.AbstractItem],
    instance: FactoryBuilder.IFactory,
):
    configs: dict = instance.config_table
    import mcpython.client.gui.HoveringItemBox

    # configs.setdefault(
    #     "tool_tip_renderer", mcpython.client.gui.HoveringItemBox.DEFAULT_ITEM_TOOLTIP
    # )
    name = configs["name"]
    if ":" not in name and "global_name" in configs:
        name = configs["global_name"] + ":" + name

    if "default_item_file" not in configs:
        configs["default_item_file"] = "assets/{}/textures/item/{}.png".format(
            *name.split(":")
        )
        configs.setdefault("used_item_files", []).append(configs["default_item_file"])

    class ModifiedClass(cls):
        NAME = name
        STACK_SIZE = configs.setdefault("max_stack_size", cls.STACK_SIZE)
        HUNGER_ADDITION = configs.setdefault(
            "food_value", cls.HUNGER_ADDITION if hasattr(cls, "HUNGER_ADDITION") else 0
        )
        HAS_BLOCK = configs.setdefault("has_block", cls.HAS_BLOCK)

        if "fuel_level" in configs:
            FUEL = configs["fuel_level"]

        @classmethod
        def get_used_texture_files(
            cls,
        ):
            return (
                configs["used_item_files"]
                if "used_item_files" in configs
                else cls.get_used_texture_files()
            )

        @classmethod
        def get_default_item_image_location(cls) -> str:
            return (
                configs["default_item_file"]
                if "default_item_file" in configs
                else cls.get_default_item_image_location()
            )

        def get_active_image_location(self):
            return (
                configs["default_item_file"]
                if "default_item_file" in configs
                else cls.get_active_image_location(self)
            )

        def get_tooltip_provider(self):
            return (
                configs["tool_tip_renderer"]
                if "tool_tip_renderer" in configs
                else cls.get_tooltip_provider(self)
            )

        if "eat_callback" in configs:

            async def on_eat(self, itemstack):
                await configs["eat_callback"](self, itemstack)

                if hasattr(cls, "on_eat"):
                    await cls.on_eat(self, itemstack)

        if "durability" in configs:
            DURABILITY = configs["durability"]
        elif hasattr(cls, "DURABILITY"):
            DURABILITY = cls.DURABILITY

        if "tool_type" in configs:
            TOOL_TYPE = configs["tool_type"]
            TOOL_LEVEL = configs["tool_level"]

            def get_speed_multiplyer(self, itemstack):
                return configs.setdefault("tool_break_multi", 1)

        elif hasattr(cls, "TOOL_TYPE"):
            TOOL_TYPE = cls.TOOL_TYPE
            TOOL_LEVEL = cls.TOOL_LEVEL

            def get_speed_multiplyer(self, itemstack):
                return cls.get_speed_multiplyer(self, itemstack)

        if "armor_points" in configs:
            DEFENSE_POINTS = configs["armor_points"]
        elif hasattr(cls, "DEFENSE_POINTS"):
            DEFENSE_POINTS = cls.DEFENSE_POINTS

        async def on_set_from_item(self, block):
            for func in configs["custom_from_item_funcs"]:
                await func(self, block)

            await super().on_set_from_item(block)

    return ModifiedClass


ItemFactoryInstance.register_direct_copy_attributes(
    "used_item_files",
)
ItemFactoryInstance.register_direct_copy_attributes(
    "tool_type", "custom_from_item_funcs", operation=lambda e: e.copy()
)
ItemFactoryInstance.register_direct_copy_attributes(
    "tool_tip_renderer",
    "name",
    "global_name",
    "max_stack_size",
    "food_value",
    "fuel_level",
    "has_block",
    "default_item_file",
    "eat_callback",
    "durability",
    "tool_break_multi",
    "tool_level",
    "armor_points",
    operation=lambda e: e,
)


ItemFactory = ItemFactoryInstance.create_class()
