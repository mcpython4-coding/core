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


@api.annotation.TestSetting(99).no_result()
def prepare_client():
    WRAPPER.prepare_client()

