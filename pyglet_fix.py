"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
# LICENSE see licenses/LICENSE_pyglet
import pyglet.event


class FixedEventDispatcher(pyglet.event.EventDispatcher):
    """
    class for an fix for the _remove_handler function of pyglet in python 3.8
    """

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
                flag = False  # todo: check if this is the right state in this case!
            if name in frame and flag:
                del frame[name]
                if not frame:
                    self._event_stack.remove(frame)


pyglet.event.EventDispatcher = FixedEventDispatcher

