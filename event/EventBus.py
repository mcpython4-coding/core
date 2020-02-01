"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import traceback
import sys
import time


class EventBus:
    """
    An class for bundling event calls to instances of this to make it easy to add/remove big event notations.
    It should be something like an sub-eventhandler
    """

    def __init__(self, args=(), kwargs={}, crash_on_error=True):
        self.event_subscriptions = {}  # name -> (function, args, kwargs)[
        self.extra_arguments = (args, kwargs)
        self.crash_on_error = crash_on_error
        self.sub_buses = []
        self.id = G.NEXT_EVENT_BUS_ID
        G.NEXT_EVENT_BUS_ID += 1
        if G.debugevents:
            with open(G.local+"/debug/eventbus_{}.txt".format(self.id), mode="w") as f: f.write("//debug profile")

    def subscribe(self, eventname: str, function, *args, info=None, **kwargs):
        """
        add an function to the event bus by event name. If event name does NOT exists, it will be created localy
        :param eventname: the event to listen to on this bis
        :param function: the function that should be called when event is sended
        :param args: the args to give
        :param kwargs: the kwargs to give
        :param info: an info to give for the caller
        """
        self.event_subscriptions.setdefault(eventname, []).append((function, args, kwargs, info))
        if G.debugevents:
            with open(G.local+"/debug/eventbus_{}.txt".format(self.id), mode="a") as f:
                f.write("\nevent subscription of {} to {}".format(function, eventname))

    def unsubscribe(self, event_name: str, function):
        """
        remove an function from the event bus
        :param event_name: the event name the function was registered to
        :param function: the function itself
        :raise ValueError: when event name is unknown OR function was never assigned
        """
        if event_name not in self.event_subscriptions or function not in self.event_subscriptions[event_name]:
            if self.crash_on_error:
                raise ValueError("can't find function")
            return
        self.event_subscriptions[event_name].remove(function)
        if G.debugevents:
            with open(G.local+"/debug/eventbus_{}.txt".format(self.id), mode="a") as f:
                f.write("\nevent unsubscribe of {} to event {}".format(function, event_name))

    def call(self, event_name, *args, **kwargs):
        """
        call an event on this event bus. also works when deactivated
        :param event_name: the name of the event to call
        :param args: arguments to give
        :param kwargs: kwargs to give
        :return: an list of tuple of (return value, info)
        """
        result = []
        if event_name not in self.event_subscriptions: return result
        exception_occ = False
        for function, eargs, ekwargs, info in self.event_subscriptions[event_name]:
            dif = "Exception"
            try:
                start = time.time()
                result.append((function(*list(args)+list(self.extra_arguments[0])+list(eargs),
                               **{**kwargs, **self.extra_arguments[1], **ekwargs}), info))
                dif = time.time() - start
            except SystemExit: raise
            except:
                if not exception_occ:
                    print("EXCEPTION DURING CALLING EVENT '{}' OVER ".format(event_name))
                    traceback.print_stack()
                    exception_occ = True
                print("exception:")
                traceback.print_exc()
                print("during calling function: {} with arguments: {}".format(function, list(args)+list(
                    self.extra_arguments[0])+list(eargs), {**kwargs, **self.extra_arguments[1], **ekwargs}, sep="\n"))
                print("function info: '{}'".format(info))
            if G.debugevents:
                with open(G.local + "/debug/eventbus_{}.txt".format(self.id), mode="a") as f:
                    f.write("\nevent call of '{}' takes {}s until finish".format(function, dif))
        if exception_occ and self.crash_on_error:
            print("\nout of the above reasons, the game has crashes")
            sys.exit(-1)
        return result

    def call_until_equal(self, eventname, value, *args, default_value=None, **kwargs):
        value = self.call_until(eventname, lambda x: x == value, *args, **kwargs)
        return value if value is not None else default_value

    def call_until_getting_value(self, eventname, *args, default_value=None, **kwargs):
        value = self.call_until(eventname, lambda x: x is not None, *args, **kwargs)
        return value if value is not None else default_value

    def call_until_not_equal(self, eventname, value, *args, default_value=None, **kwargs):
        value = self.call_until(eventname, lambda x: x != value, *args, **kwargs)
        return value if value is not None else default_value

    def call_until(self, event_name, check_function, *args, **kwargs):
        if event_name not in self.event_subscriptions: return None
        for function, eargs, ekwargs in self.event_subscriptions[event_name]:
            start = time.time()
            result = function(*list(args) + list(self.extra_arguments[0]) + list(eargs),
                              **{**kwargs, **self.extra_arguments[1], **ekwargs})
            dif = time.time() - start
            if G.debugevents:
                with open(G.local + "/debug/eventbus_{}.txt".format(self.id), mode="a") as f:
                    f.write("\nevent call of {} takes {}s until finish".format(function, dif))
            if check_function(result):
                return result
        return None

    def activate(self):
        G.eventhandler.activate_bus(self)
        for eventbus in self.sub_buses:
            eventbus.activate()

    def deactivate(self):
        G.eventhandler.deactivate_bus(self)
        for eventbus in self.sub_buses:
            eventbus.deactivate()

    def create_sub_bus(self, *args, activate=True, **kwargs):
        bus = EventBus(*args, **kwargs)
        if activate: bus.activate()
        self.sub_buses.append(bus)
        return bus

    def call_as_stack(self, eventname, *args, amount=1, **kwargs):
        result = []
        if eventname not in self.event_subscriptions:
            raise RuntimeError("event bus has no notation for this event")
        if len(self.event_subscriptions[eventname]) < amount:
            raise RuntimeError("can't run event. EventBus is for this event empty")
        exception_occ = False
        for _ in range(amount):
            function, eargs, ekwargs, info = self.event_subscriptions[eventname].pop(0)
            start = time.time()
            try:
                result.append((function(*list(args) + list(self.extra_arguments[0]) + list(eargs),
                                        **{**kwargs, **self.extra_arguments[1], **ekwargs}), info))
            except:
                if not exception_occ:
                    print("EXCEPTION DURING CALLING EVENT {} OVER ".format(eventname))
                    traceback.print_stack()
                    exception_occ = True
                print("exception:")
                traceback.print_exc()
                print("during calling function:", function, "with arguments:", list(args) + list(
                    self.extra_arguments[0]) + list(eargs), {**kwargs, **self.extra_arguments[1], **ekwargs}, sep="\n")
                print("function info:", info)
            dif = time.time() - start
            if G.debugevents:
                with open(G.local + "/debug/eventbus_{}.txt".format(self.id), mode="a") as f:
                    f.write("\nevent call of {} takes {}s until finish".format(function, dif))
        if exception_occ and self.crash_on_error:
            print("\nout of the above reasons, the game has crashes")
            sys.exit(-1)
        return result

