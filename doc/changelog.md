# Changelog of mcpython-4
Contains only some information, in ordered form, in a better form for the end user than the version.info file.


### Information on development
- the development is split up into 2 phases: the dev-branch with changes to the code and after a full release,
    the "maintain" branch of that release, for hotfixes for versions. Version maintain branches may be deleted 
    at a later date.
- developing happens also on feature branches were bigger features can be tested. It is not guaranteed that any
    if this features will make its way into the final release.
- PR's should target dev or in some cases the feature branches, only for critical bug fixes the maintain-branch,
    after a PR to the dev or for fixes only applicable to the target release, not the latest dev
- this file will keep track on every development leading into an snapshot or release. The dev-branch will be used
    for creating the entries. Every new snapshot Changelog starts with "Changelog of <type> <name>" with optional
    following the theme of the snapshot, the release date and additional information. The Changelog should be
    an grouped list of changes after topic in an logical order with all not noticeable changes removed
    followed optional by an table of issues starting with "Fixed issues:" followed by an list of grouped after
    first occurrence of the bug the list of issues with an short description and when based on a github bug report
    its github id.
- developers may want to create test builds for themselves. run dev/generate_test_build.py for it.
    When doing so, DO NOT INCLUDE version.json from root, as it will update the build ID counter

----

# Changelog of snapshot 21w<46>a
Planned to be released on 17.11.2021
targeting 1.18pre1

Backwards incompatible changes:
- async system for world saves


    Library
        - requiring now python 3.10

    Rendering:
        - added block breaking overlay

    Storage:
        - using now the network serializer versions for saving block data to disk
        - this makes it incompatible with old saves, so we removed support for them
        - using now an async foundation for world saving (saves remain compatible)

    Items:
        - added ItemEntities 
        - created when breaking blocks (both the block drops and inventory drops)
        - can be dropped from player inventory & Q hotkey
        - can be picked up
        - currently do not render correct for non-block items

    Blocks:
        - candles and candle cake are now functional
        - stone cutter can now cut stone

    World generation:
        - biome features are generating again
        - added new biomes: forest, wooded hillds, flower forest
        - added basic spawn code for pillage outposts
        - added support for loading nbt structures for world generation

    Commands:
        - added /data view recipe output <item name> command displaying all recipes yielding into the set item
        - added /data view recipe using <item name> command displaying all recipes using the set item

    Inventories:
        - added a handful of util code

    Bug fixes:
        - fixed some visual glitches
        - improved inventory interaction 
        - fixed some crashes
        - fixed dessert top layer being one block too low


# Changelog of alpha 1.2.0, compared to 21w42a
Released on 22.10.2021 targeting 1.17
No further changes


# Changelog of snapshot 21w42a
Released on 20.10.2021 targeting 1.17

WARNING: this release includes a bytecode manipulation system which allows arbitrary code manipulation,
         including code outside the game's scope (You cannot reach across processes, but still...)
         This increases security risk not by much (as mods could do anything they want before that),
         but mods can do stuff which makes it hard to track down the root cause of it. 
         As by the nature of python, there is no way to prevent bad usage of the system introduced.

Backwards incompatible:
- custom block rendering
- custom block state & model loaders
- food items with custom on_eat() implementation (signature & behaviour change)


    Optimisation:
        - speed up BlockItemGenerator by a lot
        - added profiler activateable via ALT+P

    Modding:
        - Added bytecode manipulation framework
        - started adding some more abstracted-away ways to manipulate bytecode,
            but there is still a lot of stuff missing

    Blocks (and rendering):
        - added basic redstone wire block, should be MOSTLY functional
        - added tinting of blocks, including the new redstone wire and grass block
        - added chest rendering with custom block renderers
        - added shulker box renderer
        - added fluid block renderer (simple)
        - major optimisations to the rendering code of blocks
        - added a lot new blocks (Total >= 1152)

    Dedicated servers:
        - fixed some stuff, hopefully works better now

    Issues fixed:
        - Creative tab scrollbar was working the wrong way 'round
        - tool system was completely broken
        - gamemode 0 players could not break any blocks due to missing "not" in breakable condition
        - block update was invoked twice when caused directly by the player
        - factory builder's auto-copy operation was not working correctly
        - lag when crossing chunk boarders
        - furnace inventory teture was slightly wrong renderered
        - fixed gamemode 2 and 3 players not beeing able to use num keys to switch selected item

# Changelog of snapshot 21w39a
Released on 29.09.2021 targeting 1.17

Backwards incompatible:
- rendering system (events & management got reworked)
- block face solid & redstone API
- abstract interface for world


    Resource system:
        - optimised how mc source assets are linked at setup time

    Rendering:
        - allow custom rendering events to be specified & staged correctly
        - optimised some rendering parts

    States:
        - states can now optionally define a state renderer which is only init-ed on clients

    Blocks:
        - a whole lot of new blocks, including variants not in the original game
        - no detailed list arrival, see the diff of "/data view registry minecraft:block" command

    Issues fixed:
        - Chunk.remove_block with block instances
        - player /give command & API for picking up blocks
        - falling blocks could result in a crash
        - commands executed only by someone, not somewhere, would have None as position instead of the this.position


# Changelog of snapshot 21w37a
Released on 15.09.2021 targeting 1.17

Backwards compatible: mostly compatible

    Python:
        - allowing now python 3.10, as all our dependencies have upgraded their support

    Registries:
        - some work on deferred registries, and the other registry parts

    Rendering:
        - window caption contains now in dev version branch name + last commit hash

    Bug Fixes:
        - BlockItemGenerator was doing not what it was supposed to do

    Gameplay:
        - creative item search tab is now filled with items

    Capabilities:
        - implemented capability API
        - currently supports items [AbstractItem instance, not ItemStack], blocks and entities
        - can be disabled for entries in the system
        - WARNING: block & item implementation is linked to some public-facing serialization code, meaning
            mods which are not careful enough may override the needed bindings

    Blocks:
        - block serialization code (the public facing dump_data() and inject()) were rewritten, mods
            overriding these will encounter issues!

    Networking & dedicated server:
        - added more networking code, including first real packages, including:
            - handshake (both directions)
            - sync packages (package ID's, registry content, mod list)
            - disconnection packages (init & response)
        - fixed some bugs existing in the networking API

        - fixed dedicated servers doing no mod loading, no world generation, and in general acting not like
            a game instance


# Changelog of snapshot 21w35a 
Released on 01.09.2021 targeting 1.17.1

Backwards incompatible (most parts are changed):
- JVM extraction
- ModLoader discovery service
- Big refactoring


    JVM:
        - a lot smaller stuff, fixes, more integration work
        - decoupled JVM from main code into separate repository

    Mod Loader:
        - rewritten initial discovery system for mods, making it more extendable
        - mods can now provide mod loaders, finally (before, mods where to late to do stuff)
        - mod loading order is no longer stable (inside the dependencies)

    Internals:
        - a big chunk of refactoring, most mods will NOT work

    Block Item Generator:
        - some internal changes, more fail-save, will not generate as much noise when something fails, will skip
            blocks with no-rendering, but will be mostly faster

    Rendering:
        - internal optimisations for the rendering system, refactored some bits, removed unneeded stuff


# Changelog of snapshot 21w23a
Released on 9.6.2021 targeting 1.17

Mostly backwards compatibility

    Networking:
        - further work on the network system

    Event system:
        - improved internal event bus system

    Mod loader:
        - moved ExtensionPoint class to mod package [MP4-11]
        - added ModLoader extension point for JavaFML
        - mods have now a "resource_access" attribute holding the resource access of that mod

    JavaFML:
        - implement a JVM in python for loading minecraft: java edition mods
        - added transformer system for transforming java bytecode defined objects into readable code for our loader

        The following mods are known to load partially:
            - biomesoplenty, tested with 1.16.5-13.1.0.471
            - storage drawers, tested with 1.16.3-8.2.2

        Any other mod may or may not load; Implementation wrappers for parts are welcome to be PR'ed
        We cannot guarantee any mod to load as out system changes rapidly

    Storage:
        - improved storage of block palette and entities
        - improved general storage layout


# Changelog of snapshot 21w20a 
Released on 19.5.2021 targeting 21w19a

Backwards incompatibility:
- integrated mod api framework (removed)
- refactoring of some parts


    Test Framework:
        - tweaked some stuff

    Commands:
        - added /chunk delete all command
        - added /chunk dumpdatadebug [all] command

    World generation:
        - added debug helper code for dumping the map structure in image format

    Modding:
        - removed the API management system
        - added extension point for other mod loaders

    Entity Rendering:
        - some small improvements

    Toolchain:
        - imports can now be also sorted, using the isort module

    Inventories:
        - implemented creative player inventory with creative tabs [data-driven, but extension point via events]

    Networking:
        - some smaller work on network handlers


# Changelog of snapshot 21w17a
Released on 28.04.2021 targeting 21w17a

Backwards incompatibility:
- reworked how the world generates
- reworked how the world stores data maps of chunks (e.g. heightmaps)
- broke with this world loading compatibility, did not add a DataFixer for it, so old worlds cannot be
    loaded
- rewritten command system from ground
- refactored some important bits. This breaks block construction & rendering


    Commands:
        - rewritten how commands work internally
        - a lot of migrations
        - added /worldgendebug command
        - moved some commands around, removed some, added some new nodes to some

    World Generation:
        - added async world generation process
        - added access system from other processes to the current world
        - reworked how data maps of chunks are done
        - fixed world generator for debug worlds
        - added sunflower plains biome

    Fluids:
        - implemented basic fluid API, including:
            - a fluid class
            - a fluid stack
            - a fluid item container
            - a fluid block base class

    Launch options:
        - added options to disable mod loader, data pack loader, and resource pack loader
        - boosted server load cycle even more

    Build System:
        - major fixes to the system

    Rendering:
        - some fixes around rotations in block models

    Event system:
        - major improvements, including RAM usage, call times, ...
        - fixed function unsubscribing never working


# Changelog of snapshot 21w04a
Released on 27.01.2021, targeting 21w03a

backwards incompatibility:
- item factories
- crafting recipes
- behaviour changes of BlockFaceState, for better performance
- command system
- inventory system (pushed in direction of container separation)


    Commands:
        - added /blockinfo command giving information about the block currently looking at
        - added /recipeview command for below recipe view
        - /execute has now a registry-like structure for sub-nodes
        - /execute in takes now a dimension name instead of its ID
        - defined /execute var [currently not use-able]

    Rendering:
        - improved block rendering

    Server:
        - improved server separation from client

    Crafting:
        - added a screen system for displaying recipes, with extension point for mods, with plans for features
            like in JEI
        - rewritten base recipe API

    Documentation:
        - fixed documentation generation
        - updated & improved docs

    API:
        - ItemFactory is now also created by FactoryBuilder
        - this is breaking existing code, again...
        - added a new combined factory system using in-memory calculations

    Build System:
        - improved undocumented build
        - started writing a binary building API based on https://github.com/Nuitka/Nuitka

    Fixed issues:
        - escaping in logs did not work in some edge cases correctly
        - major rendering issue when updating blocks
        - recipes were not working [MAYBE]
        - some work on block state alias system [still broken :-(]
        - fixed reload issues and general issues with in-memory data propitiation not over the default interface


# Changelog of snapshot 21w01a
Released on 06.01.2021, targeting 20w51a

Happy new year, 2021!
This time, breaks again some big parts
Affected are world generation and mod loading stage modifications, and loading-order-dependent stuff, beside
following some general structure [block models after blocks, etc.]

WARNING: this version has a major visual glitch which could not be fixed until today

    API:
        If you see this, you know that something broke again...
        - Broke BlockFactory system. Nothing will work!
        - Planning on breaking ItemFactory also...
        - ... and CombinedFactories will also be rewritten in the near future
        - even data-driven block and items may get a thing :-/
        - the new factory system is highly extendable, but may consume some more memory on the fly :-(
        - I tried to make it as fast as before, but I cannot guarantee anything at this point
        - the API is "similar" to the old, with refactors and no direct-attribute accesses anymore :-/

    World Generation:
        - noises are now better selected per world-seed, making them more compatible for mods
        - general faster [see rendering stuff below]
        - modes and biomes can now be serialized to files
        - modes can now simply be modified via files
        - features are now part of the registry system [previously, they weren't]

    Rendering:
        - improved general API
        - refactored some stuff
        - improved client/server separation
        - improved some rendering parts

    Resources:
        - implemented helper code for resource groups
        - fixed some errors around loading mod resources

    Loading:
        - rewritten how loading stages are selected
        - order may change now where no dependency is
        - you can add dependencies if needed special order
        - custom loading stages are currently hard to create [internal cache must be re-calculated],
            events for existing stages are simpler
        - there might be various errors around this, it is highly experimental

    Gameplay:
        - items can now set which blocks they can break in gamemode 2

    Behind-the-scenes:
        - improved memory usage for loading event annotations
        - improved memory usage in BlockFaceState for hidden blocks

    Server:
        - added foundation for a server launcher


# Changelog of snapshot 20w51a
Released on 18.12.2020, targeting 20w51a
WARNING:  M A J O R  BREAKING VERSION!!!!
THIS VERSION CONTAINS HIGHLY BREAKING CHANGES. IT IS NOWHERE NEAR TO BEING COMPATIBLE

THIS ALSO ENDS SUPPORT FOR ALL OLD VERSIONS BEFORE THIS RELEASE

BREAKING CHANGES MAY CONTINUE UNTIL STABLE RELEASE

THIS SNAPSHOT FIXES A  L O T  OF ISSUES [partly by rewriting the parts, partly by code review]

this is nowhere near an complete list, see version.info for more, or the github logs

    refactoring:
        - refactored nearly everything..., multiple times...
        majors:
            - globals.py to mcpython/shared.py
            - logger.py to mcpython/logger.py
            - most stuff into client/, server/ or common/-folders
            - NO support for non-mcpython-prefixed imports

    deprecation:
        - removed all deprecated stuff and a little bit more

    API:
        - improved, refactored, extended APIS [nearly all]

    Utils:
        - added more util code

    Debug:
        - added more debug info
        - added an debug generator for biome distribution

    Rendering:
        - improved some bits
        - improved texture reload
        - changed rendering code for a lot of stuff

    World Storage:
        - improved overall world storage & debug information

    World gen:
        - a lot of changes, again...
        - moved world generator config in-game

    fixed issues:
        - InventoryHandler was handling some itemstack's wrong leading into itemstack's with higher stack size
        - logging was not escaping in all cases correctly
        - mods.json was not written correctly to disk
        - normal inventory slots were not drawing correctly the item in them
        - entering an world was not triggering texture reload
        - inventory textures were not reloaded correctly
        [and a lot small ones during refactoring]


# Changelog of snapshot 20w31a

    Modding:
        - MDK has now an function to change the target version
        - MDK can access now versions from an launcher instance
        - MDK is now capable of building the mod into one final zipfile

    Data Generation:
        - DataGenerator system allows now to add new data generators during data-gen-ing
        - added data generators for more stuff
        - added data generator for language files and loot tables

    Crafting:
        - improved crafting system

    Blocks:
        - added FallingBlockEntity
        - IFallingBlock is now based around an entity instead of an simple block

    Launch-Wrapper:
        - changed how the game is launching to an more modify-able way

    Events:
        - changed a lot of events

    States:
        - block states can now have parents and alias model names

    fixed issues:
        - IHorizontalOrientableBlock was behaving incorrectly

        from previous release:
            - ItemAtlas was baking some item images in some cases not correctly
            - CombinedSlabFactory was not generating block states correctly

        long term issues:
            - Entity.tick() was never called
            - command entry for blocks was not accepting air


# Changelog of a1.0.0
(excluding the changes from the snapshots below)

    Rendering:
        - added tooltip system for items with their backends at Item-class and factory methods at ItemFactory
        - improved entity model rendering code

    Modding:
        - added possibility to register an event name for execution on mod bus on reload
        - improved reload system
        - added api management system
        - added MDK system

    Gameplay:
        - blocks can now have no collision with the player

    Blocks:
        - added nether portal block

    Commands:
        - /fill command will now update blocks at the end, not at the start
        - /setblock command will now not update the block itself

    World:
        - World.get_dimension() accepts now the dimension name, not only the id

    Saves:
        - player data of saves contains now an special region for dimension stuff
        - added data fixer part for player data

    fixed issues:
        from previous snapshot:
            - alpha rendering for blocks was broken
            - RenderingHelper's alpha on/off functions were not working

        from development versions for a1.1.0:
            - EntityModelGenerator was not parsing states correctly (20w24a)

        long-term issues:
            - block model rendering was in some cases not rendering correctly
                -> some fence & wall faces were rendering without texture
            - Chunk deserializer was not setting chunks properties properly leading into not rendering entities


# Changelog of snapshot 20w28a 
Released on 08.07.2020 (theme: fixing stuff & upgrading base to 1.16)

updated resources to 1.16 and added (some) content of the update

    Rendering:
        - improved rendering system by using MatrixStack's and RenderingHelper-instances
        - changed how item textures are baked together
        - added button to delete world in world selection screen

    World Format:
        - improved data fixer system

    Gameplay:
        - SHIFT-drag support in inventories

    Commands:
        - improved command handling
        - added /execute in <dimension id> sub-command
        - /teleport allows now the player to also change dimension

    Data Gen:
        - deprecated old AdvancedBlockFactory system
        - added CombinedBlockFactory system for doing fancy stuff with data gen & in-game objects at ones
        - added --enable-all-blocks runtime flag for enabling all optional blocks

    Profiler:
        - added profiler for world generation

    Registries:
        - registries get now "locked" after mod loading finished (they are still write-able, but this will get removed in
            the future as it will get replaced by reload-registries-events)

    World Generation:
        - implemented base generator for the nether

    fixed issues:
        from previous snapshot:
            - ordering of world selection list was wrong
            - world selection screen was not rendering all possible worlds
            - ShiftContainer was miss-behaving in certain cases
            - registry info was not dumping data correctly
            - exceptions when no save file exists
            - data fixer results may not be saved correctly
            - exception when world selection screen is empty
            - world selection screen was parsing name incorrectly

        long-term issues:
            - rendering helper was miss-doing some stuff
            - debug world was displaying some block states more than one time
            - exceptions were printed into log when loading an saved debug world
            - .setGlobalModName() on ItemFactory did not work correctly
            - ItemAtlas was crashing on missing texture file instead of replacing with missingtexture.png
            - ItemFactory's template system was broken
            - changing dimension did not work in a lot of cases

# Changelog of snapshot 20w25a 
Released on 18.06.2020 (theme: data fixers and API improvements)

    Rendering:
        - added state part serializer for progress bar
        - generation screens
        - implemented world list with selection. Moved world name enter into world generation settings screen
        - added UI element for scroll bars

    Saves:
        - rewritten data fixer system. Incompatible with old one. Old stuff still arrival, but deprecated
        - old worlds are still load-able as data-fixers were ported

    Console:
        - improved loading
        - changed some logging systems

    Commands:
        - added /shuffledata command for shuffling recipes & loot table outputs with other ones
            (must be activated in config files)

    Modding:
        - added data gen system for textures
        - changed order of loading stages to be more functional

    Loot tables:
        - implemented two new loot table conditions: minecraft:block_state_property and minecraft:damage_source_properties

    Entity API:
        - added DamageSource class

    fixed issues:
        long-term issues:
            - crafting output slot was added to inventory
            - loading bars of mod loading where not in the middle
            - % in world gen / load screen was calculated wrong leading into negative %
            - crafting slot could get saved when closing the game

        since last snapshot:
            - generator for recipe generator was not parsing output correctly leading into errors in the recipes


# Changelog of snapshot 20w24a 
Released on 10.06.2020 (theme: refactoring & data generators)

WARNING: this snapshot WILL break some backward-compatibility as it moved a lot of stuff around. Use the constants
    in globals.py for allocation.
WARNING: this snapshot adds data generators. They are useful, but currently complicated to set up. We will add
    in the future an mdk generator script for setting up an mdk package with all run-configurations,
    launcher bindings and useful helper scripts like building it into an final zip file
WARNING: this snapshot changed the way how the dev-environment is packaged. This may lead into problems
WARNING: this snapshot changed the way how final end-user directories look like and what can be modified,
    See globals.py for the locations, do NOT use G.local+"/build/[...]", use G.build+"/[...]"!!!!
WARNING: as data generators are now an thing, you can NOT rely on that your game will load up completely as an mod.
    There is the extreme "--data-gen --exit-after-data-gen --no-window" mode in which no window will open
    (and as so now draw-events or user interactions are called, only ticks) and the game will exit after the
        data gen is finished (via an extra loading stage)

    Tool Chain:
        - added system to build the project into one stand-alone zip-archive

    Modding:
        - changed version tuple builder for mcpython
        - added data generator system, moved a lot of internal stuff to there, mods are free to use it
        - data generators are arrival for BlockModel's, BlockState's, EntityModel's, Recipes and Tags
        - as the data gen system exists, the old factories for data-gen-converted stuff are now deprecated and will be
            removed until a1.5.0

    Debugging:
        - added profiler system with config options
        - made inventory interaction subscriptions more fail-self

    Project Structure:
        - refactored most of the stuff into the mcypthon-folder, but the folder itself is added to sys.path for backward
            compatibility [WARNING: this is an breaking change!!!!!!!!]
        - refactored much not-code related files into the home-folder
        - refactored & unpacked assets into the resources-folder
        - moved crafting-folder to gui/crafting, old interfaces still exists, but are deprecated

    Execution:
        - added the following command line arguments: --data-gen. --exit-after-data-gen and --no-window.
            First will generate the data (the data gen for the core will only work in dev-environment), second will
            auto-exit the game when data-gen is finished (needs --data-gen also) and last will not open an window.

    fixed issues:
        long-term issues:
            - barrel rotation was not saved
            - shift-clicking the output-slot of the crafting gave an exception
            - closing the crafting table was deleting all items which were in the crafting grid

        from previous snapshot:
            - dicts in config file failed to load
            - booleans where not correctly loaded


# Changelog of snapshot 20w22a 
Released on 30.05.2020 (theme: feature cleanup & improvements)

    Rendering:
        - optimized block rendering
        - re-ordered some UV-related stuff, you may want to update your own models

    Modding:
        - improved dependency system for mods
        - added config system for mods & internals [incompatible with mc config files]

    Factories:
        - improved existing factories & added some more factories & entries

    Logging:
        - improved exception handling

    States:
        - added StateConfigFile.py handling State-config-files

    - deprecated a lot of stuff

    fixed issues:
        from versions before this snapshot:
            - block updates were not called in every case
            - walls and fences were not updating their state correctly
            - during printing an exception, an new exception could occur
            - event "worldgen:chunk:finished" was not called in most cases
            - data packs may not get unloaded when they needed to

# Changelog of release alpha 1.0.1
    fixed bugs:
        from previous release:
            - fixed crash on startup
            - when loading a world from an never save version, the game gives out an exception


# Changelog of release alpha 1.0.0
(theme: bug fixing & system improvements)

during developing more features, the developer has decided to discard the progress. As some more difficulties had
occurred [Covid-19], the development time for these dev-cycle was far longer than expected.

    Event-system:
        - resize-event is called after every state switch now
        - improved mod loading stage calling
        - new loading events: "stage:block:factory:finish" and "stage:item:factory:finish"
        - changed signature of on_shift_click(x, y, button, modifiers, player) of slot to
          (slot, x, y, button, modifiers, player)

    Code optimisations:
        - refactored ModLoader-class & optimized some loading systems

    Mod loading:
        - added new mod.json file version
        - added @globals.modloader(<modname>, <eventname>, [<info>]) annotation

    Launch flags:
        - added --fullscreen -flag for enabling fullscreen on startup [unstable at the moment]

    Error handling:
        - improved error message when world save not found on load
        - improved exception handling by logger

    World generation:
        - improved world gen, rewritten how tasks are stored & scheduled (!)

    Tags:
        - removed tag #minecraft:furnace_fuel and replaced by an hasattr(item, "FUEL") check

    fixed bugs:
        long-time issues:
            - state of block may not be set correctly in some cases
            - memory leaks all over the place
            - offhand slot gets cleared when closing inventory
            - crash when build-folder was deleted
            - exceptions when using show-tasks in world gen arrays
            - a lot of normal fuels were not accepted by furnace as fuels


# Changelog of snapshot 20w14a

    Events:
        - added new event: "stage:blockitemfactory:finish"
        - changed some internal inventory interaction things
        - added loading phase for entities

    code improvements:
        - cleaned up base classes for block and item
        - moved Entity-class into entity/Entity.py

    Save files:
        - chunk entries containing positions are mostly stored relative to the chunk decreasing save file size
        - added saves for entities

    GUI interaction:
        - rewritten mouse interaction system to support dragging over more than one slot & better shift-clicking
        - on_shift_click can now return True when it should interrupt the following logic
        - slots can now handle an key press

    Entity system:
        - entities are now saved in saves
        - added EntityHandler with entity-registry
        - made function draw and tick called of entity
        - added EntityRenderer with parser of model files
        - added renderer for player
        - added player skins based on the player name downloaded from the official mojang servers

    Commands:
        - added /summon command

    fixed bugs:
        long-time issues:
            - internal mouse-position error when dragging [since introduction of mouse position entry]

        since introduction of game rules:
            - block-looking-at position lable was inverted to the gamerule

        since introductions of inventories to saves:
            - game gives out exceptions when trying to load an non-existing world
            - crash when inventory slot count decreases between two loads of an world


# Changelog of snapshot 20w12b 
Released on 21.03.2020

    Dimensions:
        - added dimension definition for nether and end

    Mod system:
        - removed deprecated loading phases
        - removed features.py as it was outdated

    World saves:
        - world is now saved when window is closed (only when in the state)

    Blocks:
        - added mycelium block, podzol block, barrier block
        - BlockFactory accepts now also an state-str like in block-state-files in setDefaultModelState

    Items:
        - added barrier item

    Language:
        - .lang files can now be also loaded

    Rendering:
        - added support for uv rotation in element of block-models

    fixed bugs:
        since Registry-update II:
            - Chunk.add_block did NOT accept the non-prefixed block-names like "stone"

        long-time issues:
            - icon for half hunger was not rendered correctly
            - BlockItemFactory failed to load block-items when not rebuilding for new blocks since last rebuild. This
                occured only in first run due to missing _finish call of ItemFactory-instances

        model system issues:
            - rotation of BlockModels was not working
            - multipart models failed to load when an entry had an list of models


# Changelog of snapshot 20w12a
Released on 16.03.2020

    Loot tables:
        - added class for LootTable, added sub-classes for generating the content
        - added base classes for loot table function and conditions

    Mod system:
        - added loading phase for adding loot tables

    Blocks:
        - added drops to blocks
        - added option to chest to load loot table into the inventory
        - added starter chest

    Commands:
        - added /loot command

    Rendering:
        - added loader for OpenGL-only scripts (stored in .gl files, loader under rendering/OpenGLSetupFile.py)
        - alpha blending has now disabled cull face in OpenGL to render also back-faces to user

    fixed bugs:
        model system issues:
            - rendering of multi-part models with OR condition fails due to wrong condition check
            - rendering of some blocks failed
            - custom block renderers were not working as expected

        long-term issues:
            - items in hotbar do not render in some cases
            - open inventory list of InventoryHandler gets reversed every ESC-press
            - shift crafting was duplicating output


# Changelog of snapshot 20w11a 
Released on 12.03.2020

    Rendering:
        - re-added support for custom block renderers
        - added support for OR-condition in block-states
        - block-states act when selecting from multiple models better
        - block models can now rotate themselves
        - improved block-showing performance by caching (rotated) vertices and texture data
          [this affects also world gen time]

    World generation
        - tweaked generation system to look faster (and be faster)
        - world generation is now done parallel across up to 5 chunks [not thread-parallel]
        - added an world-generation progress-view screen like in MC

    Config:
        - added config for height of world [used in BiomePlains to calculate the height map range]
        - added config for how far the world is generated when you are in-game, default is 1 chunk in each direction

    World saves:
        - added system for storage of worlds with serializers and data fixers [data fixers are unused at the moment]
        - added option to inventories and blocks to add custom data to save with it (items had such an function before)
        - added save-access-screen, save-loading screen

    Mod system:
        - mod versions should be now tuple instead of any-type
        - rewritten version compare system to be based on tuples (work with lower and upper bound for versions)

    Entities:
        - improved entity API

    Code improvements:
        - renamed some stuff to better match
        - moved player instances to World.players
        - player interaction methods now include also the player instance itself

    fixed bugs:
        command issues:
            - /generate <cx> <cz>-command was not working
            - block entries in commands were requiring the mod-prefix

        long-term issues:
            - seed was ignored by generation system
                -> noises for world gen were NOT based on world seed
                    [noticeable when loading an world and generating new chunks]

        rendering issues:
            - slabs were rendered upside-down
            - carved pumpkin item was the same as pumpkin

        - unbreakable blocks could be broken in gamemode 0


# Changelog of snapshot 20w10a 
Released on 04.03.2020

    Internals:
        - updated libraries

    Datapacks:
        - added datapack support

    Commands:
        - added gamerules
        - new commands: /clone, /tell, /replaceitem, /gamerule

    Rendering:
        - added multipart-block-model support
        - added generator code for creating BoundingBox from BlockState
        - BoxModels will now rotate properly relative to middle of block, not only changing textures

    Blocks:
        - added new blocks: fences, walls

    Events:
        - TickHandler has now an function to tick an function as fast as possible

    Config:
        - added option for fog distance

    fixed bugs:
        long-term issues:
            - various exceptions from left-over things in the registry & slot changes from last snapshot
            - various issues with slot drawing

        - fixed exception on shift-clicking crafting output of main inventory


# Changelog of snapshot 20w09a 
Released on 26.02.2020

    Rendering:
        - changed TextureAtlas-block-addition system to be based on mod-based/texture size-based atlases
        - USE_MISSING_TEXTURES_ON_MISS_TEXTURE config option is now False by default

    Blocks:
        - new blocks: furnace with inventory & crafting, barrel, ice variants, bone block, book shelf, coral blocks,
                      pumpkin, carved pumpkin, melon, clay, coarse dirt, prismarin blocks, dried kelp block, end stones,
                      glowstone, magma block, mossy stone bricks, nether bricks, nether wart block, netherrack,
                      purpur blocks, quartz slab, red nether bricks, smooth quartz slab, soul sand
        - Block-class has now an CUSTOM_WALING_SPEED_MULTIPLIER-attribute used for custom waling speeds ontop of blocks

    Inventory Interaction:
        - added key "E" to close various inventories

    Mod system:
        - changed mod.json format to have an "version"-attribute & an "loader"-attribute

    Code improvements:
        - changed some get_name-methods to NAME-attribute
        - removed some deprecated things

    Events:
        - changed how things are registered, THIS IS AN BRAKING CHANGE!

    fixed bugs:
        command issues:
            - game crashes when using "/tp <position>"-command

        rendering issues:
            - debug world doesn't use the block state definition correctly [This issue appeared very often down the road]
            - some chest textures were not drawn correct

        interaction issues:
            - can't get items out of an tag-handled slot
            - cobblestone was not arrival

        mod loading issue_
            - crash when not arrival python file is linked from mod.json file
            - crash when block-name-prefix is no mod-prefix
            - crash when model-name-prefix is no mod-prefix

# Changelog of snapshot 20w07a 
Released on 10.02.2020

based on: rendering update branch 1 & changes to master-branch

    Rendering:
        - block textures are now cut out to squares making animated textures load only the first texture, but not the
          whole
        - rendering support for "uv" coordinates
        - TextureAtlas will now resize automatically to new size if needed
        - changes the way how html characters are escaped in chat
        - changed the way how block faces are stored
        - removed custom block renderers for the moment
        - blocks are now rendered face-by-face instead of all faces at ones

    Config:
        - inventory config has now an option to offset the background
        - added config for USE_MISSING_TEXTURES_ON_MISS_TEXTURE

    Resource handling:
        - ResourceLocator.add_resources_by_modname's directory parameter is now optional
        - ResourceLocator.add_resources_by_modname will now also load tags

    Blocks:
        - added new blocks: brick slab, glass, stained glass, carpets, sandstone
        - added grass <-> dirt convert

    logging:
        - log contains now some os-specific information
        - crashes on mod bus do not crash the game any more

    Screen Info:
        - added some memory & cpu usage information

    Special keys:
        - added hot-keys: F3+A, F3+C, F3+C for 10s, F3+D, F3+I, F3+N and F3+T

    fixed bugs:
        mod system issues:
            - exceptions when trying to load recipes from an namespace with sub-recipe-folders
            - models in sub-directories where not loadable
            - on_remove function was not called correctly when an block was removed

        event issues:
            - fixed random updates
            - block inventories were not closed when block holding the inventory was removed
            - mouse button up is in some cases not handled correctly
            - closing crafting tables could duplicate output
            - when braking an chest, items were deleted

        rendering issues:
            - some textures were blurry
            - info label in-game were drawn offset in resized windows
            - chat was in some cases not displaying text correctly

        - various crashes & exceptions in log

# Changelog of snapshot 20w05a 
Released on 01.02.2020

based on: cleanup-branch version 1 [merged on 01.02.2020 onto master]
- updated textures to 1.15.2
- upgraded libraries


    informal:
        - added an file called "events.list" storing every event ever called

    Events:
        - added loading event called "stage:block:block_config" called to register block config entries
        - add new events: "command:clear:start", "command:clear:end", "command:give:start", "command:give:end",
                      "command:help:generate_pages", "command:parse_bridge:setup", "command:execute_command",
                      "command:registryinfo:parse", "chat:text_enter", "inventory:show", "modloader:mod_found",
                      "itemhandler:build:atlases:save", "itemhandler:build:atlases:load", "state:switch:pre",
                      "state:switch:post", "modelhandler:searched", "worldgen:chunk:finished", "player:die",
                      "world:reset_config", "dimension:chane:pre", "dimension:chane:post", "world:clean", "game:close",
                      "resources:load", "resources:close"
        - deprecated call_until_equal, call_until_getting_value and call_until_not_equal of EventBus, use call_until
          instead
        - added instant_ticks-attribute to TickHandler
        - added system to check if prebuilding was interrupted before in which case prebuilding would activate again

    Rendering:
        - split up ICustomBlockRenderer into IStaticCustomBlockRenderer and IObjectedCustomBlockRenderer
        - added real config background
        - chat accepts now the DELETE key, the END key and the BEGIN key

    Startup flags:
        - added new run option: --debug-world which sets the world generator to debug

    logging:
        - added logger system
        - better exception handling

    code improvements:
        - moved some project file

    - fixed bugs:
        rendering issues:
            - loading bar was offset
            - game was crashing when hovering over an button
            - chat was "open" until first opening

        world generation issues:
            - debug world generator was not working
            - chests & ender chests were not working in debug world
            - chat marker for active writing position was not correct drawn
            - chat was doing bad stuff with strings like "&#38;"

        - raw crash in BlockItemGenerator
        - possible infinite loop in deleting directories when files where opened
        - mod list storage was not correctly saved

todo: add an changelog for past version(s)

