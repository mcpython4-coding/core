import typing

from mcpython.common.container.ResourceStack import ItemStack


class ItemGroup:
    def __init__(self):
        self.entries: typing.List[ItemStack] = []

    def add(self, entry: ItemStack):
        assert not entry.is_empty(), "itemstack cannot be empty!"
        self.entries.append(entry.set_amount(1))
        return self

    def sort_after_item_name(self):
        self.entries.sort(key=lambda stack: stack.get_item_name())
        return self
