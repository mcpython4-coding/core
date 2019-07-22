"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import item.Item


@G.itemhandler
class Stone(item.Item.Item):
    @staticmethod
    def get_name() -> str:
        return "minecraft:stone"

    @staticmethod
    def get_item_image_location() -> str:
        return "assets/missingtexture.png"

