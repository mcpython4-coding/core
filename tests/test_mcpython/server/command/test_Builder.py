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
from tests.util import TestCase


class TestCommandNode(TestCase):
    def test_module_import(self):
        import mcpython.server.command.Builder

    def test_than(self):
        from mcpython.server.command.Builder import CommandNode, DefinedString

        node = CommandNode(DefinedString(), execute_on_client=True)
        sub_node = CommandNode(DefinedString())

        node.than(sub_node)

        self.assertTrue(sub_node.execute_on_client)
        self.assertIn(sub_node, node.following_nodes)

    def test_on_execution(self):
        from mcpython.server.command.Builder import CommandNode, DefinedString

        def execute():
            pass

        node = CommandNode(DefinedString())
        node.on_execution(execute)

        self.assertIn(execute, node.on_execution_callbacks)

    def test_of_name(self):
        from mcpython.server.command.Builder import CommandNode, DefinedString

        node = CommandNode(DefinedString())
        node.of_name("test:name")

        self.assertEqual(node.name, "test:name")

    def test_info(self):
        from mcpython.server.command.Builder import CommandNode, DefinedString

        node = CommandNode(DefinedString())
        node.info("test:info")

        self.assertEqual(node.info_text, "test:info")

    def test_get_executing_node(self):
        pass  # todo: implement

    async def test_run(self):
        from mcpython.server.command.Builder import CommandNode, DefinedString

        ran = False

        def run(env, data):
            nonlocal ran
            ran = True

        node = CommandNode(DefinedString())
        node.on_execution(run)

        await node.run(None, [None])

        self.assertTrue(ran)
