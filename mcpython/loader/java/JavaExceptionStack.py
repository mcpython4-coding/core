
class StackCollectingException(Exception):
    def __init__(self, text: str, base: Exception = None):
        self.text = text
        self.traces = []
        self.base = base

    def add_trace(self, line: str):
        self.traces.append(line)
        return self

    def format_exception(self):
        return self.text + "\n" + "\n".join(self.traces)

