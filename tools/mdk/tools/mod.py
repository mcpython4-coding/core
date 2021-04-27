"""
mcpython - a minecraft clone written in python licenced under the MIT-licence 
(https://github.com/mcpython4-coding/core)

Contributors: uuk, xkcdjerry (inactive)

Based on the game of fogleman (https://github.com/fogleman/Minecraft), licenced under the MIT-licence
Original game "minecraft" by Mojang Studios (www.minecraft.net), licenced under the EULA
(https://account.mojang.com/documents/minecraft_eula)
Mod loader inspired by "Minecraft Forge" (https://github.com/MinecraftForge/MinecraftForge) and similar

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared


@shared.mod_loader("{NAME}", "stage:mod:init")
def init():
    """
    Main init method of {NAME}
    """

    # Do here your combined factory stuff...
    @shared.mod_loader("{NAME}", "stage:combined_factory:blocks")
    def load_combined_factories():
        pass

    # ... and do here manual block registering ...
    @shared.mod_loader("{NAME}", "stage:block:factory_usage")
    def load_block_factories():
        pass

    # ... and here the items!
    @shared.mod_loader("{NAME}", "stage:item:factory_usage")
    def load_item_factories():
        pass

    # And do here your data gen work...
    @shared.mod_loader("{NAME}", "special:datagen:configure")
    def do_data_gen():
        import mcpython.common.data.gen.DataGeneratorManager as DataGeneratorManager

        instance = DataGeneratorManager.DataGeneratorInstance(shared.mod_loader.mods["{NAME}"].path)
