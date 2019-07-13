import enum


class EventReSubscriber:
    def __init__(self, handler=None):
        self.handler = handler
        self.eventname = None
        self.function = None

    def __call__(self, function):
        self.set_function(function)

    def set_function(self, function):
        self.function = function
        self.handler.revert_resubscriber(self, insert=True)


class EventHandler:
    def __init__(self):
        self.event_names = []  # str[]
        self.event_registrations = {}  # str: event -> function[]
        self.eventresubscriber = [EventReSubscriber(self) for _ in range(10)]

    def __call__(self, eventname):
        if len(self.eventresubscriber) == 0:
            self.eventresubscriber.append(EventReSubscriber(self))
        eventresubscriber = self.eventresubscriber.pop(0)
        eventresubscriber.eventname = eventname
        return eventresubscriber

    def revert_resubscriber(self, sub: EventReSubscriber, insert=False):
        if insert and sub.function:
            if sub.eventname not in self.event_names:
                raise ValueError("can't subscribe to event named "+str(sub.eventname))
            self.event_registrations[sub.eventname].append(sub.function)
        self.eventresubscriber.append(sub)
        sub.eventname = None
        sub.function = None

    def add_event_name(self, eventname):
        if eventname in self.event_names: return
        self.event_names.append(eventname)
        self.event_registrations[eventname] = []

    def call(self, eventname, *args, **kwargs):
        if eventname not in self.event_names:
            raise ValueError("can't call event "+str(eventname)+" because its unknown")
        for function in self.event_registrations[eventname]:
            function(*args, **kwargs)


handler = EventHandler()

