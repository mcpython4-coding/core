

Issues:
- non-stable generation seed across sessions, but stable in a session ("[WARN] seed map is empty!" is printed out)
- world generation progress is not displayed
- biome map is not saved to save files or loaded not correctly somehow


Pending for next non-snapshot release:
- issues above
- fix gamemode 0 (partially done)
- more unit tests


Toolchain:
- user_config.json storing local information across versions, like:
    - path to launcher
    - user name
    - path to mc asset folder / archive
- installer .jar file linking in the installation.json file instead of extraction

- obfuscator
- System to dynamically migrate code from deobf <-> obf and up versions [only simple changes]

- Better custom LaunchWrapper use system [in progress]
- PyCharm launch Configuration setup handler for dev env and mdk

Library backend:
- upgrade to pyglet 2.0 [For consideration]

Data generation:
- attribute for data generator instances for name, so we don't need to set it at submitting, but in advance

Block Item Generator:
- improve, cleanup, prepare for removal & export to in-inventory rendering [in progress]
- add flag to each release for enabling cache invalidation when upgrading

Data driver:
- item, block, implementation for the other recipes

UI:
- system to create your own WorldGenerationMode, which is dumped to a save-based file
- registry view UI
- config UI
- mod list UI

dedicated servers:
- split state system into two parts: the handling part and the visual part
    (so we can split of the visual part into client-only)
- split gui system into rendering & container

Test System:
The test system is a external tool developed along the game sitting on top of it. It uses
a) The python import system, for loading single files and providing dummy files
b) The custom LaunchWrapper system, for launching the game in-code
c) The modding system, for injecting code into the game without needing LaunchWrapper directly
    [This can be used after with b) the LaunchWrapper is known-good]
    It would communicate via socket with the test process

Split into 4 parts:
- Unit tests: general functional tests
- Launch tests: tests executed during loading the game [registry injection tests, loading event tests, ...]
- User interaction tests: simulation of user input over the event system
- In-game tests: tests executed in-game automatically [see mc test framework], using structures and interaction paths
    for game behaviour, can be mixed with user interaction tests


FML
- make the exception screen scrollable
- load JavaFML only when needed (e.g. via a flag, maybe --enable-fml)
- implement all of the instructions
- runtime mod reload
- an attachable debugger for certain functions / opcode regions with ui [maybe in second window?]
- a bytecode viewer for debugging single instructions [in-game, via some callback and continue system]
- jvm exception handling [currently not implemented]

