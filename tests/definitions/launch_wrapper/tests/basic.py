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
import api.annotation

WRAPPER = None


@api.annotation.TestSetting(100).no_result()
def run():
    """
    Test for the LaunchWrapper constructor
    :return:
    """

    global WRAPPER

    import mcpython.LaunchWrapper

    WRAPPER = mcpython.LaunchWrapper.LaunchWrapper()
    assert WRAPPER.is_client is True, "client should be default"

    # todo: check status

    print("LaunchWrapper creation successful")


@api.annotation.TestSetting(99)
def prepare_client():
    import mcpython.shared

    WRAPPER.prepare_client()

    if mcpython.shared.window is None:
        print("failed to create window")
        return False

    import pyglet

    if not isinstance(mcpython.shared.window, pyglet.window.Window):
        print("window instance is somehow wrong...", mcpython.shared.window)
        return False

    print("client-setup successful")
    return True


@api.annotation.TestSetting(98)
def test_event_0():
    """
    This is the first major test for the event system
    If everything goes to plan, it will handle the exception and pass it as a RuntimeError back to the event caller
    """

    import mcpython.common.event.EventHandler

    mcpython.common.event.EventHandler.PUBLIC_EVENT_BUS.crash_on_error = True
    mcpython.common.event.EventHandler.PUBLIC_EVENT_BUS.close_on_error = False
    import mcpython.shared

    def test_fail():
        raise ValueError

    mcpython.common.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
        "mcpython:test_framework:test_event_0", test_fail
    )

    try:
        mcpython.shared.event_handler.call("mcpython:test_framework:test_event_0")
    except RuntimeError:
        return True
    except ValueError:
        print("something changed the callback exception to the real one...")

    return False


@api.annotation.TestSetting(97)
def test_event_1():
    import mcpython.common.event.EventHandler
    import mcpython.shared

    SUCCESS = False

    def test_success():
        nonlocal SUCCESS
        SUCCESS = True

    mcpython.common.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
        "mcpython:test_framework:test_event_1", test_success
    )

    mcpython.shared.event_handler.call("mcpython:test_framework:test_event_1")

    print("state of event test 1:", SUCCESS)

    return SUCCESS


@api.annotation.TestSetting(97)
def test_event_2():
    import mcpython.common.event.EventHandler
    import mcpython.shared

    SUCCESS = False

    def test_success(state):
        nonlocal SUCCESS
        SUCCESS = state

    mcpython.common.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
        "mcpython:test_framework:test_event_2", test_success
    )

    mcpython.shared.event_handler.call("mcpython:test_framework:test_event_2", True)

    print("state of event test 2:", SUCCESS)

    return SUCCESS


@api.annotation.TestSetting(96).no_result()
def prepare_client_system():

    WRAPPER.setup()
    print("system-setup successful")

    # todo: check status


@api.annotation.TestSetting(95).no_result()
def run_client():
    pass
