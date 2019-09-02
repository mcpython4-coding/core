"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import traceback


class EventReSubscriber:
    """
    entry to make it possible to notate @G.eventhandler(eventname)
    """

    def __init__(self, eventhandler):
        """
        creates the eventresubscriber
        :param eventhandler: the eventhandler to re-call to
        """
        self.handler = eventhandler
        self.eventname = None
        self.function = None
        self.call_active = None

    def __call__(self, function):
        self.set_function(function)
        return function

    def set_function(self, function):
        self.function = function
        self.handler.revert_resubscriber(self, insert=True)
        return function


class EventHandler:
    """
    main class for event handling
    """

    def __init__(self):
        self.event_names = []  # str[]
        self.event_registrations = {}  # str: event -> function[]
        self.eventresubscriber = [EventReSubscriber(self) for _ in range(10)]

    def __call__(self, eventname, callactive=True):
        """
        register an callback for these
        :param eventname: the eventname
        :param callactive: if we should register it after assinging or not
        :return: an eventresubscriber object
        """
        if len(self.eventresubscriber) == 0:
            self.eventresubscriber.append(EventReSubscriber(self))
        eventresubscriber = self.eventresubscriber.pop(0)
        eventresubscriber.eventname = eventname
        eventresubscriber.call_active = callactive
        return eventresubscriber

    def revert_resubscriber(self, sub: EventReSubscriber, insert=False):
        if insert and sub.function:
            if sub.eventname not in self.event_names:
                raise ValueError("can't subscribe to event named "+str(sub.eventname))
            if sub.call_active:
                self.event_registrations[sub.eventname].append(sub.function)
        self.eventresubscriber.append(sub)
        sub.eventname = None
        sub.function = None
        sub.call_active = None

    def deactivate_from_callback(self, eventname, function):
        if function in self.event_registrations[eventname]:
            self.event_registrations[eventname].remove(function)

    def activate_to_callback(self, eventname, function):
        self.event_registrations[eventname].append(function)

    def add_event_name(self, eventname):
        if eventname in self.event_names: return
        self.event_names.append(eventname)
        self.event_registrations[eventname] = []

    def call(self, eventname, *args, **kwargs):
        if eventname not in self.event_names:
            raise ValueError("can't call event "+str(eventname)+" because its unknown")
        flag_exc = False
        for function in self.event_registrations[eventname]:
            try:
                function(*args, **kwargs)
            except:
                if not flag_exc:
                    print("exceptions during calling event named "+str(eventname)+":\ncallen over:")
                    traceback.print_stack()
                    print("exceptions:")
                    flag_exc = True
                else:
                    print()
                traceback.print_exc()


handler = G.eventhandler = EventHandler()

# register event names

handler.add_event_name("game:startup")
handler.add_event_name("game:load_finished")
handler.add_event_name("game:gameloop_startup")

handler.add_event_name("gameloop:tick:start")
handler.add_event_name("gameloop:tick:end")

handler.add_event_name("user:mouse:press")
handler.add_event_name("user:mouse:release")
handler.add_event_name("user:mouse:motion")
handler.add_event_name("user:mouse:drag")
handler.add_event_name("user:mouse:scroll")

handler.add_event_name("user:keyboard:press")
handler.add_event_name("user:keyboard:release")
handler.add_event_name("user:keyboard:enter")

handler.add_event_name("user:window:resize")

handler.add_event_name("render:draw:3d")
handler.add_event_name("render:draw:2d:background")
handler.add_event_name("render:draw:2d")
handler.add_event_name("render:draw:2d:overlay")

