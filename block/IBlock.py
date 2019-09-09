"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import enum
import block.Block
import gui.ItemStack


class InjectionMode(enum.Enum):
    """
    injection mode enum
    """

    PARALLEL = 0  # every other injection function that marks this is called if no upper is called
    IF_NO_OTHER = 1  # only if no other injection gives an function for this
    REPLACE_DOWNER = 2  # overwrites all other injections
    PARALLEL_THIS = 3  # like REPLACE_DOWNER & PARALLEL, but only both together by 1. parallel


class InjectAbleBlock(block.Block.Block):
    """
    base class for all blocks which are injectable
    """

    INJECTION_CLASSES = []  # a list of injection classes that should be injected
    injection_map = {}  # a map for functions that were injected

    @classmethod
    def is_injected(cls): return len(cls.INJECTION_CLASSES) > 0

    @classmethod
    def on_register(cls, registry):
        # init system
        cls.injection_map = {}  # function name -> [function]
        pmode = {}
        # walk through all injection classes and inject them
        for iblock in cls.INJECTION_CLASSES:
            if type(iblock) == str:
                # read the injection class from storage
                iblock = G.registry.get_by_name("block").get_attribute("injectionclasses")[iblock]
            ext: dict = iblock.get_functions_to_inject()
            # iterate over all InjectionModes provided by this
            for mode in ext.keys():
                for function in ext[mode]:
                    name, function = function.__name__, function if type(function) not in [list, set, tuple] else \
                        tuple(function)
                    if mode == InjectionMode.PARALLEL and name not in pmode:
                        if name not in cls.injection_map: cls.injection_map[name] = []
                        cls.injection_map[name].append(function)
                    elif mode == InjectionMode.IF_NO_OTHER and len(cls.INJECTION_CLASSES) == 1:
                        if name not in cls.injection_map: cls.injection_map[name] = []
                        cls.injection_map[name].append(function)
                    elif mode == InjectionMode.REPLACE_DOWNER:
                        cls.injection_map[name] = [function]
                    elif mode == InjectionMode.PARALLEL_THIS:
                        if name not in pmode:
                            pmode[name] = True
                            cls.injection_map[name] = []
                        cls.injection_map[name].append(function)

    def on_create(self):
        self.call_method("on_create")

    def call_method(self, name, *args, **kwargs) -> list:
        """
        calls an injected method tree
        :param name: the name of the function
        :param args: the arguments to give
        :param kwargs: the optional arguments to give
        :return: a list of results
        """
        if name not in self.injection_map: return []
        result = []
        for function in self.injection_map[name]:
            result.append(function(self, *args, **kwargs))
        return result

    def on_delete(self):
        self.call_method("on_delete")

    def is_brakeable(self) -> bool:
        result = self.call_method("is_brakeable")
        for element in result:
            if element is not None:
                return element

    def on_random_update(self):
        self.call_method("on_random_update")

    def on_block_update(self):
        self.call_method("on_block_update")

    def is_useable_by_item(self, item: gui.ItemStack) -> bool:
        result = self.call_method("is_useable_by_item", item)
        for element in result:
            if element is not None:
                return element

    def on_use_by_item(self, item: gui.ItemStack, triggered_by_block: bool):
        self.call_method("on_use_by_item", item, triggered_by_block)

    def get_brake_time(self, item: gui.ItemStack) -> int:
        result = self.call_method("get_brake_time", item)
        for element in result:
            if element is not None:
                return element

    def get_model_state(self) -> dict:
        m = {}
        result = self.call_method("get_model_state")
        for element in result:
            m = {**m, **element}
        return m


class IBlock:
    """
    base class for everything around base block classes.
    functions from Block can be simple injected here.
    please add all functions that should be callen here as an dict of {InjectionMode: [function or (name, function)]}
    """

    @classmethod
    def get_functions_to_inject(cls) -> dict:
        """
        :return: a InjectionMode -> functionlist map
        """
        return {InjectionMode.IF_NO_OTHER: [cls.get_functions_to_inject, cls.get_extension_name]}

    @staticmethod
    def get_extension_name() -> str:
        """
        :return: the name of the injection class
        """
        raise NotImplementedError()

