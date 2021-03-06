"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
import mcpython.common.item.AbstractDamageBarItem


class AbstractArmorItem(
    mcpython.common.item.AbstractDamageBarItem.DefaultDamageBarItem
):
    DURABILITY = 0

    def __init__(self):
        super().__init__()
        self.damage = self.DURABILITY

    DEFENSE_POINTS = 0

    def get_defense_points(self):
        return self.DEFENSE_POINTS

    STACK_SIZE = 1

    def get_damage(self) -> float:
        return self.damage / self.DURABILITY

    def get_data(self):
        return self.damage

    def set_data(self, data):
        try:
            self.damage = int(data)
        except ValueError:
            pass
