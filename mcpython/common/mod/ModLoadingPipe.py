"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import graphlib
import typing

from mcpython import shared
from mcpython import logger


class LoadingStageManager:
    """
    System for handling the order of loading phases with dynamic dependency handling
    """

    def __init__(self):
        self.stages = {}
        self.order: graphlib.TopologicalSorter = None
        self.current_stage: str = None
        self.ready = []

    def get_new_ready(self):
        self.ready.extend(self.order.get_ready())
        return self.ready.pop(0)

    def get_stage(self) -> typing.Optional["LoadingStage"]:
        if self.current_stage is None:
            if not self.order.is_active():
                return
            self.current_stage = self.get_new_ready()

        while self.current_stage not in self.stages and self.current_stage is not None:
            logger.println(
                "[MOD LOADING PIPE][INFO] skipping stage {}".format(self.current_stage)
            )
            self.next_stage()

        return self.stages[self.current_stage]

    def next_stage(self):
        self.order.done(self.current_stage)
        self.current_stage = self.get_new_ready() if self.order.is_active() else None

    def add_stage(self, stage: "LoadingStage"):
        self.stages[stage.name] = stage
        return self

    def update_order(self):
        self.order = graphlib.TopologicalSorter(
            {name: self.stages[name].dependencies for name in self.stages}
        )
        self.order.prepare()
        return self


class LoadingStage:
    def __init__(self, name: str, user_facing_name: str, *dependencies: str):
        self.name = name
        self.user_facing_name = user_facing_name
        self.events = {}
        self.dependencies = set(dependencies)

        if name != "minecraft:loading_preparation":
            self.dependencies.add("minecraft:loading_preparation")

        self.order: graphlib.TopologicalSorter = None
        self.dirty = False
        self.active_mod_index = 0
        self.max_progress = 0
        self.current_progress = 0
        self.active_event = None
        self.event_scheduled = []

    def next_event(self):
        if self.active_event is not None:
            self.order.done(self.active_event)
        self.event_scheduled.extend(self.order.get_ready())
        self.active_event = (
            self.event_scheduled.pop(0) if len(self.event_scheduled) > 0 else None
        )
        self.current_progress += 1
        self.active_mod_index = 0
        # print(self.active_event, self.events, self.event_scheduled, self.order.is_active())

    def finished(self):
        return not (self.order.is_active() or len(self.event_scheduled))

    def add_event_stage(self, event_name: str, *inner_depends: str):
        self.events[event_name] = set(inner_depends)
        self.dirty = True
        return self

    def add_event_stage_dependency(self, event_name: str, *inner_depends: str):
        self.events[event_name] |= set(inner_depends)
        self.dirty = True
        return self

    def add_dependency(self, stage_name: str):
        self.dependencies.add(stage_name)
        return self

    def update_order(self):
        if not self.dirty:
            return self

        self.order = graphlib.TopologicalSorter(self.events)
        self.order.prepare()
        self.next_event()
        return self

    @classmethod
    def finish(cls, astate):
        """
        Will finish up the system
        :param astate: the state to use
        """
        shared.mod_loader.active_loading_stage += 1
        astate.parts[0].progress += 1
        astate.parts[2].progress = 0
        manager.next_stage()
        new_stage: LoadingStage = manager.get_stage()

        if not manager.order.is_active():  # or new_stage is None:
            logger.println(
                "[INFO] locking registries..."
            )  # ... and do similar stuff :-)
            shared.event_handler.call("mod_loader:load_finished")

            shared.state_handler.switch_to("minecraft:block_item_generator")
            shared.mod_loader.finished = True
            return True

        if (
            new_stage.active_event
            in shared.mod_loader.mods[
                shared.mod_loader.mod_loading_order[0]
            ].eventbus.event_subscriptions
        ):
            astate.parts[2].progress_max = len(
                shared.mod_loader.mods[
                    shared.mod_loader.mod_loading_order[0]
                ].eventbus.event_subscriptions[new_stage.active_event]
            )
        else:
            astate.parts[2].progress_max = 0

    def call_one(self, astate):
        """
        will call one event from the stack
        :param astate: the state to use
        """
        if self.active_event is None:
            self.finish(astate)
            return

        if self.active_mod_index >= len(shared.mod_loader.mods):
            self.active_mod_index = 0
            if self.finished():
                return self.finish(astate)
            self.next_event()
            mod_instance = shared.mod_loader.mods[
                shared.mod_loader.mod_loading_order[self.active_mod_index]
            ]
            self.max_progress = (
                len(mod_instance.eventbus.event_subscriptions[self.active_event])
                if self.active_event in mod_instance.eventbus.event_subscriptions
                else 0
            )
            astate.parts[2].progress_max = self.max_progress
            astate.parts[2].progress = 0
            return

        if self.active_event is None:
            self.next_event()
            self.active_mod_index = 0

        modname = shared.mod_loader.mod_loading_order[self.active_mod_index]
        mod_instance = shared.mod_loader.mods[modname]

        # print(
        #     self.active_event, mod_instance.name,
        #     mod_instance.eventbus.event_subscriptions[self.active_event][:1]
        #     if self.active_event in mod_instance.eventbus.event_subscriptions else None
        # )
        # print(self.active_event)

        try:
            mod_instance.eventbus.call_as_stack(self.active_event)
        except RuntimeError:
            self.active_mod_index += 1
            if self.active_mod_index >= len(shared.mod_loader.mods):
                if self.finished():
                    return self.finish(astate)

                self.next_event()

                self.active_mod_index = 0
                mod_instance = shared.mod_loader.mods[
                    shared.mod_loader.mod_loading_order[self.active_mod_index]
                ]
                if self.active_event in mod_instance.eventbus.event_subscriptions:
                    self.max_progress = len(
                        mod_instance.eventbus.event_subscriptions[self.active_event]
                    )
                else:
                    self.max_progress = 0
                astate.parts[2].progress_max = self.max_progress
                astate.parts[2].progress = 0
                return

            mod_instance = shared.mod_loader.mods[
                shared.mod_loader.mod_loading_order[self.active_mod_index]
            ]
            if self.active_event in mod_instance.eventbus.event_subscriptions:
                self.max_progress = len(
                    mod_instance.eventbus.event_subscriptions[self.active_event]
                )
            else:
                self.max_progress = 0
            astate.parts[2].progress_max = self.max_progress
            astate.parts[2].progress = 0
            return
        astate.parts[2].progress += 1  # todo: this is not good, can we optimize it?


manager = LoadingStageManager()
manager.add_stage(
    LoadingStage("minecraft:loading_preparation", "preparation of loading")
    .add_event_stage("stage:pre")
    .add_event_stage("stage:mod:init", "stage:pre")
    .update_order()
)
manager.add_stage(
    LoadingStage(
        "minecraft:api_management",
        "api management",
    )
    .add_event_stage("stage:api:define")
    .add_event_stage("stage:api:check", "stage:api:define")
    .add_event_stage("stage:api:retrieve", "stage:api:check")
    .update_order()
)
manager.add_stage(
    LoadingStage(
        "minecraft:loading_stage_addition",
        "adding custom loading stages",
        "minecraft:loading_preparation",
    )
    .add_event_stage("stage:addition_of_stages")
    .add_event_stage(
        "stage:addition_of_stages:update_order", "stage:addition_of_stages"
    )
    .update_order()
)
manager.add_stage(
    LoadingStage(
        "minecraft:additional_resource_locations",
        "adding additional resource locations to the system",
        "minecraft:loading_stage_addition",
    )
    .add_event_stage("stage:resources:pipe:add_mapper")
    .add_event_stage("stage:additional_resources", "stage:resources:pipe:add_mapper")
    .update_order()
)
manager.add_stage(
    LoadingStage(
        "minecraft:configs", "reading config files", "minecraft:loading_stage_addition"
    )
    .add_event_stage("stage:mod:config:entry_loaders")
    .add_event_stage("stage:mod:config:define", "stage:mod:config:entry_loaders")
    .add_event_stage("stage:mod:config:load", "stage:mod:config:define")
    .add_event_stage("stage:mod:config:work", "stage:mod:config:load")
    .update_order()
)
manager.add_stage(
    LoadingStage(
        "minecraft:combined_factories",
        "working on combined factories",
        "minecraft:configs",
        "minecraft:additional_resource_locations",
    )
    .add_event_stage("stage:combined_factory:blocks")
    .add_event_stage("stage:combined_factory:build", "stage:combined_factory:blocks")
    .update_order()
)
manager.add_stage(
    LoadingStage("minecraft:blocks", "loading blocks", "minecraft:combined_factories")
    .add_event_stage("stage:block:factory:prepare")
    .add_event_stage("stage:block:factory_usage", "stage:block:factory:prepare")
    .add_event_stage("stage:block:factory:finish", "stage:block:factory_usage")
    .add_event_stage("stage:block:load", "stage:block:factory:finish")
    .add_event_stage(
        "stage:block:overwrite", "stage:block:load", "stage:block:factory:finish"
    )
    .update_order()
)
manager.add_stage(
    LoadingStage("minecraft:items", "loading items", "minecraft:combined_factories")
    .add_event_stage("stage:item:factory:prepare")
    .add_event_stage("stage:item:factory_usage", "stage:item:factory:prepare")
    .add_event_stage("stage:item:factory:finish", "stage:item:factory_usage")
    .add_event_stage("stage:item:load", "stage:item:factory:finish")
    .add_event_stage(
        "stage:item:overwrite", "stage:item:load", "stage:item:factory:finish"
    )
    .update_order()
)
manager.add_stage(
    LoadingStage("minecraft:inventories", "loading inventories", "minecraft:items")
    .add_event_stage("stage:inventories:pre")
    .add_event_stage("stage:inventories", "stage:inventories:pre")
    .add_event_stage("stage:inventories:post", "stage:inventories")
    .update_order()
)
manager.add_stage(
    LoadingStage("minecraft:commands", "loading commands", "minecraft:configs")
    .add_event_stage("stage:command:entries")
    .add_event_stage("stage:command:selectors", "stage:command:entries")
    .add_event_stage("stage:commands", "stage:command:selectors")
    .add_event_stage("stage:command:gamerules")
    .update_order()
)
manager.add_stage(
    LoadingStage("minecraft:entities", "loading entities", "minecraft:items")
    .add_event_stage("stage:entities:prepare")
    .add_event_stage("stage:entities", "stage:entities:prepare")
    .add_event_stage("stage:entities:ai:setup", "stage:entities")
    .add_event_stage("stage:entities:overwrite", "stage:entities:ai:setup")
    .update_order()
)

if shared.data_gen:
    manager.add_stage(
        LoadingStage(
            "minecraft:data_generator",
            "running data generators",
            "minecraft:blocks",
            "minecraft:items",
            "minecraft:commands",
            "minecraft:entities",
        )
        .add_event_stage("special:datagen:configure")
        .add_event_stage("special:datagen:generate", "special:datagen:configure")
        .update_order()
    )

    if shared.data_gen_exit:
        manager.add_stage(
            LoadingStage(
                "minecraft:data_generation_exit",
                "stopping launch",
                "minecraft:data_generator",
            )
            .add_event_stage("special:exit")
            .update_order()
        )

manager.add_stage(
    LoadingStage(
        "minecraft:language_files", "loading language data", "minecraft:data_generator"
    )
    .add_event_stage("stage:language")
    .update_order()
)
manager.add_stage(
    LoadingStage(
        "minecraft:tags",
        "loading tags",
        "minecraft:data_generator",
    )
    .add_event_stage("stage:tag:group")
    .add_event_stage("stage:tag:load", "stage:tag:group")
    .update_order()
)
manager.add_stage(
    LoadingStage(
        "minecraft:recipes",
        "loading recipes",
        "minecraft:tags",
    )
    .add_event_stage("stage:recipes")
    .add_event_stage("stage:recipe:groups", "stage:recipes")
    .add_event_stage("stage:recipe:bake", "stage:recipe:groups")
    .update_order()
)
manager.add_stage(
    LoadingStage(
        "minecraft:loot_tables", "loading loot tables", "minecraft:data_generator"
    )
    .add_event_stage("stage:loottables:locate")
    .add_event_stage("stage:loottables:functions")
    .add_event_stage("stage:loottables:conditions")
    .add_event_stage(
        "stage:loottables:load",
        "stage:loottables:locate",
        "stage:loottables:functions",
        "stage:loottables:conditions",
    )
    .update_order()
)
manager.add_stage(
    LoadingStage(
        "minecraft:factory_models",
        "factoring models",
        "minecraft:data_generator",
    )
    .add_event_stage("stage:modelfactory:prepare")
    .add_event_stage("stage:modelfactory:use", "stage:modelfactory:prepare")
    .add_event_stage("stage:modelfactory:bake", "stage:modelfactory:use")
    .add_event_stage("stage:blockstatefactory:prepare")
    .add_event_stage("stage:blockstatefactory:use", "stage:blockstatefactory:prepare")
    .add_event_stage("stage:blockstatefactory:bake", "stage:blockstatefactory:use")
    .update_order()
)
manager.add_stage(
    LoadingStage(
        "minecraft:block_states",
        "loading block states",
        "minecraft:factory_models",
        "minecraft:blocks",
    )
    .add_event_stage("stage:blockstate:register_loaders")
    .add_event_stage("stage:model:blockstate_search")
    .add_event_stage(
        "stage:model:blockstate_create",
        "stage:blockstate:register_loaders",
        "stage:model:blockstate_search",
    )
    .add_event_stage("stage:model:blockstate_bake", "stage:model:blockstate_create")
    .update_order()
)
manager.add_stage(
    LoadingStage(
        "minecraft:models",
        "loading models",
        "minecraft:factory_models",
        "minecraft:blocks",
        "minecraft:items",
    )
    .add_event_stage("stage:model:model_search")
    .add_event_stage("stage:model:model_search:intern", "stage:model:model_search")
    .add_event_stage("stage:model:model_create", "stage:model:model_search:intern")
    .add_event_stage("stage:model:model_bake_prepare", "stage:model:model_create")
    .add_event_stage("stage:model:model_bake_lookup", "stage:model:model_bake_prepare")
    .add_event_stage("stage:model:model_bake:prepare", "stage:model:model_bake_lookup")
    .add_event_stage("stage:model:model_bake", "stage:model:model_bake:prepare")
    .add_event_stage("stage:model:item:search")
    .add_event_stage("stage:model:item:bake", "stage:model:item:search")
    .update_order()
)
manager.add_stage(
    LoadingStage("minecraft:textures", "preparing texture atlases", "minecraft:models")
    .add_event_stage("stage:textureatlas:bake")
    .add_event_stage("stage:boxmodel:bake", "stage:textureatlas:bake")
    .add_event_stage("stage:block_boundingbox_get", "stage:boxmodel:bake")
    .update_order()
)
manager.add_stage(
    LoadingStage(
        "minecraft:world_generation",
        "loading world generation entries",
        "minecraft:blocks",
        "minecraft:data_generator",
    )
    .add_event_stage("stage:worldgen:serializer:prepare")
    .add_event_stage("stage:worldgen:feature", "stage:worldgen:serializer:prepare")
    .add_event_stage("stage:worldgen:serializer:biomes:load", "stage:worldgen:feature")
    .add_event_stage("stage:worldgen:biomes", "stage:worldgen:serializer:biomes:load")
    .add_event_stage("stage:worldgen:layer", "stage:worldgen:serializer:prepare")
    .add_event_stage(
        "stage:worldgen:serializer:mode:load",
        "stage:worldgen:layer",
        "stage:worldgen:biomes",
    )
    .add_event_stage(
        "stage:worldgen:serializer:mode:modify", "stage:worldgen:serializer:mode:load"
    )
    .add_event_stage("stage:worldgen:mode", "stage:worldgen:serializer:mode:modify")
    .add_event_stage("stage:dimension", "stage:worldgen:mode")
    .update_order()
)
manager.add_stage(
    LoadingStage(
        "minecraft:file_interface",
        "loading world serializer stuff",
        "minecraft:configs",
    )
    .add_event_stage("stage:serializer:parts")
    .add_event_stage("stage:datafixer:general")
    .add_event_stage("stage:datafixer:parts")
    .update_order()
)
manager.add_stage(
    LoadingStage(
        "minecraft:states",
        "loading states",
        "minecraft:configs",
    )
    .add_event_stage("stage:stateparts")
    .add_event_stage("stage:states", "stage:stateparts")
    .add_event_stage("stage:state_config:parser", "stage:states")
    .add_event_stage("stage:state_config:generate", "stage:state_config:parser")
    .add_event_stage("stage:states:post", "stage:state_config:generate")
    .update_order()
)
manager.add_stage(
    LoadingStage(
        "minecraft:post_load", "post-loading stuff", *list(manager.stages.keys())
    )
    .add_event_stage("stage:post")
    .add_event_stage("stage:final", "stage:post")
    .update_order()
    # todo: add registry lock phase
)

manager.update_order()
