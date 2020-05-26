"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import typing

import ResourceLocator
import event.EventHandler
import event.Registry
import globals as G
import logger
import state.State
import state.StatePart


class IStateConfigEntry(event.Registry.IRegistryContent):
    """
    base class for every entry in an config file
    """

    TYPE = "minecraft:state_definition_entry"

    # NAME is the type-name

    @classmethod
    def deserialize(cls, state_instance, data: dict, existing: typing.Union[None, state.StatePart.StatePart]) -> \
            state.StatePart.StatePart:
        raise NotImplementedError()


entry_registry = event.Registry.Registry("state_definition_entries", ["minecraft:state_definition_entry"])


@G.registry
class UIButtonDefaultStateConfigEntry(IStateConfigEntry):
    NAME = "minecraft:ui_button_default"

    @classmethod
    def deserialize(cls, state_instance, data: dict,
                    existing: typing.Union[None, state.StatePart.StatePart]) -> state.StatePart.StatePart:
        import state.ui.UIPartButton

        size = tuple(data["size"])
        text = data["text"] if "text" in data else ""
        position = tuple(data["position"])
        anchor_window = data["anchor_win"] if "anchor_win" in data else "WS"
        anchor_button = data["anchor_but"] if "anchor_but" in data else "WS"
        enabled = data["enabled"] if "enabled" in data else True
        has_hov = data["has_hovering_state"] if "has_hovering_state" in data else True

        on_press = getattr(state_instance, data["on_press"]) if "on_press" in data else None

        if existing is not None and issubclass(type(existing), state.ui.UIPartButton.UIPartButton):
            on_press = getattr(state_instance, data["on_press"]) if "on_press" in data else None
            existing.bboxsize = size
            existing.text = text
            existing.position = position
            existing.anchor_element = anchor_button
            existing.anchor_window = anchor_window
            existing.enabled = enabled
            existing.has_hovering_state = has_hov
            existing.on_press = on_press
            return existing
        return state.ui.UIPartButton.UIPartButton(size, text, position, anchor_button=anchor_button,
                                                  anchor_window=anchor_window, enabled=enabled,
                                                  has_hovering_state=has_hov, on_press=on_press)


@G.registry
class UILableStateConfigEntry(IStateConfigEntry):
    NAME = "minecraft:ui_lable_default"

    @classmethod
    def deserialize(cls, state_instance, data: dict, existing: typing.Union[
            None, state.StatePart.StatePart]) -> state.StatePart.StatePart:
        import state.ui.UIPartLable
        text = data["text"]
        position = tuple(data["position"])
        anchor_window = data["anchor_win"] if "anchor_win" in data else "WS"
        anchor_lable = data["anchor_lab"] if "anchor_lab" in data else "WS"
        on_press = getattr(state_instance, data["on_press"]) if "on_press" in data else None
        color = tuple(data["color"]) if "color" in data else (0, 0, 0, 0)
        text_size = data["text_size"] if "text_size" in data else 20

        if existing is not None and issubclass(type(existing), state.ui.UIPartLable.UIPartLable):
            existing.text = text
            existing.position = position
            existing.anchor_window = anchor_window
            existing.anchor_element = anchor_lable
            existing.on_press = on_press
            existing.color = color
            existing.text_size = text_size
            return existing
        return state.ui.UIPartLable.UIPartLable(text, position, anchor_lable=anchor_lable, anchor_window=anchor_window,
                                                on_press=on_press, color=color, text_size=text_size)


@G.registry
class ConfigBackground(IStateConfigEntry):
    NAME = "minecraft:config_background"

    @classmethod
    def deserialize(cls, state_instance, data: dict, existing: typing.Union[None, state.StatePart.StatePart]) -> \
            state.StatePart.StatePart:
        import state.StatePartConfigBackground
        if existing is not None and issubclass(type(existing),
                                               state.StatePartConfigBackground.StatePartConfigBackground):
            return existing
        return state.StatePartConfigBackground.StatePartConfigBackground()


configs = {}


def get_config(file: str):
    if file not in configs:
        configs[file] = StateConfigFile(file)
    return configs[file]


class StateConfigFile:
    """
    Class for deserialize an config file for an state into an state
    """

    def __init__(self, file: str):
        """
        Constructs an new deserializer for an file
        """
        self.file = file
        self.data = ResourceLocator.read(file, "json")
        self.injected_objects = set()
        event.EventHandler.PUBLIC_EVENT_BUS.subscribe("command:reload:end", self.reload)

    def inject(self, state_instance: typing.Union[state.State.State, state.StatePart.StatePart]):
        """
        will make the given state an state of the kind specified by this file
        :param state_instance: the state to inject the data into
        WARNING: will override ALL existing data from state parts and their config
        """
        self.injected_objects.add(state_instance)
        if "mouse_interactive" in self.data:
            state_instance.IS_MOUSE_EXCLUSIVE = self.data["mouse_interactive"]
        if "parts" in self.data:
            for name in self.data["parts"]:
                d = self.data["parts"][name]
                if d["type"] not in entry_registry.registered_object_map:
                    logger.println("[WARN] type '{}' as '{}' for state {} not found!".format(d["type"], name,
                                                                                             state_instance.NAME))
                    continue
                prev = state_instance.part_dict[name] if name in state_instance.part_dict else None
                part = entry_registry.registered_object_map[d["type"]].deserialize(state_instance, d, prev)
                state_instance.part_dict[name] = part
                if prev is None:
                    part.master = [state_instance]
                    part.bind_to_eventbus()
                if part not in state_instance.parts:
                    state_instance.parts.append(part)

    def reload(self):
        """
        Will reload the context and parse into the previous injected states
        Called by the system on data reload
        Will internally re-call the inject()-function on every state
        """
        self.data = ResourceLocator.read(self.file, "json")
        for state_instance in self.injected_objects:
            self.inject(state_instance)

    def __del__(self):
        if event is not None and event.EventHandler.PUBLIC_EVENT_BUS is not None:
            event.EventHandler.PUBLIC_EVENT_BUS.unsubscribe("command:reload:end", self.reload)
