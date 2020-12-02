"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import typing

import mcpython.ResourceLoader
import mcpython.common.event.EventHandler
import mcpython.common.event.Registry
from mcpython import shared as G, logger
import mcpython.client.state.State
import mcpython.client.state.StatePart


class IStateConfigEntry(mcpython.common.event.Registry.IRegistryContent):
    """
    base class for every entry in an config file
    """

    TYPE = "minecraft:state_definition_entry"

    # NAME is the type-name

    @classmethod
    def deserialize(
        cls,
        state_instance,
        data: dict,
        existing: typing.Union[None, mcpython.client.state.StatePart.StatePart],
    ) -> mcpython.client.state.StatePart.StatePart:
        raise NotImplementedError()


entry_registry = mcpython.common.event.Registry.Registry(
    "state_definition_entries", ["minecraft:state_definition_entry"], "stage:mod:config:entry_loaders"
)


@G.registry
class UIButtonDefaultStateConfigEntry(IStateConfigEntry):
    NAME = "minecraft:ui_button_default"

    @classmethod
    def deserialize(
        cls,
        state_instance,
        data: dict,
        existing: typing.Union[None, mcpython.client.state.StatePart.StatePart],
    ) -> mcpython.client.state.StatePart.StatePart:
        import mcpython.client.state.ui.UIPartButton

        size = tuple(data["size"])
        text = data["text"] if "text" in data else ""
        position = tuple(data["position"])
        anchor_window = data["anchor_win"] if "anchor_win" in data else "WS"
        anchor_button = data["anchor_but"] if "anchor_but" in data else "WS"
        enabled = data["enabled"] if "enabled" in data else True
        has_hov = data["has_hovering_state"] if "has_hovering_state" in data else True

        on_press = (
            getattr(state_instance, data["on_press"]) if "on_press" in data else None
        )

        if existing is not None and issubclass(
            type(existing), mcpython.client.state.ui.UIPartButton.UIPartButton
        ):
            on_press = (
                getattr(state_instance, data["on_press"])
                if "on_press" in data
                else None
            )
            existing.bboxsize = size
            existing.text = text
            existing.position = position
            existing.anchor_element = anchor_button
            existing.anchor_window = anchor_window
            existing.enabled = enabled
            existing.has_hovering_state = has_hov
            existing.on_press = on_press
            return existing
        return mcpython.client.state.ui.UIPartButton.UIPartButton(
            size,
            text,
            position,
            anchor_button=anchor_button,
            anchor_window=anchor_window,
            enabled=enabled,
            has_hovering_state=has_hov,
            on_press=on_press,
        )


@G.registry
class UILableStateConfigEntry(IStateConfigEntry):
    NAME = "minecraft:ui_lable_default"

    @classmethod
    def deserialize(
        cls,
        state_instance,
        data: dict,
        existing: typing.Union[None, mcpython.client.state.StatePart.StatePart],
    ) -> mcpython.client.state.StatePart.StatePart:
        import mcpython.client.state.ui.UIPartLable

        text = data["text"]
        position = tuple(data["position"])
        anchor_window = data["anchor_win"] if "anchor_win" in data else "WS"
        anchor_lable = data["anchor_lab"] if "anchor_lab" in data else "WS"
        on_press = (
            getattr(state_instance, data["on_press"]) if "on_press" in data else None
        )
        color = tuple(data["color"]) if "color" in data else (0, 0, 0, 0)
        text_size = data["text_size"] if "text_size" in data else 20

        if existing is not None and issubclass(
            type(existing), mcpython.client.state.ui.UIPartLable.UIPartLable
        ):
            existing.text = text
            existing.position = position
            existing.anchor_window = anchor_window
            existing.anchor_element = anchor_lable
            existing.on_press = on_press
            existing.color = color
            existing.text_size = text_size
            return existing
        return mcpython.client.state.ui.UIPartLable.UIPartLable(
            text,
            position,
            anchor_lable=anchor_lable,
            anchor_window=anchor_window,
            on_press=on_press,
            color=color,
            text_size=text_size,
        )


@G.registry
class UIProgressBarConfigEntry(IStateConfigEntry):
    NAME = "minecraft:ui_progressbar"

    @classmethod
    def deserialize(
        cls, state_instance, data: dict, existing
    ) -> mcpython.client.state.StatePart.StatePart:
        import mcpython.client.state.ui.UIPartProgressBar

        position = data["position"]
        size = data["size"]
        color = (1.0, 0, 0) if "color" not in data else data["color"]
        item_count = data["items"]
        status = 0 if "status" not in data else data["status"]
        text = data["text"]
        anchor_ele = data["element_anchor"] if "element_anchor" in data else "LD"
        anchor_win = data["window_anchor"] if "window_anchor" in data else "LD"
        assert type(size) == tuple
        if existing is not None and issubclass(
            type(existing), mcpython.client.state.ui.UIPartProgressBar.UIPartProgressBar
        ):
            existing.position = position
            existing.size = size
            existing.anchor_window = anchor_win
            existing.anchor_element = anchor_ele
            existing.color = color
            existing.progress = status
            existing.progress_max = item_count
            existing.text = text
            return existing
        return mcpython.client.state.ui.UIPartProgressBar.UIPartProgressBar(
            position, size, color, item_count, status, text, anchor_ele, anchor_win
        )


@G.registry
class ConfigBackground(IStateConfigEntry):
    NAME = "minecraft:config_background"

    @classmethod
    def deserialize(
        cls,
        state_instance,
        data: dict,
        existing: typing.Union[None, mcpython.client.state.StatePart.StatePart],
    ) -> mcpython.client.state.StatePart.StatePart:
        import mcpython.client.state.StatePartConfigBackground

        if existing is not None and issubclass(
            type(existing),
            mcpython.client.state.StatePartConfigBackground.StatePartConfigBackground,
        ):
            return existing
        return (
            mcpython.client.state.StatePartConfigBackground.StatePartConfigBackground()
        )


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
        self.data = mcpython.ResourceLoader.read_json(file)
        self.injected_objects = set()
        mcpython.common.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
            "command:reload:end", self.reload
        )

    def inject(
        self,
        state_instance: typing.Union[
            mcpython.client.state.State.State, mcpython.client.state.StatePart.StatePart
        ],
    ):
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
                if d["type"] not in entry_registry.entries:
                    logger.println(
                        "[WARN] type '{}' as '{}' for state {} not found!".format(
                            d["type"], name, state_instance.NAME
                        )
                    )
                    continue
                prev = (
                    state_instance.part_dict[name]
                    if name in state_instance.part_dict
                    else None
                )
                part = entry_registry.entries[d["type"]].deserialize(
                    state_instance, d, prev
                )
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
        self.data = mcpython.ResourceLoader.read_json(self.file)
        for state_instance in self.injected_objects:
            self.inject(state_instance)

    def __del__(self):
        if (
            mcpython is not None
            and mcpython.common.event.EventHandler.PUBLIC_EVENT_BUS is not None
        ):
            mcpython.common.event.EventHandler.PUBLIC_EVENT_BUS.unsubscribe(
                "command:reload:end", self.reload
            )
