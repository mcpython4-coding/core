asyncio is part of python since python 3.4.

It is a framework for running tasks semi-parallel with the async def / await syntax

In this syntax, each task is defined via async def <...>.
The task is for execution scheduled to the main event loop, and executed.
When the task is await-ing another task, it is interrupted and another task may get executed,
until the awaited task is finished.

This can be used for multiprocessing-world-generation, to await access to other processes data
(like existing world data).