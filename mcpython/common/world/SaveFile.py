"""
mcpython - a minecraft clone written in python licenced under the MIT-licence 
(https://github.com/mcpython4-coding/core)

Contributors: uuk, xkcdjerry (inactive)

Based on the game of fogleman (https://github.com/fogleman/Minecraft), licenced under the MIT-licence
Original game "minecraft" by Mojang Studios (www.minecraft.net), licenced under the EULA
(https://account.mojang.com/documents/minecraft_eula)
Mod loader inspired by "Minecraft Forge" (https://github.com/MinecraftForge/MinecraftForge) and similar

This project is not official by mojang and does not relate to it.
"""
import asyncio
import os
import pickle
import sys
import typing

import aiofiles
import mcpython.common.event.Registry
import mcpython.common.world.datafixers.IDataFixer
import mcpython.common.world.serializer.IDataSerializer
import mcpython.util.picklemagic
import simplejson as json
from mcpython import shared
from mcpython.engine import logger
from mcpython.engine.network.util import (
    ReadBuffer,
    TableIndexedOffsetTable,
    WriteBuffer,
    write_bin,
)

"""
How to decide when an new version is needed?
- you do better an new version in case of an update
- you may use the old one if your data is still compatible or it is auto-fixing it OR you were on an unstable 
    feature-branch
- you must increase the version number in case of any problems with loading new data arrays in compatible released 
    versions [e.g. an hotfix for an snapshot which changed some parts of the save]
    
When to remove the data-fixers from an version?
- the version is not played by anybody
- two major updated were in between
- the version was only short-living and is very outdated

How to remove an version
a) when the version is the last supported version of its kind, remove the DataFixer
b) when the version is an minor between versions, remove the DataFixer and change the one before to skip the removed one
c) when the version is an major version, remove all data-fixers up to the point

History of save versions:
- 1: introduced: 07.03.2020, outdated since: 10.03.2020, not loadable since: 12.12.2020
    - added save system
- 2: introduced: 10.03.2020, outdated since: 13.03.2020, not loadable since: 12.12.2020
    - removed temperature maps from saves
    - optimized landmass map in saves
- 3: introduced: 13.03.2020 [part of loot table update], outdated since: 31.03.2020, not loadable since: 12.12.2020
    - chest container stores now also the loot table link when set
- 4: introduced: 31.03.2020, outdated since: -, not loadable since: 12.12.2020
    - block coordinates are stored now relative to chunk; decreases chunk size
- 5: introduced: 17.03.2020 [part of entity update], outdated since: 11.06.2020, not loadable since: 12.12.2020
    - added entity serializer
- 6: introduced: 11.06.2020, outdated since: 12.12.2020, not loadable since: 12.12.2020
    - re-write of data fixer system, old still fix-able
    - removed "version"-attribute out of region files and inventory files
    - data fixers are applied to the WHOLE world ON LOAD, not when needed
- 7: introduced: 12.12.2020, outdated since: 21.05.2021, not loadable since: 21.05.2021
    - major code refactoring breaking nearly everything
    - player data reformat
- 10: introduced: 21.05.2021, outdated since: 26.10.2021, not loadable since: 26.10.2021
    - improved block palette
    - improved entity storage
    - removed some sanity checks for backwards compatibility
- 11: introduced: 26.10.2021, outdated since: 29.12.2021, not loadable since: 29.12.2021
    - chunk block data is now serialized via the network API, not the old storage API
- 12: introduced: 29.12.2021, outdated since: -, not loadable since: -
    - containers & data maps contain now their version
"""

# the latest version, used for upgrading
shared.STORAGE_VERSION = LATEST_VERSION = 12

# where the stuff should be saved
SAVE_DIRECTORY = (
    shared.home + "/saves"
    if "--saves-directory" not in sys.argv
    else sys.argv[sys.argv.index("--saves-directory") + 1]
)


class DataFixerNotFoundException(Exception):
    pass


def register_storage_fixer(
    _, fixer: mcpython.common.world.datafixers.IDataFixer.IStorageVersionFixer
):
    SaveFile.storage_version_fixers.setdefault(fixer.FIXES_FROM, []).append(fixer)
    return fixer


def register_mod_fixer(
    _, fixer: mcpython.common.world.datafixers.IDataFixer.IModVersionFixer
):
    SaveFile.mod_fixers.setdefault(fixer.MOD_NAME, {}).setdefault(
        fixer.FIXES_FROM, []
    ).append(fixer)
    return fixer


class RegionFileAccess:
    def __init__(self, save_file: "SaveFile", file: str, data: bytes):
        self.data = data
        self.file = file
        self.save_file = save_file
        self.table: TableIndexedOffsetTable | None = None

    async def decode(self):
        buffer = ReadBuffer(self.data)
        self.table: TableIndexedOffsetTable = await buffer.read_named_offset_table()

    async def get_chunk_data(self, cx: int, cz: int) -> ReadBuffer:
        try:
            return ReadBuffer(await self.table.getByName(f"{cx}::{cz}"))
        except KeyError:
            pass

    async def write_chunk_data(self, cx: int, cz: int, data: WriteBuffer | bytes):
        if isinstance(data, bytes):
            data = WriteBuffer().write_const_bytes(data)
        self.table.writeData(f"{cx}::{cz}", data)

    async def dump(self):
        # todo: add scheduler for dumping region files to storage for later
        buffer = WriteBuffer()
        await self.table.assemble(buffer, write_bin)

        await self.save_file.dump_via_network_buffer(self.file, buffer)


class UnableToFixDataException(Exception):
    pass


class SaveFile:
    """
    Interface to a stored file on the disk
    Used to load certain parts into the system & store them

    Contains the registries for data fixers
    """

    storage_version_fixers = {}
    mod_fixers = {}

    storage_fixer_registry = mcpython.common.event.Registry.Registry(
        "minecraft:storage_fixer",
        ["minecraft:storage_version_fixer"],
        "stage:datafixer:general",
        injection_function=register_storage_fixer,
        dump_content_in_saves=False,
    )
    mod_fixer_registry = mcpython.common.event.Registry.Registry(
        "minecraft:mod_fixer",
        ["minecraft:mod_version_fixer"],
        "stage:datafixer:general",
        injection_function=register_mod_fixer,
        dump_content_in_saves=False,
    )
    group_fixer_registry = mcpython.common.event.Registry.Registry(
        "minecraft:group_fixer",
        ["minecraft:group_fixer"],
        "stage:datafixer:general",
        dump_content_in_saves=False,
    )
    part_fixer_registry = mcpython.common.event.Registry.Registry(
        "minecraft:part_fixer",
        ["minecraft:part_fixer"],
        "stage:datafixer:parts",
        dump_content_in_saves=False,
    )

    def __init__(self, directory_name: str):
        """
        Creates a new SaveFile object, normally not needed for the modder
        :param directory_name: the name of the directory
        """
        self.directory = os.path.join(SAVE_DIRECTORY, directory_name)
        self.version = LATEST_VERSION
        self.save_in_progress = False
        self.region_accesses = {}

    def region_iterator(self):
        """
        Iterator iterating over ALL region files from a save file
        todo: can we cache this data somewhere?
        """
        for dim in os.listdir(self.directory + "/dim"):
            for region in os.listdir(self.directory + "/dim/" + dim):
                yield dim, region

    async def load_world_async(self):
        """
        Async-loads all setup-data into the world using the default configuration for worlds
        """
        await shared.world.cleanup()  # make sure everything is removed before we start

        try:
            await self.read_async("minecraft:general")

            # Data fixers sadly cannot be applied async, so here we go...
            while self.version != LATEST_VERSION:
                if self.version not in self.storage_version_fixers:
                    logger.println(
                        "[ERROR] unable to data-fix world. No data fixer found for version {}".format(
                            self.version
                        )
                    )
                    await shared.world.cleanup()

                    if shared.IS_CLIENT:
                        await shared.state_handler.change_state("minecraft:start_menu")
                    else:
                        sys.exit(-1)
                    raise UnableToFixDataException("See log")

                fixers = self.storage_version_fixers[self.version]
                if len(fixers) > 1:
                    # search for the one fixing to the nearest version to the searched for
                    fixer = min(fixers, key=lambda f: abs(LATEST_VERSION - f.FIXES_TO))
                else:
                    fixer = fixers[0]

                await self.apply_storage_fixer_async(fixer.NAME)
                await self.read_async("minecraft:general")
                self.version = fixer.FIXES_TO

            await self.dump_async(None, "minecraft:general")

            await asyncio.gather(
                self.read_async("minecraft:player_data"),
                self.read_async("minecraft:gamerule"),
                self.read_async("minecraft:registry_info_serializer"),
            )

        except mcpython.common.world.serializer.IDataSerializer.MissingSaveException:
            logger.println(
                "[WARN] save '{}' not found, falling back to selection menu".format(
                    self.directory
                )
            )
            await shared.world.cleanup()
            await shared.state_handler.change_state("minecraft:world_selection")
            return

        except (SystemExit, KeyboardInterrupt, OSError):
            raise

        except:  # lgtm [py/catch-base-exception]
            await shared.world.cleanup()
            await shared.state_handler.change_state("minecraft:start_menu")
            logger.print_exception(
                "exception during loading world. falling back to start menu..."
            )
            return

    async def save_world_async(self, *_, override=False):
        """
        Save all base-data into the system
        :param _: used when used by special event triggers
        :param override: flag for saving the chunks
        """
        if self.save_in_progress:
            raise IOError("can't save world. save in process")

        try:
            # Make sure that nothing else is going on...
            self.save_in_progress = True
            shared.world_generation_handler.enable_generation = False

            logger.println("saving world...")
            await self.dump_async(None, "minecraft:general")

            await asyncio.gather(
                self.dump_async(None, "minecraft:player_data"),
                self.dump_async(None, "minecraft:gamerule"),
                self.dump_async(None, "minecraft:registry_info_serializer"),
            )

            async def save_dimension(dimension):
                if not dimension.chunks:
                    return

                logger.println("saving dimension " + dimension.get_name())

                count = len(dimension.chunks)

                print(end="")
                for i, chunk in enumerate(dimension.chunks):
                    print(
                        "\r"
                        + str(round((i + 1) / count * 100))
                        + "% ("
                        + str(i + 1)
                        + "/"
                        + str(count)
                        + ")",
                        end="",
                    )
                    # todo: save all loaded dimension, not only the active one
                    if dimension.get_chunk(*chunk).loaded:
                        await self.dump_async(
                            None,
                            "minecraft:chunk",
                            dimension=dimension.id,
                            chunk=chunk,
                            override=override,
                        )

                print()

            await asyncio.gather(
                *(save_dimension(d) for d in shared.world.dimensions.values())
            )

            logger.println("save complete!")

            # And open the system again
            shared.world_generation_handler.enable_generation = True
            self.save_in_progress = False

        except (SystemExit, KeyboardInterrupt, OSError):
            raise

        except:  # lgtm [py/catch-base-exception]
            if shared.IS_CLIENT:
                logger.print_exception(
                    "Exception during saving world. Falling back to start menu"
                )
                await shared.world.cleanup()
                await shared.state_handler.change_state("minecraft:start_menu")

            else:
                logger.print_exception("Exception during saving world")
                await shared.NETWORK_MANAGER.disconnect()
                sys.exit(-1)

    async def apply_storage_fixer_async(self, name: str, *args, **kwargs):
        """
        Will apply a fixer to fix the storage version
        :param name: the name of the fixer to use
        :param args: the args to send
        :param kwargs: the kwargs to use
        :raises DataFixerNotFoundException: if the name is invalid
        """
        if name not in self.storage_fixer_registry.entries:
            raise DataFixerNotFoundException(name)

        fixer: mcpython.common.world.datafixers.IDataFixer.IStorageVersionFixer = (
            self.storage_fixer_registry.entries[name]
        )

        try:
            await fixer.apply(self, *args, **kwargs)
            await asyncio.gather(
                *(
                    self.apply_group_fixer_async(*args, **kwargs)
                    for name, args, kwargs in fixer.GROUP_FIXER_NAMES
                )
            )

        except (SystemExit, KeyboardInterrupt, OSError):
            raise

        except:  # lgtm [py/catch-base-exception]
            logger.print_exception(
                "during data-fixing storage version '{}'".format(name)
            )
            await shared.state_handler.change_state("minecraft:start_menu")

    async def apply_group_fixer_async(self, name: str, *args, **kwargs):
        """
        Will apply a group fixer to the system
        :param name: the name of the group fixer to use
        :param args: the args to use
        :param kwargs: the kwargs to use
        :raises DataFixerNotFoundException: if the name is invalid
        """
        if name not in self.group_fixer_registry.entries:
            raise DataFixerNotFoundException(name)

        fixer: mcpython.common.world.datafixers.IDataFixer.IGroupFixer = (
            self.group_fixer_registry.entries[name]
        )

        try:
            await fixer.apply(self, *args, **kwargs)
            await asyncio.gather(
                *(
                    self.apply_group_fixer_async(*args, **kwargs)
                    for name, args, kwargs in fixer.GROUP_FIXER_NAMES
                )
            )

        except (SystemExit, KeyboardInterrupt, OSError):
            raise
        except:  # lgtm [py/catch-base-exception]
            logger.print_exception(
                "During data-fixing group fixer '{}' (FATAL)".format(name)
            )
            await shared.world.cleanup()
            await shared.state_handler.change_state("minecraft:start_menu")

    async def apply_part_fixer_async(self, name: str, *args, **kwargs):
        """
        Will apply a part fixer to the system
        :param name: the name to use
        :param args: the args to send
        :param kwargs: the kwargs
        :raises DataFixerNotFoundException: if the name is invalid
        """
        if name not in self.part_fixer_registry.entries:
            raise DataFixerNotFoundException(name)

        fixer: mcpython.common.world.datafixers.IDataFixer.IPartFixer = (
            self.part_fixer_registry.entries[name]
        )

        try:
            await fixer.apply(self, *args, **kwargs)
        except:  # lgtm [py/catch-base-exception]
            logger.print_exception("During data-fixing part '{}' (fatal)".format(name))
            await shared.world.cleanup()
            await shared.state_handler.change_state("minecraft:start_menu")

    async def apply_mod_fixer_async(
        self, modname: str, source_version: tuple, *args, **kwargs
    ):
        """
        Applies a mod fixer(list) to the system
        :param modname: the mod name
        :param source_version: where to start from
        :param args: args to call with
        :param kwargs: kwargs to call with
        :raises DataFixerNotFoundException: if the name is invalid
        """
        if modname not in self.mod_fixers or modname not in shared.mod_loader.mods:
            raise DataFixerNotFoundException(modname)

        instance = shared.mod_loader.mods[modname]
        fixers = self.mod_fixers[modname]

        while instance.version != source_version:
            possible_fixers = set()
            for fixer in fixers:
                if source_version is None or (
                    len(fixer.FIXES_FROM) == len(source_version)
                    and source_version <= fixer.FIXES_FROM
                ):
                    possible_fixers.add(fixer)

            if len(possible_fixers) == 0:
                return

            if source_version is not None or len(possible_fixers) == 1:
                fixer: mcpython.common.world.datafixers.IDataFixer.IModVersionFixer = (
                    fixers[0]
                )
            else:
                fixer: mcpython.common.world.datafixers.IDataFixer.IModVersionFixer = (
                    min(
                        possible_fixers,
                        key=lambda v: self._get_distance(v, source_version),
                    )
                )

            try:
                await fixer.apply(self, *args, **kwargs)
                await asyncio.gather(
                    [
                        self.apply_group_fixer_async(name, *args, **kwargs)
                        for (name, args, kwargs) in fixer.GROUP_FIXER_NAMES
                    ]
                )
                await asyncio.gather(
                    [
                        self.apply_part_fixer_async(name, *args, **kwargs)
                        for (name, args, kwargs) in fixer.PART_FIXER_NAMES
                    ]
                )
            except (SystemExit, KeyboardInterrupt, OSError):
                raise
            except:  # lgtm [py/catch-base-exception]
                logger.print_exception(
                    "during data-fixing mod {} from {} to {} (fatal)".format(
                        modname, fixer.FIXES_FROM, fixer.FIXES_TO
                    )
                )
                await shared.world.cleanup()
                await shared.state_handler.change_state("minecraft:start_menu")
                return

            source_version = fixer.FIXES_TO

    @classmethod
    def _get_distance(cls, v, t):
        s = 0
        for i in range(len(v)):
            f = len(v) - i - 1
            s += 100**f * abs(v[i] - t[i])
        return s

    @classmethod
    def get_serializer_for(cls, part):
        for (
            serializer
        ) in (
            mcpython.common.world.serializer.IDataSerializer.data_serializer_registry.entries.values()
        ):
            if serializer.PART == part:
                return serializer

        raise ValueError("can't find serializer named '{}'".format(part))

    async def read_async(self, part, **kwargs):
        """
        Reads a part of the save-file
        :param part: the part to load
        :param kwargs: kwargs given to the loader
        :return: whatever the loader returns
        """
        try:
            return await self.get_serializer_for(part).load(self, **kwargs)

        except (SystemExit, KeyboardInterrupt, OSError):
            raise

        except mcpython.common.world.serializer.IDataSerializer.InvalidSaveException:
            logger.print_exception(
                "during reading part '{}' from save files under '{}' with arguments {}".format(
                    part, self.directory, kwargs
                )
            )

    async def dump_async(self, data, part, **kwargs):
        """
        Similar to read(...), but the other way round.
        :param data: the data to store, optional, may be None
        :param part: the part to save
        :param kwargs: the kwargs to give the saver
        """
        try:
            await self.get_serializer_for(part).save(data, self, **kwargs)

        except (SystemExit, KeyboardInterrupt, OSError):
            raise

        except:
            logger.print_exception("during dumping {} to '{}'".format(data, part))

    # Helper functions for fixers, loaders and savers
    # todo: add nbt serializer

    async def access_file_json_async(self, file: str):
        """
        Access a saved json file
        :param file: the file to load
        :return: the data of the file or None if an error has occur
        """
        file = os.path.join(self.directory, file)
        if not os.path.isfile(file):
            return

        try:
            async with aiofiles.open(file) as f:
                return json.loads(await f.read())

        except (SystemExit, KeyboardInterrupt, OSError):
            raise
        except json.decoder.JSONDecodeError:
            logger.print_exception(
                "File '{}' seems to be corrupted, below the loader exception".format(
                    file
                )
            )
            return

    async def access_file_pickle_async(self, file: str):
        """
        Access save a pickle file
        :param file: the file to load
        :return: the data of the file or None if an error has occurred
        """
        file = os.path.join(self.directory, file)
        if not os.path.isfile(file):
            return
        try:
            async with aiofiles.open(file, mode="rb") as f:
                return mcpython.util.picklemagic.safe_loads(await f.read())

        except (pickle.UnpicklingError, EOFError, ModuleNotFoundError):
            logger.print_exception(
                "File '{}' seems to be corrupted. See error message for info, below the loading exception".format(
                    file
                )
            )
            return

        except (SystemExit, KeyboardInterrupt, OSError):
            raise

        except AttributeError:
            logger.print_exception(
                "Module changed in between code systems, leading into corrupted file {}".format(
                    file
                )
            )

    async def access_raw_async(self, file: str):
        """
        Access save a file in binary mode
        :param file: the file to load
        :return: the data of the file or None if an error has occurred
        """
        file = os.path.join(self.directory, file)
        if not os.path.isfile(file):
            return

        async with aiofiles.open(file, mode="rb") as f:
            return await f.read()

    async def access_via_network_buffer(self, file: str):
        data = await self.access_raw_async(file)
        return ReadBuffer(data) if data is not None else None

    async def dump_file_json_async(self, file: str, data):
        """
        saves stuff with json into the system
        :param file: the file to save to
        :param data: the data to save
        """
        file = os.path.join(self.directory, file)
        d = os.path.dirname(file)
        if not os.path.isdir(d):
            os.makedirs(d)
        try:
            data = json.dumps(data, indent="  ")
            async with aiofiles.open(file, mode="w") as f:
                await f.write(data)
        except (SystemExit, KeyboardInterrupt, OSError):
            raise
        except:
            logger.print_exception("during dumping {} to '{}'".format(data, file))

    async def dump_file_pickle_async(self, file: str, data):
        """
        Saves stuff with pickle into the system
        :param file: the file to save to
        :param data: the data to save
        """
        file = os.path.join(self.directory, file)
        d = os.path.dirname(file)
        if not os.path.isdir(d):
            os.makedirs(d)
        try:
            data = mcpython.util.picklemagic.safe_dumps(data)
            async with aiofiles.open(file, mode="wb") as f:
                await f.write(data)
        except (SystemExit, KeyboardInterrupt, OSError):
            raise
        except:  # lgtm [py/catch-base-exception]
            logger.print_exception("during dumping {} to '{}'".format(data, file))

    async def dump_raw_async(self, file: str, data: bytes):
        """
        saves bytes into the system
        :param file: the file to save to
        :param data: the data to save
        """
        file = os.path.join(self.directory, file)
        d = os.path.dirname(file)
        if not os.path.isdir(d):
            os.makedirs(d)
        async with aiofiles.open(file, mode="wb") as f:
            await f.write(data)

    async def dump_via_network_buffer(self, file: str, buffer: WriteBuffer):
        await self.dump_raw_async(file, buffer.get_data())

    async def get_region_access(
        self, dimension: str, region: typing.Tuple[int, int]
    ) -> RegionFileAccess:
        file = "dim/{}/{}_{}.region".format(dimension, *region)

        if file in self.region_accesses:
            return self.region_accesses[file]

        d = await self.access_raw_async(file)
        if d is None:
            d = WriteBuffer().write_int(0).get_data()

        obj = RegionFileAccess(self, file, d)
        await obj.decode()

        self.region_accesses[file] = obj

        return obj


@shared.mod_loader("minecraft", "stage:datafixer:general")
async def load_elements():
    from mcpython.common.world.datafixers.versions import blocks, data_maps
