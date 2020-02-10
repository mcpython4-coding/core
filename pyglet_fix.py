import pyglet.event


class FixedEventDispatcher(pyglet.event.EventDispatcher):
    def _remove_handler(self, name, handler):
        """Used internally to remove all handler instances for the given event name.

        This is normally called from a dead ``WeakMethod`` to remove itself from the
        event stack.

        Fix for python 3.8
        """
        # Iterate over a copy as we might mutate the list
        for frame in list(self._event_stack):
            try:
                flag = frame[name] == handler
            except TypeError:
                flag = False
            if name in frame and flag:
                del frame[name]
                if not frame:
                    self._event_stack.remove(frame)


pyglet.event.EventDispatcher = FixedEventDispatcher

