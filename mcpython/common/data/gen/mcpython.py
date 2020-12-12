from mcpython.common.data.gen.TextureDataGen import TextureConstructor
from mcpython.common.data.gen.DataGeneratorManager import DataGeneratorInstance
from mcpython import shared


generator = DataGeneratorInstance(
    shared.local + "/resources/generated" if shared.dev_environment else shared.local
)

generator.annotate(
    TextureConstructor("chest_gui")
    .add_image_layer_top("minecraft:gui/container/shulker_box")
    .crop((0, 0, 176 / 255, 166 / 255))
    .scaled((2, 2)),
    "assets/minecraft/textures/gui/chest_gui_generated.png",
)
generator.annotate(
    TextureConstructor("crafting_table_gui")
    .add_image_layer_top("minecraft:gui/container/crafting_table")
    .crop((0, 0, 176 / 255, 166 / 255))
    .scaled((2, 2)),
    "assets/minecraft/textures/gui/crafting_table_generated.png",
)
