"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import storage.datafixer.IDataFixer
import storage.serializer.IDataSerializer
import json
import pickle
import os
import logger
import traceback
import sys

"""
History of save versions:
- 1: introduced: 07.03.2020, outdated since: -, not loadable since: -
"""


LATEST_VERSION = 1

G.STORAGE_VERSION = LATEST_VERSION

SAVE_DIRECTORY = G.local+"/saves" if "--saves-directory" not in sys.argv else \
    sys.argv[sys.argv.index("--saves-directory")+1]


class SaveFile:
    def __init__(self, directory_name):
        self.directory = os.path.join(SAVE_DIRECTORY, directory_name)
        self.version = LATEST_VERSION
        self.save_in_progress = False

    def load_world(self):
        G.world.cleanup()
        self.read("minecraft:general")

        while self.version != LATEST_VERSION:
            if self.version not in storage.datafixer.IDataFixer.generaldatafixerregistry.registered_object_map:
                raise IOError("unsupported storage version '{}'. Latest: '{}', Found transformers from: '{}'".format(
                    self.version, LATEST_VERSION, "', '".join(
                        storage.datafixer.IDataFixer.generaldatafixerregistry.registered_object_map.keys())))
            generaldatafixer = storage.datafixer.IDataFixer.generaldatafixerregistry.registered_object_map[self.version]
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

    def save_world(self, *_, override=False):
        if self.save_in_progress: raise IOError("can't save world. save in process")
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
        self.save_in_progress = False

    def upgrade(self, part=None, version=None, **kwargs):
        """
        upgrades the part of the SaveFile to the latest version supported
        :param part: the part to update, or None, if all should upgrade
        :param kwargs: kwargs given to the fixers
        :param version: which version to upgrade from
        """
        if version is None: version = self.version
        new_version = None
        flag = True
        while flag:
            for fixer in storage.datafixer.IDataFixer.datafixerregistry.registered_object_map.values():
                if fixer.TRANSFORMS[0] == version and (part is None or part == fixer.PART):
                    fixer.fix(self, **kwargs)
                    if fixer.TRANSFORMS[1] == LATEST_VERSION:
                        flag = False
                    else:
                        new_version = fixer.TRANSFORMS[1]
            version = new_version

    def read(self, part, **kwargs):
        """
        reads an part of the save-file
        :param part: the part to load
        :param kwargs: kwargs given to the loader
        :return: whatever the loader returns
        """
        for serializer in storage.serializer.IDataSerializer.dataserializerregistry.registered_object_map.values():
            if serializer.PART == part:
                try:
                    return serializer.load(self, **kwargs)
                except storage.serializer.IDataSerializer.InvalidSaveException:
                    traceback.print_exc()
                    logger.write_exception("during writing part '{}' to save files under '{}' with arguments {}".
                                           format(part, self.directory, kwargs))
                    return
        raise ValueError("can't find serializer named '{}'".format(part))

    def dump(self, data, part, **kwargs):
        """
        similar to read(...), but the other way round.
        :param data: the data to store, optional, may be None
        :param part: the part to save
        :param kwargs: the kwargs to give the saver
        """
        for serializer in storage.serializer.IDataSerializer.dataserializerregistry.registered_object_map.values():
            if serializer.PART == part:
                serializer.save(data, self, **kwargs)
                return
        raise ValueError("can't find serializer named '{}'".format(part))

    # Helper functions for fixers, loaders and savers
    # todo: add nbt serializer

    def access_file_json(self, file):
        file = os.path.join(self.directory, file)
        if not os.path.isfile(file): return None
        try:
            with open(file) as f: return json.load(f)
        except json.decoder.JSONDecodeError:
            logger.println("[SAVE][CORRUPTED] file '{}' seems to be corrupted".format(file))
            return None

    def access_file_pickle(self, file):
        file = os.path.join(self.directory, file)
        if not os.path.isfile(file): return None
        try:
            with open(file, mode="rb") as f: return pickle.load(f)
        except (pickle.UnpicklingError, EOFError):
            logger.println("[SAVE][CORRUPTED] file '{}' seems to be corrupted".format(file))
            return None

    def access_raw(self, file):
        file = os.path.join(self.directory, file)
        if not os.path.isfile(file): return None
        with open(file, mode="rb") as f: return f.read()

    def dump_file_json(self, file, data):
        file = os.path.join(self.directory, file)
        d = os.path.dirname(file)
        if not os.path.isdir(d): os.makedirs(d)
        data = json.dumps(data)
        with open(file, mode="w") as f: f.write(data)

    def dump_file_pickle(self, file, data):
        file = os.path.join(self.directory, file)
        d = os.path.dirname(file)
        if not os.path.isdir(d): os.makedirs(d)
        data = pickle.dumps(data)
        with open(file, mode="wb") as f: return f.write(data)

    def dump_raw(self, file, data):
        file = os.path.join(self.directory, file)
        d = os.path.dirname(file)
        if not os.path.isdir(d): os.makedirs(d)
        with open(file, mode="wb") as f: return f.write(data)


