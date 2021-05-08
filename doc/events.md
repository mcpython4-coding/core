# Event System

---

The event system is split into two major phases, the loading phase and the gameloop phase.

Loading phase events are called on the individual mod event buses, located under [mod instance].eventbus,
reachable also via the annotation @shared.modloader([mod name], [event name]).

The other events are called on the event handler, shared.eventhandler. You may use your own event bus instance
created for the event handler or use the public one, located under
mcpython/common/event/EventHandler.py/PUBLIC_EVENT_BUS

---

The following events are part of the gameloop phase
-

Disclaimer: the events are currently WIP and may change at any point

Disclaimer: during this phase of transition, not all events may be listed here

---

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
    In the moment the event is invoked
  
- minecraft:modloader:missing_dependency(event cancel, mod loader instance, mod instance, dependency)
  
    Called by ModLoader when a mod is missing a dependency. Canceling will ignore the error

- minecraft:modloader:incompatible_mod(event cancel, mod loader instance, mod instance, dependency)
  
    Called by ModLoader when a mod is incompatible with a provided mod. Canceling will ignore the error

