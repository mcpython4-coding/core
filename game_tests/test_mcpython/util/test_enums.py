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
from game_tests.util import TestCase


class TestEnumSide(TestCase):
    def test_module_import(self):
        import mcpython.util.enums

    def test_rotate(self):
        from mcpython.util.enums import EnumSide

        self.assertEqual(EnumSide.NORTH.rotate((0, 0, 0)), EnumSide.NORTH)
        self.assertEqual(EnumSide.UP.rotate((0, 90, 0)), EnumSide.UP)
        self.assertEqual(EnumSide.NORTH.rotate((0, 90, 0)), EnumSide.EAST)
        self.assertEqual(EnumSide.NORTH.rotate((0, 180, 0)), EnumSide.SOUTH)

    def test_rotate_reverse(self):
        from mcpython.util.enums import EnumSide

        for face in EnumSide.iterate()[2:]:
            self.assertEqual(face.rotate((0, 90, 0)).rotate_reverse((0, 90, 0)), face)
            self.assertEqual(face.invert().invert(), face)

    def test_side_list_to_bit_map(self):
        from mcpython.util.enums import EnumSide

        faces = [EnumSide.NORTH, EnumSide.EAST, EnumSide.UP]
        self.assertEqual(
            EnumSide.side_list_to_bit_map(faces),
            EnumSide.UP.bitflag | EnumSide.EAST.bitflag | EnumSide.NORTH.bitflag,
        )

    def test_bitmap_to_side_list(self):
        from mcpython.util.enums import EnumSide

        faces = EnumSide.bitmap_to_side_list(
            EnumSide.UP.bitflag | EnumSide.EAST.bitflag | EnumSide.NORTH.bitflag
        )
        self.assertEqual(set(faces), {EnumSide.NORTH, EnumSide.EAST, EnumSide.UP})

    def test_rotate_bitmap(self):
        from mcpython.util.enums import EnumSide

        faces = 0b110011
        self.assertEqual(
            faces,
            EnumSide.rotate_bitmap(
                EnumSide.rotate_bitmap(faces, (0, -90, 0)), (0, 90, 0)
            ),
        )
