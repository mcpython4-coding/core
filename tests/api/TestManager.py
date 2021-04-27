import typing
import importlib
import api.annotation


class TestStage:
    def __init__(self, manager: "TestManager", name: str, fail_on_single=False):
        self.manager = manager
        self.name = name
        self.fail_on_single = fail_on_single

        self.tests = []

    def add_module(self, module: str):
        self.tests.append((0, module))
        return self

    def add_module_with_annotations(self, module: str):
        api.annotation.TESTS.clear()

        importlib.import_module(module)

        for test in api.annotation.TESTS:
            self.tests.append((1, test.run))

    def run(self) -> bool:
        results = []
        failed = []

        for type, *data in self.tests:
            if type == 0:
                result = importlib.import_module(data[0]).run()
            elif type == 1:
                result = data[0]()
            else:
                raise RuntimeError

            if not result:
                if self.fail_on_single:
                    print(f"failed at test {data}")
                    return False

                failed.append(data)

            results.append(result)

        if len(failed) > 0:
            print("failed at the following tests:")
            for e in failed:
                print("-", repr(e))
            return False

        return True


class TestManager:
    def __init__(self):
        self.tests: typing.List[TestStage] = []

    def stage(self, name: str, fail_on_single=False) -> TestStage:
        stage = TestStage(self, name, fail_on_single=fail_on_single)
        self.tests.append(stage)
        return stage

    def run(self):
        for stage in self.tests:
            print(f"running test stage '{stage.name}'")
            stage.run()

