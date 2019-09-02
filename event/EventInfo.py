"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""


class IEventInfo:
    """
    base class for every event info
    """

    def equals(self, *args):
        raise NotImplementedError()


class KeyPressEventInfo(IEventInfo):
    """
    info for key press
    """

    def __init__(self, symbol: int, modifer=[]):
        self.symbol = symbol
        self.modifier = modifer

    def equals(self, symbol, modifiers):
        return symbol == self.symbol and all([modifiers & x for x in self.modifier])


class MousePressEventInfo(IEventInfo):
    """
    info for mouse press
    """

    def __init__(self, mouse: int, modifier=[], area=None):
        self.mouse = mouse
        self.modifier = modifier
        self.area = area

    def equals(self, x, y, button, modifiers):
        return button == self.mouse and all([modifiers & x for x in self.modifier]) and (
            (self.area[0][0] <= x <= self.area[1][0] and self.area[0][1] <= y <= self.area[1][1]) if self.area else True
        )


class CallbackHelper:
    def __init__(self, function, args=[], kwargs={}, extra_arg_filter=None, enable_extra_args=True):
        """
        creates an new object
        :param function: the function to call
        :param args: the args given
        :param kwargs: the kwargs given
        :param extra_arg_filter: an function(args, kwargs) -> args, kwargs which filters them
        :param enable_extra_args: weither args given by __call__ should be included
        """
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.filter = extra_arg_filter
        self.enable_extra_args = enable_extra_args

    def __call__(self, *args, **kwargs):
        if self.enable_extra_args:
            if self.filter:
                args, kwargs = self.filter(args, kwargs)
            return self.function(*list(args)+list(self.args), **{**kwargs, **self.kwargs})
        else:
            return self.function(*self.args, **self.kwargs)

