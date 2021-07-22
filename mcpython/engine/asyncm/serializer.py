import marshal
import types


GLOBAL = globals()

exec("""
import time, os, asyncio
""", GLOBAL)


def serialize_task(function, args, kwargs, meta=None):
    return marshal.dumps(function.__code__), args, kwargs, meta


def deserialize_task(data):
    return (types.FunctionType(marshal.loads(data[0]), GLOBAL),) + data[1:]

