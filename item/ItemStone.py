import globals as G
import item.Item


@G.itemhandler
class Stone(item.Item.Item):
    @staticmethod
    def get_name() -> str:
        return "minecraft:stone"

