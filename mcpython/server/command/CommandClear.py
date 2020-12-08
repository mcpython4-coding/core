from mcpython.server.command.CommandBuilder import (
    ICommandMatcher,
    CommandBuilder,
    ExecutingCommandInfo,
    SelectorMatcher,
)


def execute_clear(
    matcher: ICommandMatcher,
    builder: CommandBuilder,
    context: ExecutingCommandInfo,
    tree,
):
    this = context.entity
    if isinstance(matcher, SelectorMatcher):
        this = matcher.entity

    this.clear_inventory()


clear = (
    CommandBuilder("clear")
    .add_subsequent_stage(
        SelectorMatcher(
            allowed_entity_tags=["#minecraft:player_like"], max_entity_count=1
        ).execute_on_end(execute_clear)
    )
    .execute_on_end(execute_clear)
)
