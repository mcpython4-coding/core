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
import sys
import traceback
import typing

import pyglet.app
from mcpython import shared
from mcpython.engine import logger


class CancelAbleEvent:
    """
    Tracker class for a cancelable event
    """

    def __init__(self):
        self.canceled = False

    def cancel(self):
        self.canceled = True


class EventBus:
    """
    An class for bundling event calls to instances of this to make it easy to add/remove big event notations.
    It should be something like an sub-event-handler

    todo: make thread-safe
    """

    def __init__(
        self,
        crash_on_error: bool = True,
    ):
        """
        Creates a new EventBus instance
        :param crash_on_error: if an crash should be triggered on an exception of an func
        """
        self.id = shared.NEXT_EVENT_BUS_ID
        shared.NEXT_EVENT_BUS_ID += 1

        # name -> (function, args, kwargs)[
        self.event_subscriptions: typing.Dict[
            str,
            typing.List[
                typing.Tuple[typing.Callable, typing.Iterable, typing.Dict, typing.Any]
            ],
        ] = {}
        self.popped_event_subscriptions = {}

        self.crash_on_error = crash_on_error
        self.close_on_error = True

        self.sub_buses = []

    def subscribe(
        self, event_name: str, function: typing.Callable, *args, info=None, **kwargs
    ):
        """
        Adds a function to the event bus by event name. Dynamically creates underlying data structure for new
        event names

        :param event_name: the event to listen to on this bis
        :param function: the function that should be called when event is send
        :param args: the args to give
        :param kwargs: the kwargs to give
        :param info: an info to give for the caller
        """
        self.event_subscriptions.setdefault(event_name, []).append(
            (function, args, kwargs, info)
        )

    def unsubscribe(self, event_name: str, function: typing.Callable):
        """
        Remove a function from the event bus from a given event
        :param event_name: the event name the function was registered to
        :param function: the function itself
        :raise ValueError: when event name is unknown OR function was never assigned
        """
        if event_name not in self.event_subscriptions:
            raise ValueError(f"cannot find function {function} in event {event_name}")

        any_found = False
        for signature in self.event_subscriptions[event_name][:]:
            if signature[0] == function:
                self.event_subscriptions[event_name].remove(signature)
                any_found = True

        if not any_found:
            raise ValueError(f"cannot find function {function} in event {event_name}")

    def call(self, event_name: str, *args, **kwargs):
        """
        Call an event on this event bus. Also works when deactivated
        :param event_name: the name of the event to call
        :param args: arguments to give
        :param kwargs: kwargs to give
        """
        from mcpython.common.mod.util import LoadingInterruptException

        if event_name not in self.event_subscriptions:
            return

        exception_occ = False
        for function, extra_args, extra_kwargs, info in self.event_subscriptions[
            event_name
        ]:
            try:
                function(
                    *list(args) + list(extra_args),
                    **{**kwargs, **extra_kwargs},
                )

            except SystemExit:
                raise

            except LoadingInterruptException:
                raise

            except MemoryError:  # Memory error is something fatal
                shared.window.close()
                pyglet.app.exit()
                print("closing due to missing memory")
                sys.exit(-1)

            except:
                exception_occ = True
                logger.print_exception(
                    "during calling function: {} with arguments: {}, {}".format(
                        function,
                        list(args) + list(extra_args),
                        {**kwargs, **extra_kwargs},
                        sep="\n",
                    ),
                    "function info: '{}'".format(info) if info is not None else "",
                    "during event:",
                    event_name,
                )

        if exception_occ and self.crash_on_error:
            logger.println("\nout of the above reasons, the game is being closed")

            if self.close_on_error:
                shared.window.close()
                pyglet.app.exit()
                import mcpython.common.state.LoadingExceptionViewState
                from mcpython.common.mod.util import LoadingInterruptException

                mcpython.common.state.LoadingExceptionViewState.error_occur(
                    traceback.format_exc()
                )
                return

            else:
                raise RuntimeError

    def call_cancelable(self, event_name: str, *args, **kwargs):
        """
        Will call a cancel able event.
        Works the same way as call, but will use call_until() with an CancelAbleEvent as first parameter which is checked after each call
        :param event_name: the name to call
        :param args: args to call with
        :param kwargs:  kwargs to call with
        :return: if it was canceled or not
        """
        handler = CancelAbleEvent()
        self.call_until(
            event_name, lambda _: handler.canceled, *((handler,) + args), **kwargs
        )
        return handler

    def call_until(
        self,
        event_name: str,
        check_function: typing.Callable[[typing.Any], bool],
        *args,
        **kwargs,
    ):
        """
        Will call the event stack until an check_function returns True or all subscriptions where done
        :param event_name: the name of the event
        :param check_function: the check function to call with
        :param args: the args to call with
        :param kwargs: the kwargs to call with
        :return: the result in the moment of True or None
        """
        if event_name not in self.event_subscriptions:
            return

        for function, extra_args, extra_kwargs, info in self.event_subscriptions[
            event_name
        ]:
            try:
                result = function(
                    *list(args) + list(extra_args),
                    **{**kwargs, **extra_kwargs},
                )

                if check_function(result):
                    return result

            except MemoryError:
                shared.window.close()
                pyglet.app.exit()
                print("closing due to missing memory")
                sys.exit(-1)
            except SystemExit:
                raise
            except:
                logger.print_exception(
                    "during calling function: {} with arguments: {}, {}".format(
                        function,
                        list(args) + list(extra_args),
                        {**kwargs, **extra_kwargs},
                        sep="\n",
                    ),
                    "function info: '{}'".format(info) if info is not None else "",
                    "during event:",
                    event_name,
                )
                raise

    def activate(self):
        shared.event_handler.activate_bus(self)

        for eventbus in self.sub_buses:
            eventbus.activate()

    def deactivate(self):
        shared.event_handler.deactivate_bus(self)

        for eventbus in self.sub_buses:
            eventbus.deactivate()

    def create_sub_bus(self, *args, activate=True, **kwargs):
        bus = EventBus(*args, **kwargs)

        if activate:
            bus.activate()

        self.sub_buses.append(bus)
        return bus

    def call_as_stack(
        self, event_name: str, *args, amount=1, store_stuff=True, **kwargs
    ):
        result = []
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

        for _ in range(amount):
            function, extra_args, extra_kwargs, info = d = self.event_subscriptions[
                event_name
            ].pop(0)

            if store_stuff:
                self.popped_event_subscriptions.setdefault(event_name, []).append(d)

            try:
                result.append(
                    (
                        function(
                            *list(args) + list(extra_args),
                            **{**kwargs, **extra_kwargs},
                        ),
                        info,
                    )
                )
            except SystemExit:
                raise
            except MemoryError:
                import mcpython.common.state.LoadingExceptionViewState
                from mcpython.common.mod.util import LoadingInterruptException

                mcpython.common.state.LoadingExceptionViewState.error_occur(
                    traceback.format_exc()
                )
                return
            except:
                raise

        return result

    def reset_event_stack(self, event_name: str):
        """
        Will reset all event subscriptions which where popped from the normal list
        :param event_name: the name of the event to restore
        """
        self.event_subscriptions.setdefault(event_name, []).extend(
            self.popped_event_subscriptions.setdefault(event_name, [])
        )
        del self.popped_event_subscriptions[event_name]
