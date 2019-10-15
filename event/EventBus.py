"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import traceback
import sys


class EventBus:
    """
    An class for bundling event calls to instances of this to make it easy to add/remove big event notations.
    It should be something like an sub-eventhandler
    """

    def __init__(self, args=(), kwargs={}, crash_on_error=True):
        self.eventsubscribtions = {}  # name -> (function, args, kwargs)[
        self.extra_arguments = (args, kwargs)
        self.crash_on_error = crash_on_error

    def subscribe(self, eventname: str, function, *args, **kwargs):
        """
        add an function to the event bus by event name. If event name does NOT exists, it will be created localy
        :param eventname: the event to listen to on this bis
        :param function: the function that should be callen when event is sended
        :param args: the args to give
        :param kwargs: the kwargs to give
        """
        self.eventsubscribtions.setdefault(eventname, []).append((function, args, kwargs))

    def desubscribe(self, eventname: str, function):
        """
        remove an function from the event bus
        :param eventname: the eventname the function was registrated to
        :param function: the function itself
        :raise ValueError: when event name is unknown OR function was never assigned
        """
        if eventname not in self.eventsubscribtions or function not in self.eventsubscribtions[eventname]:
            if self.crash_on_error:
                raise ValueError("can't find function")
            return
        self.eventsubscribtions[eventname].remove(function)

    def call(self, eventname, *args, **kwargs):
        """
        call an event on this eventbus. also works when deactivated
        :param eventname: the name of the event to call
        :param args: arguments to give
        :param kwargs: kwargs to give
        :return: an list of return values
        """
        result = []
        if eventname not in self.eventsubscribtions: return result
        exception_occ = False
        for function, eargs, ekwargs in self.eventsubscribtions[eventname]:
            try:
                result.append(function(*list(args)+list(self.extra_arguments[0])+list(eargs),
                              **{**kwargs, **self.extra_arguments[1], **ekwargs}))
            except:
                if not exception_occ:
                    print("EXCEPTION DURING CALLING EVENT {} OVER ".format(eventname))
                    traceback.print_stack()
                    exception_occ = True
                print("exception:")
                traceback.print_exc()
                print("during calling function:", function, "with arguments:", list(args)+list(
                    self.extra_arguments[0])+list(eargs), {**kwargs, **self.extra_arguments[1], **ekwargs}, sep="\n")
        if exception_occ and self.crash_on_error:
            print("\nout of the above reasons, the game has crashes")
            sys.exit(-1)
        return result

    def call_until_equal(self, eventname, value, *args, default_value=None, **kwargs):
        if eventname not in self.eventsubscribtions: return default_value
        for function, eargs, ekwargs in self.eventsubscribtions[eventname]:
            result = function(*list(args) + list(self.extra_arguments[0]) + list(eargs),
                              **{**kwargs, **self.extra_arguments[1], **ekwargs})
            if result == value:
                return result
        return default_value

    def call_until_getting_value(self, eventname, *args, default_value=None, **kwargs):
        if eventname not in self.eventsubscribtions: return default_value
        for function, eargs, ekwargs in self.eventsubscribtions[eventname]:
            result = function(*list(args) + list(self.extra_arguments[0]) + list(eargs),
                              **{**kwargs, **self.extra_arguments[1], **ekwargs})
            if result is not None:
                return result
        return default_value

    def call_until_not_equal(self, eventname, value, *args, default_value=None, **kwargs):
        if eventname not in self.eventsubscribtions: return default_value
        for function, eargs, ekwargs in self.eventsubscribtions[eventname]:
            result = function(*list(args) + list(self.extra_arguments[0]) + list(eargs),
                              **{**kwargs, **self.extra_arguments[1], **ekwargs})
            if result != value:
                return result
        return default_value

    def activate(self): G.eventhandler.activate_bus(self)

    def deactivate(self): G.eventhandler.deactivate_bus(self)

