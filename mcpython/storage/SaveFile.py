"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import mcpython.storage.datafixer.IDataFixer
import mcpython.storage.serializer.IDataSerializer
import json
import pickle
import os
import logger
import sys

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
- 1: introduced: 07.03.2020, outdated since: 10.03.2020, not loadable since: -
    - added save system
- 2: introduced: 10.03.2020, outdated since: 13.03.2020, not loadable since: -
    - removed temperature maps from saves
    - optimized landmass map in saves
- 3: introduced: 13.03.2020 [part of loot table update], outdated since: 31.03.2020, not loadable since: -
    - chest container stores now also the loot table link when set
- 4: introduced: 31.03.2020, outdated since: -, not loadable since: -
    - block coordinates are stored now relative to chunk; decreases chunk size
- 5: introduced: 17.03.2020 [part of entity update], outdated since: -, not loadable since: -
    - added entity serializer
"""


G.STORAGE_VERSION = LATEST_VERSION = 5  # the latest version, used for upgrading

# where the stuff should be saved
SAVE_DIRECTORY = G.home+"/saves" if "--saves-directory" not in sys.argv else \
    sys.argv[sys.argv.index("--saves-directory")+1]


class SaveFile:
    """
    Interface to an stored file on the disk
    Used to load certain parts into the system & store them
    """

    def __init__(self, directory_name: str):
        """
        Creates an new SaveFile object
        :param directory_name: the name of the directory
        """
        self.directory = os.path.join(SAVE_DIRECTORY, directory_name)
        self.version = LATEST_VERSION
        self.save_in_progress = False

    def load_world(self):
        """
        loads all setup-data into the world
        """
        G.world.cleanup()
        try:
            self.read("minecraft:general")

            while self.version != LATEST_VERSION:
                if self.version not in mcpython.storage.datafixer.IDataFixer.generaldatafixerregistry.registered_object_map:
                    raise IOError("unsupported storage version '{}'. Latest: '{}', Found transformers from: '{}'".format(
                        str(self.version), str(LATEST_VERSION), "', '".join(
                            [str(e) for e in mcpython.storage.datafixer.IDataFixer.generaldatafixerregistry.registered_object_map.
                                keys()])))
                generaldatafixer = mcpython.storage.datafixer.IDataFixer.generaldatafixerregistry.registered_object_map[self.version]
                for fix in generaldatafixer.LOAD_FIXES:
                    if type(fix) != tuple:
                        self.upgrade(fix)
                    else:
                        self.upgrade(fix[0], **fix[1])
                self.version = generaldatafixer.UPGRADES_TO

            self.dump(None, "minecraft:general")
            self.read("minecraft:player_data")
            self.read("minecraft:gamerule")
            self.read("minecraft:registry_info_serializer")
        except mcpython.storage.serializer.IDataSerializer.MissingSaveException:
            logger.println("[WARN] save '{}' not found, falling back to selection menu".format(self.directory))
            G.world.cleanup()
            G.statehandler.switch_to("minecraft:world_selection")
        except:
            G.world.cleanup()
            G.statehandler.switch_to("minecraft:startmenu")
            logger.write_exception("exception during loading world. falling back to start menu...")

    def save_world(self, *_, override=False):
        """
        save all base-data into the system
        :param _: used when used by special event triggers
        :param override: flag for saving the chunks
        """
        if self.save_in_progress: raise IOError("can't save world. save in process")
        try:
            self.save_in_progress = True
            G.worldgenerationhandler.enable_generation = False
            print("saving world...")
            self.dump(None, "minecraft:general")
            self.dump(None, "minecraft:player_data")
            self.dump(None, "minecraft:gamerule")
            self.dump(None, "minecraft:registry_info_serializer")
            for chunk in G.world.get_active_dimension().chunks:
                if G.world.get_active_dimension().get_chunk(*chunk).loaded:
                    self.dump(None, "minecraft:chunk", dimension=G.world.active_dimension, chunk=chunk, override=override)
            print("save complete!")
            G.worldgenerationhandler.enable_generation = True
        except:
            G.world.cleanup()
            G.statehandler.switch_to("minecraft:startmenu")
            logger.write_exception("exception during saving world. falling back to start menu...")
        self.save_in_progress = False

    def upgrade(self, part=None, version=None, to=None, **kwargs):
        """
        upgrades the part of the SaveFile to the latest version supported
        :param part: the part to update, or None, if all should upgrade
        :param kwargs: kwargs given to the fixers
        :param version: which version to upgrade from
        :param to: to which version to upgrade to
        """
        if version is None: version = self.version
        if to is None: to = LATEST_VERSION
        new_version = None
        flag = True
        while flag:
            for fixer in mcpython.storage.datafixer.IDataFixer.datafixerregistry.registered_object_map.values():
                if fixer.TRANSFORMS[0] == version and (part is None or part == fixer.PART):
                    print("applying fixer '{}' with config {}".format(fixer.NAME, kwargs))
                    fixer.fix(self, **kwargs)
                    if fixer.TRANSFORMS[1] == to:
                        flag = False
                    else:
                        new_version = fixer.TRANSFORMS[1]
                    break
            else:
                raise mcpython.storage.datafixer.IDataFixer.DataFixerException(
                    "invalid version: '{}' to upgrade to '{}'. No datafixers found for the part '{}'!".format(version,
                                                                                                              to, part))
            version = new_version

    def read(self, part, **kwargs):
        """
        reads an part of the save-file
        :param part: the part to load
        :param kwargs: kwargs given to the loader
        :return: whatever the loader returns
        """
        for serializer in mcpython.storage.serializer.IDataSerializer.dataserializerregistry.registered_object_map.values():
            if serializer.PART == part:
                try:
                    return serializer.load(self, **kwargs)
                except mcpython.storage.serializer.IDataSerializer.InvalidSaveException:
                    logger.write_exception("during reading part '{}' from save files under '{}' with arguments {}".
                                           format(part, self.directory, kwargs))
                    raise
        raise ValueError("can't find serializer named '{}'".format(part))

    def dump(self, data, part, **kwargs):
        """
        similar to read(...), but the other way round.
        :param data: the data to store, optional, may be None
        :param part: the part to save
        :param kwargs: the kwargs to give the saver
        """
        for serializer in mcpython.storage.serializer.IDataSerializer.dataserializerregistry.registered_object_map.values():
            if serializer.PART == part:
                serializer.save(data, self, **kwargs)
                return
        raise ValueError("can't find serializer named '{}'".format(part))

    # Helper functions for fixers, loaders and savers
    # todo: add nbt serializer

    def access_file_json(self, file: str):
        """
        access save an json file
        :param file: the file to load
        :return: the data of the file or None if an error has occur
        """
        file = os.path.join(self.directory, file)
        if not os.path.isfile(file): return
        try:
            with open(file) as f: return json.load(f)
        except json.decoder.JSONDecodeError:
            logger.println("[SAVE][CORRUPTED] file '{}' seems to be corrupted".format(file))
            return

    def access_file_pickle(self, file: str):
        """
        access save an pickle file
        :param file: the file to load
        :return: the data of the file or None if an error has occur
        """
        file = os.path.join(self.directory, file)
        if not os.path.isfile(file): return
        try:
            with open(file, mode="rb") as f: return pickle.load(f)
        except (pickle.UnpicklingError, EOFError):
            logger.println("[SAVE][CORRUPTED] file '{}' seems to be corrupted".format(file))
            return

    def access_raw(self, file: str):
        """
        access save an file in binary mode
        :param file: the file to load
        :return: the data of the file or None if an error has occur
        """
        file = os.path.join(self.directory, file)
        if not os.path.isfile(file): return
        with open(file, mode="rb") as f: return f.read()

    def dump_file_json(self, file: str, data):
        """
        saves stuff with json into the system
        :param file: the file to save to
        :param data: the data to save
        """
        file = os.path.join(self.directory, file)
        d = os.path.dirname(file)
        if not os.path.isdir(d): os.makedirs(d)
        data = json.dumps(data)
        with open(file, mode="w") as f: f.write(data)

    def dump_file_pickle(self, file: str, data):
        """
        saves stuff with pickle into the system
        :param file: the file to save to
        :param data: the data to save
        """
        file = os.path.join(self.directory, file)
        d = os.path.dirname(file)
        if not os.path.isdir(d): os.makedirs(d)
        data = pickle.dumps(data)
        with open(file, mode="wb") as f: return f.write(data)

    def dump_raw(self, file: str, data: bytes):
        """
        saves bytes into the system
        :param file: the file to save to
        :param data: the data to save
        """
        file = os.path.join(self.directory, file)
        d = os.path.dirname(file)
        if not os.path.isdir(d): os.makedirs(d)
        with open(file, mode="wb") as f: return f.write(data)

