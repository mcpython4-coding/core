

Features scheduled for implementation for alpha 1.3.0, [planned to be released sometime in december 2021]
- abstraction of direct rendering calls to some higher level (-> pyglet 2.0 preparations)
- reload data only when needed, so a resource pack / data pack change occurred
- split gui system into rendering & container
- add ore gen
- refactor event names
- moved tool system to tags (see mc)
- do not read inventory config for each inventory, load it ones & share


Animated textures:
- New atlases for textures with animation, where for each frame a new one is created, so we can switch between them 
each rendering frame (So, for each frame count & timing, a new one is needed)
- WARNING: for that to work, we need to add a way for block models to prevent optimisation for mass-addition 
    as animated textures need their own texture atlas & group, not the same as the normals


Issues:
- biome map is not saved to save files or loaded not correctly somehow
- hiding faces to rotated blocks like logs fails
- shift-clicking and shift-moving over slots does not move the items to "the other" area of the inventory
- tools are consumed when right-clicking on a block
- you can create ItemStacks with more than allowed items by combining two item stacks
- you can fall through blocks when digging down


Toolchain:
- user_config.json storing local information across versions, like:
    - path to launcher
    - username

- Better custom LaunchWrapper use system [in progress]
- PyCharm launch Configuration setup handler for dev env and mdk
- create docker files of the project during building
- add a mode where the window opens only when the load is complete
- add a mode where a world is directly loaded and then displayed (combine-able with above)

Library backend:
- upgrade to pyglet 2.0 [For consideration]

Blocks:
- add anvil UI
- fluid system around blocks should provide a way to customize 
a) Fluid bucket name (on FluidBlock)
b) Fluid block name (on Bucket)
c) events for above @ Fluid class
- real stairs
- collision detection based on physic bounding boxes

Data generation:
- attribute for data generator instances for name, so we don't need to set it at submitting, but in advance

Block Item Generator:
- improve, cleanup, prepare for removal & export to in-inventory rendering [in progress]
- add flag to each release for enabling cache invalidation when upgrading

Data driver:
- implementation for the other recipes
- add data-driven factory system
- move more game logic to tags
- add scoreboards with commands, execute command entry, ...
- parser for the new mc world gen config format
- add TranslationComponent-class supported by buttons, labels, ... to dynamic cache the translation
- make loot table system only load needed loot tables, etc.

UI:
- system for the end user to create your own WorldGenerationMode, which is dumped to a save-based file
- registry view UI
- config UI
- mod list UI
- some style information for UI elements (dark mode, round edges, ...)
-> Round button corners & colors
-> World selection list round white outline 

Test System:
The test system is an external tool developed along the game sitting on top of it. It uses
a) The python import system, for loading single files and providing dummy files
b) The custom LaunchWrapper system, for launching the game in-code
c) The modding system, for injecting code into the game without needing LaunchWrapper directly
    [This can be used after with b) the LaunchWrapper is known-good]
    It would communicate via socket with the test process

Split into 2 parts:
- Unit tests: general functional tests [created]
- In-Game tests, either:
  - User interaction tests: simulation of user input over the event system
  - In-game tests: tests executed in-game automatically [see mc test framework], using structures and interaction paths
      for game behaviour, can be mixed with user interaction tests

