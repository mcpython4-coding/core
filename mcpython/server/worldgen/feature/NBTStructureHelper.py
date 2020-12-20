import python_nbt.nbt as nbt
import mcpython.ResourceLoader
from mcpython import shared


class StructureNBTHelper:
    @classmethod
    def from_file(cls, file: str):
        data = mcpython.ResourceLoader.read_raw(file)
        with open(shared.tmp.name + "/tmp.nbt", mode="wb") as f:
            f.write(data)
        return cls(nbt.read_from_nbt_file(shared.tmp.name + "/tmp.nbt").json_obj())

    def __init__(self, data: dict):
        pass
