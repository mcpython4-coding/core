import asyncio
import typing
from functools import partial, wraps
import os
import zipfile


def wrap(func):
    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)

    return run


class AsyncZipfile:
    def __init__(self):
        self.__underlying: typing.Optional[zipfile.ZipFile] = None

    def load_from_file(self, file: str):
        self.__underlying = zipfile.ZipFile(file)

