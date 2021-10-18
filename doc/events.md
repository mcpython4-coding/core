# Event System

---

The event system is split into two major phases, the loading phase and the gameloop phase.

Loading phase events are called on the individual mod event buses, located under [mod instance].eventbus,
reachable also via the annotation @shared.modloader([mod name], [event name]).

The other events are called on the event handler, shared.eventhandler. You may use your own event bus instance
created for the event handler or use the public one, located under
mcpython/common/event/EventHandler.py/PUBLIC_EVENT_BUS

---

# The following events are part of the gameloop phase


Disclaimer: the events are currently WIP and may change at any point

Disclaimer: during this phase of transition, not all events may be listed here

---

## Game loading

- minecraft:game:startup()
  
    Invoked by the LaunchWrapper after setup() is finished

- minecraft:game:gameloop_startup()

    Invoked directly above the pyglet.app.run() method call by LaunchWrapper

- minecraft:modloader:location_lookup_complete(mod loader instance, mod location list)
  
    Called by ModLoader when look_out(True) is called. It is intended for modifying the passed location list.
    As lists are mutable, subscribers can simply modify the list
  
- minecraft:modloader:mod_selection_complete(mod loader instance, mod name -> mod instance)
  
    Called by ModLoader when look_out() is called, later than minecraft:modloader:location_lookup_complete.
    It comes with the final mod mapping, and has parsed all arguments & locations at this point.
    It is followed by a lookup of the past mods, to look out for mod changes and potential needed setups.
  
- minecraft:modloader:mod_change(event cancel, mod loader instance, mod name, mod instance)
    
    Called by ModLoader when check_for_update() is called. It indicates that the given mod was updated/removed.
    Used only for informal reasons. You can still undo some changes made before this function, including de-activating
    the rebuild state, by canceling the event
  
- minecraft:modloader:mod_addition(event cancel, mod loader instance, mod name, mod instance)
    
    Called by ModLoader when check_for_update() is called. It indicates that the given mod was not present before.
    Used only for informal reasons. You can still undo some changes made before this function, including de-activating
    the rebuild state, by canceling the event
  
- minecraft:mod_loader:duplicated_mod_found(mod loader instance, mod instance)

    Called by ModLoader when a duplicated mod was found; Can be used for canceling the duplication found.
    Keep in mind that it is called only since the first occurs, and the mod is removed from the loading system
    At the moment the event is invoked
  
- minecraft:modloader:missing_dependency(event cancel, mod loader instance, mod instance, dependency)
  
    Called by ModLoader when a mod is missing a dependency. Canceling will ignore the error

- minecraft:modloader:incompatible_mod(event cancel, mod loader instance, mod instance, dependency)
  
    Called by ModLoader when a mod is incompatible with a provided mod. Canceling will ignore the error


## Resource Loading

- minecraft:model_handler:searched() [client-only]

    Invoked by the ModelHandler when model lookup has been completed

- minecraft:data:blockstates:custom_injection() and minecraft:data:models:custom_injection() [client-only]

    Invoked by ModelHandler when it is time to inject the respective stuff into the system

- minecraft:textures:atlas:build(TextureAtlasGenerator) [client-only]

    Invoked by the TextureAtlasGenerator when it is about to start its baking process. Can be used to inject custom
    textures or modify existing ones.

- minecraft:data:shuffle:all() 

    Invoked when it is time to shuffle the data for fun.


## Networking

- minecraft:modlist:sync:setup(Server2ClientHandshake, modlist: list) [server-only]

    Invoked when the server prepares to send the mod list to the client. Can be used for modifications.

- minecraft:network:registry_sync:setup(RegistrySyncInitPackage) [client-only]

    Invoked by the RegistrySyncInitPackage when setup() is invoked. In normal lifecycle, invoked only on the 
    client. 

- minecraft:network:registry_sync:init(RegistrySyncInitPackage) [server-only]

    Invoked by the RegistrySyncInitPackage when the corresponding package is handled. Can be used to request custom
    registries from the client side.

- minecraft:network:registry_sync:setup(RegistrySyncPackage) [sever-only]

    Invoked during package construction on the server. Intended for modification of the list to send to the server.

- minecraft:network:registry_sync:data_recv(RegistrySyncPackage, here: set, there: set) [client-only]
    
    Invoked by the RegistrySyncPackage when data is scheduled for comparison. Intended for modifying the registry
    content in the local copies of the registry contents.

- minecraft:network:registry_sync:fail(event cancel, RegistrySyncPackage, here: set, there: set) [client-only]

    Event invoked when registration sync of a specific registry failed. Can be canceled for ignoring the error 
    and sending the confirmation package back to the client.

- minecraft:network:registry_sync:success(event cancel, RegistrySyncResultPackage) [client-only]

    Marks the success of registry sync. May be canceled when you want to cancel the connection.
    In that case you need to print your own error message.

- minecraft:network:registry_sync:fail(RegistrySyncResultPackage) [client-only]
  
    The other event beside the one above. Invoked when sync failed naturally, meaning canceling above will 
    skip this call. Cannot enforce connection when you want to connect, but cannot. Use above events for 
    the specific registries when wanting to skip certain verifications.

## Rendering

- minecraft:inventory:show(Inventory) and minecraft:inventory:hide(Inventory) [client-only]

    Invoked by ContainerManager when showing/hiding inventories

