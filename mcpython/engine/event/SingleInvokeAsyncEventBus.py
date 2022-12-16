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
import sys
import traceback
import typing

import pyglet.app
from bytecodemanipulation.Optimiser import guarantee_builtin_names_are_protected

from bytecodemanipulation.Optimiser import cache_global_name

from mcpython import shared
from mcpython.engine import logger


class SingleInvokeAsyncEventBus:
    """
    Special async variant of the normal event bus

    Allows by design only one invocation
    """

    def __init__(
        self,
        crash_on_error: bool = True,
    ):
        self.id = shared.NEXT_EVENT_BUS_ID
        shared.NEXT_EVENT_BUS_ID += 1

        # name -> (function, args, kwargs)[
        self.event_subscriptions: typing.Dict[
            str,
            typing.List[
                typing.Tuple[
                    typing.Awaitable,
                    typing.Any,
                ]
            ],
        ] = {}
        self.popped_event_subscriptions = {}

        self.crash_on_error = crash_on_error
        self.close_on_error = True

        self.sub_buses = []

    @guarantee_builtin_names_are_protected()
    def subscribe(
        self,
        event_name: str,
        function: typing.Awaitable = None,
        info=None,
    ):
        """
        Adds a function to the event bus by event name. Dynamically creates underlying data structure for new
        event names

        :param event_name: the event to listen to on this bus
        :param function: the awaitable object to run
        :param info: an info to give for the caller
        """
        assert isinstance(
            function, typing.Awaitable
        ), f"This event bus only accepts coroutines, got {type(function)}"

        self.event_subscriptions.setdefault(event_name, []).append((function, info))
        return self

    @cache_global_name("asyncio", lambda: asyncio)
    @cache_global_name("traceback", lambda: traceback)
    @guarantee_builtin_names_are_protected()
    async def call(self, event_name: str):
        """
        Call an event on this event bus. Also works when deactivated
        :param event_name: the name of the event to call
        """
        from mcpython.common.mod.util import LoadingInterruptException

        if event_name not in self.event_subscriptions:
            return

        try:
            await asyncio.gather(*(e[0] for e in self.event_subscriptions[event_name]))

            # We can remove the data as coroutines can only be invoked ones
            del self.event_subscriptions[event_name]

        except (SystemExit, KeyboardInterrupt, LoadingInterruptException):
            raise

        except MemoryError:  # Memory error is something fatal
            shared.window.close()
            pyglet.app.exit()
            print("closing due to missing memory")
            sys.exit(-1)

        except:  # lgtm [py/catch-base-exception]
            logger.print_exception()
            logger.println("Out of the above reasons, the game is being closed")

            if self.close_on_error:
                shared.window.close()
                pyglet.app.exit()
                import mcpython.common.state.LoadingExceptionViewState
                from mcpython.common.mod.util import LoadingInterruptException

                mcpython.common.state.LoadingExceptionViewState.error_occur(
                    traceback.format_exc()
                )
                return

            raise RuntimeError
    def activate(self):
        shared.event_handler.activate_bus(self)

        for eventbus in self.sub_buses:
            eventbus.activate()

    def deactivate(self):
        shared.event_handler.deactivate_bus(self)

        for eventbus in self.sub_buses:
            eventbus.deactivate()

    @cache_global_name("SingleInvokeAsyncEventBus", lambda: SingleInvokeAsyncEventBus)
    def create_sub_bus(self, *args, activate=True, **kwargs):
        bus = SingleInvokeAsyncEventBus(*args, **kwargs)

        if activate:
            bus.activate()

        self.sub_buses.append(bus)
        return bus

    @cache_global_name("asyncio", lambda: asyncio)
    @cache_global_name("traceback", lambda: traceback)
    @guarantee_builtin_names_are_protected()
    async def call(self, event_name: str, amount=1):
        if event_name not in self.event_subscriptions:
            raise RuntimeError(
                "event bus has no notation for the '{}' event".format(event_name)
            )

        if len(self.event_subscriptions[event_name]) < amount:
            raise RuntimeError(
                "can't run event. EventBus has for the event '{}' not enough subscriber(s) (expected: {})".format(
                    event_name, amount
                )
            )

        try:
            await asyncio.gather(
                *(e[0] for e in self.event_subscriptions[event_name][:amount])
            )
        except TypeError:
            print(self.event_subscriptions[event_name][:amount])
            raise

        except (SystemExit, KeyboardInterrupt):
            raise
        except MemoryError:
            import mcpython.common.state.LoadingExceptionViewState
            from mcpython.common.mod.util import LoadingInterruptException

            mcpython.common.state.LoadingExceptionViewState.error_occur(
                traceback.format_exc()
            )
            return
        finally:
            self.popped_event_subscriptions.setdefault(event_name, []).extend(
                self.event_subscriptions[event_name][:amount]
            )
            del self.event_subscriptions[event_name][:amount]

    def reset_event_stack(self, event_name: str):
        """
        Will reset all event subscriptions which where popped from the normal list
        :param event_name: the name of the event to restore
        """
        self.event_subscriptions.setdefault(event_name, []).extend(
            self.popped_event_subscriptions.setdefault(event_name, [])
        )
        del self.popped_event_subscriptions[event_name]
