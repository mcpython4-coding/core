"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
import sys
import time
import typing

from mcpython import shared, logger


class CancelAbleEvent:
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
        args: typing.Iterable = (),
        kwargs: dict = None,
        crash_on_error: bool = True,
    ):
        """
        Creates an new EventBus instance
        :param args: the args to send to every function call
        :param kwargs: the kwargs to send to every function call
        :param crash_on_error: if an crash should be triggered on an exception of an func
        """
        if kwargs is None:
            kwargs = {}
        self.event_subscriptions = {}  # name -> (function, args, kwargs)[
        self.popped_event_subscriptions = {}
        self.extra_arguments = (args, kwargs)
        self.crash_on_error = crash_on_error
        self.sub_buses = []
        self.id = shared.NEXT_EVENT_BUS_ID
        shared.NEXT_EVENT_BUS_ID += 1
        if shared.debug_events:
            with open(
                shared.local + "/debug/eventbus_{}.txt".format(self.id), mode="w"
            ) as f:
                f.write("//debug profile")

    def subscribe(
        self, event_name: str, function: typing.Callable, *args, info=None, **kwargs
    ):
        """
        add an function to the event bus by event name. If event name does NOT exists, it will be created locally
        :param event_name: the event to listen to on this bis
        :param function: the function that should be called when event is send
        :param args: the args to give
        :param kwargs: the kwargs to give
        :param info: an info to give for the caller
        """
        if (function, args, kwargs, info) in self.event_subscriptions.setdefault(
            event_name, []
        ):
            return
        self.event_subscriptions[event_name].append((function, args, kwargs, info))
        if shared.debug_events:
            with open(
                shared.local + "/debug/eventbus_{}.txt".format(self.id), mode="a"
            ) as f:
                f.write(
                    "\nevent subscription of '{}' to '{}'".format(function, event_name)
                )

    def unsubscribe(self, event_name: str, function):
        """
        remove an function from the event bus
        :param event_name: the event name the function was registered to
        :param function: the function itself
        :raise ValueError: when event name is unknown OR function was never assigned
        """
        if (
            event_name not in self.event_subscriptions
            or function not in self.event_subscriptions[event_name]
        ):
            if self.crash_on_error:
                raise ValueError(
                    "can't find function {} in event '{}'".format(function, event_name)
                )
            return
        self.event_subscriptions[event_name].remove(function)
        if shared.debug_events:
            with open(
                shared.local + "/debug/eventbus_{}.txt".format(self.id), mode="a"
            ) as f:
                f.write(
                    "\nevent unsubscribe of '{}' to event '{}'".format(
                        function, event_name
                    )
                )

    def call(self, event_name: str, *args, **kwargs):
        """
        call an event on this event bus. also works when deactivated
        :param event_name: the name of the event to call
        :param args: arguments to give
        :param kwargs: kwargs to give
        :return: an list of tuple of (return value, info)
        """
        result = []
        if event_name not in self.event_subscriptions:
            return result
        exception_occ = False
        for function, eargs, ekwargs, info in self.event_subscriptions[event_name]:
            dif = "Exception"
            try:
                start = time.time()
                result.append(
                    (
                        function(
                            *list(args) + list(self.extra_arguments[0]) + list(eargs),
                            **{**kwargs, **self.extra_arguments[1], **ekwargs}
                        ),
                        info,
                    )
                )
                dif = time.time() - start
            except SystemExit:
                raise
            except MemoryError:
                sys.exit(-1)
            except:
                exception_occ = True
                logger.print_exception(
                    "during calling function: {} with arguments: {}, {}".format(
                        function,
                        list(args) + list(self.extra_arguments[0]) + list(eargs),
                        {**kwargs, **self.extra_arguments[1], **ekwargs},
                        sep="\n",
                    ),
                    "function info: '{}'".format(info) if info is not None else "",
                    "during event:",
                    event_name,
                )
            if shared.debug_events:
                with open(
                    shared.local + "/debug/eventbus_{}.txt".format(self.id), mode="a"
                ) as f:
                    f.write(
                        "\nevent call of '{}' takes {}s until finish".format(
                            function, dif
                        )
                    )
        if exception_occ and self.crash_on_error:
            logger.println("\nout of the above reasons, the game has crashed")
            sys.exit(-1)
        return result

    def call_cancelable(self, event_name: str, *args, **kwargs):
        """
        Will call an cancel able event.
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
        **kwargs
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
            return None
        for function, eargs, ekwargs, info in self.event_subscriptions[event_name]:
            start = time.time()
            try:
                result = function(
                    *list(args) + list(self.extra_arguments[0]) + list(eargs),
                    **{**kwargs, **self.extra_arguments[1], **ekwargs}
                )
                dif = time.time() - start
                if shared.debug_events:
                    with open(
                        shared.local + "/debug/eventbus_{}.txt".format(self.id),
                        mode="a",
                    ) as f:
                        f.write(
                            "\nevent call of {} takes {}s until finish".format(
                                function, dif
                            )
                        )
                if check_function(result):
                    return result
            except MemoryError:
                sys.exit(-1)
            except SystemExit:
                raise
            except:
                logger.print_exception(
                    "during calling function: {} with arguments: {}, {}".format(
                        function,
                        list(args) + list(self.extra_arguments[0]) + list(eargs),
                        {**kwargs, **self.extra_arguments[1], **ekwargs},
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

    def call_as_stack(self, event_name, *args, amount=1, **kwargs):
        result = []
        if event_name not in self.event_subscriptions:
            raise RuntimeError(
                "event bus has no notation for the '{}' event".format(event_name)
            )
        if len(self.event_subscriptions[event_name]) < amount:
            raise RuntimeError(
                "can't run event. EventBus is for the event '{}' empty".format(
                    event_name
                )
            )
        exception_occ = False
        for _ in range(amount):
            function, eargs, ekwargs, info = d = self.event_subscriptions[
                event_name
            ].pop(0)
            self.popped_event_subscriptions.setdefault(event_name, []).append(d)
            start = time.time()
            try:
                result.append(
                    (
                        function(
                            *list(args) + list(self.extra_arguments[0]) + list(eargs),
                            **{**kwargs, **self.extra_arguments[1], **ekwargs}
                        ),
                        info,
                    )
                )
            except SystemExit:
                raise
            except MemoryError:
                sys.exit(-1)
            except:
                exception_occ = True
                logger.print_exception(
                    "during calling function:",
                    function,
                    "with arguments:",
                    list(args) + list(self.extra_arguments[0]) + list(eargs),
                    {**kwargs, **self.extra_arguments[1], **ekwargs},
                    "function info:",
                    info,
                    "during event:",
                    event_name,
                )
            dif = time.time() - start
            if shared.debug_events:
                with open(
                    shared.local + "/debug/eventbus_{}.txt".format(self.id), mode="a"
                ) as f:
                    f.write(
                        "\nevent call of {} takes {}s until finish".format(
                            function, dif
                        )
                    )
        if exception_occ and self.crash_on_error:
            logger.println("\nout of the above reasons, the game has crashes")
            sys.exit(-1)
        return result

    def resetEventStack(self, event_name: str):
        """
        Will reset all event subscriptions which where popped from the normal list
        :param event_name: the name of the event to restore
        """
        self.event_subscriptions.setdefault(event_name, []).extend(
            self.popped_event_subscriptions.setdefault(event_name, [])
        )
        del self.popped_event_subscriptions[event_name]
