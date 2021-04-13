from mcpython.server.command.Builder import (
    Command,
    CommandNode,
    Selector,
)
from mcpython import shared


def clear(entities):
    for entity in entities:
        for inventory in entity.get_inventories():
            inventory.clear()
        entity.on_inventory_cleared()


setblock = (
    Command("clear")
    .than(
        CommandNode(Selector())
        .of_name("target")
        .on_execution(lambda env, data: clear(data[1](env)))
        .info("clears the inventory of all entities of target")
    )
    .on_execution(lambda env, data: clear((env.get_this(),)))
    .info("Clears the inventory of the executing entity")
)

shared.command_parser.register_command(setblock)
