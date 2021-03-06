"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
import simplejson as json
import os
import pickle
import sys

from mcpython import shared, logger
import mcpython.common.event.Registry
import mcpython.common.world.datafixers.IDataFixer
import mcpython.common.world.serializer.IDataSerializer

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
- 7: introduced: 12.12.2020, outdated since: -, not loadable since: -
    - major code refactoring breaking nearly everything
    - player data reformat
"""

shared.STORAGE_VERSION = LATEST_VERSION = 8  # the latest version, used for upgrading

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


def register_mod_fixer(
    _, fixer: mcpython.common.world.datafixers.IDataFixer.IModVersionFixer
):
    SaveFile.mod_fixers.setdefault(fixer.MOD_NAME, {}).setdefault(
        fixer.FIXES_FROM, []
    ).append(fixer)


class SaveFile:
    """
    Interface to an stored file on the disk
    Used to load certain parts into the system & store them
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
        Creates an new SaveFile object
        :param directory_name: the name of the directory
        """
        self.directory = os.path.join(SAVE_DIRECTORY, directory_name)
        self.version = LATEST_VERSION
        self.save_in_progress = False

    def region_iterator(self):
        """
        Iterator iterating over ALL region files from an save file
        """
        for dim in os.listdir(self.directory + "/dim"):
            for region in os.listdir(self.directory + "/dim/" + dim):
                yield dim, region

    def load_world(self):
        """
        loads all setup-data into the world
        """
        shared.world.cleanup()  # make sure everything is removed before we start
        try:
            self.read("minecraft:general")
            while self.version != LATEST_VERSION:
                if self.version not in self.storage_version_fixers:
                    logger.println(
                        "[ERROR] unable to data-fix world. No data fixer found for version {}".format(
                            self.version
                        )
                    )
                    shared.world.cleanup()
                    shared.state_handler.switch_to("minecraft:startmenu")
                    return
                fixers = self.storage_version_fixers[self.version]
                if len(fixers) > 1:
                    # search for the one fixing to the nearest version to the searched for
                    fixer = min(fixers, key=lambda f: abs(LATEST_VERSION - f.FIXES_TO))
                else:
                    fixer = fixers[0]
                self.apply_storage_fixer(fixer.NAME)
                self.read("minecraft:general")
                self.version = fixer.FIXES_TO
            self.dump(None, "minecraft:general")
            self.read("minecraft:player_data")
            self.read("minecraft:gamerule")
            self.read("minecraft:registry_info_serializer")
        except mcpython.common.world.serializer.IDataSerializer.MissingSaveException:
            logger.println(
                "[WARN] save '{}' not found, falling back to selection menu".format(
                    self.directory
                )
            )
            shared.world.cleanup()
            shared.state_handler.switch_to("minecraft:world_selection")
            return
        except:
            shared.world.cleanup()
            shared.state_handler.switch_to("minecraft:startmenu")
            logger.print_exception(
                "exception during loading world. falling back to start menu..."
            )
            return
        # todo: load data packs for save files and than enable the below
        # shared.commandparser.parse("/reload")

    def save_world(self, *_, override=False):
        """
        save all base-data into the system
        :param _: used when used by special event triggers
        :param override: flag for saving the chunks
        """
        if self.save_in_progress:
            raise IOError("can't save world. save in process")
        try:
            self.save_in_progress = True
            shared.world_generation_handler.enable_generation = False
            logger.println("saving world...")
            self.dump(None, "minecraft:general")
            self.dump(None, "minecraft:player_data")
            self.dump(None, "minecraft:gamerule")
            self.dump(None, "minecraft:registry_info_serializer")
            for chunk in shared.world.get_active_dimension().chunks:
                # todo: save all loaded dimension, not only the active one
                if shared.world.get_active_dimension().get_chunk(*chunk).loaded:
                    self.dump(
                        None,
                        "minecraft:chunk",
                        dimension=shared.world.get_active_player().dimension.id,
                        chunk=chunk,
                        override=override,
                    )
            logger.println("save complete!")
            shared.world_generation_handler.enable_generation = True
        except:
            shared.world.cleanup()
            shared.state_handler.switch_to("minecraft:startmenu")
            logger.print_exception(
                "exception during saving world. falling back to start menu..."
            )
        self.save_in_progress = False

    def apply_storage_fixer(self, name: str, *args, **kwargs):
        """
        will apply an fixer to fix the storage version
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
            fixer.apply(self, *args, **kwargs)
            for name, args, kwargs in fixer.GROUP_FIXER_NAMES:
                self.apply_group_fixer(*args, **kwargs)
        except:
            logger.print_exception(
                "during data-fixing storage version '{}'".format(name)
            )
            shared.state_handler.switch_to("minecraft:startmenu")

    def apply_group_fixer(self, name: str, *args, **kwargs):
        """
        will apply an group fixer to the system
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
            fixer.apply(self, *args, **kwargs)
            for name, args, kwargs in fixer.PART_FIXER_NAMES:
                self.apply_part_fixer(name, *args, **kwargs)
        except:
            logger.print_exception("during data-fixing group fixer '{}'".format(name))
            shared.state_handler.switch_to("minecraft:startmenu")

    def apply_part_fixer(self, name: str, *args, **kwargs):
        """
        will apply an part fixer to the system
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
            fixer.apply(self, *args, **kwargs)
        except:
            logger.print_exception("during data-fixing part '{}'".format(name))
            shared.state_handler.switch_to("minecraft:startmenu")

    def apply_mod_fixer(self, modname: str, source_version: tuple, *args, **kwargs):
        """
        applies an mod fixer(list) to the system
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
                fixer.apply(self, *args, **kwargs)
                [
                    self.apply_group_fixer(name, *args, **kwargs)
                    for (name, args, kwargs) in fixer.GROUP_FIXER_NAMES
                ]
                [
                    self.apply_part_fixer(name, *args, **kwargs)
                    for (name, args, kwargs) in fixer.PART_FIXER_NAMES
                ]
            except:
                logger.print_exception(
                    "during data-fixing mod {} from {} to {}".format(
                        modname, fixer.FIXES_FROM, fixer.FIXES_TO
                    )
                )
                shared.state_handler.switch_to("minecraft:startmenu")
                return

            source_version = fixer.FIXES_TO

    @classmethod
    def _get_distance(cls, v, t):
        s = 0
        for i in range(len(v)):
            f = len(v) - i - 1
            s += 100 ** f * abs(v[i] - t[i])
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

    def read(self, part, **kwargs):
        """
        reads an part of the save-file
        :param part: the part to load
        :param kwargs: kwargs given to the loader
        :return: whatever the loader returns
        """
        try:
            return self.get_serializer_for(part).load(self, **kwargs)
        except mcpython.common.world.serializer.IDataSerializer.InvalidSaveException:
            logger.print_exception(
                "during reading part '{}' from save files under '{}' with arguments {}".format(
                    part, self.directory, kwargs
                )
            )

    def dump(self, data, part, **kwargs):
        """
        similar to read(...), but the other way round.
        :param data: the data to store, optional, may be None
        :param part: the part to save
        :param kwargs: the kwargs to give the saver
        """
        try:
            self.get_serializer_for(part).save(data, self, **kwargs)
        except:
            logger.print_exception("during dumping {} to '{}'".format(data, part))

    # Helper functions for fixers, loaders and savers
    # todo: add nbt serializer

    def access_file_json(self, file: str):
        """
        access save an json file
        :param file: the file to load
        :return: the data of the file or None if an error has occur
        """
        file = os.path.join(self.directory, file)
        if not os.path.isfile(file):
            return
        try:
            with open(file) as f:
                return json.load(f)
        except json.decoder.JSONDecodeError:
            logger.println(
                "[SAVE][CORRUPTED] file '{}' seems to be corrupted".format(file)
            )
            return

    def access_file_pickle(self, file: str):
        """
        Access save a pickle file
        :param file: the file to load
        :return: the data of the file or None if an error has occur
        """
        file = os.path.join(self.directory, file)
        if not os.path.isfile(file):
            return
        try:
            with open(file, mode="rb") as f:
                return pickle.load(f)
        except (pickle.UnpicklingError, EOFError, ModuleNotFoundError):
            logger.println(
                "[SAVE][CORRUPTED] file '{}' seems to be corrupted. See error message for info".format(
                    file
                )
            )
            return
        except AttributeError:
            logger.println(
                "[SAVE][INVALID] module changed in between code systems, leading into corrupted file {}".format(
                    file
                )
            )

    def access_raw(self, file: str):
        """
        Access save a file in binary mode
        :param file: the file to load
        :return: the data of the file or None if an error has occur
        """
        file = os.path.join(self.directory, file)
        if not os.path.isfile(file):
            return
        with open(file, mode="rb") as f:
            return f.read()

    def dump_file_json(self, file: str, data):
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
            with open(file, mode="w") as f:
                f.write(data)
        except:
            logger.print_exception("during dumping {} to '{}'".format(data, file))

    def dump_file_pickle(self, file: str, data):
        """
        saves stuff with pickle into the system
        :param file: the file to save to
        :param data: the data to save
        """
        file = os.path.join(self.directory, file)
        d = os.path.dirname(file)
        if not os.path.isdir(d):
            os.makedirs(d)
        try:
            data = pickle.dumps(data)
            with open(file, mode="wb") as f:
                return f.write(data)
        except:
            logger.print_exception("during dumping {} to '{}'".format(data, file))

    def dump_raw(self, file: str, data: bytes):
        """
        saves bytes into the system
        :param file: the file to save to
        :param data: the data to save
        """
        file = os.path.join(self.directory, file)
        d = os.path.dirname(file)
        if not os.path.isdir(d):
            os.makedirs(d)
        with open(file, mode="wb") as f:
            return f.write(data)


@shared.mod_loader("minecraft", "stage:datafixer:general")
def load_elements():
    from mcpython.common.world.datafixers import DataFixer7to8
