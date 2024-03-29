"""
mcpython - a minecraft clone written in python licenced under the MIT-licence 
(https://github.com/mcpython4-coding/core)

Contributors: uuk, xkcdjerry (inactive)

Based on the game of fogleman (https://github.com/fogleman/Minecraft), licenced under the MIT-licence
Original game "minecraft" by Mojang Studios (www.minecraft.net), licenced under the EULA
(https://account.mojang.com/documents/minecraft_eula)
Mod loader inspired by "Minecraft Forge" (https://github.com/MinecraftForge/MinecraftForge) and similar

This project is not official by mojang and does not relate to it.
"""
import typing

import mcpython.common.event.api
import mcpython.common.event.Registry
import mcpython.common.state.AbstractState
import mcpython.common.state.AbstractStatePart
import mcpython.engine.event.EventHandler
import mcpython.engine.ResourceLoader
from mcpython import shared
from mcpython.engine import logger


class IStateConfigEntry(mcpython.common.event.api.IRegistryContent):
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
        existing: typing.Union[
            None, mcpython.common.state.AbstractStatePart.AbstractStatePart
        ],
    ) -> mcpython.common.state.AbstractStatePart.AbstractStatePart:
        raise NotImplementedError()


entry_registry = mcpython.common.event.Registry.Registry(
    "minecraft:state_definition_entries",
    ["minecraft:state_definition_entry"],
    "stage:mod:config:entry_loaders",
    sync_via_network=False,
)


@shared.registry
class UIButtonDefaultStateConfigEntry(IStateConfigEntry):
    NAME = "minecraft:ui_button_default"

    @classmethod
    def deserialize(
        cls,
        state_instance,
        data: dict,
        existing: typing.Union[
            None, mcpython.common.state.AbstractStatePart.AbstractStatePart
        ],
    ) -> mcpython.common.state.AbstractStatePart.AbstractStatePart:
        import mcpython.common.state.ui.UIPartButton

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
            type(existing), mcpython.common.state.ui.UIPartButton.UIPartButton
        ):
            on_press = (
                getattr(state_instance, data["on_press"])
                if "on_press" in data
                else None
            )
            existing.bounding_box_size = size
            existing.text = text
            existing.position = position
            existing.anchor_element = anchor_button
            existing.anchor_window = anchor_window
            existing.enabled = enabled
            existing.has_hovering_state = has_hov
            existing.on_press = on_press
            return existing
        return mcpython.common.state.ui.UIPartButton.UIPartButton(
            size,
            text,
            position,
            anchor_button=anchor_button,
            anchor_window=anchor_window,
            enable=enabled,
            has_hovering_state=has_hov,
            on_press=on_press,
        )


@shared.registry
class UILableStateConfigEntry(IStateConfigEntry):
    NAME = "minecraft:ui_lable_default"

    @classmethod
    def deserialize(
        cls,
        state_instance,
        data: dict,
        existing: typing.Union[
            None, mcpython.common.state.AbstractStatePart.AbstractStatePart
        ],
    ) -> mcpython.common.state.AbstractStatePart.AbstractStatePart:
        import mcpython.common.state.ui.UIPartLabel

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
            type(existing), mcpython.common.state.ui.UIPartLabel.UIPartLabel
        ):
            existing.text = text
            existing.position = position
            existing.anchor_window = anchor_window
            existing.anchor_element = anchor_lable
            existing.on_press = on_press
            existing.color = color
            existing.text_size = text_size
            return existing
        return mcpython.common.state.ui.UIPartLabel.UIPartLabel(
            text,
            position,
            anchor_lable=anchor_lable,
            anchor_window=anchor_window,
            on_press=on_press,
            color=color,
            text_size=text_size,
        )


@shared.registry
class UIProgressBarConfigEntry(IStateConfigEntry):
    NAME = "minecraft:ui_progressbar"

    @classmethod
    def deserialize(
        cls, state_instance, data: dict, existing
    ) -> mcpython.common.state.AbstractStatePart.AbstractStatePart:
        import mcpython.common.state.ui.UIPartProgressBar

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
            type(existing), mcpython.common.state.ui.UIPartProgressBar.UIPartProgressBar
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
        return mcpython.common.state.ui.UIPartProgressBar.UIPartProgressBar(
            position, size, color, item_count, status, text, anchor_ele, anchor_win
        )


@shared.registry
class ConfigBackground(IStateConfigEntry):
    NAME = "minecraft:config_background"

    @classmethod
    def deserialize(
        cls,
        state_instance,
        data: dict,
        existing: typing.Union[
            None, mcpython.common.state.AbstractStatePart.AbstractStatePart
        ],
    ) -> mcpython.common.state.AbstractStatePart.AbstractStatePart:
        import mcpython.common.state.ConfigBackgroundPart

        if existing is not None and issubclass(
            type(existing),
            mcpython.common.state.ConfigBackgroundPart.ConfigBackground,
        ):
            return existing
        return mcpython.common.state.ConfigBackgroundPart.ConfigBackground()


configs = {}


def get_config(file: str):
    if file not in configs:
        configs[file] = StateConfigFile(file)
    return configs[file]


class StateConfigFile:
    """
    Class for deserialize a config file for a state into a state
    """

    def __init__(self, file: str):
        """
        Constructs n new deserializer for a file
        """
        self.file = file
        self.data = None
        self.injected_objects = set()
        mcpython.engine.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
            "command:reload:end", self.reload
        )

    def inject(
        self,
        state_instance: typing.Union[
            mcpython.common.state.AbstractState.AbstractState,
            mcpython.common.state.AbstractStatePart.AbstractStatePart,
        ],
        retry: bool = True,
    ):
        """
        Will make the given state an state of the kind specified by this file
        :param state_instance: the state to inject the data into
        :param retry: internal flag if to schedule a reload if the data is not arrival
        WARNING: will override ALL existing data from state parts and their config
        """
        if self.data is None:
            if retry:
                shared.tick_handler.schedule_once(self.reload())
                shared.tick_handler.schedule_once(
                    lambda: self.inject(state_instance, retry=False)
                )
            return

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

    async def reload(self):
        """
        Will reload the context and parse into the previous injected states
        Called by the system on data reload
        Will internally re-call the inject()-function on every state
        """
        self.data = await mcpython.engine.ResourceLoader.read_json(self.file)
        for state_instance in self.injected_objects:
            self.inject(state_instance)

    def __del__(self):
        if (
            mcpython is not None
            and mcpython.engine.event.EventHandler.PUBLIC_EVENT_BUS is not None
        ):
            mcpython.engine.event.EventHandler.PUBLIC_EVENT_BUS.unsubscribe(
                "command:reload:end", self.reload
            )
