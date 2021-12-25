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
from mcpython import shared
from pyglet.window import mouse

from .AbstractToolItem import AbstractToolItem


class AbstractAxeItem(AbstractToolItem):
    # todo: make this data driven
    AXE_TRANSFORMS = {
        "minecraft:oak_log": "minecraft:stripped_oak_log",
        "minecraft:oak_wood": "minecraft:stripped_oak_wood",

        "minecraft:spruce_log": "minecraft:stripped_spruce_log",
        "minecraft:spruce_wood": "minecraft:stripped_spruce_wood",

        "minecraft:birch_log": "minecraft:stripped_birch_log",
        "minecraft:birch_wood": "minecraft:stripped_birch_wood",

        "minecraft:jungle_log": "minecraft:stripped_jungle_log",
        "minecraft:jungle_wood": "minecraft:stripped_jungle_wood",

        "minecraft:dark_oak_log": "minecraft:stripped_dark_oak_log",
        "minecraft:dark_oak_wood": "minecraft:stripped_dark_oak_wood",

        "minecraft:acacia_log": "minecraft:stripped_acacia_log",
        "minecraft:stripped_acacia_log": "minecraft:stripped_acacia_log",

        "minecraft:warped_stem": "minecraft:stripped_warped_stem",
        "minecraft:warped_hyphae": "minecraft:stripped_warped_hyphae",

        "minecraft:crimson_stem": "minecraft:stripped_crimson_stem",
        "minecraft:crimson_hyphae": "minecraft:stripped_crimson_hyphae",
    }

    async def on_player_interact(
        self, player, block, button: int, modifiers: int, itemstack, previous
    ) -> bool:
        if button != mouse.RIGHT:
            return False

        if block.NAME in self.AXE_TRANSFORMS:
            state = block.get_model_state()
            new = await shared.world.get_active_dimension().add_block(block.position, self.AXE_TRANSFORMS[block.NAME])
            new.set_model_state(state)

            if shared.IS_CLIENT:
                new.face_info.update()

            if player is None or player.gamemode in (0, 2):
                self.add_damage(1)

                if self.damage <= 0:
                    itemstack.add_amount(-1)
                    if not itemstack.is_empty():
                        itemstack.item.damage = self.DURABILITY

            return True

        return False

