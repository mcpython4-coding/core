import typing
from abc import ABC


class ITagTarget(ABC):
    TAGS: typing.List[str] = []


