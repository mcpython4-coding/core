import globals as G
import sys
import os


@G.modloader("{NAME}", "stage:mod:init")
def init():
    @G.modloader("{NAME}", "stage:combined_factory:blocks")
    def load_combined_factories():  # Do here your combined factory stuff...
        pass

    @G.modloader("{NAME}", "stage:block:factory_usage")
    def load_block_factories():  # ... and do here manual block registering ...
        pass

    @G.modloader("{NAME}", "stage:item:factory_usage")
    def load_item_factories():  # ... and here the items!
        pass

