
[issue 1-8 are part of github-only and are mostly fixed at the moment]


- issue 28: [caused by issue 185]
    - bug: F3+A - hot-key does not reload the world correctly
    - since: unknown, found after fixing issue 19 & implementing hot-keys
    - possible fix: rewrite this part of the method of the Chunk-class

- issue 34:
    - bug: jumping from downwards into a block, you get damage
    - since: block damage was introduced
    - fix: rewrite collision system & check for overlap value

- issue 35:
    - bug: going inside a non-full block will give you damage instead of bouncing of the block (e.g. glass)
    - since: block damage was introduced
    - fix: check for solid block
    - better fix: use rewritten collision system based on AABB's to determine if you are in an block or not

- issue 55:
    - bug: alpha textures are not rendered behind alpha-textures
    - since: alpha rendering was implemented
    - fix: order alpha face rendering! (maybe implement an AlphaRenderingRenderer extends ICustomDrawRenderer)

- issue 80:
    - bug: in some cases, mouse button up is still not handled
    - fix: call mouse button up event before changing the active state only on the event bus for it

- issue 113:
    - bug: "uv-lock"-parameter is ignored in block-states
    - fix: implement [see https://minecraft.gamepedia.com/Model]

- issue 118:
    - bug: block models ignore rescale parameter in elements
    - fix: implement [see https://minecraft.gamepedia.com/Model]

- issue 122:
    - bug: z-fighting at border between two fences
    - possible fix: decrease box size of fences "by hand" (manipulate model data)

- issue 139:
    - bug: during in-game generation, block faces of neighbor chunks are not updated
    - possible fix: update all blocks next to the new chunk OR remove the hide-faces in not generated chunks

- issue 140:
  - bug: (sometimes, )you fall through one or more block (in gamemode 0)
  - reproduce: use e.g. diamond pickaxe and break stone blocks until bottom of world in gamemode 0

- issue 157:
    - bug: loading hangs before showing the chunk loading screen due to deserialization times
    - fix: add color indicating that the deserialization is in progress

- issue 159:
    - bug: various maps are stored not chunk-relative making file size big at outer positions
    - fix: implement relative-storage

- issue 161:
    - bug: when saving, moving slot is not saved
    - fix: like in kill-method, force-close all inventories on save
    - other fix: save moving slot also & load it [warning: also save what inventories are open]

- issue 164:
    - bug: saving/loading big worlds take long time
    - fix: do NOT load every time the whole .region file, store it in RAM [we have enough of it]
    - additional fix: load them part by part
    - 3rd fix: move to other process

- issue 165:
    - bug: changing chunks in a big world takes a long time due to internal re-calculations
    - fix: see issue 164

- issue 168:
    - bug: when starting in-game generation, game hangs for a moment
    - fix: make generation off-thread

- issue 175:
    - bug: structures overlapping into not-generated chunks are not shown when the chunks respecify are generated
    - fix: add a special list of pre-generated blocks which is injected into actual generation task array when the chunk
           generation is requested

- issue 176:
    - bug: structures overlapping into not-generated chunks are not saved (?)
    - fix: see issue 175

- issue 177:
    - bug: grass block faces generated next to leaves are not visible
    - possible cause: wrong is_solid calculation?

- issue 178:
    - bug: hotbar is not transparent(rendered)
    - fix: enable alpha blending in this phase [somehow not correctly working!]

- issue 185:
    - bug: in big worlds, chunks can get randomly hidden (or unloaded?) [e.g. debug world]
    - fix: implement chunk load ticket system [WIP]
    - root cause search: implement logger for unloading & hiding chunks
    - temporary fix: prevented from unloading [for some short moment, they get unloaded]

- issue 196:
    - bug: when in gui and picking up an itemstack during holding one, it gets reset
    - reproduce: craft one thing with an item in mouse and the item is not picked up

- issue 199:
    - bug: dynamic generated dimension ids are not saved in saves leading into miss-matches when changing dimension list
    - fix: add them to the storage system and re-assign on load

[1001]