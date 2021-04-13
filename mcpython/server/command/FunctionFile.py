from mcpython import shared


class FunctionFile:
    @classmethod
    def from_file(cls, file: str) -> "FunctionFile":
        with open(file) as f:
            lines = f.read().split("\n")

        instance = cls()

        for line in lines:
            line = line.strip()
            if len(line) == 0 or line.startswith("#"): continue

            instance.command_nodes.append(shared.command_parser.parse(line if not line.startswith("/") else "/"+line))

        return instance

    def __init__(self):
        self.command_nodes = []

    def execute(self, info):
        for node, data in self.command_nodes:
            for func in node.on_execution_callbacks:
                func(info, data)

