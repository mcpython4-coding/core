import unittest
from unittest.util import safe_repr

import typing

import asyncio


class TestCase(unittest.TestCase):
    def _callTestMethod(self, method):
        result = method()

        if isinstance(result, typing.Awaitable):
            asyncio.get_event_loop().run_until_complete(result)

    def _callSetUp(self):
        result = self.setUp()

        if isinstance(result, typing.Awaitable):
            asyncio.get_event_loop().run_until_complete(result)

    def _callTearDown(self):
        result = self.tearDown()

        if isinstance(result, typing.Awaitable):
            asyncio.get_event_loop().run_until_complete(result)

    async def assertRaisesAsync(self, exception, test_awaitable, msg: str = ""):
        try:
            await test_awaitable
        except Exception as e:
            if isinstance(e, exception):
                return
            msg = self._formatMessage(msg, "%s did not raise exception %s, but instead %s" % (safe_repr(test_awaitable), safe_repr(exception), safe_repr(e)))
            raise self.failureException(msg)

        msg = self._formatMessage(msg, "%s did not raise exception %s" % (
            safe_repr(test_awaitable), safe_repr(exception)))
        raise self.failureException(msg)

