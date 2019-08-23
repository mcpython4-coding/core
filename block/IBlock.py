"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import enum
import block.Block
import gui.ItemStack


class InjectionMode(enum.Enum):
    PARALLEL = 0
    IF_NO_OTHER = 1
    REPLACE_DOWNER = 2
    PARALLEL_THIS = 3


class InjectAbleBlock(block.Block.Block):
    INJECTION_CLASSES = []
    injection_map = {}

    @classmethod
    def is_injected(cls): return len(cls.INJECTION_CLASSES) > 0

    @classmethod
    def on_register(cls, registry):
        # init system
        cls.injection_map = {}  # function name -> [function]
        pmode = {}
        for iblock in cls.INJECTION_CLASSES:
            if type(iblock) == str:
                iblock = G.blockhandler.injectionclasses[iblock]
            ext: dict = iblock.get_functions_to_inject()
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
        if name not in self.injection_map: return []
        result = []
        for function in self.injection_map[name]:
            result.append(function(self, *args, **kwargs))

    def on_delete(self):
        self.call_method("on_delete")

    def get_model_name(self):
        result = self.call_method("get_model_name")
        for element in result:
            if element is not None:
                return element

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


class IBlock:
    """
    base class for everything around base block classes.
    functions from Block can be simple injected here.
    please add all functions that should be callen here as an dict of {InjectionMode: [function or (name, function)]}
    """

    @classmethod
    def get_functions_to_inject(cls) -> dict:
        return {InjectionMode.IF_NO_OTHER: [cls.get_functions_to_inject, cls.get_extension_name]}

    @staticmethod
    def get_extension_name() -> str:
        raise NotImplementedError()

