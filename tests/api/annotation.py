import traceback
import typing

TESTS = []


class TestSetting:
    def __init__(self, priority=0):
        self.priority = priority
        TESTS.append(self)

        self.run_helper = lambda func, args, kwargs: func(*args, **kwargs)
        self.target = None

    def no_result(self):

        def run(func, args, kwargs):
            try:
                self.target(*args, **kwargs)
            except:
                traceback.print_exc()
                return False

            return True

        self.run_helper = run

        return self

    def run_helper(self, func, *args, **kwargs):
        try:
            func(*args, **kwargs)
        except:
            traceback.print_exc()
            return False
        return True

    def expect_exception(self, exception):
        base = self.run_helper

        def run(func, args, kwargs):
            try:
                return base(*args, **kwargs)
            except exception:
                return False

        self.run_helper = run

        return self

    def expects_output(self, compare):
        def run(func, args, kwargs):
            try:
                result = func(*args, **kwargs)
            except:
                traceback.print_exc()
                return False

            return result == compare

        self.run_helper = run

        return self

    def expects_output_check_func(self, check: typing.Callable[[typing.Any], bool]):
        def run(func, args, kwargs):
            try:
                result = func(*args, **kwargs)
            except:
                traceback.print_exc()
                return False

            return check(result)

        self.run_helper = run

        return self

    def __call__(self, func):
        self.target = func
        return func

    def run(self):
        # todo: include args
        return self.run_helper(self.target, [], {})

    def __repr__(self):
        return f"TestSetting(target={self.target})"

