import mod.Mod
import globals as G


testmod = mod.Mod.Mod("testmod", "0.0.1")


def inject():  # special method called when system is ready for accepting these code
    # needed for enabling recipe loading for these mod
    print("hello from prepare phase")
    import crafting.CraftingHandler
    testmod.eventbus.subscribe("stage:recipes", G.craftinghandler.load, "testmod", info="loading crafting recipes")
    import texture.model.ModelHandler
    testmod.eventbus.subscribe("stage:model:model_search", G.modelhandler.add_from_mod, "testmod",
                               info="searching for block models")
    import texture.model.BlockState
    testmod.eventbus.subscribe("stage:model:blockstate_search",
                               texture.model.BlockState.BlockStateDefinition.from_directory,
                               "assets/testmod/blockstates", info="searching for block states")

    # print(testmod.eventbus.eventsubscribtions)


# todo: add example item class, crafting recipes


# testmod.eventbus.subscribe("stage:prepare", inject, info="adding event subscriptions")


def create_example_block():
    import factory.BlockFactory
    factory.BlockFactory.BlockFactory().setName("testmod:example").finish()


def create_example_item():
    import factory.ItemFactory
    factory.ItemFactory.ItemFactory().setDefaultItemFile(
        "assets/missingtexture.png").setName("testmod:exampleitem").finish()


# stage:block:base for factory work, stage:block:load for direct class work
# testmod.eventbus.subscribe("stage:block:base", create_example_block, info="creating example block")
# stage:item:base for factory work, stage:item:load for direct class work
# testmod.eventbus.subscribe("stage:item:base", create_example_item, info="creating example item")

