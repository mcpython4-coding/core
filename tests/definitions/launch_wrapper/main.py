import api.TestManager


def launch(config):
    manager = api.TestManager.TestManager()
    manager.stage("Basic", fail_on_single=True).add_module_with_annotations("definitions.launch_wrapper.tests.basic")

    manager.run()

