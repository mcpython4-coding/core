"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import mcpython.event.Registry
from abc import ABC


class IDataFixer(mcpython.event.Registry.IRegistryContent):
    FIXES_FROM = None
    FIXES_TO = None

    @classmethod
    def apply(cls, savefile, *args):
        pass


class IStorageVersionFixer(IDataFixer, ABC):
    """
    Fixer for fixing an save from an old save format.
    Only implemented internally
    """
    TYPE = "minecraft:storage_version_fixer"

    GROUP_FIXER_NAMES = []  # an list of (name_of_group_fixer, args, kwargs) to apply when trying to load


class IModVersionFixer(IDataFixer, ABC):
    """
    Fixer for another mod version. Can be used by mods to make old versions compatible.
    Used internally also for the core data.
    FIXES_FROM and FIXES_TO contain the mod versions.

    FIXES_FROM may be None if it should be applied when the mod gets added to the save file.
    FIXES_TO may be None if it is an cleanup-fixer
    """
    TYPE = "minecraft:mod_version_fixer"

    MOD_NAME = None  # the mod name to fix under

    GROUP_FIXER_NAMES = []  # an list of (name_of_group_fixer, args, kwargs) to apply when trying to load
    PART_FIXER_NAMES = []  # an list of (name_of_part_fixer, args, kwargs) to apply when trying to load


class IGroupFixer(IDataFixer, ABC):
    """
    Fixer for an certain data group (e.g. the gamerule data or an chunk in the world).
    Mods can implement their own files in saves and use these to fix them
    """
    TYPE = "minecraft:group_fixer"

    PART_FIXER_NAMES = []  # an list of (name_of_part_fixer, args, kwargs) to apply when fixing


class IPartFixer(IDataFixer, ABC):
    """
    Fixer for an part of an IGroupFixer. Certain files are able to contain data from different mods.
    Mods can register data fixers to fix their own data
    """
    TYPE = "minecraft:part_fixer"

    TARGET_SERIALIZER_NAME = None  # the name of the fixer dedicated to these part

    @classmethod
    def apply(cls, savefile, *args, **kwargs):
        """
        default implementation of the IPartFixer apply() calling apply_part_fixer(cls) on the SERIALIZER specified
        by TARGET_SERIALIZER_NAME
        Mods may want to override this method when doing other special stuff
        """
        savefile.get_serializer_for(cls.TARGET_SERIALIZER_NAME).apply_part_fixer(savefile, cls, *args, **kwargs)

