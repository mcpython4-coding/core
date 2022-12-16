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
import asyncio
import typing
import unittest
from unittest.util import safe_repr

from mcpython import shared


class TestCase(unittest.TestCase):
    def _callTestMethod(self, method):
        shared.CURRENT_EVENT_SUB = method.__name__

        result = method()

        if isinstance(result, typing.Awaitable):
            asyncio.run(result)

    def _callSetUp(self):
        result = self.setUp()

        if isinstance(result, typing.Awaitable):
            asyncio.run(result)

    def _callTearDown(self):
        result = self.tearDown()

        if isinstance(result, typing.Awaitable):
            asyncio.run(result)

    async def assertRaisesAsync(self, exception, test_awaitable, msg: str = ""):
        try:
            await test_awaitable
        except Exception as e:
            if isinstance(e, exception):
                return
            msg = self._formatMessage(
                msg,
                "%s did not raise exception %s, but instead %s"
                % (safe_repr(test_awaitable), safe_repr(exception), safe_repr(e)),
            )
            raise self.failureException(msg)

        msg = self._formatMessage(
            msg,
            "%s did not raise exception %s"
            % (safe_repr(test_awaitable), safe_repr(exception)),
        )
        raise self.failureException(msg)
