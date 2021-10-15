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
import typing

import mcpython.engine.ResourceLoader
import mcpython.util.texture
import PIL.Image
from mcpython import shared
from mcpython.common.event.DeferredRegistryHelper import DeferredRegistry


def colorize_texture(
    factory: "CombinedFactoryInstance",
    image: PIL.Image.Image,
    color: typing.Tuple[int, int, int, int],
) -> PIL.Image.Image:
    return mcpython.util.texture.colorize(image, color)


class CombinedFactoryInstance:
    """
    Factory system for constructing a whole block/item group at ones
    This is the simple variant, allowing for configuration and than single block construction
    todo: add a variant with template system for defining e.g. wood which than construct all needed wood items for
        it
    todo: add a system to auto-add to creative tabs
    """

    FILE_COUNTER = 0

    def __init__(
        self,
        target_base_name: str,
        default_texture: str = "assets/missing_texture.png",
        color: typing.Tuple[int, int, int, int] = None,
        color_texture_consumer: typing.Callable[
            [
                "CombinedFactoryInstance",
                PIL.Image.Image,
                typing.Tuple[int, int, int, int],
            ],
            PIL.Image.Image,
        ] = colorize_texture,
        deferred_registry: DeferredRegistry = None,
    ):
        """
        Creates a new CombinedFactoryInstance instance
        :param target_base_name: the base name of the block
        :param default_texture: the default texture file
        :param color: a optional color to color the texture in
        :param color_texture_consumer: a consumer for colorizing the textures
        """
        self.target_base_name = target_base_name
        self.default_texture = default_texture
        self.color = color
        self.color_texture_consumer = color_texture_consumer
        self.deferred_registry = deferred_registry

    def create_colored_texture(
        self, texture: typing.Union[PIL.Image.Image, str], color=None
    ):
        """
        Helper function for colorizing the texture at runtime
        :param texture: the texture to transform
        :param color: optional: the color, when differing from color attribute
        """
        if not os.path.exists(shared.build + "/colorized_images"):
            os.makedirs(shared.build + "/colorized_images")

        if isinstance(texture, str):
            texture = mcpython.engine.ResourceLoader.read_image(texture)

        file = shared.build + "/colorized_images/{}.png".format(
            CombinedFactoryInstance.FILE_COUNTER
        )
        CombinedFactoryInstance.FILE_COUNTER += 1
        if color is None:
            color = self.color
        if color is None:
            texture.save(file)
        else:
            self.color_texture_consumer(self, texture, color).save(file)
        return file

    def create_full_block(self, suffix=None, texture=None, color=None, **consumers):
        """
        Creates a full block using the "minecraft:block/cube_all"-model
        :param suffix: suffix for the name, when None, the name itself is used, when not None, a _ is inserted in
            between
        :param texture: the texture to use, None for default
        :param color: color to use for colorizing; None for default
        :param consumers: the consumers send to create_block_simple()
        """
        if texture is None:
            texture = self.default_texture
        name = (
            (
                self.target_base_name
                if suffix is None
                else self.target_base_name + "_" + suffix
                if not callable(suffix)
                else suffix(self.target_base_name)
            )
            if not suffix or ":" not in suffix
            else suffix
        )
        self.create_block_simple(
            name,
            textures={"all": self.create_colored_texture(texture, color=color)},
            block_parent="minecraft:block/cube_all",
            **consumers,
        )
        return self

    def create_block_simple(
        self,
        name: str,
        textures=None,
        block_parent="minecraft:block/block",
        model_info=None,
        block_factory_consumer: typing.Callable[
            ["CombinedFactoryInstance", typing.Any], None
        ] = None,
        block_model_consumer: typing.Callable[
            ["CombinedFactoryInstance", dict], dict
        ] = None,
        item_model_consumer: typing.Callable[
            ["CombinedFactoryInstance", dict], dict
        ] = None,
        block_state_consumer: typing.Callable[
            ["CombinedFactoryInstance", dict], dict
        ] = None,
    ):
        """
        Helper method for creating a full set of block & item with needed data
        Use the consumers to modify the generated content if you need to
        :param name: the name of the block/item
        :param textures: the textures to use
        :param block_parent: the block model parent
        :param block_factory_consumer: a consumer taking a BlockFactory
        :param block_model_consumer: a consumer for the block model data, returning modified data
        :param item_model_consumer: a consumer for the item model data, returning modified data
        :param block_state_consumer: a consumer for the block state data, returning modified data
        """
        mod_name = name.split(":")[0]
        if mod_name not in shared.mod_loader:
            mod_name = "minecraft"
        model_name = "{}:block/{}".format(*name.split(":"))

        @shared.mod_loader(mod_name, "stage:block:factory_usage")
        def block_instance():
            import mcpython.common.factory.BlockFactory

            instance = mcpython.common.factory.BlockFactory.BlockFactory().set_name(
                name
            )
            if callable(block_factory_consumer):
                block_factory_consumer(self, instance)

            if self.deferred_registry is None:
                instance.finish()
            else:
                self.deferred_registry.create_later(instance)

        if shared.IS_CLIENT:

            @shared.mod_loader(mod_name, "stage:model:model_search")
            def block_model():
                data = {"parent": block_parent, "textures": textures}
                if callable(block_model_consumer):
                    data = block_model_consumer(self, data)

                shared.model_handler.add_from_data(model_name, data)

            @shared.mod_loader(mod_name, "stage:model:blockstate_search")
            def block_state():
                data = {
                    "variants": {
                        "default": {"model": model_name}
                        | (model_info if model_info is not None else {})
                    }
                }
                if callable(block_state_consumer):
                    data = block_state_consumer(self, data)

                import mcpython.client.rendering.model.BlockState

                mcpython.client.rendering.model.BlockState.BlockStateContainer.from_data(
                    name, data
                )

            # todo: implement item models here

        return self

    def generate_log_like(
        self,
        suffix=None,
        front_texture=None,
        side_texture=None,
        color=None,
        **consumers,
    ):
        """
        Creates a set for a log like block
        :param suffix: the name suffix
        :param front_texture: the front texture
        :param side_texture: the side texture
        :param color: the color for the texture
        :param consumers: consumers for the data
        """
        if front_texture is None:
            front_texture = self.default_texture
        if side_texture is None:
            side_texture = self.default_texture
        name = (
            (
                self.target_base_name
                if suffix is None
                else self.target_base_name + "_" + suffix
                if not callable(suffix)
                else suffix(self.target_base_name)
            )
            if not suffix or ":" not in suffix
            else suffix
        )
        front_texture = self.create_colored_texture(front_texture, color=color)
        side_texture = self.create_colored_texture(side_texture, color=color)
        textures = {"end": front_texture, "side": side_texture}
        self.create_multi_variant_block(
            name,
            {
                "state": "axis=x",
                "parent": "minecraft:block/cube_column_horizontal",
                "model_name_suffix": "horizontal",
                "textures": textures,
                "model_info": {"x": 90, "y": 90},
            },
            {
                "state": "axis=y",
                "parent": "minecraft:block/cube_column",
                "model_name_suffix": "standing",
                "textures": textures,
            },
            {"state": "axis=z", "reuse": True, "model_info": {"x": 90}},
            block_factory_consumer=lambda _, instance: instance.set_log()
            == (
                0
                if "block_factory_consumer" not in consumers
                else consumers["block_factory_consumer"](_, instance)
            ),
            **{
                key: value
                for key, value in consumers.items()
                if key != "block_factory_consumer"
            },
        )
        return self

    def create_button_block(self, suffix=None, texture=None, color=None, **consumers):
        if texture is None:
            texture = self.default_texture
        name = (
            (
                self.target_base_name
                if suffix is None
                else self.target_base_name + "_" + suffix
                if not callable(suffix)
                else suffix(self.target_base_name)
            )
            if not suffix or ":" not in suffix
            else suffix
        )
        normal_model = "{}:block/{}_normal".format(*name.split(":"))
        pressed_model = "{}:block/{}_pressed".format(*name.split(":"))
        self.create_multi_variant_block(
            name,
            block_state_parent="minecraft:button_template",
            block_state_alias={"normal": normal_model, "pressed": pressed_model},
            block_factory_consumer=lambda _, instance: instance.set_button()
            == (
                0
                if "block_factory_consumer" not in consumers
                else consumers["block_factory_consumer"](_, instance)
            ),
            **{
                key: value
                for key, value in consumers.items()
                if key != "block_factory_consumer"
            },
        )

        if shared.IS_CLIENT:
            mod_name = name.split(":")[0]
            if mod_name not in shared.mod_loader:
                mod_name = "minecraft"

            @shared.mod_loader(mod_name, "stage:model:model_search")
            def generate_models():
                self.inner_generate_model(
                    {
                        "parent": "minecraft:block/button",
                        "textures": {"texture": texture},
                    },
                    normal_model,
                )
                self.inner_generate_model(
                    {
                        "parent": "minecraft:block/button_pressed",
                        "textures": {"texture": texture},
                    },
                    pressed_model,
                )

        return self

    def create_slab_block(self, suffix=None, texture=None, color=None, **consumers):
        if texture is None:
            texture = self.default_texture
        name = (
            (
                self.target_base_name
                if suffix is None
                else self.target_base_name + "_" + suffix
                if not callable(suffix)
                else suffix(self.target_base_name)
            )
            if not suffix or ":" not in suffix
            else suffix
        )
        texture = self.create_colored_texture(texture, color=color)
        slab_data = {"top": texture, "bottom": texture, "side": texture}
        self.create_multi_variant_block(
            name,
            {
                "state": "type=bottom",
                "parent": "minecraft:block/slab",
                "model_name_suffix": "bottom",
                "textures": slab_data,
            },
            {
                "state": "type=top",
                "parent": "minecraft:block/slab_top",
                "model_name_suffix": "top",
                "textures": slab_data,
            },
            {
                "state": "type=double",
                "parent": "minecraft:block/cube_all",
                "model_name_suffix": "double",
                "textures": {"all": texture},
            },
            block_factory_consumer=lambda _, instance: instance.set_slab()
            == (
                0
                if "block_factory_consumer" not in consumers
                else consumers["block_factory_consumer"](_, instance)
            ),
            **{
                key: value
                for key, value in consumers.items()
                if key != "block_factory_consumer"
            },
        )
        return self

    def create_multi_variant_block(
        self,
        name: str,
        *states,
        block_factory_consumer: typing.Callable[
            ["CombinedFactoryInstance", typing.Any], None
        ] = None,
        block_state_consumer: typing.Callable[
            ["CombinedFactoryInstance", dict], dict
        ] = None,
        block_state_parent=None,
        block_state_alias=None,
    ):
        mod_name = name.split(":")[0]
        if mod_name not in shared.mod_loader:
            mod_name = "minecraft"
        model_name = "{}:block/{}".format(*name.split(":"))

        @shared.mod_loader(mod_name, "stage:block:factory_usage")
        def block_instance():
            import mcpython.common.factory.BlockFactory

            instance = mcpython.common.factory.BlockFactory.BlockFactory().set_name(
                name
            )
            if callable(block_factory_consumer):
                block_factory_consumer(self, instance)

            if self.deferred_registry is None:
                instance.finish()
            else:
                self.deferred_registry.create_later(instance)

        if shared.IS_CLIENT:

            @shared.mod_loader(mod_name, "stage:model:model_search")
            def block_model():
                for variant in states:
                    self.inner_generate_model(variant, model_name)

            @shared.mod_loader(mod_name, "stage:model:blockstate_search")
            def block_state():
                data = {
                    "variants": {
                        variant["state"]: {
                            "model": model_name
                            + "_"
                            + variant.setdefault("model_name_suffix", "default")
                        }
                        | variant.setdefault("model_info", {})
                        for variant in states
                    }
                }

                if block_state_parent is not None:
                    data["parent"] = block_state_parent

                if block_state_alias is not None:
                    data["alias"] = block_state_alias

                if callable(block_state_consumer):
                    data = block_state_consumer(self, data)

                import mcpython.client.rendering.model.BlockState

                mcpython.client.rendering.model.BlockState.BlockStateContainer.from_data(
                    name, data
                )

            # todo: implement item models here

        return self

    def create_wall(self, suffix=None, texture=None, color=None, **consumers):
        if texture is None:
            texture = self.default_texture

        name = (
            (
                self.target_base_name
                if suffix is None
                else self.target_base_name + "_" + suffix
                if not callable(suffix)
                else suffix(self.target_base_name)
            )
            if not suffix or ":" not in suffix
            else suffix
        )

        texture = self.create_colored_texture(texture, color=color)
        wall_textures = {"wall": texture}
        # todo: can we use some form of template here?
        self.create_multipart_block(
            name,
            {
                "when": {"up": "true"},
                "model_name_suffix": "post",
                "textures": wall_textures,
                "parent": "minecraft:block/template_wall_post",
            },
            {
                "when": {"north": "low"},
                "model_name_suffix": "side",
                "model_info": {"uvlock": True},
                "textures": wall_textures,
                "parent": "minecraft:block/template_wall_side",
            },
            {
                "when": {"east": "low"},
                "model_name_suffix": "side",
                "reuse": True,
                "model_info": {"uvlock": True, "y": 90},
                "textures": wall_textures,
            },
            {
                "when": {"south": "low"},
                "model_name_suffix": "side",
                "reuse": True,
                "model_info": {"uvlock": True, "y": 180},
                "textures": wall_textures,
            },
            {
                "when": {"west": "low"},
                "model_name_suffix": "side",
                "reuse": True,
                "model_info": {"uvlock": True, "y": 270},
                "textures": wall_textures,
            },
            {
                "when": {"north": "tall"},
                "model_name_suffix": "side_tall",
                "model_info": {"uvlock": True},
                "textures": wall_textures,
                "parent": "minecraft:block/template_wall_side_tall",
            },
            {
                "when": {"east": "tall"},
                "model_name_suffix": "side_tall",
                "reuse": True,
                "model_info": {"uvlock": True, "y": 90},
                "textures": wall_textures,
            },
            {
                "when": {"south": "tall"},
                "model_name_suffix": "side_tall",
                "reuse": True,
                "model_info": {"uvlock": True, "y": 180},
                "textures": wall_textures,
            },
            {
                "when": {"west": "tall"},
                "model_name_suffix": "side_tall",
                "reuse": True,
                "model_info": {"uvlock": True, "y": 270},
                "textures": wall_textures,
            },
            block_factory_consumer=lambda _, instance: instance.set_wall()
            .set_solid(False)
            .set_all_side_solid(False)
            == (
                0
                if "block_factory_consumer" not in consumers
                else consumers["block_factory_consumer"](_, instance)
            ),
            **{
                key: value
                for key, value in consumers.items()
                if key != "block_factory_consumer"
            },
        )
        return self

    def create_fence(self, suffix=None, texture=None, color=None, **consumers):
        if texture is None:
            texture = self.default_texture
        name = (
            (
                self.target_base_name
                if suffix is None
                else self.target_base_name + "_" + suffix
                if not callable(suffix)
                else suffix(self.target_base_name)
            )
            if not suffix or ":" not in suffix
            else suffix
        )
        texture = self.create_colored_texture(texture, color=color)
        fence_textures = {"texture": texture}
        # todo: can we use some form of template here?
        self.create_multipart_block(
            name,
            {
                "when": {},
                "model_name_suffix": "post",
                "textures": fence_textures,
                "parent": "minecraft:block/fence_post",
            },
            {
                "when": {"north": "true"},
                "model_name_suffix": "side",
                "model_info": {"uvlock": True},
                "textures": fence_textures,
                "parent": "minecraft:block/fence_side",
            },
            {
                "when": {"east": "low"},
                "model_name_suffix": "side",
                "reuse": True,
                "model_info": {"uvlock": True, "y": 90},
                "textures": fence_textures,
            },
            {
                "when": {"south": "true"},
                "model_name_suffix": "side",
                "reuse": True,
                "model_info": {"uvlock": True, "y": 180},
                "textures": fence_textures,
            },
            {
                "when": {"west": "true"},
                "model_name_suffix": "side",
                "reuse": True,
                "model_info": {"uvlock": True, "y": 270},
                "textures": fence_textures,
            },
            block_factory_consumer=lambda _, instance: instance.set_fence()
            == (
                0
                if "block_factory_consumer" not in consumers
                else consumers["block_factory_consumer"](_, instance)
            ),
            **{
                key: value
                for key, value in consumers.items()
                if key != "block_factory_consumer"
            },
        )
        return self

    def create_multipart_block(
        self,
        name: str,
        *parts,
        block_factory_consumer: typing.Callable[
            ["CombinedFactoryInstance", typing.Any], None
        ] = None,
        block_state_consumer: typing.Callable[
            ["CombinedFactoryInstance", dict], dict
        ] = None,
    ):
        mod_name = name.split(":")[0]
        if mod_name not in shared.mod_loader:
            mod_name = "minecraft"
        model_name = "{}:block/{}".format(*name.split(":"))

        @shared.mod_loader(mod_name, "stage:block:factory_usage")
        def block_instance():
            import mcpython.common.factory.BlockFactory

            instance = mcpython.common.factory.BlockFactory.BlockFactory().set_name(
                name
            )
            if callable(block_factory_consumer):
                block_factory_consumer(self, instance)

            if self.deferred_registry is None:
                instance.finish()
            else:
                self.deferred_registry.create_later(instance)

        if shared.IS_CLIENT:

            @shared.mod_loader(mod_name, "stage:model:model_search")
            def block_model():
                for part in parts:
                    self.inner_generate_model(part, model_name)

            @shared.mod_loader(mod_name, "stage:model:blockstate_search")
            def block_state():
                data = {
                    "multipart": [
                        {
                            "when": part["when"],
                            "apply": {
                                "model": model_name
                                + "_"
                                + part.setdefault("model_name_suffix", "default")
                            }
                            | part.setdefault("model_info", {}),
                        }
                        for part in parts
                    ]
                }
                if callable(block_state_consumer):
                    data = block_state_consumer(self, data)

                import mcpython.client.rendering.model.BlockState

                mcpython.client.rendering.model.BlockState.BlockStateContainer.from_data(
                    name, data
                )

            # todo: implement item models here

        return self

    def inner_generate_model(self, variant, model_name: str):
        if "reuse" in variant and variant["reuse"]:
            return

        data = {
            "parent": variant.setdefault("parent", "minecraft:block/block"),
            "textures": variant.setdefault("textures", {}),
        }
        if "model_consumer" in variant:
            data = variant["model_consumer"](self, data)

        shared.model_handler.add_from_data(
            model_name + "_" + variant.setdefault("model_name_suffix", "default"),
            data,
        )
