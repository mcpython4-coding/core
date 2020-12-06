import enum
import typing


def onlyInClient() -> typing.Callable:
    return lambda a: a

